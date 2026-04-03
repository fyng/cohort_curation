"""Shared helper functions for parser components."""

from __future__ import annotations

import re
from pathlib import Path


def slugify(text: str) -> str:
    """Create a filesystem-safe slug from text."""
    lowered = text.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered)
    return lowered.strip("-") or "untitled"


def estimate_tokens(text: str) -> int:
    """Estimate token count using a conservative words-to-tokens conversion."""
    words = len(text.split())
    return max(1, int(words * 1.3))


def markdown_escape(cell: str) -> str:
    """Escape markdown table delimiter characters."""
    return cell.replace("|", "\\|").replace("\n", " ").strip()


def relative_path(path: Path, start: Path) -> str:
    """Return a stable POSIX relative path string."""
    return path.relative_to(start).as_posix()
