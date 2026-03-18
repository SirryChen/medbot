---
name: family-medical-record
description: Create and maintain structured family medical records under family/<member_id>. Use when adding a family member, updating symptoms, allergies, diagnoses, medications, or report summaries.
---

# Family Medical Record

Use this skill to keep each household member's medical data in a stable file layout.

## Trigger This Skill Proactively

Use this skill aggressively when the user reveals real household health information, even if they did not explicitly ask to save it.

Common triggers:

- "I had hypertension before."
- "My father also has hypertension."
- "My mother is allergic to penicillin."
- "My child started coughing last night."
- "I take amlodipine every morning."
- "My blood pressure was 148/96 today."

If one message contains information about multiple people, create or update each person's record separately.
If the member folder does not exist yet, initialize it first, then write the new information.
Use the dedicated `family_record` tool for these updates. Do not directly edit `record.md`, `symptoms.md`, or `medications.md` with raw file tools.

## Reply Style After Recording

After using `family_record`, do not make the record note the main body of the reply.

Preferred structure:

1. Start with a brief, human response that shows care or concern.
2. Give short, practical next-step guidance when appropriate.
3. Add an explicit record confirmation at the end, such as "I have recorded that your father had a 39 C fever and cough this morning."

Rules:

- Keep the record confirmation explicit. Do not hide it.
- Keep the record confirmation secondary. Do not open with "I recorded..." unless the user asked specifically about saving.
- Do not sound like a bookkeeping machine or simply restate structured fields.
- When symptoms may be more serious, raise the urgency clearly but calmly.
- For red-flag situations such as high fever, breathing difficulty, chest pain, confusion, seizure, blue lips, or fast worsening symptoms, advise prompt medical evaluation.
- If the user shares symptoms for a family member, acknowledge both the family member's discomfort and the user's concern.

## Initialize A Member

Prefer the bundled script for first-time setup. Run it from this skill's `scripts/` directory.

Arguments:

- `member_id` — stable lowercase kebab-case ID
- `root` — workspace path or the `family/` directory
- `display_name` — optional human-readable name

The script creates:

- `family/<member_id>/record.md`
- `family/<member_id>/symptoms.md`
- `family/<member_id>/medications.md`
- `family/<member_id>/metrics/`
- `family/<member_id>/reports/`

## Canonical Record

`record.md` is the durable summary. Keep it human-readable and structured.

Required sections:

```markdown
# <Display Name>

## Identity
- Member ID:
- Preferred name:
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
- Keep this short. Detailed events live in `symptoms.md`.

## Recent Metrics Summary
- Key latest values and notable trends. Detailed series live in `metrics/`.

## Recent Reports Summary
- Key findings and dates. Full report summaries live in `reports/`.

## Safety Notes
- Red flags:
- Open questions for clinician:
- Last updated:
```

## Symptom Log

Use `symptoms.md` as append-only chronology.

Format:

```markdown
# Symptom Timeline

- [2026-03-14 09:30] fatigue started after breakfast; severity 4/10; no fever; note: improved after rest
- [2026-03-14 20:10] dry cough worse at night; severity 6/10; note: disturbed sleep
```

Rules:

- append, do not reorder history
- include onset/change time when known
- include severity, duration, triggers, associated symptoms when available
- if the user is unsure, mark as uncertain instead of guessing

## Medication File

Keep `medications.md` separated from the main record so reminders and interaction checks stay easy to manage.

Suggested entry template:

```markdown
# Medications

## Active
- Drug:
  Generic name:
  Purpose:
  Dose:
  Route:
  Frequency:
  Scheduled times:
  Start date:
  End date:
  Prescriber:
  Reminder job IDs:
  Interaction review:
  Notes:

## Stopped Or Historical
- Drug:
  Reason stopped:
  Last taken:
  Notes:
```

## Update Policy

When new information arrives:

1. Update the narrowest source file first.
2. Refresh `record.md` only if the durable summary changed.
3. Preserve old facts unless the user explicitly corrected them.
4. Mark uncertain, patient-reported, or unverified content clearly.
5. Do not wait for an explicit "please record this" command when the user has stated durable health facts.
