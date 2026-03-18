---
name: medication-reminder
description: Schedule, update, and remove medication reminders with the cron tool while keeping medications.md in sync. Use when the user wants medication schedules, dose reminders, or adherence reminders.
---

# Medication Reminder

Use this skill for medication schedules and reminders.

## Before Scheduling

Read or update:

- `family/<member_id>/medications.md`

Make sure the medication entry includes:

- drug name
- dose
- route
- frequency
- scheduled times
- start date
- end date if known

## Scheduling Rule

Create one cron job per time point.

Message template:

```text
[Medication Reminder] <member_id> <drug> <dose> at <HH:MM>
```

Examples:

- one-time: use `at`
- every N hours: use `every_seconds`
- daily fixed time: use `cron_expr`

## After Scheduling

Write the returned job IDs into the matching medication entry in `medications.md`.

## When Stopping Or Editing

1. `cron(action="list")` if job IDs are missing
2. remove outdated jobs
3. update `medications.md`
4. create replacement jobs if needed

## Safety

- Never alter dose or frequency unless the user explicitly asks.
- If the user mentions missed doses, log the event but do not provide clinical rescue advice beyond reminding them to follow their prescription or clinician instructions.
