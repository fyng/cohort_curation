"""Shared I/O helpers for loading cohort data files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast

import pandas as pd

from .constants import DATA_ROOT_ENV_VAR, DEFAULT_DATA_ROOT_CANDIDATES


def resolve_data_root(data_root: str | Path | None = None) -> Path:
    """Resolve the data root directory for all loaders.

    Resolution order:
    1. Explicit data_root argument.
    2. COHORT_CURATION_DATA_ROOT environment variable.
    3. Existing default candidates in the current working directory.
    """
    if data_root is not None:
        resolved = Path(data_root).expanduser().resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"Data root does not exist: {resolved}")
        return resolved

    env_value = os.environ.get(DATA_ROOT_ENV_VAR)
    if env_value:
        resolved = Path(env_value).expanduser().resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"{DATA_ROOT_ENV_VAR} points to missing path: {resolved}")
        return resolved

    for candidate in DEFAULT_DATA_ROOT_CANDIDATES:
        resolved = candidate.resolve()
        if resolved.exists():
            return resolved

    tried = ", ".join(str(path) for path in DEFAULT_DATA_ROOT_CANDIDATES)
    raise FileNotFoundError(
        "Could not resolve a data root. Provide data_root explicitly, set "
        f"{DATA_ROOT_ENV_VAR}, or create one of: {tried}"
    )


def get_data_file_path(file_name: str, data_root: str | Path | None = None) -> Path:
    """Build an absolute path for a file in the resolved data root."""
    root = resolve_data_root(data_root)
    path = root / file_name
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    return path


def read_tsv(
    file_name: str,
    data_root: str | Path | None = None,
    *,
    comment: str | None = "#",
    dtype: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Read a tab-delimited file from the data root."""
    path = get_data_file_path(file_name, data_root)
    dtype_arg = cast(Any, dtype)
    return pd.read_csv(path, sep="\t", comment=comment, dtype=dtype_arg)


def read_parquet(file_name: str, data_root: str | Path | None = None) -> pd.DataFrame:
    """Read a parquet file from the data root."""
    path = get_data_file_path(file_name, data_root)
    return pd.read_parquet(path)
