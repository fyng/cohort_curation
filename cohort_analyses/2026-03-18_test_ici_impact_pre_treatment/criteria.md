# Clinical Cohort Curation Criteria

## Cohort Name
Test ICI + pre-treatment IMPACT sample cohort

## Inclusion Criteria
1. Age >= 18 years
   - Implemented using `CURRENT_AGE_DEID` from patient clinical table.
2. Any sex and any ethnicity
   - No filtering on `GENDER`, `ETHNICITY`, or `ANCESTRY_LABEL`.
3. Received at least one treatment with agent in:
   - Pembrolizumab
   - Durvalumab
   - Cemiplimab
   - Atezolizumab
   - Avelumab
4. Has at least one IMPACT sample before the earliest qualifying treatment start date,
   where sample date is within 365 days before treatment start.
   - IMPACT sample identified by `GENE_PANEL` beginning with `IMPACT`.
   - Time window: `earliest_treatment_start - 365 <= sample_start_date < earliest_treatment_start`.

## Exclusion Criteria
1. Missing patient age (`CURRENT_AGE_DEID`) for the age criterion.
2. No qualifying treatment from the specified list.
3. No IMPACT sample in the required pre-treatment 1-year window.

## Output
- `final_cohort_patient_ids.txt`
- One `PATIENT_ID` per line.

## Reproducibility Notes
- Assume the working directory is project root.
- Data source is configured by `--data-root` (default: `data`).
- Script is standalone and only depends on the `cohort_curation` package loaders.
- Run command (from project root):

```bash
.venv/bin/python cohort_analyses/2026-03-18_test_ici_impact_pre_treatment/build_cohort.py \
   --data-root data \
   --output cohort_analyses/2026-03-18_test_ici_impact_pre_treatment/final_cohort_patient_ids.txt
```
