"""Diagnosis timeline data loaders."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from ..reference_data import ACTION_LABELS, FILE_NAMES
from ..io import read_tsv


DIAGNOSIS_COLUMNS = [
    "PATIENT_ID",
    "START_DATE",
    "ACTION",
    "CLINICAL_GROUP",
    "STAGE_CDM_DERIVED_GRANULAR",
    "STAGE",
    "CANCER_TYPE",
    "CANCER_TYPE_DETAILED",
    "CANCER_SITE",
    "CANCER_SITE_DETAILED",
    "MORPH_CODE",
    "TOPOLOGY_CODE",
]


def load_diagnosis_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw diagnosis timeline data."""
    return read_tsv(FILE_NAMES["diagnosis"], data_root=data_root)


def parse_dx_description(text: Any) -> tuple[str, str, str, str, str, str]:
    """Parse diagnosis description into canonical fields.

    Expected format:
    "Cancer type, details | Cancer site, details (MORPH_CODE|TOPOLOGY_CODE)"
    """
    if not isinstance(text, str) or not text.strip():
        return "", "", "", "", "", ""

    cancer_type = ""
    cancer_type_detailed = ""
    cancer_site = ""
    cancer_site_detailed = ""
    morph_code = ""
    top_code = ""

    tokens = text.split("|", 1)
    if len(tokens) != 2:
        return cancer_type, cancer_type_detailed, cancer_site, cancer_site_detailed, morph_code, top_code

    left = tokens[0].strip()
    right = tokens[1].strip()

    left_tokens = left.split(",", 1)
    cancer_type = left_tokens[0].strip()
    if len(left_tokens) == 2:
        cancer_type_detailed = left_tokens[1].strip()

    match = re.search(r"(.*)\s*\(([^()]*)\)\s*$", right)
    if match:
        site_text = match.group(1).strip()
        codes_text = match.group(2).strip()
        codes = codes_text.split("|", 1)
        morph_code = codes[0].strip() if len(codes) > 0 else ""
        top_code = codes[1].strip() if len(codes) > 1 else ""
    else:
        site_text = right

    if "," in site_text:
        site_tokens = site_text.split(",", 1)
        cancer_site = site_tokens[0].strip()
        cancer_site_detailed = site_tokens[1].strip()
    else:
        cancer_site = site_text.strip()

    return cancer_type, cancer_type_detailed, cancer_site, cancer_site_detailed, morph_code, top_code


def load_diagnosis_harmonized(data_root: str | None = None) -> pd.DataFrame:
    """Load diagnosis data with parsed labels and standardized schema."""
    df = load_diagnosis_raw(data_root=data_root).copy()

    if "DX_DESCRIPTION" in df.columns:
        parsed = df["DX_DESCRIPTION"].apply(parse_dx_description)
        (
            df["CANCER_TYPE"],
            df["CANCER_TYPE_DETAILED"],
            df["CANCER_SITE"],
            df["CANCER_SITE_DETAILED"],
            df["MORPH_CODE"],
            df["TOPOLOGY_CODE"],
        ) = zip(*parsed)

    if "STAGE_CDM_DERIVED_GRANULAR" in df.columns:
        df["STAGE"] = df["STAGE_CDM_DERIVED_GRANULAR"]

    df["ACTION"] = ACTION_LABELS["diagnosis"]

    output_cols = [col for col in DIAGNOSIS_COLUMNS if col in df.columns]
    return df[output_cols].copy()
