"""Imaging-derived timeline data loaders."""

from __future__ import annotations

import pandas as pd

from ..reference_data import ACTION_LABELS, FILE_NAMES
from ..io import read_tsv


def load_tumor_sites_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw tumor site timeline table."""
    return read_tsv(FILE_NAMES["tumor_sites"], data_root=data_root, comment=None)


def load_tumor_sites_harmonized(data_root: str | None = None) -> pd.DataFrame:
    """Load tumor sites with standardized schema and action label."""
    df = load_tumor_sites_raw(data_root=data_root).copy()
    keep_cols = [
        "PATIENT_ID",
        "START_DATE",
        "SOURCE_SPECIFIC",
        "TUMOR_SITE",
    ]
    keep_cols = [col for col in keep_cols if col in df.columns]
    df = df[keep_cols].drop_duplicates()
    df["ACTION"] = ACTION_LABELS["tumor_sites"]
    return df


def load_cancer_presence_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw cancer-presence timeline table."""
    return read_tsv(FILE_NAMES["cancer_presence"], data_root=data_root, comment=None)


def load_progression_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw progression timeline table."""
    return read_tsv(FILE_NAMES["progression"], data_root=data_root, comment=None)


def load_progression_harmonized(data_root: str | None = None) -> pd.DataFrame:
    """Load progression events with standardized labels and action type."""
    df = load_progression_raw(data_root=data_root).copy()

    keep_cols = [
        "PATIENT_ID",
        "START_DATE",
        "SOURCE_SPECIFIC",
        "PROGRESSION",
        "PROGRESSION_PROBABILITY",
    ]
    keep_cols = [col for col in keep_cols if col in df.columns]
    df = df[keep_cols].drop_duplicates()

    if "PROGRESSION" in df.columns:
        df["PROGRESSION_LABEL"] = df["PROGRESSION"].replace({"Yes": "Progression event", "No": "No progression event"})

    df["ACTION"] = ACTION_LABELS["progression"]
    return df
