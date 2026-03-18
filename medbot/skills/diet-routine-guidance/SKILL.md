---
name: diet-routine-guidance
description: Generate personalized and dynamically adjusted diet, sleep, and daily routine guidance for a specific family member from their medical record, symptoms, medications, metrics, reports, allergies, and seasonal triggers such as pollen exposure.
---

# Diet And Routine Guidance

Use this skill when the user wants practical lifestyle guidance for a specific family member based on that person's medical archive.

This skill is for:

- personalized diet suggestions
- sleep and wake schedule suggestions
- daily activity and rest pacing
- environment-sensitive reminders such as pollen-season precautions

This skill does **not** replace a clinician, nutritionist, or emergency evaluation.

## Read These Sources First

For `family/<member_id>/`, read:

- `record.md`
- `symptoms.md`
- `medications.md`
- relevant files in `metrics/`
- recent summaries in `reports/`

Also use:

- current date and season
- the member's location or region if already available locally
- user-stated preferences, restrictions, budget, appetite, sleep pattern, and schedule if provided

## Core Goal

Produce advice that is:

- personalized to the member's conditions and recent changes
- dynamic, meaning recent symptoms, measurements, medications, and season can change the advice
- practical, using concrete and low-burden actions
- safety-bounded, never pretending to be a treatment plan

## Personalization Factors

Check these before giving advice:

1. Baseline conditions
   - hypertension
   - diabetes or prediabetes
   - kidney disease
   - liver disease
   - gastrointestinal conditions
   - asthma or allergic disease
   - obesity or underweight
   - pregnancy status if relevant
2. Allergies and contraindications
   - food allergies
   - drug allergies
   - pollen or seasonal allergies
3. Active symptoms
   - fever
   - cough
   - sore throat
   - fatigue
   - poor appetite
   - nausea, vomiting, diarrhea
   - insomnia
   - dizziness
4. Medications
   - timing constraints with meals
   - possible sleep disruption
   - hydration or sodium considerations
5. Recent metrics and reports
   - blood pressure trend
   - blood glucose trend
   - weight change
   - other recorded measurements
6. Real-life constraints
   - work or school schedule
   - exercise tolerance
   - caregiver availability
   - cultural diet pattern

## Guidance Workflow

1. Identify the member's durable constraints from `record.md`.
2. Read recent changes from `symptoms.md`, `medications.md`, `metrics/`, and `reports/`.
3. Decide whether the advice should focus on:
   - recovery support
   - chronic disease stability
   - symptom reduction
   - sleep regularity
   - safer daily pacing
4. Adjust diet, schedule, and environment advice to recent data, not only old history.
5. Surface red flags if the archive suggests worsening symptoms or unsafe trends.

## Diet Guidance Rules

When preparing diet suggestions:

- prefer simple, specific, food-level advice over vague healthy-eating slogans
- consider meal timing, portion regularity, hydration, and symptom tolerance
- if diabetes or glucose instability is present, emphasize stable meal timing and lower sugar load
- if hypertension or edema risk is present, emphasize lower sodium choices
- if poor appetite, nausea, or acute illness is present, prefer easy-to-tolerate, bland, smaller meals
- if diarrhea or vomiting is active, emphasize hydration and easy digestion
- if insomnia or reflux is present, reduce late-night heavy meals, caffeine, and alcohol when relevant
- if food allergy exists, never recommend the trigger food
- if kidney, liver, or other organ-related restrictions are uncertain, stay conservative and say clinician-specific diet limits may apply

## Sleep And Routine Rules

When preparing routine suggestions:

- give a realistic sleep window and wake window rather than generic "sleep early"
- align with the member's existing school, work, or caregiving schedule if known
- if fatigue is active, suggest lighter activity and rest pacing instead of full inactivity unless symptoms are severe
- if insomnia is active, suggest sleep hygiene steps with low burden
- if cough, nocturia, reflux, pain, or medication timing may interrupt sleep, mention that link when supported by the archive
- if dizziness, weakness, fever, or acute illness is present, reduce strenuous activity advice
- if recent metrics show instability, recommend more regular meals, sleep, and monitoring cadence

## Environmental Trigger Rules

If the member has allergic rhinitis, asthma, pollen allergy, or clear seasonal trigger notes:

1. Check whether the current period is likely a pollen season for the member's region if that can be inferred safely from local records or user-provided context.
2. If recent symptoms also fit allergy flare patterns, add a focused outdoor reminder section.
3. Include practical details such as:
   - reduce outdoor activity during high pollen periods
   - consider a mask and glasses when going outside
   - keep windows closed when pollen is heavy
   - wash face, hands, and hair or change outer clothing after returning home
   - monitor for worsening wheeze, shortness of breath, or persistent nighttime symptoms
4. If no local season information is available, say the reminder is precautionary rather than confirmed by a local forecast.

## Output Structure

Prefer this format:

```markdown
## Personalized Diet And Routine Guidance: <Display Name>

### Current Basis
- Main conditions:
- Recent symptoms or changes:
- Relevant medications:
- Relevant recent measurements:

### Diet Suggestions
- ...

### Sleep And Daily Routine
- ...

### Environment And Going-Out Reminders
- ...

### What To Monitor
- ...

### Red Flags
- ...

### Safety Note
- ...
```

## Style Rules

- keep advice concrete and short
- prefer "today / this week / if symptoms worsen" framing
- distinguish confirmed facts from likely inferences
- if the record is incomplete, say what is missing
- if files conflict, state the conflict instead of merging silently

## Safety Boundaries

- Never diagnose.
- Never tell the user to stop, start, or change medication unless a clinician instruction is already documented.
- Never claim a food or routine plan can cure disease.
- Never ignore severe symptoms, rapidly worsening symptoms, breathing trouble, chest pain, confusion, dehydration, or very abnormal home measurements.
- If risk appears significant, advise prompt clinician review or urgent care depending on severity.
