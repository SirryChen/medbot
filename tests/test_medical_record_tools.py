from pathlib import Path

import pytest

from medbot.agent.tools.filesystem import EditFileTool, WriteFileTool
from medbot.agent.tools.medical_records import ExportMedicalRecordTool, FamilyRecordTool


@pytest.mark.asyncio
async def test_family_record_tool_repairs_corrupt_record_and_dedupes(tmp_path: Path) -> None:
    member_dir = tmp_path / "family" / "sirry"
    member_dir.mkdir(parents=True)
    (member_dir / "record.md").write_text(
        "高血压，失眠，高血压，失眠，布诺芬",
        encoding="utf-8",
    )

    tool = FamilyRecordTool(workspace=tmp_path)
    result = await tool.execute(
        member_id="sirry",
        display_name="Sirry",
        chronic_conditions=["hypertension", "hypertension"],
        symptoms=["insomnia", "fever", "insomnia"],
        medications=["amlodipine", "ibuprofen", "amlodipine"],
        family_history=["father has hypertension"],
    )

    record = (member_dir / "record.md").read_text(encoding="utf-8")
    symptoms = (member_dir / "symptoms.md").read_text(encoding="utf-8")
    medications = (member_dir / "medications.md").read_text(encoding="utf-8")

    assert "Structured family record updated." in result
    assert "# Sirry" in record
    assert "## Identity" in record
    assert "- Chronic conditions: hypertension" in record
    assert "- Family history: father has hypertension" in record
    assert record.count("hypertension") == 2
    assert symptoms.count("patient-reported: insomnia") == 1
    assert symptoms.count("patient-reported: fever") == 1
    assert medications.count("- Drug: amlodipine") == 1
    assert medications.count("- Drug: ibuprofen") == 1


@pytest.mark.asyncio
async def test_export_medical_record_tool_writes_file_and_returns_path(tmp_path: Path) -> None:
    family_tool = FamilyRecordTool(workspace=tmp_path)
    await family_tool.execute(
        member_id="sirry",
        display_name="Sirry",
        chronic_conditions=["hypertension"],
        symptoms=["insomnia"],
        medications=["amlodipine"],
    )

    export_tool = ExportMedicalRecordTool(workspace=tmp_path)
    result = await export_tool.execute(member_id="sirry", export_date="20260317")

    out_path = tmp_path / "family" / "sirry" / "doctor_export_20260317.md"
    assert out_path.exists()
    assert "Doctor summary exported successfully." in result
    assert str(out_path) in result
    assert "Doctor Summary: Sirry" in out_path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_write_file_blocked_for_structured_family_record(tmp_path: Path) -> None:
    tool = WriteFileTool(workspace=tmp_path)
    result = await tool.execute(
        path=str(tmp_path / "family" / "sirry" / "record.md"),
        content="bad write",
    )

    assert "Error" in result
    assert "family_record" in result


@pytest.mark.asyncio
async def test_edit_file_blocked_for_doctor_export(tmp_path: Path) -> None:
    export_path = tmp_path / "family" / "sirry" / "doctor_export_20260317.md"
    export_path.parent.mkdir(parents=True)
    export_path.write_text("hello", encoding="utf-8")

    tool = EditFileTool(workspace=tmp_path)
    result = await tool.execute(
        path=str(export_path),
        old_text="hello",
        new_text="bye",
    )

    assert "Error" in result
    assert "export_medical_record" in result
