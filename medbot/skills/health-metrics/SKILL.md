---
name: health-metrics
description: Record blood pressure, blood glucose, and other time-series health metrics into family/<member_id>/metrics and generate trend charts. Use when logging measurements, querying recent values, or plotting trends.
---

# Health Metrics

Use append-only JSONL files under `family/<member_id>/metrics/`.

## File Layout

- `blood_pressure.jsonl`
- `blood_glucose.jsonl`
- `<metric_name>.jsonl` for other metrics

## Entry Formats

Blood pressure:

```json
{"timestamp":"2026-03-14 08:30","systolic":128,"diastolic":82,"pulse":74,"unit":"mmHg","position":"sitting","source":"home cuff","notes":"before breakfast"}
```

Blood glucose:

```json
{"timestamp":"2026-03-14 07:10","value":6.2,"unit":"mmol/L","meal_context":"fasting","source":"fingerstick","notes":""}
```

Generic metric:

```json
{"timestamp":"2026-03-14 20:00","value":72.4,"unit":"kg","source":"home scale","notes":""}
```

## Logging Rules

- append one JSON object per line
- keep the original timestamp
- do not rewrite old measurements unless the user is correcting bad data
- update `record.md` only for durable trends or latest important values

## Querying

When the user asks for trends:

1. read the relevant metric file
2. sort mentally by timestamp if needed
3. report latest value, range, and visible trend

## Trend Charts

Use the bundled script from this skill's `scripts/` directory to render SVG charts from a metric JSONL file.

Output path suggestion:

- `family/<member_id>/metrics/charts/<metric_name>.svg`

Rules:

- use one line for generic metrics
- use two lines for blood pressure: systolic and diastolic
- mention missing or sparse data if the series is short
