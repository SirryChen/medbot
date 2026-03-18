---
name: medical-record-export
description: Export a structured doctor-facing summary for one family member from family/<member_id> medical files. Use when the user asks for a medical summary, visit note, referral note, or doctor-ready record.
---

# Medical Record Export

Use this skill to create a concise, clinician-friendly summary from a member's structured files.
Use the dedicated `export_medical_record` tool to create the export file and always tell the user the exact output path afterward.

## Format Conversion And Sending

If the user wants to export and then send the record to a chat channel such as `qq` or `whatsapp`, also load and follow:

- `medbot/skills/markdown-converter-1.0.0/SKILL.md`

Default behavior:

1. Always export the doctor-facing summary as Markdown first.
2. By default, also generate a PDF version alongside the Markdown export.
3. If the user asks to forward or send the export to a channel and does not specify a file format, send the PDF version by default.
4. If the user explicitly requests a format such as `pdf`, `docx`, or another supported target format, convert and send that requested format instead.
5. If the user only asks to export and does not ask to send, keep the Markdown export and the PDF export locally, and tell the user both output paths.

When sending:

- Prefer the doctor-facing export, not raw record files.
- Tell the user exactly which file was sent and which local files were generated.

## Sources

Read these files first:

- `family/<member_id>/record.md`
- `family/<member_id>/symptoms.md`
- `family/<member_id>/medications.md`
- relevant `family/<member_id>/metrics/*.jsonl`
- recent `family/<member_id>/reports/*.md`

## Output

Write the export to:

- `family/<member_id>/doctor_export_<YYYYMMDD>.md`
- `family/<member_id>/doctor_export_<YYYYMMDD>.pdf` by default as a companion export

## Doctor-Facing Template

```markdown
# Doctor Summary: <Display Name>

## Patient Snapshot
- Age / sex:
- Major chronic conditions:
- Allergies:
- Current medications:

## Current Reason For Review
- Main concerns:
- Symptom onset and progression:

## Active Problems
- Problem:
  Status:
  Evidence:

## Medications
- Drug:
  Dose:
  Frequency:
  Purpose:
  Start date:

## Recent Measurements
- Blood pressure:
- Blood glucose:
- Other relevant metrics:

## Recent Tests And Reports
- Date:
  Source:
  Key findings:

## Questions For Clinician
- ...
```

## Rules

- Prefer facts over narrative.
- Keep uncertain facts labeled as patient-reported or unverified.
- Do not invent diagnoses or interpretations beyond what the files support.
- Highlight date, trend, and severity when those matter clinically.
- If the source files conflict, state the conflict instead of merging silently.
- When channel delivery is requested, default to sending the PDF unless the user explicitly requested another format.
- Always report the generated local file paths after export or conversion.
