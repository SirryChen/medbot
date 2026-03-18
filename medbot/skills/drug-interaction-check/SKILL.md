---
name: drug-interaction-check
description: Review a family member's active medications for possible conflicts before or after adding a drug. Use when the user asks whether medications are safe together or when updating medications.md.
---

# Drug Interaction Check

This skill performs a safety-oriented review, not a definitive medical judgment.

## Inputs

Read:

- `family/<member_id>/medications.md`

Collect:

- active drugs
- dose and route if available
- supplements and over-the-counter drugs if mentioned
- allergies or contraindications from `record.md`

## Review Flow

1. Normalize every medication to an English generic name before querying, even if the user wrote Chinese, a brand name, or a shorthand.
2. If the exact English generic name is uncertain, generate 1 to 3 common English candidates and try them one by one.
3. Use the `drug_interaction_check` tool with the most likely English candidates.
4. If only one candidate returns a clean, plausible match, use that result.
5. If multiple different candidates all match plausibly, ask the user to confirm the intended drug.
6. If the tool reports ambiguous drug names, ask the user for the exact generic drug name.
7. If no candidate can be found in the database, state clearly:
   - the database does not include this drug
   - this does not mean the combination is safe
   - interactions may still exist
   - the user should consult a doctor or pharmacist
8. Summarize the final result as one of:
   - major concern
   - moderate concern
   - minor concern
   - no reliable conflict found
   - unable to verify

## Output Format

```markdown
## Interaction Review
- Drugs reviewed:
- Result:
- Why:
- Source or basis:
- Next safe action:
```

## Safety Rules

- Never claim a medication combination is fully safe.
- If data is missing or uncertain, say so clearly.
- In user-facing wording, say "database" rather than naming the external site unless the user asks.
- Advise pharmacist or clinician confirmation for any non-trivial interaction question.
- Do not change medications on the user's behalf.
