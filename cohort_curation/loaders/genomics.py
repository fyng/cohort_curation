"""Sample and genomics data loaders."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..reference_data import ACTION_LABELS, FILE_NAMES
from ..io import read_tsv


SAMPLE_DTYPES: dict[str, Any] = {
    "PDL1_POSITIVE": str,
    "TUMOR_PURITY": str,
    "MSI_COMMENT": str,
    "MSI_TYPE": str,
}

MUTATION_DTYPES: dict[str, Any] = {
    "Exon_Number": str,
    "COMMENTS": str,
    "PATH_SCORE": str,
    "ALLELE_NUM": str,
    "IS_NEW": str,
}


def _normalize_text_series(series: pd.Series) -> pd.Series:
    return series.where(series.isna(), series.astype(str).str.replace(r"[\s/]+", "-", regex=True))


def _parse_week_added(week_series: pd.Series) -> pd.Series:
    # Notebook format: YYYY, Wk. %U
    return pd.to_datetime(week_series.astype(str) + "-0", format="%Y, Wk. %U-%w", errors="coerce")


def load_sample_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw sample-level clinical table."""
    return read_tsv(FILE_NAMES["sample"], data_root=data_root, dtype=SAMPLE_DTYPES)


def load_specimen_surgery_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load specimen surgery timeline table."""
    return read_tsv(FILE_NAMES["specimen_surgery"], data_root=data_root, comment=None)


def load_sample_harmonized(data_root: str | None = None) -> pd.DataFrame:
    """Load sample table with schema and label harmonization only."""
    df = load_sample_raw(data_root=data_root).copy()

    keep_cols = [
        "SAMPLE_ID",
        "PATIENT_ID",
        "WEEK_ADDED",
        "CANCER_TYPE",
        "SAMPLE_TYPE",
        "CANCER_TYPE_DETAILED",
        "PRIMARY_SITE",
        "METASTATIC_SITE",
        "ONCOTREE_CODE",
        "MSI_TYPE",
        "CVR_TMB_COHORT_PERCENTILE",
        "TUMOR_PURITY",
    ]
    keep_cols = [col for col in keep_cols if col in df.columns]
    df = df[keep_cols].copy()

    if "WEEK_ADDED" in df.columns:
        df["WEEK_ADDED"] = _parse_week_added(df["WEEK_ADDED"])

    if "MSI_TYPE" in df.columns:
        df["MSI_TYPE"] = df["MSI_TYPE"].replace({"Do Not Report": "Unknown", "Do not report": "Unknown"})

    if "CVR_TMB_COHORT_PERCENTILE" in df.columns:
        numeric = pd.to_numeric(df["CVR_TMB_COHORT_PERCENTILE"], errors="coerce")
        df["CVR_TMB_COHORT_DECILE"] = (numeric // 10).astype("Int64")
        df = df.drop(columns=["CVR_TMB_COHORT_PERCENTILE"])

    normalize_cols = [
        "CANCER_TYPE",
        "SAMPLE_TYPE",
        "CANCER_TYPE_DETAILED",
        "PRIMARY_SITE",
        "METASTATIC_SITE",
        "ONCOTREE_CODE",
        "MSI_TYPE",
        "TUMOR_PURITY",
    ]
    for col in normalize_cols:
        if col in df.columns:
            df[col] = _normalize_text_series(df[col])

    specimen = load_specimen_surgery_raw(data_root=data_root)
    if {"SAMPLE_ID", "START_DATE"}.issubset(specimen.columns):
        df = df.merge(specimen[["SAMPLE_ID", "START_DATE"]], on="SAMPLE_ID", how="left")

    df["ACTION"] = ACTION_LABELS["sample"]
    return df


def load_mutations_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw mutation table and normalize sample identifier column name."""
    df = read_tsv(FILE_NAMES["mutations"], data_root=data_root, dtype=MUTATION_DTYPES)
    if "Tumor_Sample_Barcode" in df.columns:
        df = df.rename(columns={"Tumor_Sample_Barcode": "SAMPLE_ID"})
    return df


def load_cna_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw long-format copy number table with label harmonization."""
    df = read_tsv(FILE_NAMES["cna_long"], data_root=data_root, comment=None)

    if "Alteration" in df.columns:
        df["ALTERATION_LABEL"] = df["Alteration"].map({-2.0: "Del", -1.5: "Del", 0.0: "Diploid", 2.0: "Amp"})

    return df


def load_sv_raw(data_root: str | None = None) -> pd.DataFrame:
    """Load raw structural variant table."""
    return read_tsv(FILE_NAMES["sv"], data_root=data_root)


def _build_sv_gene_events(df_sv: pd.DataFrame) -> pd.DataFrame:
    """Project structural-variant gene columns into a SAMPLE_ID x gene event table."""
    parts: list[pd.DataFrame] = []
    for gene_col in ["Site1_Hugo_Symbol", "Site2_Hugo_Symbol"]:
        if {"SAMPLE_ID", gene_col}.issubset(df_sv.columns):
            part = (
                df_sv[["SAMPLE_ID", gene_col]]
                .rename(columns={gene_col: "Hugo_Symbol"})
                .dropna(subset=["SAMPLE_ID", "Hugo_Symbol"])
            )
            parts.append(part)

    if not parts:
        return pd.DataFrame(columns=["SAMPLE_ID", "Hugo_Symbol", "SV_EVENT_COUNT"])

    sv_long = pd.concat(parts, ignore_index=True)
    return sv_long.groupby(["SAMPLE_ID", "Hugo_Symbol"]).size().reset_index(name="SV_EVENT_COUNT")


def load_genomics_event_table(data_root: str | None = None) -> pd.DataFrame:
    """Build a minimally harmonized genomics event table.

    This combines mutation, CNA, and structural-variant data by sample and gene without QC thresholds.
    """
    sample = load_sample_harmonized(data_root=data_root)
    mut = load_mutations_raw(data_root=data_root)
    cna = load_cna_raw(data_root=data_root)
    sv = load_sv_raw(data_root=data_root)

    mut_cols = [col for col in ["SAMPLE_ID", "Hugo_Symbol", "Variant_Classification"] if col in mut.columns]
    cna_cols = [col for col in ["SAMPLE_ID", "Hugo_Symbol", "Alteration", "ALTERATION_LABEL"] if col in cna.columns]

    mut_small = mut[mut_cols].copy() if mut_cols else pd.DataFrame(columns=["SAMPLE_ID", "Hugo_Symbol"])
    if {"SAMPLE_ID", "Hugo_Symbol", "Variant_Classification"}.issubset(mut_small.columns):
        mut_small = mut_small.groupby(["SAMPLE_ID", "Hugo_Symbol"]).size().reset_index(name="MUTATION_COUNT")

    cna_small = cna[cna_cols].copy() if cna_cols else pd.DataFrame(columns=["SAMPLE_ID", "Hugo_Symbol"])
    sv_small = _build_sv_gene_events(sv)

    merged = mut_small.merge(cna_small, on=["SAMPLE_ID", "Hugo_Symbol"], how="outer")
    merged = merged.merge(sv_small, on=["SAMPLE_ID", "Hugo_Symbol"], how="outer")

    sample_cols = [col for col in ["SAMPLE_ID", "PATIENT_ID", "START_DATE", "ACTION"] if col in sample.columns]
    merged = merged.merge(sample[sample_cols], on="SAMPLE_ID", how="left")

    if "Hugo_Symbol" in merged.columns:
        merged = merged.rename(columns={"Hugo_Symbol": "GENE_ALT"})

    return merged
