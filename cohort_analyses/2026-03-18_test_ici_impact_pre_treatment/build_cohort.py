#!/usr/bin/env python3
"""Build a test clinical cohort using explicit inclusion/exclusion criteria.

This script writes final PATIENT_ID values to a text file, one per line.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cohort_curation.loaders import genomics, patient, procedures


TARGET_AGENTS = {
    "pembrolizumab",
    "durvalumab",
    "cemiplimab",
    "atezolizumab",
    "avelumab",
}


def normalize_agent_name(series: pd.Series) -> pd.Series:
    """Normalize treatment agent text for robust exact matching."""
    return series.astype("string").str.strip().str.lower()


def resolve_age_column(df_patient: pd.DataFrame) -> str:
    """Select age column used for the adult criterion."""
    preferred = ["CURRENT_AGE_DEID", "CURRENT_AGE", "AGE"]
    for col in preferred:
        if col in df_patient.columns:
            return col
    raise ValueError("No supported age column found. Expected one of CURRENT_AGE_DEID, CURRENT_AGE, AGE.")


def build_cohort(data_root: str, output_file: Path) -> pd.Series:
    # Load required tables using cohort_curation loader functions.
    df_patient = patient.load_patient_harmonized(data_root)
    df_treatment = procedures.load_treatment_harmonized(data_root)
    df_sample_h = genomics.load_sample_harmonized(data_root)
    df_sample_raw = genomics.load_sample_raw(data_root)

    # Merge sample metadata so we have both START_DATE and GENE_PANEL.
    sample_cols = [col for col in ["SAMPLE_ID", "GENE_PANEL"] if col in df_sample_raw.columns]
    df_samples = df_sample_h.merge(df_sample_raw[sample_cols], on="SAMPLE_ID", how="left")

    # Inclusion 1: Age >= 18.
    age_col = resolve_age_column(df_patient)
    df_patient[age_col] = pd.to_numeric(df_patient[age_col], errors="coerce")
    adult_patients = set(df_patient.loc[df_patient[age_col] >= 18, "PATIENT_ID"].dropna().astype(str))

    # Inclusion 2: All sex and ethnicity.
    # No filter is applied for sex, ethnicity, or ancestry.

    # Inclusion 3: Treatment includes any target ICI agent.
    treatment = df_treatment.copy()
    if "AGENT" not in treatment.columns:
        treatment["AGENT"] = pd.Series(index=treatment.index, dtype="string")
    if "START_DATE" not in treatment.columns:
        treatment["START_DATE"] = pd.Series(index=treatment.index, dtype="float64")
    treatment["AGENT_NORM"] = normalize_agent_name(treatment.get("AGENT", pd.Series(dtype="string")))
    treatment["START_DATE"] = pd.to_numeric(treatment["START_DATE"], errors="coerce")

    qualifying_treatments = treatment[treatment["AGENT_NORM"].isin(TARGET_AGENTS)].copy()

    earliest_treatment = (
        qualifying_treatments.dropna(subset=["PATIENT_ID", "START_DATE"])
        .groupby("PATIENT_ID")["START_DATE"]
        .min()
        .reset_index(name="EARLIEST_TARGET_TREATMENT_START")
    )

    # Inclusion 4: At least one IMPACT sample before earliest target treatment,
    # and within 1 year (365 days) before treatment start.
    samples = df_samples.copy()
    if "GENE_PANEL" not in samples.columns:
        samples["GENE_PANEL"] = pd.Series(index=samples.index, dtype="string")
    if "START_DATE" not in samples.columns:
        samples["START_DATE"] = pd.Series(index=samples.index, dtype="float64")
    samples["GENE_PANEL"] = samples.get("GENE_PANEL", pd.Series(dtype="string")).astype("string")
    samples["START_DATE"] = pd.to_numeric(samples["START_DATE"], errors="coerce")

    impact_samples = samples[
        samples["GENE_PANEL"].str.upper().str.startswith("IMPACT", na=False)
    ].dropna(subset=["PATIENT_ID", "START_DATE"])

    merged = earliest_treatment.merge(
        impact_samples[["PATIENT_ID", "SAMPLE_ID", "START_DATE", "GENE_PANEL"]],
        on="PATIENT_ID",
        how="inner",
    )

    merged = merged.rename(columns={"START_DATE": "SAMPLE_START_DATE"})

    in_window = (
        (merged["SAMPLE_START_DATE"] >= (merged["EARLIEST_TARGET_TREATMENT_START"] - 365))
        & (merged["SAMPLE_START_DATE"] < merged["EARLIEST_TARGET_TREATMENT_START"])
    )
    qualifying_pre_treatment_samples = merged[in_window].copy()

    sample_eligible_patients = set(
        qualifying_pre_treatment_samples["PATIENT_ID"].dropna().astype(str).unique().tolist()
    )

    # Final cohort: adults + qualifying treatment + valid pre-treatment IMPACT sample.
    final_patients = sorted(adult_patients.intersection(sample_eligible_patients))
    final_series = pd.Series(final_patients, name="PATIENT_ID", dtype="string")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(final_patients) + ("\n" if final_patients else ""), encoding="utf-8")

    print(f"Total patients in patient table: {len(df_patient):,}")
    print(f"Adults (age >= 18): {len(adult_patients):,}")
    print(f"Patients with target treatment: {earliest_treatment['PATIENT_ID'].nunique():,}")
    print(f"Patients with qualifying pre-treatment IMPACT sample: {len(sample_eligible_patients):,}")
    print(f"Final cohort size: {len(final_patients):,}")
    print(f"Wrote PATIENT_ID list to: {output_file}")

    return final_series


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the test clinical cohort.")
    default_output = str(
        Path("cohort_analyses")
        / Path(__file__).resolve().parent.name
        / "final_cohort_patient_ids.txt"
    )
    parser.add_argument(
        "--data-root",
        default="data",
        help="Path to cohort data folder (default: data)",
    )
    parser.add_argument(
        "--output",
        default=default_output,
        help="Output txt filename (default: cohort file next to this script)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    build_cohort(data_root=args.data_root, output_file=output_path)


if __name__ == "__main__":
    main()
