# Cohort Curation Package Assets

This document defines technical asset boundaries inside `cohort_curation/`.
Behavior workflow documentation is maintained in `.github/skills/cohort-curation/`.

## Boundary Rules
- Keep reusable code templates, dictionary assets, and dataframe contracts in `cohort_curation/`.
- Keep agent behavior instructions in `.github/skills/cohort-curation/`.
- Keep cohort-specific inclusion and exclusion logic in each cohort analysis script.

## Core Technical Assets
- `cohort_criteria_template.md`: criteria document template used to author `cohort.md`.
- `build_cohort_template.py`: script scaffold for new cohort analysis implementations.
- `reference_guide.md`: consolidated human-readable data contracts and reference tables.
- `reference_data.py`: consolidated machine-readable constants and dataframe interfaces.

## Loader and IO Layer
- `io.py` resolves data roots and file reads.
- `reference_data.py` defines data file names, recognized constants, and harmonization maps.
- `loaders/` modules provide domain-specific raw and harmonized dataframe outputs.

## Output Contract
- Cohort scripts write one `PATIENT_ID` per line.
- Cohort outputs stay inside `cohort_analyses/YYYY-MM-DD_<cohort_name>/`.
