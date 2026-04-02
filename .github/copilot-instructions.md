# Project Guidelines

## Code Style
- Prefer small, explicit Python functions and clear pandas transformations over chained one-liners.
- Keep cohort scripts standalone with `argparse` and root-relative paths.
- Use `Path` for file outputs and write one `PATIENT_ID` per line for cohort outputs.

## Architecture
- `cohort_curation/` is the reusable package layer for domain loaders (`raw` and `harmonized` access).
- `cohort_analyses/YYYY-MM-DD_<name>/` contains per-analysis artifacts:
  - `cohort.md`
  - `build_cohort.py`
  - `final_cohort_patient_ids.txt`
- Cohort-specific filtering/inclusion logic belongs in analysis scripts, not in package loaders.

## Interactive Cohort Curation Workflow
- Follow `WORKFLOW.md` for cohort curation tasks.
- Start by asking the user to describe the cohort in plain language.
- Translate user natural-language criteria into recognized constants before finalizing `cohort.md`.
- Use `cohort_curation/recognized_constants_snapshot.json` as the source of recognized constants.
- Use oncology domain knowledge to choose relevant constants when user terms are high-level.
- Record a clear term-mapping section in `cohort.md` (user phrase -> recognized constants).
- Create the analysis folder and draft `cohort.md` from `cohort_criteria_template.md`.
- For unspecified critical criteria, ask clarifying questions interactively.
- Every clarifying question must include 3 default options and one ignore/defer option.
- Update `cohort.md` with each user response.
- Always pause and request user review of `cohort.md` before code generation.
- Do not generate `build_cohort.py` until the user confirms they are ready.
- Do not run analysis scripts unless the user explicitly requests execution.

Example mapping:
- User input: `PD1/PDL1 immunotherapy`
- Treatment mapping: `Pembrolizumab`, `Durvalumab`, `Cemiplimab`, `Atezolizumab`, `Avelumab`

## Build and Run
- Install package: `pip install -e .`
- Run cohort script from project root only after user confirmation:
  - `.venv/bin/python cohort_analyses/YYYY-MM-DD_<name>/build_cohort.py --data-root data --output cohort_analyses/YYYY-MM-DD_<name>/final_cohort_patient_ids.txt`
- Validate output only after execution:
  - `wc -l cohort_analyses/YYYY-MM-DD_<name>/final_cohort_patient_ids.txt`
  - `head -n 10 cohort_analyses/YYYY-MM-DD_<name>/final_cohort_patient_ids.txt`

## Conventions
- Assume Linux working directory is project root for all documented commands.
- Keep all paths project-root relative; avoid machine-specific absolute paths.
- Use `cohort_criteria_template.md` when drafting new `cohort.md` files.
- Always annotate in `build_cohort.py` where each inclusion/exclusion criterion is implemented.
- Prefer defensive column handling in pandas (column checks, `pd.to_numeric(..., errors="coerce")`).
