import importlib
import sys
from pathlib import Path

from medbot.agent.skills import SkillsLoader


FAMILY_SCRIPT_DIR = Path("medbot/skills/family-medical-record/scripts").resolve()
if str(FAMILY_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(FAMILY_SCRIPT_DIR))

METRIC_SCRIPT_DIR = Path("medbot/skills/health-metrics/scripts").resolve()
if str(METRIC_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(METRIC_SCRIPT_DIR))

init_member = importlib.import_module("init_member")
render_metric_svg = importlib.import_module("render_metric_svg")


def test_medbot_skills_are_discoverable(tmp_path: Path) -> None:
    loader = SkillsLoader(tmp_path)
    names = {skill["name"] for skill in loader.list_skills(filter_unavailable=False)}

    assert "family-medical-record" in names
    assert "medical-record-export" in names
    assert "medication-reminder" in names
    assert "health-metrics" in names
    assert "drug-interaction-check" in names
    assert "medical-report-ingest" in names
    assert "diet-routine-guidance" in names
    assert "risk-monitoring" in names
    assert "skill-filter" in names
    assert "skill-finder" in names


def test_init_member_creates_expected_family_files(tmp_path: Path) -> None:
    member_dir = init_member.init_member("mom", tmp_path, "Mom")

    assert member_dir == (tmp_path / "family" / "mom")
    assert (member_dir / "record.md").exists()
    assert (member_dir / "symptoms.md").exists()
    assert (member_dir / "medications.md").exists()
    assert (member_dir / "metrics").is_dir()
    assert (member_dir / "reports").is_dir()


def test_render_metric_svg_for_generic_series(tmp_path: Path) -> None:
    metric_file = tmp_path / "blood_glucose.jsonl"
    metric_file.write_text(
        '\n'.join(
            [
                '{"timestamp":"2026-03-14 07:10","value":6.2,"unit":"mmol/L"}',
                '{"timestamp":"2026-03-15 07:15","value":5.8,"unit":"mmol/L"}',
            ]
        )
        + '\n',
        encoding="utf-8",
    )

    output = render_metric_svg.render_file(metric_file, tmp_path / "chart.svg", "Glucose Trend")
    svg = output.read_text(encoding="utf-8")

    assert output.exists()
    assert "Glucose Trend" in svg
    assert "polyline" in svg
    assert "mmol/L" in svg


def test_render_metric_svg_for_blood_pressure_series(tmp_path: Path) -> None:
    metric_file = tmp_path / "blood_pressure.jsonl"
    metric_file.write_text(
        '\n'.join(
            [
                '{"timestamp":"2026-03-14 08:30","systolic":128,"diastolic":82,"unit":"mmHg"}',
                '{"timestamp":"2026-03-15 08:45","systolic":132,"diastolic":84,"unit":"mmHg"}',
            ]
        )
        + '\n',
        encoding="utf-8",
    )

    output = render_metric_svg.render_file(metric_file, tmp_path / "bp.svg", "Blood Pressure Trend")
    svg = output.read_text(encoding="utf-8")

    assert output.exists()
    assert "Blood Pressure Trend" in svg
    assert "Systolic" in svg
    assert "Diastolic" in svg
