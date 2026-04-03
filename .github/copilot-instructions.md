# Project Guidelines

## Scope
- This repository supports multiple workflow types over a shared clinical data package.
- Keep workflow-specific procedures in dedicated skills under `.github/skills/`.

## Skill Routing
- For cohort curation tasks, use the `cohort-curation` skill at `.github/skills/cohort-curation/SKILL.md`.
- Use `cohort_curation/WORKFLOW.md` and `cohort_curation/cohort_criteria_template.md` for cohort-curation protocol details.

## Code Style
- Prefer small, explicit Python functions and clear pandas transformations over chained one-liners.
- Keep scripts standalone with `argparse` and root-relative paths.
- Use `Path` for file outputs.

## Architecture
- `cohort_curation/` is the reusable package layer for domain loaders (`raw` and `harmonized` access).
- Keep workflow-specific inclusion/exclusion logic in workflow scripts, not package loaders.

## Conventions
- Assume Linux working directory is project root for all documented commands.
- Keep all paths project-root relative; avoid machine-specific absolute paths.
- Prefer defensive column handling in pandas (column checks, `pd.to_numeric(..., errors="coerce")`).
