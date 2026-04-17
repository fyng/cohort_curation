---
name: cohort-curation
description: "Use when curating oncology patient cohorts from clinical data: define cohort.md criteria, map terms to recognized constants, resolve key ambiguities, and gate script generation/execution."
argument-hint: "Describe diagnosis, exposure, timing windows, and inclusion/exclusion requirements."
---

# Cohort Curation Skill

Use this skill for interactive cohort definition and script handoff.

## Scope
- Keep agent behavior instructions in this skill folder.
- Keep code templates and technical references in `cohort_curation/`.

## Required Source Rules
- Cancer stage comes from diagnosis timeline `data_timeline_diagnosis.txt` using `CLINICAL_GROUP` and `STAGE_CDM_DERIVED_GRANULAR`.
- Tumor genomics sources:
   - mutations: `data_mutations_extended.txt` with `Hugo_Symbol`
   - structural variants: `data_sv.txt` with `Site1_Hugo_Symbol`, `Site2_Hugo_Symbol`
   - copy number alterations: `data_CNA_long_format.txt` with `Hugo_Symbol`
- Surgery source is `data_timeline_surgery.txt`; map procedure names with `surg_purpose_map.csv` (`DATA` -> `REFINEMENT_RESULT`); only `Tumor removal` is curative surgery.

## Canonical Workflow
1. Capture the cohort intent in plain language.
2. Create `cohort_analyses/YYYY-MM-DD_<cohort_name>/` and draft `cohort.md` from `cohort_curation/cohort_criteria_template.md`.
3. Start term mapping before criteria lock, then maintain mappings iteratively as criteria are refined.
4. Map terms to constants from `cohort_curation/reference_data.py` (`RECOGNIZED_CONSTANTS`); do not invent constants.
5. For disease mapping, use sample-level fields `CANCER_TYPE`, `CANCER_TYPE_DETAILED`, and `ONCOTREE_CODE`.
6. If disease mapping is ambiguous, ask a targeted clarification before proceeding.
7. If a criterion includes a gene name, clarify mutation-only vs mutation plus CNA and SV before proceeding.
8. Ask clarifying questions only for unresolved high-impact criteria:
   - diagnosis or stage definition
   - index date definition
   - exposure requirement or window
   - biomarker or sample requirement
   - follow-up or outcome window
9. For each clarification question, provide exactly 3 default options plus 1 defer or ignore option.
10. Update `cohort.md` after each user response.
11. Pause for explicit user review of `cohort.md` before generating `build_cohort.py`.
12. Generate `build_cohort.py` only after explicit readiness confirmation.
13. Execute scripts only after explicit user request.

## Guardrails
- For subtype intent, prefer `CANCER_TYPE_DETAILED` and `ONCOTREE_CODE` over broad `CANCER_TYPE`.
- Treat a patient as disease-matched when any linked sample matches the selected disease mapping.
- Keep cohort filtering logic in cohort-specific scripts, not package loaders.
- Write final outputs as one `PATIENT_ID` per line.

## References
- [Interactive protocol](./references/protocol.md)
- [Implementation checklist](./references/implementation.md)
