#!/usr/bin/env python3
"""Initialize a family medical record directory."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

MEMBER_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _record_template(member_id: str, display_name: str) -> str:
    name = display_name or member_id
    return f"""# {name}

## Identity
- Member ID: {member_id}
- Preferred name: {display_name}
- Sex:
- Birth date:
- Height:
- Weight:
- Blood type:
- Emergency contact:

## Baseline Conditions
- Chronic conditions:
- Past surgeries or hospitalizations:
- Family history:
- Lifestyle factors:

## Allergies And Contraindications
- Drug allergies:
- Food allergies:
- Other contraindications:

## Active Care Plan
- Active diagnoses or concerns:
- Current clinicians:
- Current medications:
- Monitoring goals:

## Recent Symptom Summary
- None recorded yet.

## Recent Metrics Summary
- None recorded yet.

## Recent Reports Summary
- None recorded yet.

## Safety Notes
- Red flags:
- Open questions for clinician:
- Last updated:
"""


def _symptoms_template() -> str:
    return "# Symptom Timeline\n\n"


def _medications_template() -> str:
    return """# Medications

## Active

## Stopped Or Historical
"""


def init_member(member_id: str, root: Path, display_name: str = "") -> Path:
    """Create the family member directory and starter files."""
    if not MEMBER_ID_RE.fullmatch(member_id):
        raise ValueError("member_id must be lowercase kebab-case")

    root = root.expanduser().resolve()
    member_dir = root / member_id if root.name == "family" else root / "family" / member_id
    metrics_dir = member_dir / "metrics"
    reports_dir = member_dir / "reports"

    metrics_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    files = {
        member_dir / "record.md": _record_template(member_id, display_name),
        member_dir / "symptoms.md": _symptoms_template(),
        member_dir / "medications.md": _medications_template(),
    }

    for path, content in files.items():
        if not path.exists():
            path.write_text(content, encoding="utf-8")

    return member_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a family medical record directory")
    parser.add_argument("member_id", help="Stable lowercase kebab-case member ID, such as mom or alice-zhang")
    parser.add_argument("--root", default=".", help="Workspace root or family directory")
    parser.add_argument("--display-name", default="", help="Optional human-readable display name")
    args = parser.parse_args()

    member_dir = init_member(args.member_id, Path(args.root), args.display_name)
    print(member_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
