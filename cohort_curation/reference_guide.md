# Cohort Curation Reference Guide

This is the human-readable reference for cohort curation data contracts.

## Canonical Reference Files

- Human-readable reference: `cohort_curation/reference_guide.md`
- Machine-readable reference: `cohort_curation/reference_data.py`

## Python Access

```python
from cohort_curation.reference_data import (
    RECOGNIZED_CONSTANTS,
    DATAFRAME_INTERFACES,
    FILE_NAMES,
    ACTION_LABELS,
)
```

## Recognized Constants Categories

Source dictionary: `RECOGNIZED_CONSTANTS` in `reference_data.py`.

- `treatment_names`
- `genomic_panel_names`
- `ancestry_labels`
- `sex_labels`
- `ethnicity_labels`
- `smoking_labels`
- `prior_medication_labels`
- `os_status_labels`
- `sample_type_labels`
- `msi_type_labels`
- `action_labels`

## File Key Map

Source dictionary: `FILE_NAMES` in `reference_data.py`.

| File key | Relative data path |
| --- | --- |
| `patient` | `data_clinical_patient.txt` |
| `sample` | `data_clinical_sample.txt` |
| `ancestry` | `data_clinical_supp_ancestry.txt` |
| `mutations` | `data_mutations_extended.txt` |
| `sv` | `data_sv.txt` |
| `cna_long` | `data_CNA_long_format.txt` |
| `diagnosis` | `data_timeline_diagnosis.txt` |
| `follow_up` | `data_timeline_follow_up.txt` |
| `specimen_surgery` | `data_timeline_specimen_surgery.txt` |
| `tumor_sites` | `data_timeline_tumor_sites.txt` |
| `cancer_presence` | `data_timeline_cancer_presence.txt` |
| `progression` | `data_timeline_progression.txt` |
| `treatment` | `data_timeline_treatment.txt` |
| `surgery` | `data_timeline_surgery.txt` |
| `radiation` | `data_timeline_radiation.txt` |
| `mmr` | `data_timeline_mmr.txt` |
| `pdl1` | `data_timeline_pdl1.txt` |
| `gleason` | `data_timeline_gleason.txt` |
| `labs_metabolic_tsv` | `labs_metabolic_20240813.tsv` |
| `ca_15_3_labs` | `data_timeline_ca_15_3_labs.txt` |
| `ca_19_9_labs` | `data_timeline_ca_19_9_labs.txt` |
| `ca_125_labs` | `data_timeline_ca_125_labs.txt` |
| `cea_labs` | `data_timeline_cea_labs.txt` |
| `psa_labs` | `data_timeline_psa_labs.txt` |
| `tsh_labs` | `data_timeline_tsh_labs.txt` |
| `bmi` | `data_timeline_bmi.txt` |
| `ecog_kps` | `data_timeline_ecog_kps.txt` |

## Source Columns for Key Cohort Concepts

| Concept | Source table | Source columns |
| --- | --- | --- |
| Cancer stage | `data_timeline_diagnosis.txt` | `CLINICAL_GROUP`, `STAGE_CDM_DERIVED_GRANULAR` |
| Mutations | `data_mutations_extended.txt` | `SAMPLE_ID`, `Hugo_Symbol` |
| Structural variants | `data_sv.txt` | `SAMPLE_ID`, `Site1_Hugo_Symbol`, `Site2_Hugo_Symbol` |
| Copy number alterations | `data_CNA_long_format.txt` | `SAMPLE_ID`, `Hugo_Symbol` |
| Surgery mapping | `surg_purpose_map.csv` | `DATA` -> `REFINEMENT_RESULT` |
| Curative surgery | `data_timeline_surgery.txt` | `SURGERY_CATEGORY == Tumor removal` |

## Dataframe Interfaces

Source dictionary: `DATAFRAME_INTERFACES` in `reference_data.py`.

Interface keys:
- `patient.load_patient_harmonized`
- `diagnosis.load_diagnosis_harmonized`
- `genomics.load_sample_harmonized`
- `genomics.load_mutations_raw`
- `genomics.load_cna_raw`
- `genomics.load_sv_raw`
- `genomics.load_genomics_event_table`
- `procedures.load_treatment_harmonized`
- `procedures.load_surgery_harmonized`
- `procedures.load_curative_surgery_harmonized`
- `procedures.load_radiation_harmonized`
- `imaging.load_tumor_sites_harmonized`
- `imaging.load_progression_harmonized`
- `histopathology.load_histopathology_harmonized`
- `followup.load_followup_first_consult`
- `labs.load_labs_harmonized`

## Label Maps and Actions

Source dictionaries in `reference_data.py`:

- `PATIENT_PRIOR_MED_MAP`
- `PATIENT_SMOKING_MAP`
- `PATIENT_OS_STATUS_MAP`
- `ACTION_LABELS`
