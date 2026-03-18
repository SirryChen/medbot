"""Drug interaction tool backed by DDInter."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlencode

import httpx

from medbot.agent.tools.base import Tool

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_2) AppleWebKit/537.36"
DDINTER_BASE_URL = "https://ddinter.scbdd.com"


def _normalize_name(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


@dataclass
class ResolvedDrug:
    query: str
    name: str
    internal_id: str


class DrugInteractionCheckTool(Tool):
    """Check drug-drug interactions using DDInter."""

    name = "drug_interaction_check"
    description = (
        "Check potential drug-drug interactions for 2-5 drugs by name using DDInter. "
        "Returns matched drugs, severity, interaction descriptions, and management guidance."
    )
    parameters = {
        "type": "object",
        "properties": {
            "drugs": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of 2-5 drug names to check",
            },
        },
        "required": ["drugs"],
    }

    def __init__(self, base_url: str = DDINTER_BASE_URL):
        self.base_url = base_url.rstrip("/")

    async def execute(self, drugs: list[str], **kwargs: Any) -> str:
        cleaned = list(OrderedDict.fromkeys(drug.strip() for drug in drugs if drug and drug.strip()))
        if len(cleaned) < 2:
            return "Error: provide at least two drug names"
        if len(cleaned) > 5:
            return "Error: provide at most five drug names"

        async with httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT, "X-Requested-With": "XMLHttpRequest"},
            follow_redirects=True,
            timeout=20.0,
            verify=False,
        ) as client:
            resolved: list[ResolvedDrug] = []
            for drug in cleaned:
                result = await self._resolve_drug(client, drug)
                if isinstance(result, str):
                    return result
                resolved.append(result)

            response = await client.post(
                f"{self.base_url}/ddinter/checker/",
                content=urlencode([("choices", item.internal_id) for item in resolved]),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            payload = response.json()
            return self._format_result(resolved, payload)

    async def _resolve_drug(self, client: httpx.AsyncClient, drug: str) -> ResolvedDrug | str:
        if len(drug) < 3:
            return f"Error: drug name '{drug}' must be at least 3 characters for DDInter lookup"

        response = await client.get(f"{self.base_url}/check-datasource/{quote(drug)}/")
        response.raise_for_status()
        candidates = response.json().get("data", [])
        if not candidates:
            return f"Error: DDInter could not find a drug matching '{drug}'"

        normalized_query = _normalize_name(drug)
        exact_matches = [
            item for item in candidates if _normalize_name(item.get("name", "")) == normalized_query
        ]
        if len(exact_matches) == 1:
            match = exact_matches[0]
            return ResolvedDrug(query=drug, name=match["name"], internal_id=match["internalID"])

        if len(candidates) == 1:
            match = candidates[0]
            return ResolvedDrug(query=drug, name=match["name"], internal_id=match["internalID"])

        suggestions = ", ".join(
            f"{item.get('name', '?')} [{item.get('internalID', '?')}]"
            for item in candidates[:5]
        )
        return (
            f"Error: ambiguous drug name '{drug}'. "
            f"Top DDInter matches: {suggestions}. Use a more specific generic name."
        )

    @staticmethod
    def _format_result(resolved: list[ResolvedDrug], payload: dict[str, Any]) -> str:
        resolved_line = ", ".join(f"{item.name} [{item.internal_id}]" for item in resolved)
        state = payload.get("state", "")
        lines = [
            "DDInter drug interaction review",
            f"Resolved drugs: {resolved_line}",
            "Source: https://ddinter.scbdd.com/inter-checker/",
        ]

        if state == "none":
            lines.append("Result: DDInter returned no interaction records for this combination.")
            lines.append("Caution: absence of a record does not guarantee safety.")
            return "\n".join(lines)

        interactions = payload.get("data", [])
        if state != "success" or not interactions:
            lines.append("Result: DDInter did not return a usable interaction result.")
            return "\n".join(lines)

        level = payload.get("level", {})
        lines.append(
            "Severity counts: "
            f"major={level.get('3', 0)}, moderate={level.get('2', 0)}, "
            f"minor={level.get('1', 0)}, unknown={level.get('0', 0)}"
        )

        for idx, item in enumerate(interactions, start=1):
            lines.extend(
                [
                    "",
                    f"{idx}. {item.get('drug_a_name', '?')} <-> {item.get('drug_b_name', '?')}",
                    f"   Severity: {item.get('idx__level', 'Unknown')}",
                    f"   Description: {item.get('idx__interaction_description', '').strip()}",
                    f"   Management: {item.get('idx__management', '').strip()}",
                    f"   DDInter record ID: {item.get('id', '')}",
                ]
            )

        lines.append("")
        lines.append("Caution: DDInter states its database is incomplete and results are for reference only.")
        return "\n".join(lines)
