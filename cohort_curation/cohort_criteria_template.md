# Cohort Criteria Template

Use this template for new cohort analyses. Keep all paths relative to the project root.

## Cohort Metadata
- Cohort name:
- Analysis folder: `cohort_analyses/YYYY-MM-DD_<cohort_name>`
- Script: `cohort_analyses/YYYY-MM-DD_<cohort_name>/build_cohort.py`
- Output: `cohort_analyses/YYYY-MM-DD_<cohort_name>/final_cohort_patient_ids.txt`

## Clinical Question
- Primary objective:
- Secondary objectives:

## Term Mapping Registry
Source dictionary:
- `cohort_curation/reference_data.py` (`RECOGNIZED_CONSTANTS`)

Mapping rows:

| User phrase | Constant category | Recognized constants | Mapping rationale |
| --- | --- | --- | --- |
|  |  |  |  |

## Inclusion Criteria (Required)
1. Diagnosis definition:
   - Cancer type/site:
   - Confirmation source (table/column):
2. Age:
   - Minimum age at index date:
3. Treatment exposure:
   - Required line/agent/class:
   - Exposure time window relative to index:
4. Baseline sample/biomarker requirement:
   - Marker/panel/test required:
   - Pre-index or post-index window:
5. Follow-up sufficiency:
   - Minimum follow-up duration or event ascertainment requirement:

## Exclusion Criteria (Required)
1. Missing or invalid key dates (index, treatment, sample).
2. Missing required covariates/outcomes.
3. Conflicting timeline logic (events impossible by date ordering).
4. Prior malignancy rules (if applicable).

## Optional Criterion Groups
- Demographics and age bounds.
- Disease and stage stratification.
- Prior therapy and line-of-therapy constraints.
- Biomarker and genomics requirements.
- Organ function or performance status proxies.
- Timeline and data-quality constraints.

## Operational Definitions
- Index date:
- Baseline window:
- Exposure window:
- Outcome window:
- Censoring rules:

## Data Dependencies
- Loader modules used:
  - `cohort_curation.loaders.patient`
  - `cohort_curation.loaders.procedures`
  - `cohort_curation.loaders.genomics`
  - Add other loaders as needed.
- Human reference guide: `cohort_curation/reference_guide.md`
- Machine-readable reference: `cohort_curation/reference_data.py`

## Outputs
- Final patient list path:
- Optional intermediate QC tables:

## Criteria Completeness Matrix

| Criterion group | Status (`complete` / `deferred` / `n/a`) | Notes |
| --- | --- | --- |
| Diagnosis or stage definition |  |  |
| Index date |  |  |
| Exposure requirement and window |  |  |
| Biomarker or sample requirement and window |  |  |
| Follow-up or outcome window |  |  |
| Exclusion criteria completeness |  |  |

## Reproducibility Metadata
- Script entrypoint:
- Default `--data-root` value:
- Default `--output` value:
- QC metrics emitted by script:
