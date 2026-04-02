# Cohort Criteria

## Cohort Metadata
- Cohort name: PD1/PDL1 ICI with pre-treatment IMPACT and early post-ICI progression
- Analysis folder: `cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_progression`
- Script: `cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_progression/build_cohort.py`
- Output: `cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_progression/final_cohort_patient_ids.txt`

## Clinical Question
- Primary objective: Identify adult pan-cancer patients treated with PD1/PDL1 immunotherapy who had at least one IMPACT sample within 365 days before treatment start and radiologic progression within 3 months after treatment start.
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
- User phrase: `radiological progression finding`
  - Constant category: progression timeline (`data_timeline_progression.txt` via imaging loader)
   - Operational value:
    - `PROGRESSION = Yes`

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
   - Exposure time window relative to index: index is first qualifying PD1/PDL1 treatment start date.
4. Baseline sample/biomarker requirement:
   - Marker/panel/test required: at least one IMPACT panel sample.
   - Pre-index window: sample START_DATE in [-365, 0) days relative to index date.
5. Follow-up/event requirement:
   - At least one progression event within 3 months after index date.
   - Implementation: progression timeline record with `PROGRESSION = Yes` and START_DATE in [0, 90] days after index.

## Exclusion Criteria (Required)
1. Missing or invalid key dates (index treatment date, sample date, progression date).
2. Missing age needed to verify age >= 18.
3. No qualifying PD1/PDL1 treatment exposure.
4. No qualifying IMPACT sample in baseline window.
5. No qualifying post-index progression event in outcome window.
6. Conflicting timeline logic (for example, progression date before index when evaluating post-index outcome).

## Operational Definitions
- Index date: earliest START_DATE among qualifying PD1/PDL1 treatment records.
- Baseline window: 365 days before index, excluding index day for sample requirement.
- Exposure window: at/before index for treatment ascertainment.
- Outcome window: day 0 through day 90 after index, inclusive.
- Censoring rules: not yet specified (likely event ascertainment only for this inclusion-style cohort).

## Outputs
- Final patient list path: `cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_progression/final_cohort_patient_ids.txt`
- Optional intermediate QC tables: to be defined at script stage.

## Reproducibility
- Run command (from project root):

```bash
.venv/bin/python cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_progression/build_cohort.py \
  --data-root data \
  --output cohort_analyses/2026-03-18_pd1_pdl1_impact_pre_progression/final_cohort_patient_ids.txt
```

- Package/API dependencies (anticipated):
  - `cohort_curation.loaders.patient`
  - `cohort_curation.loaders.procedures`
  - `cohort_curation.loaders.genomics`
  - `cohort_curation.loaders.imaging`
