---
name: risk-monitoring
description: Run a daily risk scan across all family member medical archives, detect actionable issues such as missing disease-related active medications, markedly high BMI, missing follow-up signals, and medication conflicts, then remind the user at a configurable local time. Default schedule is 12:00 in the user's timezone.
---

# Risk Monitoring

Use this skill to set up and run a daily household health risk scan.

This skill is for:

- scanning all member records under `family/`
- finding issues that deserve a reminder or review
- sending one concise daily summary to the user
- keeping the scan time pinned to the user's timezone

This skill is a monitoring and reminder layer. It does **not** diagnose, prescribe, or replace clinician review.

## Main Use Cases

- enable daily household archive scanning
- update the scan time
- run a one-time manual audit
- explain why a risk item was triggered
- disable or remove the monitoring job

## Data Scope

Scan all member folders under `family/`.

For each `family/<member_id>/`, read:

- `record.md`
- `symptoms.md`
- `medications.md`
- relevant files in `metrics/`
- recent files in `reports/`

## Scheduling Rule

Create one daily monitoring cron job for the household, not one job per member.

Default schedule:

- `12:00` in the user's local timezone

Use timezone-aware cron:

```text
cron(action="add", message="<daily risk monitoring task>", cron_expr="0 12 * * *", tz="<IANA timezone>")
```

Examples:

- `Asia/Shanghai`
- `Asia/Hong_Kong`
- `America/Los_Angeles`

If the user's timezone is unknown, ask first. Do not silently use the server timezone when the user asked for local-time reminders.

When the user wants a different time:

- update the existing job instead of creating duplicates

## Daily Task Message

Use a task-style cron message so the agent executes the scan and sends a result, for example:

```text
[Daily Risk Monitoring] Scan all family records under family/, detect actionable health risks, summarize by member, and send a concise reminder only if issues are found. Use the configured timezone and keep the message short.
```

## Risk Rules

Only report issues that are plausible from the archive. Do not invent facts.

### 1. Condition Without Matching Active Medication

Trigger a reminder when all of these are true:

- `record.md` shows an active chronic condition or ongoing concern, such as hypertension, diabetes, dyslipidemia, asthma, or chronic gastritis
- `medications.md` does not show a clear related active medication
- the archive does **not** clearly state one of these exceptions:
  - clinician documented non-drug management
  - medication intentionally stopped
  - diagnosis is historical only
  - user declined medication and this is already known

Output wording should be cautious:

- say `condition documented but no corresponding active medication found in the current archive`
- do **not** say the patient must be taking a drug

### 2. Markedly High BMI

If both height and weight are available, calculate BMI.

Trigger levels:

- `BMI >= 35` -> high-priority lifestyle review reminder
- `BMI >= 40` -> stronger reminder and clinician follow-up suggestion

Do not trigger if the height or weight data is clearly outdated and no recent data exists unless you label it as based on old measurements.

### 3. Medication Conflict

If there are at least two active medications:

1. normalize the active drug list
2. run `drug-interaction-check`
3. trigger if the result is:
   - major concern
   - moderate concern
4. include the interacting pair and severity in the reminder

If the database cannot verify a drug, report:

- interaction status could not be fully verified

Do not present `no reliable conflict found` as proof of safety.

### 4. Persistently Abnormal Home Metrics

Trigger a reminder when recent measurements suggest a concerning pattern, for example:

- repeated high blood pressure values
- repeated high fasting or random glucose values
- clear worsening trend over several recent entries

Rules:

- prefer repeated patterns over one isolated outlier
- mention the latest values and rough trend
- if there are too few data points, say data is sparse

### 5. Missing Follow-Up Signals

Trigger a reminder when:

- a chronic condition is documented
- but there are no recent related measurements, report summaries, or follow-up notes for a long time

Use cautious wording such as:

- `no recent follow-up evidence found in the archive`

Do not guess the medically correct follow-up interval if the archive does not specify one.

### 6. Symptom-Condition Mismatch Or Escalation

Trigger a reminder when:

- recent symptoms suggest worsening control of a known condition
- or `symptoms.md` contains repeated or escalating entries without recent review notes

Examples:

- hypertension history plus recurrent headache/dizziness entries
- asthma or allergy history plus worsening cough, wheeze, or nighttime symptoms
- diabetes history plus polyuria, excessive thirst, weight loss, or repeated hyperglycemia notes

## Scan Workflow

1. Enumerate all members in `family/`.
2. Read each member's key files.
3. Build a short structured risk list per member.
4. For medication conflicts, use `drug-interaction-check` when the active medication list is sufficient.
5. Merge results into one household summary.
6. If no issues are found, send either:
   - no message
   - or a very short `no new actionable risks found today` summary, depending on user preference
7. If issues are found, send a concise reminder at the scheduled time.

## Reminder Output Format

Prefer this structure:

```markdown
## Daily Risk Summary

### <member_id> / <Display Name>
- Risk:
- Why it triggered:
- Evidence from archive:
- Suggested next step:
- Priority: low | medium | high
```

Keep it short. Focus on what changed or what needs review.

## Suggested Next Step Rules

Use low-burden next steps such as:

- review whether the archive is missing a current medication
- verify whether a medication was stopped by a clinician
- check home blood pressure or blood glucose more regularly
- update height or weight if outdated
- ask a clinician or pharmacist about a possible interaction
- arrange follow-up if symptoms or home data are worsening

## Configuration To Store

When monitoring is enabled, keep a concise record of:

- whether household daily risk monitoring is enabled
- the cron job ID
- the configured reminder time
- the configured timezone
- whether `no issues found` messages should be suppressed

Store only concise configuration notes, not the full daily reports.

## Editing Or Disabling

When the user changes the schedule:

1. locate the existing job with `cron(action="list")` if needed
2. remove the old job
3. create the replacement job with the new time or timezone
4. update the stored monitoring configuration note

When the user disables monitoring:

1. remove the cron job
2. update the stored configuration note

## Safety Boundaries

- Never diagnose from archive patterns alone.
- Never claim a missing medication record means non-adherence.
- Never assume every disease requires medication.
- Never change medication instructions automatically.
- Never hide uncertainty when data is incomplete, old, or conflicting.
- If the archive suggests urgent risk, explicitly recommend prompt medical review or urgent care depending on severity.
