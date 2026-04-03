# Cohort Criteria Template

Use this template for new cohort analyses. Keep all paths relative to the project root.

## Cohort Metadata
- Cohort name:
- Analysis folder: `cohort_analyses/YYYY-MM-DD_<cohort_name>`
- Script: `cohort_analyses/YYYY-MM-DD_<cohort_name>/build_cohort.py`
- Output: `cohort_analyses/YYYY-MM-DD_<cohort_name>/final_cohort_patient_ids.txt`

## Clinical Question
- Primary objective:
- Secondary objectives:

## Term Mapping (Natural Language -> Recognized Constants)
Use recognized constants from:
- `cohort_curation/recognized_constants_snapshot.json`.

For high-level user phrases, use oncology domain knowledge to select the most relevant constants from the snapshot.

Document every non-literal user phrase that maps to coded values.

Example:
- User phrase: `PD1/PDL1 immunotherapy`
- Treatment constants: `Pembrolizumab`, `Durvalumab`, `Cemiplimab`, `Atezolizumab`, `Avelumab`

Mappings for this cohort:
- User phrase:
   - Constant category:
   - Recognized constants:

## Inclusion Criteria (Required)
1. Diagnosis definition:
   - Cancer type/site:
   - Confirmation source (pathology/ICD/staging):
2. Age:
   - Minimum age at index date:
3. Treatment exposure:
   - Required line/agent/class:
   - Exposure time window relative to index:
4. Baseline sample/biomarker requirement:
   - Marker/panel/test required:
   - Pre-index or post-index window:
5. Follow-up sufficiency:
   - Minimum follow-up duration or event ascertainment requirement:

## Exclusion Criteria (Required)
1. Missing or invalid key dates (index, treatment, sample).
2. Missing required covariates/outcomes.
3. Conflicting timeline logic (events impossible by date ordering).
4. Prior malignancy rules (if applicable).

## Additional Common Criteria To Consider
The following are common in oncology clinical trial-style cohort curation.

### Demographics
- Include/exclude by upper age threshold (for frailty-sensitive studies).
- Restrict by pediatric/adult populations only.
- Consider sex-specific disease constraints when biologically relevant.
- Rationale: improves comparability to target trial population.
- Bias caution: can reduce representativeness of older or underserved groups.

### Disease & Stage
- Require stage at diagnosis (for example metastatic only).
- Require histology subtype or exclude rare subtypes.
- Exclude in situ-only disease if invasive disease is the target.
- Rationale: controls heterogeneity in prognosis and treatment pathways.
- Bias caution: staging and histology completeness vary across sites and years.

### Prior Therapy / Line of Therapy
- Exclude prior exposure to same drug class before index.
- Require first-line setting only, or specific line number.
- Exclude investigational trial-only regimens if non-comparable.
- Rationale: reduces confounding from heavily pretreated populations.
- Bias caution: line-of-therapy can be difficult to infer and inconsistently documented.

### Biomarkers / Genomics
- Require availability of PD-L1/MMR/MSI/TMB or specific mutation status.
- Specify assay timing window around index date.
- Optionally include unknown biomarker as separate stratum instead of exclusion.
- Rationale: aligns cohort with precision oncology treatment intent.
- Bias caution: testing itself is selective and may introduce access bias.

### Organ Function / Performance Status Proxies
- Require baseline lab availability (CBC/CMP, renal/hepatic markers).
- Require ECOG/KPS within a baseline window.
- Exclude severe organ dysfunction beyond protocol-like thresholds.
- Rationale: approximates trial eligibility and treatment fitness.
- Bias caution: stricter requirements can disproportionately exclude sicker patients.

### Timeline and Data Quality
- Require at least one pre-index and one post-index encounter.
- Exclude patients lost to follow-up before outcome assessment window.
- Restrict calendar period to modern treatment era.
- Rationale: improves outcome capture quality.
- Bias caution: may favor high-utilization patients and larger centers.

## Operational Definitions
- Index date:
- Baseline window:
- Exposure window:
- Outcome window:
- Censoring rules:

## Outputs
- Final patient list path:
- Optional intermediate QC tables:

## Reproducibility
- Run command (from project root):

```bash
.venv/bin/python cohort_analyses/YYYY-MM-DD_<cohort_name>/build_cohort.py \
  --data-root data \
  --output cohort_analyses/YYYY-MM-DD_<cohort_name>/final_cohort_patient_ids.txt
```

- Package/API dependencies:
  - `cohort_curation.loaders.patient`
  - `cohort_curation.loaders.procedures`
  - `cohort_curation.loaders.genomics`
  - Add other loaders as needed
