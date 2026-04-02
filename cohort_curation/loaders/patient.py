"""Patient domain data loaders."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from ..constants import FILE_NAMES, PATIENT_OS_STATUS_MAP, PATIENT_PRIOR_MED_MAP, PATIENT_SMOKING_MAP
from ..io import read_tsv


PATIENT_DTYPES: dict[str, Any] = {"OTHER_PATIENT_ID": str}


def load_patient_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw patient-level clinical data."""
    return read_tsv(FILE_NAMES["patient"], data_root=data_root, dtype=PATIENT_DTYPES)


def load_ancestry_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load ancestry supplement table."""
    return read_tsv(FILE_NAMES["ancestry"], data_root=data_root)


def load_followup_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load follow-up timeline table."""
    return read_tsv(FILE_NAMES["follow_up"], data_root=data_root)


def _build_followup_last_status(df_followup: pd.DataFrame) -> pd.DataFrame:
    if not {"PATIENT_ID", "START_DATE", "SOURCE"}.issubset(df_followup.columns):
        return pd.DataFrame(columns=["PATIENT_ID", "FU_DATE", "FU_STATUS"])

    followup_small = df_followup[["PATIENT_ID", "START_DATE", "SOURCE"]].copy()
    max_dates = followup_small.groupby("PATIENT_ID")["START_DATE"].max().reset_index(name="FU_DATE")
    merged = followup_small.merge(max_dates, on="PATIENT_ID", how="inner")
    merged = merged[merged["START_DATE"] == merged["FU_DATE"]]

    result = (
        merged.groupby(["PATIENT_ID", "FU_DATE"])["SOURCE"]
        .apply(lambda values: "Deceased" if (values == "Patient Deceased").any() else "Living")
        .reset_index(name="FU_STATUS")
    )
    return result


def load_patient_harmonized(data_root: str | None = None) -> pd.DataFrame:
    """Load patient data with notebook-consistent label harmonization.

    This function performs import-time harmonization only, including:
    - categorical label maps for smoking/prior medications/OS status
    - optional OS days derivation from OS months
    - ancestry label merge
    - follow-up last-contact merge for missing OS fields
    """
    df = load_patient_raw(data_root=data_root).copy()

    if "PRIOR_MED_TO_MSK" in df.columns:
        df["PRIOR_MED_TO_MSK"] = df["PRIOR_MED_TO_MSK"].map(PATIENT_PRIOR_MED_MAP)

    smoking_col = "SMOKING_PREDICTIONS_3_CLASSES"
    if smoking_col in df.columns:
        df[smoking_col] = df[smoking_col].map(PATIENT_SMOKING_MAP)
        df = df.rename(columns={smoking_col: "SMOKING_PRED"})

    if "OS_STATUS" in df.columns:
        df["OS_STATUS"] = df["OS_STATUS"].map(PATIENT_OS_STATUS_MAP)

    if "OS_MONTHS" in df.columns:
        df["OS_DAYS"] = np.round(30.42 * pd.to_numeric(df["OS_MONTHS"], errors="coerce"))
        df = df.drop(columns=["OS_MONTHS"])

    if {"OS_DAYS", "OS_STATUS"}.issubset(df.columns):
        deceased_zero_mask = (df["OS_DAYS"] == 0.0) & (df["OS_STATUS"] == "Deceased")
        df.loc[deceased_zero_mask, "OS_DAYS"] = np.nan

    ancestry = load_ancestry_raw(data_root=data_root)
    ancestry_cols = [col for col in ["PATIENT_ID", "ANCESTRY_LABEL"] if col in ancestry.columns]
    if ancestry_cols == ["PATIENT_ID", "ANCESTRY_LABEL"]:
        df = df.merge(ancestry[ancestry_cols], on="PATIENT_ID", how="left")

    followup = load_followup_raw(data_root=data_root)
    df_followup_last = _build_followup_last_status(followup)
    if not df_followup_last.empty and "PATIENT_ID" in df.columns:
        df = df.merge(df_followup_last, on="PATIENT_ID", how="left")

    if {"OS_DAYS", "FU_DATE"}.issubset(df.columns):
        missing_os = df["OS_DAYS"].isna()
        df.loc[missing_os, "OS_DAYS"] = df.loc[missing_os, "FU_DATE"]

    if {"OS_STATUS", "FU_STATUS"}.issubset(df.columns):
        missing_status = df["OS_STATUS"].isna()
        df.loc[missing_status, "OS_STATUS"] = df.loc[missing_status, "FU_STATUS"]

    drop_cols = [col for col in ["FU_DATE", "FU_STATUS"] if col in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    return df
