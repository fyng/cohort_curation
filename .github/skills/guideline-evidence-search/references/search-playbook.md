# Search Playbook

## Inputs
- User clinical question
- Suspected or explicit cancer type
- Desired response format (bullets, table, concise answer, etc.)

## Retrieval Steps
1. Resolve cancer type to one parsed folder under `guidelines/parsed/`.
2. Open `sections/toc.md` first to understand document structure.
3. Use `sections/index.json` to shortlist candidate sections by title and page range.
4. Read selected section markdown files.
5. Inspect linked table and flowchart artifacts for decision logic.
6. Use chunks for additional detail if section files are long.
7. Pull exact evidence lines needed for user-facing synthesis.

## Topic Routing Hints
- Diagnosis, staging, and initial workup: often in early disease-specific sections.
- Treatment recommendations: often grouped by stage, subtype, line of therapy, or modality.
- Principles pages: useful for imaging, surgery, radiation, systemic therapy, and toxicity management.
- Subtypes and biomarkers: often represented in dedicated sections and pathway panels.

## Citation Policy
- Prefer section-level citations first.
- Add table/flowchart citations when they materially support decisions.
- Use page artifacts only when section/chunk/table/flowchart evidence is insufficient.

## Failure Handling
- If a needed topic is not found, report what was searched and where.
- Suggest adjacent sections that are likely relevant.
- Ask one focused clarification question only when necessary.
