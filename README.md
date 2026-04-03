This repository provides a reusable clinical data package and agent-driven workflows over real-world oncology data. Cohort curation is currently implemented as a dedicated skill, and additional workflows can be added in the same pattern.

## Human + AI Agent Collaboration
This repository is designed to be used collaboratively by a human user and an AI coding agent.

Expected interaction model:
- The human user defines the clinical intent and reviews criteria decisions.
- The AI agent drafts cohort artifacts, asks clarifying questions, and implements scripts.
- The human user approves the finalized criteria before code generation and any execution.

This collaborative workflow is required for cohort curation tasks.


## Regimen Curation
Sample prompt:
"""Use the Regimen Curation Orchestrator agent.

Curate treatment regimens for this cohort subset:

Cancer type: lung adenocarcinoma (LUAD)
Stage: IV
Age: >21
Sex: all
Prior treatment status: all"""

## Cohort Curation 
### Cohort Curation Workflow (Brief)
For each new cohort analysis:
1. Describe the cohort in plain language to the AI agent.
2. The agent creates `cohort_analyses/YYYY-MM-DD_<cohort_name>/cohort.md` using `cohort_curation/cohort_criteria_template.md`.
3. The agent asks follow-up clarifying questions for unspecified high-impact criteria.
4. The user reviews and edits `cohort.md` manually.
5. Only after explicit user confirmation, the agent generates `build_cohort.py`.
6. The agent runs analysis only if the user explicitly requests execution.

Use the cohort skill at `.github/skills/cohort-curation/SKILL.md`.
See `cohort_curation/WORKFLOW.md` for the full interactive protocol.

### Usage Instructions for Human Users
1. Start in project root and open a chat with your AI agent.
2. Provide a plain-language cohort request (disease, treatment, timing, inclusion/exclusion).

    Example initial prompt:
    ```
    Help me curate a cohort:
    - Age >=18
    - Any sex and ethnicity
    - All cancer types
    - patients treated with PD1/PDL1 immunotherapy
    - patients have IMPACT at least one IMPACT sample collected within 365 days BEFORE starting PD1/PDL1 immunotherapy
    - patients have a radiological progression finding within 3 months after PD1/PDL1 immunotherapy
    ```

3. Answer the agent's clarification prompts.
4. Review and edit the generated `cohort.md` file.
5. Tell the agent when you are ready for script generation.
6. If desired, explicitly ask the agent to run the script and validate output counts.

Important:
- Do not assume scripts will run automatically.
- Execution should happen only after you explicitly request it.


## Data
The cohort contains over 100,000 cancer patients across multiple cancer types. Data is stored under `data/` and organized as tab-separated tables by domain.

Patient timelines are keyed by `PATIENT_ID`, with event-time fields such as `START_DATE` and `STOP_DATE` where available.
In the notebook workflow, timelines are aligned relative to each patient's first sequencing record (derived from `WEEK_ADDED` in `data_clinical_sample.txt`).

### Domain File Groups
- Patient clinical: `data_clinical_patient.txt`, `data_clinical_supp_ancestry.txt`
- Sample/genomics: `data_clinical_sample.txt`, `data_mutations_extended.txt`, `data_CNA_long_format.txt`, `data_sv.txt`
- Diagnosis timeline: `data_timeline_diagnosis.txt`
- Labs timeline: `labs_metabolic_20240813.tsv`, `data_timeline_ca_15_3_labs.txt`, `data_timeline_ca_19_9_labs.txt`, `data_timeline_ca_125_labs.txt`, `data_timeline_cea_labs.txt`, `data_timeline_psa_labs.txt`, `data_timeline_tsh_labs.txt`, `data_timeline_bmi.txt`, `data_timeline_ecog_kps.txt`
- Imaging/progression timeline: `data_timeline_tumor_sites.txt`, `data_timeline_cancer_presence.txt`, `data_timeline_progression.txt`
- Treatment/procedures timeline: `data_timeline_treatment.txt`, `data_timeline_surgery.txt`, `data_timeline_radiation.txt`, `data_timeline_specimen_surgery.txt`
- Histopathology timeline: `data_timeline_mmr.txt`, `data_timeline_pdl1.txt`, `data_timeline_gleason.txt`
- Follow-up timeline: `data_timeline_follow_up.txt`

