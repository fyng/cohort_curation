#!/usr/bin/env python3
"""Build PD1/PDL1 + pre-treatment IMPACT + early progression cohort.

Writes one PATIENT_ID per line to the output text file.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cohort_curation.loaders import genomics, imaging, patient, procedures


TARGET_AGENTS = {
    "atezolizumab",
    "avelumab",
    "cemiplimab",
    "durvalumab",
    "dostarlimab",
    "nivolumab",
    "pembrolizumab",
    "retifanlimab",
    "toripalimab",
}


def normalize_text(series: pd.Series) -> pd.Series:
    """Normalize string values for exact matching."""
    return series.astype("string").str.strip().str.lower()


def resolve_age_column(df_patient: pd.DataFrame) -> str:
    """Select a supported age column for the adult criterion."""
    for col in ["CURRENT_AGE_DEID", "CURRENT_AGE", "AGE"]:
        if col in df_patient.columns:
            return col
    raise ValueError("No supported age column found. Expected one of CURRENT_AGE_DEID, CURRENT_AGE, AGE.")


def build_cohort(data_root: str, output_file: Path) -> pd.Series:
    # Load required domain tables.
    df_patient = patient.load_patient_harmonized(data_root=data_root)
    df_treatment = procedures.load_treatment_harmonized(data_root=data_root)
    df_sample_h = genomics.load_sample_harmonized(data_root=data_root)
    df_sample_raw = genomics.load_sample_raw(data_root=data_root)
    df_progression = imaging.load_progression_harmonized(data_root=data_root)

    # Inclusion criterion: Age >= 18 years.
    age_col = resolve_age_column(df_patient)
    df_patient[age_col] = pd.to_numeric(df_patient[age_col], errors="coerce")
    adult_patients = set(df_patient.loc[df_patient[age_col] >= 18, "PATIENT_ID"].dropna().astype(str))

    # Inclusion criterion: PD1/PDL1 treatment exposure from the confirmed broad agent list.
    treatment = df_treatment.copy()
    if "AGENT" not in treatment.columns:
        treatment["AGENT"] = pd.Series(index=treatment.index, dtype="string")
    if "START_DATE" not in treatment.columns:
        treatment["START_DATE"] = pd.Series(index=treatment.index, dtype="float64")
    treatment["AGENT_NORM"] = normalize_text(treatment["AGENT"])
    treatment["START_DATE"] = pd.to_numeric(treatment["START_DATE"], errors="coerce")

    qualifying_treatments = treatment[treatment["AGENT_NORM"].isin(TARGET_AGENTS)].copy()
    earliest_treatment = (
        qualifying_treatments.dropna(subset=["PATIENT_ID", "START_DATE"])
        .groupby("PATIENT_ID", as_index=False)
        .agg(INDEX_DATE=("START_DATE", "min"))
    )

    treatment_eligible_patients = set(earliest_treatment["PATIENT_ID"].dropna().astype(str))

    # Inclusion criterion: IMPACT panel sample in baseline window [-365, 0) before index.
    sample_raw_cols = [col for col in ["SAMPLE_ID", "GENE_PANEL"] if col in df_sample_raw.columns]
    df_sample = df_sample_h.merge(df_sample_raw[sample_raw_cols], on="SAMPLE_ID", how="left")

    if "GENE_PANEL" not in df_sample.columns:
        df_sample["GENE_PANEL"] = pd.Series(index=df_sample.index, dtype="string")
    if "START_DATE" not in df_sample.columns:
        df_sample["START_DATE"] = pd.Series(index=df_sample.index, dtype="float64")

    df_sample["GENE_PANEL"] = df_sample["GENE_PANEL"].astype("string")
    df_sample["START_DATE"] = pd.to_numeric(df_sample["START_DATE"], errors="coerce")

    impact_samples = df_sample[
        df_sample["GENE_PANEL"].str.upper().str.startswith("IMPACT", na=False)
    ].dropna(subset=["PATIENT_ID", "START_DATE"])

    sample_vs_index = earliest_treatment.merge(
        impact_samples[["PATIENT_ID", "SAMPLE_ID", "START_DATE", "GENE_PANEL"]],
        on="PATIENT_ID",
        how="inner",
    ).rename(columns={"START_DATE": "SAMPLE_DATE"})

    sample_in_window = (
        (sample_vs_index["SAMPLE_DATE"] >= (sample_vs_index["INDEX_DATE"] - 365))
        & (sample_vs_index["SAMPLE_DATE"] < sample_vs_index["INDEX_DATE"])
    )

    qualifying_samples = sample_vs_index[sample_in_window].copy()
    sample_eligible_patients = set(qualifying_samples["PATIENT_ID"].dropna().astype(str).unique().tolist())

    # Inclusion criterion: progression in post-index window [0, 90], with PROGRESSION == Yes only.
    progression = df_progression.copy()
    if "PROGRESSION" not in progression.columns:
        progression["PROGRESSION"] = pd.Series(index=progression.index, dtype="string")
    if "START_DATE" not in progression.columns:
        progression["START_DATE"] = pd.Series(index=progression.index, dtype="float64")

    progression["PROGRESSION_NORM"] = normalize_text(progression["PROGRESSION"])
    progression["START_DATE"] = pd.to_numeric(progression["START_DATE"], errors="coerce")

    progression_yes = progression[
        progression["PROGRESSION_NORM"] == "yes"
    ].dropna(subset=["PATIENT_ID", "START_DATE"])

    progression_vs_index = earliest_treatment.merge(
        progression_yes[["PATIENT_ID", "START_DATE"]],
        on="PATIENT_ID",
        how="inner",
    ).rename(columns={"START_DATE": "PROGRESSION_DATE"})

    progression_delta = progression_vs_index["PROGRESSION_DATE"] - progression_vs_index["INDEX_DATE"]
    progression_in_window = (progression_delta >= 0) & (progression_delta <= 90)

    qualifying_progressions = progression_vs_index[progression_in_window].copy()
    progression_eligible_patients = set(
        qualifying_progressions["PATIENT_ID"].dropna().astype(str).unique().tolist()
    )

    # Final cohort intersection of all required inclusion criteria.
    final_patients = sorted(
        adult_patients
        .intersection(treatment_eligible_patients)
        .intersection(sample_eligible_patients)
        .intersection(progression_eligible_patients)
    )
    final_series = pd.Series(final_patients, name="PATIENT_ID", dtype="string")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(final_patients) + ("\n" if final_patients else ""), encoding="utf-8")

    print(f"Total patient rows: {len(df_patient):,}")
    print(f"Adults (age >= 18): {len(adult_patients):,}")
    print(f"PD1/PDL1 treatment-eligible patients: {len(treatment_eligible_patients):,}")
    print(f"Baseline IMPACT sample-eligible patients: {len(sample_eligible_patients):,}")
    print(f"Post-index progression-eligible patients: {len(progression_eligible_patients):,}")
    print(f"Final cohort size: {len(final_patients):,}")
    print(f"Wrote output to: {output_file}")

    return final_series


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build cohort: PD1/PDL1-treated adults with pre-treatment IMPACT and early progression."
    )
    default_output = (
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
        default=str(default_output),
        help="Output txt path (default: final_cohort_patient_ids.txt next to this script)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_cohort(data_root=args.data_root, output_file=Path(args.output))


if __name__ == "__main__":
    main()
