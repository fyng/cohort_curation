# Cohort Criteria

## Cohort Metadata
- Cohort name: PD1/PDL1 ICI with pre-treatment IMPACT and delayed first post-ICI progression
- Analysis folder: `cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_first_progression_gt365`
- Script: `cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_first_progression_gt365/build_cohort.py`
- Output: `cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_first_progression_gt365/final_cohort_patient_ids.txt`

## Clinical Question
- Primary objective: Identify adult pan-cancer patients treated with PD1/PDL1 immunotherapy who had at least one IMPACT sample within 365 days before treatment start and whose first post-treatment radiologic progression occurs more than 365 days after treatment start.
- Secondary objectives: Not specified yet.

## Term Mapping (Natural Language -> Recognized Constants)
Source: `cohort_curation/recognized_constants_snapshot.json`

Mappings for this cohort:
- User phrase: `PD1/PDL1 immunotherapy`
  - Constant category: `treatment_names`
  - Recognized constants (confirmed broad PD1/PDL1 set):
    - `Atezolizumab`
    - `Avelumab`
    - `Cemiplimab`
    - `Durvalumab`
    - `Dostarlimab`
    - `Nivolumab`
    - `Pembrolizumab`
    - `Retifanlimab`
    - `Toripalimab`
- User phrase: `IMPACT sample`
  - Constant category: `genomic_panel_names`
  - Recognized constants:
    - `IMPACT341`
    - `IMPACT410`
    - `IMPACT468`
    - `IMPACT505`
    - `IMPACT-HEME-400`
    - `IMPACT-HEME-468`
- User phrase: `first progression found after PD1/PDL1 treatment start is >365 days`
  - Constant category: progression timeline (`data_timeline_progression.txt` via imaging loader)
  - Operational value:
    - Restrict to records with `PROGRESSION = Yes`
    - For each patient, define first post-index progression as the minimum progression START_DATE with START_DATE >= INDEX_DATE
    - Require first post-index progression date minus INDEX_DATE > 365 days

## Inclusion Criteria (Required)
1. Diagnosis definition:
   - Cancer type/site: all cancer types (no cancer-type restriction).
   - Confirmation source: diagnosis/sample presence in harmonized tables (no additional histology/stage restriction).
2. Age:
   - Minimum age at index date: 18 years.
3. Treatment exposure:
   - Required line/agent/class: at least one of the following PD1/PDL1 agents:
     - `Atezolizumab`
     - `Avelumab`
     - `Cemiplimab`
     - `Durvalumab`
     - `Dostarlimab`
     - `Nivolumab`
     - `Pembrolizumab`
     - `Retifanlimab`
     - `Toripalimab`
   - Exposure time window relative to index: index is first qualifying PD1/PDL1 treatment START_DATE.
4. Baseline sample/biomarker requirement:
   - Marker/panel/test required: at least one IMPACT panel sample.
   - Pre-index window: sample START_DATE in [-365, 0) days relative to index date.
5. Follow-up/event requirement:
   - At least one progression event exists after index date.
   - Implementation: progression timeline records with `PROGRESSION = Yes`; first post-index progression must occur strictly more than 365 days after index.

## Exclusion Criteria (Required)
1. Missing or invalid key dates (index treatment date, sample date, progression date).
2. Missing age needed to verify age >= 18.
3. No qualifying PD1/PDL1 treatment exposure.
4. No qualifying IMPACT sample in baseline window.
5. No post-index progression record with `PROGRESSION = Yes`.
6. First post-index progression occurs on or before day 365.
7. Conflicting timeline logic (for example, progression date before index when evaluating post-index outcome).

## Operational Definitions
- Index date: earliest START_DATE among qualifying PD1/PDL1 treatment records.
- Baseline window: 365 days before index, excluding index day for sample requirement.
- Exposure window: at/before index for treatment ascertainment.
- Outcome definition: first post-index progression date is the minimum progression START_DATE with START_DATE >= INDEX_DATE and `PROGRESSION = Yes`; include patient only if this first progression is > 365 days from index.
- Censoring rules: not yet specified (event ascertainment only for this inclusion-style cohort).

## Outputs
- Final patient list path: `cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_first_progression_gt365/final_cohort_patient_ids.txt`
- Optional intermediate QC tables: to be defined at script stage.

## Reproducibility
- Run command (from project root):

```bash
.venv/bin/python cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_first_progression_gt365/build_cohort.py \
  --data-root data \
  --output cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_first_progression_gt365/final_cohort_patient_ids.txt
```

- Package/API dependencies (anticipated):
  - `cohort_curation.loaders.patient`
  - `cohort_curation.loaders.procedures`
  - `cohort_curation.loaders.genomics`
  - `cohort_curation.loaders.imaging`
