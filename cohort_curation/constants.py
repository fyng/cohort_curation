"""Shared constants for data file access."""

from pathlib import Path

DATA_ROOT_ENV_VAR = "COHORT_CURATION_DATA_ROOT"

# When no explicit root is provided, these locations are checked in order.
DEFAULT_DATA_ROOT_CANDIDATES = (
    Path("data"),
    Path("data/msk_solid_heme_epic"),
)

FILE_NAMES = {
    "patient": "data_clinical_patient.txt",
    "sample": "data_clinical_sample.txt",
    "ancestry": "data_clinical_supp_ancestry.txt",
    "mutations": "data_mutations_extended.txt",
    "cna_long": "data_CNA_long_format.txt",
    "diagnosis": "data_timeline_diagnosis.txt",
    "follow_up": "data_timeline_follow_up.txt",
    "specimen_surgery": "data_timeline_specimen_surgery.txt",
    "tumor_sites": "data_timeline_tumor_sites.txt",
    "cancer_presence": "data_timeline_cancer_presence.txt",
    "progression": "data_timeline_progression.txt",
    "treatment": "data_timeline_treatment.txt",
    "surgery": "data_timeline_surgery.txt",
    "radiation": "data_timeline_radiation.txt",
    "mmr": "data_timeline_mmr.txt",
    "pdl1": "data_timeline_pdl1.txt",
    "gleason": "data_timeline_gleason.txt",
    "labs_metabolic_tsv": "labs_metabolic_20240813.tsv",
    "ca_15_3_labs": "data_timeline_ca_15_3_labs.txt",
    "ca_19_9_labs": "data_timeline_ca_19_9_labs.txt",
    "ca_125_labs": "data_timeline_ca_125_labs.txt",
    "cea_labs": "data_timeline_cea_labs.txt",
    "psa_labs": "data_timeline_psa_labs.txt",
    "tsh_labs": "data_timeline_tsh_labs.txt",
    "bmi": "data_timeline_bmi.txt",
    "ecog_kps": "data_timeline_ecog_kps.txt",
}

PATIENT_PRIOR_MED_MAP = {
    "Prior medications to MSK": "Yes",
    "No prior medications": "No",
    "Unknown": "Unknown",
}

PATIENT_SMOKING_MAP = {
    "Former/Current Smoker": "Yes",
    "Never": "Never",
    "Unknown": "Unknown",
}

PATIENT_OS_STATUS_MAP = {
    "1:DECEASED": "Deceased",
    "0:LIVING": "Living",
}

ACTION_LABELS = {
    "sample": "SEQUENCE",
    "diagnosis": "DIAGNOSE",
    "labs": "LAB",
    "tumor_sites": "OBSERVE",
    "progression": "PROGRESSION",
    "treatment": "TREAT",
    "histopath": "HISTOPATH",
    "followup_first_consult": "FIRST_CONSULT",
}
