# Interactive Cohort Curation Protocol

## Inputs
- User's plain-language cohort intent.
- Recognized constants snapshot: `cohort_curation/recognized_constants_snapshot.json`.

## Steps
1. Intake in plain language
- Ask for diagnosis, treatment exposure, timing windows, and key inclusion/exclusion criteria.

2. Term mapping before criteria lock
- Map natural-language terms to recognized constants.
- Record mappings explicitly in `cohort.md` as user phrase -> constants.
- Example mapping:
  - User phrase: `PD1/PDL1 immunotherapy`
  - Treatments: `Pembrolizumab`, `Durvalumab`, `Cemiplimab`, `Atezolizumab`, `Avelumab`

3. Draft criteria document first
- Create folder: `cohort_analyses/YYYY-MM-DD_<cohort_name>`.
- Create `cohort.md` from `cohort_curation/cohort_criteria_template.md`.
- Keep `cohort.md` as the source of truth throughout curation.

4. Clarify missing high-impact criteria
- Ask one follow-up question per unresolved high-impact criterion.
- Every question must include:
  - 3 default options
  - 1 option to ignore/defer

5. Update and review gate
- Update `cohort.md` after each answer.
- Pause for manual user review before any code generation.

6. Readiness and execution gates
- Generate `build_cohort.py` only after explicit user confirmation.
- Execute scripts only after explicit user request.

## Typical Clarification Topics
- Diagnosis/stage definition
- Index date
- Exposure window
- Biomarker/sample requirements
- Follow-up minimum and censoring