### Label Harmonization Used by Notebook
The notebook performs import-time harmonization that is now exposed through package loaders, including:
- Patient label maps (`PRIOR_MED_TO_MSK`, smoking labels, `OS_STATUS`) and ancestry merge
- Sample normalization (`MSI_TYPE` normalization, `CVR_TMB_COHORT_DECILE`, categorical text cleanup)
- Diagnosis parsing from `DX_DESCRIPTION` to structured cancer/site fields
- Labs test-name normalization to canonical labels
- Standardized `ACTION` event labels (`DIAGNOSE`, `SEQUENCE`, `LAB`, `OBSERVE`, `PROGRESSION`, `TREAT`, `HISTOPATH`, `FIRST_CONSULT`)

Filtering thresholds and cohort inclusion logic are intentionally not part of the package loaders.

## Guideline PDF Parsing
Large guideline PDFs can be parsed into LLM-friendly markdown artifacts under `guidelines/parsed/`.

Run the batch parser from project root:

```bash
python -m parse_pdf --raw-root guidelines/raw --parsed-root guidelines/parsed
```

Parse a single file:

```bash
python -m parse_pdf --raw-root guidelines/raw --parsed-root guidelines/parsed --pdf breast.pdf
```

Output structure per guideline:
- `pages/`: cleaned page markdown + metadata json
- `sections/`: hierarchy-aware section markdown, TOC, section index
- `chunks/`: ~1200-1800 token markdown chunks + chunk index
- `tables/`: extracted markdown tables + index
- `flowcharts/`: arrow-flow text artifacts + graph json
- `reports/`: validation and sanitization reports

Strict validation is enabled by default and fails when prohibited header/footer content remains in parsed markdown files.

## Using The Package

### Install

```bash
pip install -e .
```

### Quick Start

```python
from cohort_curation.loaders import (
	patient,
	genomics,
	diagnosis,
	labs,
	imaging,
	procedures,
	histopathology,
	followup,
)

# Set explicit root if your data is not in ./data
data_root = "data"

df_patient = patient.load_patient_harmonized(data_root=data_root)
df_sample = genomics.load_sample_harmonized(data_root=data_root)
df_genomics = genomics.load_genomics_event_table(data_root=data_root)
df_diag = diagnosis.load_diagnosis_harmonized(data_root=data_root)
df_labs = labs.load_labs_harmonized(data_root=data_root)
df_tumor = imaging.load_tumor_sites_harmonized(data_root=data_root)
df_prog = imaging.load_progression_harmonized(data_root=data_root)
df_treat = procedures.load_treatment_harmonized(data_root=data_root)
df_surgery = procedures.load_surgery_harmonized(data_root=data_root)
df_radiation = procedures.load_radiation_harmonized(data_root=data_root)
df_histopath = histopathology.load_histopathology_harmonized(data_root=data_root)
df_consult = followup.load_followup_first_consult(data_root=data_root)
```

### Data Root Resolution

Loaders resolve data files in this order:
1. `data_root` argument passed to the loader
2. `COHORT_CURATION_DATA_ROOT` environment variable
3. Existing local defaults: `data/`, then `data/msk_solid_heme_epic/`

Example:

```bash
export COHORT_CURATION_DATA_ROOT=/path/to/data
```

### Package Layout

- `cohort_curation/loaders/patient.py`: patient and follow-up derived patient harmonization
- `cohort_curation/loaders/genomics.py`: sample, mutation, CNA, genomics event table
- `cohort_curation/loaders/diagnosis.py`: diagnosis import and `DX_DESCRIPTION` parsing
- `cohort_curation/loaders/labs.py`: metabolic and supplementary labs import and label normalization
- `cohort_curation/loaders/imaging.py`: tumor-site, progression, and cancer-presence loaders
- `cohort_curation/loaders/procedures.py`: treatment, surgery, radiation loaders
- `cohort_curation/loaders/histopathology.py`: MMR/PDL1/Gleason merged timeline loader
- `cohort_curation/loaders/followup.py`: raw and first-consult follow-up loaders


