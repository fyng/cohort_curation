---
name: cohort-curation
description: "Use when curating oncology patient cohorts from real-world data, drafting cohort.md criteria, mapping natural-language terms to recognized constants, asking clarification questions, and generating build_cohort.py after explicit user confirmation."
argument-hint: "Describe cohort intent, diagnosis, treatment exposure, timing windows, and key inclusion/exclusion criteria."
---

# Cohort Curation Skill

Use this skill for end-to-end interactive cohort curation tasks.

## When to Use
- User asks to curate, design, draft, refine, or implement a patient cohort.
- User provides clinical criteria in natural language.
- Work requires mapping clinical terms to recognized data constants.
- Task requires drafting `cohort.md` and optionally generating `build_cohort.py`.

## Required Workflow
1. Ask the user to describe the cohort in plain language.
2. Translate natural-language terms to recognized constants before finalizing criteria.
3. Create `cohort_analyses/YYYY-MM-DD_<cohort_name>/`.
4. Draft `cohort.md` using `cohort_curation/cohort_criteria_template.md`.
5. Ask clarifying questions for missing high-impact criteria.
6. For every clarifying question, include exactly 3 default options plus 1 ignore/defer option.
7. Update `cohort.md` immediately after each user response.
8. Pause and request explicit user review of `cohort.md` before code generation.
9. Do not generate `build_cohort.py` until user confirms readiness.
10. Do not run scripts unless the user explicitly asks for execution.

## Guardrails
- Use `cohort_curation/recognized_constants_snapshot.json` as the source of recognized constants.
- When user language is high-level, use oncology domain knowledge to choose relevant constants.
- Keep cohort filtering logic in cohort-specific scripts, not in package loaders.
- Write one `PATIENT_ID` per line to final cohort output files.

## References
- [Interactive protocol](./references/protocol.md)
- [Implementation checklist](./references/implementation.md)
