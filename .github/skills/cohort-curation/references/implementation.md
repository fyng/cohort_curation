# Cohort Implementation Checklist

## Artifacts
Each cohort analysis folder should contain:
- `cohort.md`
- `build_cohort.py`
- `final_cohort_patient_ids.txt` (after execution)

## Script Conventions
- Use standalone `argparse` scripts.
- Keep paths project-root relative.
- Annotate where each inclusion/exclusion criterion is implemented.
- Use defensive pandas handling for optional or malformed columns.

## Run Commands (from project root)
Install package:

```bash
pip install -e .
```

Run cohort script (only after user asks):

```bash
.venv/bin/python cohort_analyses/YYYY-MM-DD_<cohort_name>/build_cohort.py \
  --data-root data \
  --output cohort_analyses/YYYY-MM-DD_<cohort_name>/final_cohort_patient_ids.txt
```

Validate output:

```bash
wc -l cohort_analyses/YYYY-MM-DD_<cohort_name>/final_cohort_patient_ids.txt
head -n 10 cohort_analyses/YYYY-MM-DD_<cohort_name>/final_cohort_patient_ids.txt
```

## Notes
- Keep cohort-specific inclusion/exclusion logic in analysis scripts, not package loaders.
- Write one `PATIENT_ID` per line in final outputs.
