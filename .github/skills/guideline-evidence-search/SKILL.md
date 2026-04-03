---
name: guideline-evidence-search
description: "Use when searching parsed clinical guidelines for diagnosis, workup, treatment, prognosis, and subtype-specific recommendations. Identify the cancer type first, read the guideline TOC/page guide first, review relevant sections plus tables/flowcharts, and return evidence in the requested format with source citations."
argument-hint: "Describe cancer type (or suspected type), clinical question, and preferred output format."
---

# Guideline Evidence Search

Use this skill to answer clinical guideline questions from parsed artifacts under `guidelines/parsed/`.

## When to Use
- User asks for guideline evidence on diagnosis, workup, treatment, prognosis, surveillance, or disease subtypes.
- User asks for section-level evidence synthesis from parsed guideline files.
- User asks for decision workflow evidence that may be summarized in tables or pathway/flowchart artifacts.

## Required Workflow
1. Identify the target cancer type before reading detailed content.
2. Read the section guide first:
   - `guidelines/parsed/<cancer>/sections/toc.md`
   - `guidelines/parsed/<cancer>/sections/index.json`
3. Locate candidate sections based on intent category:
   - diagnosis/staging/workup
   - treatment principles
   - disease-subtype recommendations
   - surveillance/follow-up
   - references/discussion
4. Read section markdown files for narrative context.
5. Always inspect supportive structured artifacts when available:
   - tables in `tables/index.json` and table markdown files
   - flowcharts in `flowcharts/index.json` and flowchart markdown/json files
6. Use chunk files (`chunks/index.json`) for long sections when additional detail is needed.
7. Synthesize evidence and match the exact output format requested by the user.

## Decision Points and Branching
- If cancer type is missing or ambiguous, infer from user terms and confirm when confidence is low.
- If multiple cancers are requested, repeat the same TOC-first workflow per cancer and then compare.
- If no exact-match section title exists, expand search to nearby categories (for example, workup -> staging/principles).
- If section narrative is sparse, prioritize linked tables/flowcharts and relevant chunks.

## Quality Checks Before Responding
- Cancer type is explicit and mapped to a parsed guideline folder.
- TOC/page guide was consulted before deep reads.
- Evidence includes both narrative and structured artifacts (table/flowchart) when available.
- Output matches requested format and scope.
- Claims are tied to concrete file citations.
- Uncertainty or evidence gaps are clearly stated.

## Cancer Type Mapping (Current Parsed Set)
- `aml`: Acute Myeloid Leukemia
- `breast`: Breast Cancer
- `colon`: Colon/Colorectal Cancer
- `nscl`: Non-Small Cell Lung Cancer
- `pancreatic`: Pancreatic Adenocarcinoma
- `prostate`: Prostate Cancer

## References
- [Search playbook](./references/search-playbook.md)
- [Output templates](./references/output-templates.md)
