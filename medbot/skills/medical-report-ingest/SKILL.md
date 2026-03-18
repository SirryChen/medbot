---
name: medical-report-ingest
description: Summarize a medical report into a family member's record and reports folder. Use when the user provides a lab result, scan report, discharge summary, pathology note, or other medical report text/file.
---

# Medical Report Ingest

Use this skill to turn raw report content into a durable summary.

## Inputs

Read:

- the report file or pasted text
- `family/<member_id>/record.md`
- recent `family/<member_id>/reports/` when comparison matters

If the report is a PDF, use `read_file` directly on the PDF path. The tool extracts text from the PDF before summarization.

## Save Location

Write a report summary to:

- `family/<member_id>/reports/<YYYYMMDD>-<slug>.md`

Then refresh `record.md` if the report changes the durable summary.

## Summary Template

```markdown
# <Report Title>

- Date:
- Source:
- Member:
- Report type:

## Key Findings
- ...

## Abnormal Or Notable Items
- ...

## Follow-up Needed
- ...

## Raw Evidence Snippets
- ...
```

## Rules

- Separate direct report facts from your summary.
- Quote exact abnormal values when available.
- If the source is incomplete or image-only, state the limitation.
- Do not diagnose beyond the report text.
