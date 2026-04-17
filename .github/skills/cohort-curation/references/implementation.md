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

## Required Package Assets
- `cohort_curation/build_cohort_template.py`
- `cohort_curation/reference_guide.md`
- `cohort_curation/reference_data.py`

## Output Contract
- Keep output path inside the active cohort analysis folder.
- Emit per-filter row counts for quality-control traceability.

## Minimal Validation
- Confirm output file exists after execution.
- Confirm output IDs are unique and non-null.
- Confirm every implemented filter maps to a criterion in `cohort.md`.
