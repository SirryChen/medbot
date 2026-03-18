"""Helpers for structured family medical records and doctor exports."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


def slugify_member_id(value: str) -> str:
    """Convert free text to a stable lowercase kebab-case member id."""
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "member"


def _clean_item(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value.rstrip(".,; ")


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        cleaned = _clean_item(item)
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(cleaned)
    return out


def _merge_items(existing: list[str], new_items: list[str] | None) -> list[str]:
    return _dedupe([*existing, *(new_items or [])])


def _split_list_field(value: str) -> list[str]:
    raw = (value or "").strip()
    if not raw or raw.lower() == "none recorded yet.":
        return []
    parts = re.split(r"\s*;\s*|\s*\|\s*", raw)
    return _dedupe(parts)


def _join_list(items: list[str]) -> str:
    return "; ".join(_dedupe(items))


def _join_summary(items: list[str], placeholder: str = "None recorded yet.") -> str:
    merged = _join_list(items)
    return merged or placeholder


def _now_label(ts: str | None = None) -> str:
    if ts:
        return ts.strip()
    return datetime.now().strftime("%Y-%m-%d %H:%M")


@dataclass
class RecordState:
    member_id: str
    display_name: str = ""
    preferred_name: str = ""
    sex: str = ""
    birth_date: str = ""
    height: str = ""
    weight: str = ""
    blood_type: str = ""
    emergency_contact: str = ""
    chronic_conditions: list[str] | None = None
    past_surgeries_or_hospitalizations: list[str] | None = None
    family_history: list[str] | None = None
    lifestyle_factors: list[str] | None = None
    drug_allergies: list[str] | None = None
    food_allergies: list[str] | None = None
    other_contraindications: list[str] | None = None
    active_diagnoses_or_concerns: list[str] | None = None
    current_clinicians: list[str] | None = None
    current_medications: list[str] | None = None
    monitoring_goals: list[str] | None = None
    recent_symptom_summary: list[str] | None = None
    recent_metrics_summary: list[str] | None = None
    recent_reports_summary: list[str] | None = None
    red_flags: list[str] | None = None
    open_questions_for_clinician: list[str] | None = None
    last_updated: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "chronic_conditions",
            "past_surgeries_or_hospitalizations",
            "family_history",
            "lifestyle_factors",
            "drug_allergies",
            "food_allergies",
            "other_contraindications",
            "active_diagnoses_or_concerns",
            "current_clinicians",
            "current_medications",
            "monitoring_goals",
            "recent_symptom_summary",
            "recent_metrics_summary",
            "recent_reports_summary",
            "red_flags",
            "open_questions_for_clinician",
        ):
            if getattr(self, field_name) is None:
                setattr(self, field_name, [])


def _default_record_state(member_id: str, display_name: str = "") -> RecordState:
    return RecordState(
        member_id=member_id,
        display_name=display_name,
        preferred_name=display_name,
    )


_LABEL_TO_ATTR: dict[str, str] = {
    "Member ID": "member_id",
    "Preferred name": "preferred_name",
    "Sex": "sex",
    "Birth date": "birth_date",
    "Height": "height",
    "Weight": "weight",
    "Blood type": "blood_type",
    "Emergency contact": "emergency_contact",
    "Chronic conditions": "chronic_conditions",
    "Past surgeries or hospitalizations": "past_surgeries_or_hospitalizations",
    "Family history": "family_history",
    "Lifestyle factors": "lifestyle_factors",
    "Drug allergies": "drug_allergies",
    "Food allergies": "food_allergies",
    "Other contraindications": "other_contraindications",
    "Active diagnoses or concerns": "active_diagnoses_or_concerns",
    "Current clinicians": "current_clinicians",
    "Current medications": "current_medications",
    "Monitoring goals": "monitoring_goals",
    "Recent Symptom Summary": "recent_symptom_summary",
    "Recent Metrics Summary": "recent_metrics_summary",
    "Recent Reports Summary": "recent_reports_summary",
    "Red flags": "red_flags",
    "Open questions for clinician": "open_questions_for_clinician",
    "Last updated": "last_updated",
}


_LIST_ATTRS = {
    "chronic_conditions",
    "past_surgeries_or_hospitalizations",
    "family_history",
    "lifestyle_factors",
    "drug_allergies",
    "food_allergies",
    "other_contraindications",
    "active_diagnoses_or_concerns",
    "current_clinicians",
    "current_medications",
    "monitoring_goals",
    "recent_symptom_summary",
    "recent_metrics_summary",
    "recent_reports_summary",
    "red_flags",
    "open_questions_for_clinician",
}


_REQUIRED_SECTIONS = (
    "## Identity",
    "## Baseline Conditions",
    "## Allergies And Contraindications",
    "## Active Care Plan",
    "## Recent Symptom Summary",
    "## Recent Metrics Summary",
    "## Recent Reports Summary",
    "## Safety Notes",
)


def parse_record(record_path: Path, member_id: str, display_name: str = "") -> RecordState:
    """Parse a structured record file; fallback to a clean default state."""
    if not record_path.exists():
        return _default_record_state(member_id, display_name)

    text = record_path.read_text(encoding="utf-8").strip()
    if not text:
        return _default_record_state(member_id, display_name)

    if not all(marker in text for marker in _REQUIRED_SECTIONS):
        first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
        if first_line.startswith("# "):
            first_line = first_line[2:].strip()
        if first_line and len(first_line) <= 60 and first_line.count(",") <= 1:
            display_name = display_name or first_line
        return _default_record_state(member_id, display_name)

    state = _default_record_state(member_id, display_name)
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            state.display_name = stripped[2:].strip()
            continue
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        label, value = stripped[2:].split(":", 1)
        attr = _LABEL_TO_ATTR.get(label.strip())
        if not attr:
            continue
        value = value.strip()
        if attr in _LIST_ATTRS:
            setattr(state, attr, _split_list_field(value))
        else:
            setattr(state, attr, value)

    if not state.display_name:
        state.display_name = display_name or state.preferred_name or member_id
    if not state.preferred_name:
        state.preferred_name = state.display_name
    return state


def render_record(state: RecordState) -> str:
    """Render a clean, deduplicated record.md."""
    display_name = state.display_name or state.preferred_name or state.member_id
    preferred_name = state.preferred_name or display_name
    return f"""# {display_name}

