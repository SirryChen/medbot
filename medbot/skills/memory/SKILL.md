---
name: memory
description: Two-layer memory plus structured family medical records. Use for long-term facts, household member records, symptom timelines, medications, measurements, and report summaries.
always: true
---

# Memory

## Core Layers

- `memory/MEMORY.md` — Long-term facts that should stay in active context. Keep this concise.
- `memory/HISTORY.md` — Append-only event log. Search it when you need older conversation details.
- `family/<member_id>/...` — Structured medical records for household members. Use this for detailed health data instead of bloating `MEMORY.md`.

## Family Medical Structure

Use stable lowercase kebab-case for `member_id`, for example `mom`, `dad`, `alice-zhang`.

Create and maintain this structure:

- `family/<member_id>/record.md` — The canonical structured medical record for one person.
- `family/<member_id>/symptoms.md` — Append-only symptom updates with timestamps.
- `family/<member_id>/medications.md` — Current and recent medications, reminder IDs, and interaction notes.
- `family/<member_id>/metrics/*.jsonl` — Time-series measurements such as blood pressure or blood glucose.
- `family/<member_id>/reports/` — Summaries of uploaded or pasted medical reports.

Keep `memory/MEMORY.md` limited to:

- family member registry and aliases
- durable care preferences
- durable risk notes that should always stay in context
- pointers to important member files

Do not dump full medical histories into `memory/MEMORY.md`.

## Record Rules

When health information changes:

1. Update the member's append-only log first:
   - symptoms -> `symptoms.md`
   - measurements -> `metrics/*.jsonl`
   - reports -> `reports/*.md`
2. Then refresh `record.md` if the new information changes the durable summary.
3. Keep timestamps in ISO form when possible, for example `2026-03-14 09:30`.
4. Never silently delete prior clinical facts. Mark corrections clearly.
5. Never invent diagnoses, lab values, or medication plans.

## Search Strategy

- For quick recall, read the relevant member files directly.
- For large histories, use targeted command-line search or a short Python filter.
- Search `symptoms.md`, `medications.md`, `metrics/`, and `reports/` before answering longitudinal medical questions.

## When To Load Other Skills

Read these skills when the task matches:

- `family-medical-record` — create or update the structured member record
- `medical-record-export` — prepare a doctor-facing summary
- `medication-reminder` — schedule medication reminders
- `health-metrics` — log/query measurements and generate trend charts
- `drug-interaction-check` — review medication conflicts
- `medical-report-ingest` — summarize a report into the member record
- `diet-routine-guidance` — generate personalized diet, sleep, and seasonal environment guidance
- `risk-monitoring` — run daily household risk scans and schedule summary reminders

## Auto-consolidation

Conversation consolidation still writes to `memory/MEMORY.md` and `memory/HISTORY.md`. Use the `family/` tree for detailed healthcare records that need stable structure.
