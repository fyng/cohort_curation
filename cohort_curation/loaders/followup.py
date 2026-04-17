"""Follow-up timeline data loaders."""

from __future__ import annotations

import pandas as pd

from ..reference_data import ACTION_LABELS, FILE_NAMES
from ..io import read_tsv


def load_followup_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw follow-up timeline table."""
    return read_tsv(FILE_NAMES["follow_up"], data_root=data_root)


def load_followup_first_consult(data_root: str | None = None) -> pd.DataFrame:
    """Return first-consult follow-up events with standardized ACTION label."""
    df = load_followup_raw(data_root=data_root).copy()

    if "SOURCE" in df.columns:
        df = df[df["SOURCE"] == "First Consult"].copy()

    drop_cols = [col for col in ["EVENT_TYPE", "SUBTYPE", "SOURCE"] if col in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    df["ACTION"] = ACTION_LABELS["followup_first_consult"]
    return df