## Identity
- Member ID: {state.member_id}
- Preferred name: {preferred_name}
- Sex: {state.sex}
- Birth date: {state.birth_date}
- Height: {state.height}
- Weight: {state.weight}
- Blood type: {state.blood_type}
- Emergency contact: {state.emergency_contact}

## Baseline Conditions
- Chronic conditions: {_join_list(state.chronic_conditions)}
- Past surgeries or hospitalizations: {_join_list(state.past_surgeries_or_hospitalizations)}
- Family history: {_join_list(state.family_history)}
- Lifestyle factors: {_join_list(state.lifestyle_factors)}

## Allergies And Contraindications
- Drug allergies: {_join_list(state.drug_allergies)}
- Food allergies: {_join_list(state.food_allergies)}
- Other contraindications: {_join_list(state.other_contraindications)}

## Active Care Plan
- Active diagnoses or concerns: {_join_list(state.active_diagnoses_or_concerns)}
- Current clinicians: {_join_list(state.current_clinicians)}
- Current medications: {_join_list(state.current_medications)}
- Monitoring goals: {_join_list(state.monitoring_goals)}

## Recent Symptom Summary
- {_join_summary(state.recent_symptom_summary)}

## Recent Metrics Summary
- {_join_summary(state.recent_metrics_summary)}

## Recent Reports Summary
- {_join_summary(state.recent_reports_summary)}

