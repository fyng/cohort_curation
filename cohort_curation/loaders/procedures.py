"""Treatment, surgery, and radiation timeline loaders."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..constants import ACTION_LABELS, FILE_NAMES
from ..io import read_tsv, resolve_data_root


def load_treatment_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw treatment timeline table."""
    return read_tsv(FILE_NAMES["treatment"], data_root=data_root)


def load_treatment_harmonized(data_root: str | None = None) -> pd.DataFrame:
    """Load treatment table with standardized labels and action column."""
    df = load_treatment_raw(data_root=data_root).copy()

    if "SUBTYPE" in df.columns:
        df = df.rename(columns={"SUBTYPE": "TREATMENT"})

    if {"START_DATE", "STOP_DATE"}.issubset(df.columns):
        start = pd.to_numeric(df["START_DATE"], errors="coerce")
        stop = pd.to_numeric(df["STOP_DATE"], errors="coerce")
        df["STOP_DATE"] = stop.fillna(start + 1)

    df["ACTION"] = ACTION_LABELS["treatment"]
    return df


def load_surgery_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw surgery timeline table."""
    return read_tsv(FILE_NAMES["surgery"], data_root=data_root, comment=None)


def load_surgery_harmonized(
    data_root: str | None = None,
    map_file: str | None = "procedure_map/surg_purpose_map.csv",
) -> pd.DataFrame:
    """Load surgery data with optional mapping-table join and standardized labels."""
    df = load_surgery_raw(data_root=data_root).copy()

    if "PROCEDURE_DESCRIPTION" in df.columns:
        df["PROCEDURE_DESCRIPTION"] = df["PROCEDURE_DESCRIPTION"].astype(str).str.strip()

    if {"START_DATE", "STOP_DATE"}.issubset(df.columns):
        start = pd.to_numeric(df["START_DATE"], errors="coerce")
        stop = pd.to_numeric(df["STOP_DATE"], errors="coerce")
        df["STOP_DATE"] = stop.fillna(start + 1)

    if map_file:
        root = resolve_data_root(data_root)
        map_path = root / map_file
        if map_path.exists():
            df_map = pd.read_csv(map_path)
            if {"DATA", "REFINEMENT_RESULT"}.issubset(df_map.columns) and "PROCEDURE_DESCRIPTION" in df.columns:
                df = df.merge(
                    df_map[["DATA", "REFINEMENT_RESULT"]],
                    left_on="PROCEDURE_DESCRIPTION",
                    right_on="DATA",
                    how="left",
                )
                df = df.rename(columns={"REFINEMENT_RESULT": "SURGERY_CATEGORY"})
                df = df.drop(columns=[col for col in ["DATA"] if col in df.columns])

    df["AGENT"] = "Surgery"
    df["ACTION"] = ACTION_LABELS["treatment"]
    return df


def load_radiation_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw radiation timeline table."""
    return read_tsv(FILE_NAMES["radiation"], data_root=data_root, comment=None)


def load_radiation_harmonized(
    data_root: str | None = None,
    map_file: str | None = "procedure_map/radonc_site_map.csv",
) -> pd.DataFrame:
    """Load radiation table with optional plan mapping and standardized labels."""
    df = load_radiation_raw(data_root=data_root).copy()

    if "PLAN" in df.columns:
        df["PLAN"] = df["PLAN"].astype(str).str.strip()

    if {"START_DATE", "STOP_DATE"}.issubset(df.columns):
        start = pd.to_numeric(df["START_DATE"], errors="coerce")
        stop = pd.to_numeric(df["STOP_DATE"], errors="coerce")
        df["STOP_DATE"] = stop.fillna(start + 1)

    if map_file:
        root = resolve_data_root(data_root)
        map_path = root / map_file
        if map_path.exists():
            df_map = pd.read_csv(map_path)
            if {"RADIATION_PLAN", "REFINEMENT_RESULT"}.issubset(df_map.columns) and "PLAN" in df.columns:
                df = df.merge(
                    df_map[["RADIATION_PLAN", "REFINEMENT_RESULT"]],
                    left_on="PLAN",
                    right_on="RADIATION_PLAN",
                    how="left",
                )
                df = df.rename(columns={"REFINEMENT_RESULT": "RADIATION_CATEGORY"})
                df = df.drop(columns=[col for col in ["RADIATION_PLAN"] if col in df.columns])

    if "SUBTYPE" in df.columns:
        df = df.rename(columns={"SUBTYPE": "AGENT"})

    df["ACTION"] = ACTION_LABELS["treatment"]
    return df
