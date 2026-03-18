"""Dedicated tools for structured family records and doctor exports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from medbot.agent.tools.base import Tool
from medbot.medical_records import dump_result, export_member_record, update_family_member


class FamilyRecordTool(Tool):
    """Create or update a structured family record."""

    def __init__(self, workspace: Path):
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "family_record"

    @property
    def description(self) -> str:
        return (
            "Create or update a structured household medical record under family/<member_id>. "
            "Use this instead of write_file/edit_file for record.md, symptoms.md, or medications.md. "
            "Supports proactive capture of chronic conditions, symptoms, medications, allergies, "
            "family history, and other durable health facts."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        list_prop = {
            "type": "array",
            "items": {"type": "string"},
        }
        return {
            "type": "object",
            "properties": {
                "member_id": {"type": "string", "description": "Stable member id such as sirry, father, or mother"},
                "display_name": {"type": "string", "description": "Human-readable member name"},
                "sex": {"type": "string"},
                "birth_date": {"type": "string"},
                "height": {"type": "string"},
                "weight": {"type": "string"},
                "blood_type": {"type": "string"},
                "emergency_contact": {"type": "string"},
                "chronic_conditions": list_prop,
                "past_surgeries_or_hospitalizations": list_prop,
                "family_history": list_prop,
                "lifestyle_factors": list_prop,
                "drug_allergies": list_prop,
                "food_allergies": list_prop,
                "other_contraindications": list_prop,
                "diagnoses_or_concerns": list_prop,
                "current_clinicians": list_prop,
                "monitoring_goals": list_prop,
                "symptoms": list_prop,
                "medications": list_prop,
                "recent_reports": list_prop,
                "recent_metrics": list_prop,
                "red_flags": list_prop,
                "open_questions_for_clinician": list_prop,
                "reported_at": {"type": "string"},
            },
            "required": ["member_id"],
        }

    async def execute(self, member_id: str, **kwargs: Any) -> str:
        result = update_family_member(self._workspace, member_id, **kwargs)
        return (
            "Structured family record updated.\n"
            f"{dump_result(result)}"
        )


class ExportMedicalRecordTool(Tool):
    """Export a doctor-facing summary file for one household member."""

    def __init__(self, workspace: Path):
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "export_medical_record"

    @property
    def description(self) -> str:
        return (
            "Export a doctor-facing medical summary to family/<member_id>/doctor_export_<YYYYMMDD>.md. "
            "Use this instead of spawn or write_file when the user asks to export or prepare a record for a visit."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "member_id": {"type": "string", "description": "Stable member id such as sirry"},
                "questions_for_clinician": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional questions to include for the clinician",
                },
                "export_date": {
                    "type": "string",
                    "description": "Optional date tag in YYYYMMDD format; defaults to today",
                },
            },
            "required": ["member_id"],
        }

    async def execute(
        self,
        member_id: str,
        questions_for_clinician: list[str] | None = None,
        export_date: str | None = None,
        **kwargs: Any,
    ) -> str:
        path = export_member_record(
            self._workspace,
            member_id,
            questions_for_clinician=questions_for_clinician,
            export_date=export_date,
        )
        return (
            "Doctor summary exported successfully.\n"
            f"Path: {path}\n"
            "Tell the user this exact path."
        )