## Safety Notes
- Red flags: {_join_list(state.red_flags)}
- Open questions for clinician: {_join_list(state.open_questions_for_clinician)}
- Last updated: {state.last_updated}
"""


def _ensure_member_files(workspace: Path, member_id: str, display_name: str = "") -> Path:
    family_dir = workspace / "family"
    member_dir = family_dir / member_id
    metrics_dir = member_dir / "metrics"
    reports_dir = member_dir / "reports"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    record_path = member_dir / "record.md"
    symptoms_path = member_dir / "symptoms.md"
    medications_path = member_dir / "medications.md"

    if not record_path.exists():
        record_path.write_text(render_record(_default_record_state(member_id, display_name)), encoding="utf-8")
    if not symptoms_path.exists():
        symptoms_path.write_text("# Symptom Timeline\n\n", encoding="utf-8")
    if not medications_path.exists():
        medications_path.write_text("# Medications\n\n## Active\n\n## Stopped Or Historical\n", encoding="utf-8")

    return member_dir


def _append_symptoms(symptoms_path: Path, items: list[str], reported_at: str | None = None) -> int:
    if not items:
        return 0
    if not symptoms_path.exists():
        symptoms_path.write_text("# Symptom Timeline\n\n", encoding="utf-8")
    text = symptoms_path.read_text(encoding="utf-8")
    added = 0
    ts = _now_label(reported_at)
    for item in _dedupe(items):
        marker = f"patient-reported: {item}"
        if marker in text:
            continue
        if not text.endswith("\n"):
            text += "\n"
        text += f"- [{ts}] patient-reported: {item}\n"
        added += 1
    symptoms_path.write_text(text, encoding="utf-8")
    return added


def _med_block(name: str) -> str:
    return (
        f"- Drug: {name}\n"
        "  Generic name:\n"
        "  Purpose:\n"
        "  Dose:\n"
        "  Route:\n"
        "  Frequency:\n"
        "  Scheduled times:\n"
        "  Start date:\n"
        "  End date:\n"
        "  Prescriber:\n"
        "  Reminder job IDs:\n"
        "  Interaction review:\n"
        "  Notes: patient-reported\n"
    )


def _append_medications(medications_path: Path, items: list[str]) -> int:
    if not items:
        return 0
    if not medications_path.exists():
        medications_path.write_text("# Medications\n\n## Active\n\n## Stopped Or Historical\n", encoding="utf-8")
    text = medications_path.read_text(encoding="utf-8")
    existing = {
        _clean_item(match.group(1)).casefold()
        for match in re.finditer(r"^- Drug:\s*(.+)$", text, flags=re.MULTILINE)
    }
    added = 0
    blocks: list[str] = []
    for item in _dedupe(items):
        key = item.casefold()
        if key in existing:
            continue
        existing.add(key)
        blocks.append(_med_block(item))
        added += 1
    if not blocks:
        return 0

    marker = "## Stopped Or Historical"
    insertion = ("\n" if not text.endswith("\n") else "") + "\n".join(blocks)
    if marker in text:
        text = text.replace(marker, insertion + "\n" + marker, 1)
    else:
        text += insertion
    medications_path.write_text(text, encoding="utf-8")
    return added


def update_family_member(
    workspace: Path,
    member_id: str,
    *,
    display_name: str = "",
    sex: str = "",
    birth_date: str = "",
    height: str = "",
    weight: str = "",
    blood_type: str = "",
    emergency_contact: str = "",
    chronic_conditions: list[str] | None = None,
    past_surgeries_or_hospitalizations: list[str] | None = None,
    family_history: list[str] | None = None,
    lifestyle_factors: list[str] | None = None,
    drug_allergies: list[str] | None = None,
    food_allergies: list[str] | None = None,
    other_contraindications: list[str] | None = None,
    diagnoses_or_concerns: list[str] | None = None,
    current_clinicians: list[str] | None = None,
    monitoring_goals: list[str] | None = None,
    symptoms: list[str] | None = None,
    medications: list[str] | None = None,
    recent_reports: list[str] | None = None,
    recent_metrics: list[str] | None = None,
    red_flags: list[str] | None = None,
    open_questions_for_clinician: list[str] | None = None,
    reported_at: str | None = None,
) -> dict[str, str | int]:
    """Initialize/update a structured household member record."""
    member_id = slugify_member_id(member_id)
    member_dir = _ensure_member_files(workspace, member_id, display_name)
    record_path = member_dir / "record.md"
    symptoms_path = member_dir / "symptoms.md"
    medications_path = member_dir / "medications.md"

    state = parse_record(record_path, member_id, display_name)
    if display_name:
        state.display_name = display_name
        state.preferred_name = display_name

    for attr, value in (
        ("sex", sex),
        ("birth_date", birth_date),
        ("height", height),
        ("weight", weight),
        ("blood_type", blood_type),
        ("emergency_contact", emergency_contact),
    ):
        if value:
            setattr(state, attr, value.strip())

    state.chronic_conditions = _merge_items(state.chronic_conditions, chronic_conditions)
    state.past_surgeries_or_hospitalizations = _merge_items(
        state.past_surgeries_or_hospitalizations, past_surgeries_or_hospitalizations
    )
    state.family_history = _merge_items(state.family_history, family_history)
    state.lifestyle_factors = _merge_items(state.lifestyle_factors, lifestyle_factors)
    state.drug_allergies = _merge_items(state.drug_allergies, drug_allergies)
    state.food_allergies = _merge_items(state.food_allergies, food_allergies)
    state.other_contraindications = _merge_items(
        state.other_contraindications, other_contraindications
    )
    state.active_diagnoses_or_concerns = _merge_items(
        state.active_diagnoses_or_concerns, diagnoses_or_concerns
    )
    state.current_clinicians = _merge_items(state.current_clinicians, current_clinicians)
    state.monitoring_goals = _merge_items(state.monitoring_goals, monitoring_goals)
    state.recent_reports_summary = _merge_items(state.recent_reports_summary, recent_reports)
    state.recent_metrics_summary = _merge_items(state.recent_metrics_summary, recent_metrics)
    state.red_flags = _merge_items(state.red_flags, red_flags)
    state.open_questions_for_clinician = _merge_items(
        state.open_questions_for_clinician, open_questions_for_clinician
    )

    symptom_count = _append_symptoms(symptoms_path, symptoms or [], reported_at)
    medication_count = _append_medications(medications_path, medications or [])
    state.recent_symptom_summary = _merge_items(state.recent_symptom_summary, symptoms)
    state.current_medications = _merge_items(state.current_medications, medications)
    state.last_updated = _now_label(reported_at)

    record_path.write_text(render_record(state), encoding="utf-8")
    return {
        "member_id": member_id,
        "member_dir": str(member_dir),
        "record_path": str(record_path),
        "symptoms_path": str(symptoms_path),
        "medications_path": str(medications_path),
        "symptoms_added": symptom_count,
        "medications_added": medication_count,
    }


def _last_nonempty_lines(path: Path, limit: int = 10) -> list[str]:
    if not path.exists():
        return []
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return lines[-limit:]


def export_member_record(
    workspace: Path,
    member_id: str,
    *,
    questions_for_clinician: list[str] | None = None,
    export_date: str | None = None,
) -> Path:
    """Export a clinician-facing summary markdown file and return its path."""
    member_id = slugify_member_id(member_id)
    member_dir = workspace / "family" / member_id
    record_path = member_dir / "record.md"
    if not record_path.exists():
        raise FileNotFoundError(f"Family record not found for member '{member_id}'")

    state = parse_record(record_path, member_id)
    symptoms = _last_nonempty_lines(member_dir / "symptoms.md", limit=8)
    medications = _last_nonempty_lines(member_dir / "medications.md", limit=20)
    reports_dir = member_dir / "reports"
    report_files = sorted(reports_dir.glob("*.md"))[-5:] if reports_dir.exists() else []
    reports = [p.name for p in report_files]
    metrics_dir = member_dir / "metrics"
    metric_files = sorted(metrics_dir.glob("*.jsonl"))[-5:] if metrics_dir.exists() else []
    metrics = [p.name for p in metric_files]

    date_tag = (export_date or datetime.now().strftime("%Y%m%d")).strip()
    out_path = member_dir / f"doctor_export_{date_tag}.md"
    display_name = state.display_name or state.preferred_name or state.member_id
    questions = _merge_items(state.open_questions_for_clinician, questions_for_clinician)
    symptom_lines = "\n".join(f"- {line}" for line in symptoms) if symptoms else "- No symptom timeline recorded."
    active_problems = _dedupe([*state.chronic_conditions, *state.active_diagnoses_or_concerns])
    active_problem_block = "\n".join(
        f"- Problem: {item}\n  Status: active or relevant\n  Evidence: patient record"
        for item in active_problems
    ) or "- Problem:\n  Status:\n  Evidence:"
    medication_block = "\n".join(
        f"- {line}" for line in medications if not line.startswith("#")
    ) or "- None recorded."
    question_block = "\n".join(f"- {item}" for item in questions) if questions else "- ..."

    content = f"""# Doctor Summary: {display_name}

## Patient Snapshot
- Age / sex: {state.birth_date or ""} / {state.sex}
- Major chronic conditions: {_join_list(state.chronic_conditions)}
- Allergies: {_join_list([*state.drug_allergies, *state.food_allergies, *state.other_contraindications])}
- Current medications: {_join_list(state.current_medications)}

## Current Reason For Review
- Main concerns: {_join_summary(state.recent_symptom_summary)}
- Symptom onset and progression:
{symptom_lines}

## Active Problems
{active_problem_block}

## Medications
{medication_block}

## Recent Measurements
- Summary: {_join_summary(state.recent_metrics_summary)}
- Files: {_join_list(metrics)}

## Recent Tests And Reports
- Summary: {_join_summary(state.recent_reports_summary)}
- Files: {_join_list(reports)}

## Questions For Clinician
{question_block}
"""
    out_path.write_text(content, encoding="utf-8")
    return out_path


def dump_result(result: dict[str, str | int]) -> str:
    """Format a compact JSON-like tool result for LLM consumption."""
    return json.dumps(result, ensure_ascii=False, indent=2)
