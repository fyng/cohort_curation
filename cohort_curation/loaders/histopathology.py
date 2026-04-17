"""Histopathology timeline data loaders."""

from __future__ import annotations

import pandas as pd

from ..reference_data import ACTION_LABELS, FILE_NAMES
from ..io import read_tsv


def _load_histopath_component(file_key: str, data_root: str | None = None) -> pd.DataFrame:
    df = read_tsv(FILE_NAMES[file_key], data_root=data_root)
    drop_cols = [col for col in ["STOP_DATE", "EVENT_TYPE", "SUBTYPE", "SOURCE"] if col in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols)
    return df


def load_mmr_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw MMR timeline data."""
    return _load_histopath_component("mmr", data_root=data_root)


def load_pdl1_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw PDL1 timeline data."""
    return _load_histopath_component("pdl1", data_root=data_root)


def load_gleason_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw Gleason timeline data."""
    return _load_histopath_component("gleason", data_root=data_root)


def load_histopathology_harmonized(data_root: str | None = None) -> pd.DataFrame:
    """Outer-merge MMR, PDL1, and Gleason timeline events with ACTION label."""
    df_mmr = load_mmr_raw(data_root=data_root)
    df_pdl1 = load_pdl1_raw(data_root=data_root)
    df_gleason = load_gleason_raw(data_root=data_root)

    key_cols = ["PATIENT_ID", "START_DATE"]
    merged = df_mmr.merge(df_pdl1, on=key_cols, how="outer").merge(df_gleason, on=key_cols, how="outer")
    merged["ACTION"] = ACTION_LABELS["histopath"]
    return merged
