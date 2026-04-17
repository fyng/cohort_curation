#!/usr/bin/env python3
"""Template for cohort analysis scripts.

Copy this file into a cohort analysis folder and replace TODO sections with
cohort-specific inclusion and exclusion logic from cohort.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

from cohort_curation.loaders import diagnosis, genomics, patient, procedures


def normalize_text(series: pd.Series) -> pd.Series:
    """Normalize string values for stable matching."""
    return series.astype("string").str.strip().str.lower()


def require_columns(df: pd.DataFrame, required: list[str], table_name: str) -> None:
    """Raise a clear error when required columns are missing."""
    missing = [col for col in required if col not in df.columns]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Missing required columns in {table_name}: {joined}")


def write_patient_ids(patient_ids: Iterable[str], output_file: Path) -> None:
    """Write one PATIENT_ID per line in sorted order."""
    ordered = sorted({pid for pid in patient_ids if pid})
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(ordered) + ("\n" if ordered else ""), encoding="utf-8")


def build_cohort(data_root: str, output_file: Path) -> pd.Series:
    """Build and persist the cohort patient list."""
    df_patient = patient.load_patient_harmonized(data_root=data_root)
    df_diagnosis = diagnosis.load_diagnosis_harmonized(data_root=data_root)
    df_treatment = procedures.load_treatment_harmonized(data_root=data_root)
    df_sample = genomics.load_sample_harmonized(data_root=data_root)

    require_columns(df_patient, ["PATIENT_ID"], "patient")
    require_columns(df_diagnosis, ["PATIENT_ID"], "diagnosis")
    require_columns(df_treatment, ["PATIENT_ID"], "treatment")
    require_columns(df_sample, ["PATIENT_ID", "SAMPLE_ID"], "sample")

    all_patients = set(df_patient["PATIENT_ID"].dropna().astype(str))

    # TODO: Replace placeholders with cohort-specific filters from cohort.md.
    diagnosis_patients = all_patients.copy()
    treatment_patients = all_patients.copy()
    sample_patients = all_patients.copy()
    exclusion_patients: set[str] = set()

    final_patients = sorted(
        all_patients
        .intersection(diagnosis_patients)
        .intersection(treatment_patients)
        .intersection(sample_patients)
        .difference(exclusion_patients)
    )

    write_patient_ids(final_patients, output_file)

    print(f"Total patient rows: {len(df_patient):,}")
    print(f"Diagnosis-eligible patients: {len(diagnosis_patients):,}")
    print(f"Treatment-eligible patients: {len(treatment_patients):,}")
    print(f"Sample-eligible patients: {len(sample_patients):,}")
    print(f"Excluded patients: {len(exclusion_patients):,}")
    print(f"Final cohort size: {len(final_patients):,}")
    print(f"Wrote output to: {output_file}")

    return pd.Series(final_patients, name="PATIENT_ID", dtype="string")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a cohort patient list from curated criteria.")
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
