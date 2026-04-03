# Clinical Cohort Curation Workflow

This workflow assumes the Linux working directory is the project root.

## Interactive Workflow

### 1) Intake: ask for cohort description in words
Start by prompting the user to describe the intended cohort in plain language.

### 1.5) Translate user terms to recognized constants
Before finalizing criteria text, map natural-language terms to known data constants from
`cohort_curation/recognized_constants_snapshot.json`.

Use oncology domain knowledge to select relevant constants from the snapshot when user input is high-level.

Examples:
- User term: "PD1/PDL1 immunotherapy"
- Recognized treatments: `Pembrolizumab`, `Durvalumab`, `Cemiplimab`, `Atezolizumab`, `Avelumab`

Record this translation in `cohort.md` so criteria are auditable and executable.

### 2) Create analysis folder
Create under `cohort_analyses/` with date + short cohort label:
- `cohort_analyses/YYYY-MM-DD_<cohort_name>`

### 3) Draft criteria document first
Create `cohort.md` in the analysis folder using `cohort_curation/cohort_criteria_template.md`.
Prefill using user-provided details.

### 4) Clarify missing high-impact criteria interactively
For each important unspecified item, ask a follow-up question.
For every question, provide:
- 3 default options
- 1 option to ignore/defer the criterion

Examples of high-impact criteria to clarify:
- Diagnosis/stage definition
- Index date
- Exposure window
- Biomarker/sample requirements
- Follow-up minimum and censoring

### 5) Update `cohort.md` after each answer
Keep `cohort.md` as the source of truth. Reflect user choices immediately.
When users give high-level terms, include a "Term Mapping" section in `cohort.md` that lists:
- user phrase
- mapped recognized constants

### 6) Mandatory user review pause
After drafting and clarifications, always pause and ask the user to manually review/edit `cohort.md`.
Do not create `build_cohort.py` yet.

### 7) Wait for explicit readiness confirmation
Only proceed when the user explicitly says they are ready.

### 8) Then generate script and run only if requested
After readiness confirmation:
- Create `build_cohort.py` with clear comments marking each inclusion/exclusion criterion.
- Write final IDs to `final_cohort_patient_ids.txt` (one `PATIENT_ID` per line).
- Execute the script only when the user explicitly asks to run analysis.

## Output Artifacts
Each cohort analysis folder should eventually contain:
- `cohort.md`
- `build_cohort.py`
- `final_cohort_patient_ids.txt` (only after execution)

This keeps cohort curation interactive, auditable, and reproducible.
