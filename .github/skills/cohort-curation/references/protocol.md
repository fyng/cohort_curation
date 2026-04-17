# Cohort Curation Protocol Details

This file extends `../SKILL.md` with implementation-facing protocol details.
Canonical gating rules and clarification format are defined only in `../SKILL.md`.

## Inputs
- Plain-language cohort intent.
- Criteria template: `cohort_curation/cohort_criteria_template.md`.
- Human reference guide: `cohort_curation/reference_guide.md`.
- Machine-readable reference data: `cohort_curation/reference_data.py`.

## Mapping Procedure
1. Draft cohort metadata and clinical objective in `cohort.md`.
2. Build explicit mappings in the form: user phrase -> constant category -> recognized constants.
3. For disease and subtype mapping, evaluate sample-level fields in this order:
   - `CANCER_TYPE_DETAILED`
   - `ONCOTREE_CODE`
   - `CANCER_TYPE`
4. Record the chosen disease mapping and fallback rationale in `cohort.md`.
5. Record the patient-level matching rule used by the cohort definition.

## Criteria Completeness Check
Mark each item as complete, deferred, or not applicable in `cohort.md`:
- Diagnosis or stage definition.
- Index date definition.
- Exposure requirement and time window.
- Biomarker or sample requirement and time window.
- Follow-up or outcome ascertainment window.
- Exclusion logic for missing key fields and impossible date ordering.

## Script Handoff Contract
Before `build_cohort.py` generation, `cohort.md` should contain:
- Finalized term mappings.
- Numeric date windows and anchors.
- Inclusion criteria tied to concrete fields or loader outputs.
- Exclusion criteria tied to deterministic checks.
- Output path inside the cohort analysis folder.
