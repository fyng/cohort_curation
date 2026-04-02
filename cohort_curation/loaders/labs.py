"""Laboratory data loaders and label harmonization."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..constants import ACTION_LABELS, FILE_NAMES
from ..io import read_tsv, resolve_data_root


LAB_TEST_NAME_MAP = {
    "hgb": "Hemoglobin",
    "rbc": "Red Blood Cell",
    "hct": "Hematocrit",
    "red blood cell distribution width rdw": "RDW",
    "rdw": "RDW",
    "platelets": "Platelet",
    "wbc": "White Blood Cell",
    "neutrophil": "Neutrophil",
    "abs neut": "Neutrophil",
    "absolute neutrophil": "Neutrophil",
    "lymph": "Lymphocyte",
    "abs lymph": "Lymphocyte",
    "absolute lymphocyte": "Lymphocyte",
    "mono": "Monocyte",
    "abs mono": "Monocyte",
    "absolute monocyte": "Monocyte",
    "eos": "Eosinophil",
    "abs eos": "Eosinophil",
    "absolute eosinophil": "Eosinophil",
    "baso": "Basophil",
    "abs baso": "Basophil",
    "absolute basophil": "Basophil",
    "absolute immature granulocyte": "Immature Granulocyte",
    "immature granulocyte": "Immature Granulocyte",
    "creatinine": "Creatinine",
    "creatinine whole blood": "Creatinine",
    "creatinine plasma": "Creatinine",
    "glucose plasma": "Glucose",
    "glucose whole blood": "Glucose",
    "glucose": "Glucose",
    "calcium plasma": "Calcium",
    "calcium": "Calcium",
    "sodium plasma": "Sodium",
    "sodium whole blood": "Sodium",
    "sodium": "Sodium",
    "chloride plasma": "Chloride",
    "chloride whole blood": "Chloride",
    "chloride": "Chloride",
    "potassium plasma": "Potassium",
    "potassium whole blood": "Potassium",
    "potassium": "Potassium",
    "carbon dioxide co2 plasma": "CO2",
    "co2 carbon dioxide": "CO2",
    "co2 plasma": "CO2",
    "carbon dioxide co2 total": "CO2",
    "total co2": "CO2",
    "blood urea nitrogen bun plasma": "BUN",
    "bun plasma": "BUN",
    "bun": "BUN",
    "blood urea nitrogen bun": "BUN",
    "blood urea nitrogen plasma": "BUN",
    "blood urea nitrogen bun whole blood": "BUN",
    "bun whole blood": "BUN",
    "albumin plasma": "Albumin",
    "albumin": "Albumin",
    "protein total plasma": "Total Protein",
    "protein total": "Total Protein",
    "bilirubin total plasma": "Total Bilirubin",
    "bilirubin total": "Total Bilirubin",
    "alkaline phosphatase alk plasma": "ALK",
    "alkaline phosphatase plasma": "ALK",
    "alkaline phosphatase alk": "ALK",
    "alkaline phosphatase": "ALK",
    "aspartate aminotransferase ast plasma": "AST",
    "aspartate aminotransferase ast": "AST",
    "ast plasma": "AST",
    "ast": "AST",
    "alanine aminotransferase alt plasma": "ALT",
    "alanine aminotransferase alt": "ALT",
    "alt plasma": "ALT",
    "alt": "ALT",
    "egfr ckdepi 2021": "eGFR",
    "egfr nonafrican american": "eGFR",
    "egfr african american": "eGFR",
    "estimated gfr egfr": "eGFR",
    "egfr pediatric": "eGFR",
}

DEFAULT_SUPPLEMENTARY_LAB_KEYS = [
    "ca_15_3_labs",
    "ca_19_9_labs",
    "ca_125_labs",
    "cea_labs",
    "psa_labs",
    "tsh_labs",
    "bmi",
    "ecog_kps",
]


LAB_RAW_DTYPES = {
    "LR_MRN": "Int64",
    "LR_SUBTEST_NAME": str,
    "LR_TEST_NAME": str,
    "LR_RESULT_VALUE": str,
    "LR_UNIT_MEASURE": str,
}


def load_labs_metabolic_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load metabolic labs from parquet if available, else TSV."""
    root = resolve_data_root(data_root)

    parquet_candidates = [
        root / "labs" / "labs_metabolic_20240813.parquet",
        root / "labs_metabolic_20240813.parquet",
    ]
    for path in parquet_candidates:
        if path.exists():
            return pd.read_parquet(path)

    return read_tsv(FILE_NAMES["labs_metabolic_tsv"], data_root=data_root, comment=None, dtype=LAB_RAW_DTYPES)


def harmonize_lab_names(df: pd.DataFrame, name_col: str = "LR_SUBTEST_NAME") -> pd.DataFrame:
    """Apply notebook-consistent lab test name normalization map."""
    out = df.copy()
    if name_col in out.columns:
        out[name_col] = out[name_col].replace(LAB_TEST_NAME_MAP)
    return out


def load_labs_supplementary(
    data_root: str | None = None,
    file_keys: list[str] | None = None,
) -> pd.DataFrame:
    """Load supplementary timeline lab files and harmonize LR column names."""
    keys = file_keys or DEFAULT_SUPPLEMENTARY_LAB_KEYS
    parts: list[pd.DataFrame] = []

    for key in keys:
        file_name = FILE_NAMES[key]
        df = read_tsv(file_name, data_root=data_root, comment=None)

        if key == "bmi" and "RESULT" in df.columns:
            df["RESULT"] = pd.to_numeric(df["RESULT"], errors="coerce")

        if key == "ecog_kps":
            if "ECOG_KPS" in df.columns:
                df = df.rename(columns={"ECOG_KPS": "LR_RESULT_VALUE"})
            df["LR_SUBTEST_NAME"] = "ECOG_KPS"

        df = df.rename(columns={"TEST": "LR_SUBTEST_NAME", "RESULT": "LR_RESULT_VALUE"})
        parts.append(df)

    if not parts:
        return pd.DataFrame()

    return pd.concat(parts, ignore_index=True)


def load_labs_harmonized(
    data_root: str | None = None,
    include_supplementary: bool = True,
) -> pd.DataFrame:
    """Load labs with import-time schema and label harmonization only."""
    metabolic = load_labs_metabolic_raw(data_root=data_root)
    frames = [harmonize_lab_names(metabolic)]

    if include_supplementary:
        supplemental = load_labs_supplementary(data_root=data_root)
        if not supplemental.empty:
            frames.append(supplemental)

    df = pd.concat(frames, ignore_index=True, sort=False)

    if "LR_SUBTEST_NAME" in df.columns:
        df["LR_SUBTEST_NAME"] = df["LR_SUBTEST_NAME"].astype("string")

    df["ACTION"] = ACTION_LABELS["labs"]

    # Keep source metadata columns when present.
    priority_cols = ["PATIENT_ID", "START_DATE", "LR_SUBTEST_NAME", "LR_RESULT_VALUE", "ACTION"]
    ordered = [col for col in priority_cols if col in df.columns]
    remaining = [col for col in df.columns if col not in ordered]
    return df[ordered + remaining]
