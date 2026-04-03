"""Configuration models and defaults for PDF parsing."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StripRuleConfig:
    """Rules for removing page header/footer noise and identity text."""

    top_band_ratio: float = 0.14
    bottom_band_ratio: float = 0.12
    header_phrases: tuple[str, ...] = (
        "PLEASE NOTE",
        "NCCN Guidelines Version",
        "NCCN Guidelines Index",
        "Table of Contents",
        "Discussion",
        "Printed by",
        "Downloaded",
        "MAY NOT distribute this Content",
    )
    footer_phrases: tuple[str, ...] = (
        "National Comprehensive Cancer Network",
        "All rights reserved",
        "NCCN Guidelines",
        "Version",
        "MS-",
        "NCCN Content",
    )
    always_strip_phrases: tuple[str, ...] = (
        "MAY NOT distribute this Content",
        "National Comprehensive Cancer Network",
        "All rights reserved",
        "not be reproduced in any form",
        "express written permission of NCCN",
        "Any clinician seeking to apply or consult the NCCN Guidelines",
        "disclaims any responsibility",
        "makes no representations",
    )


@dataclass(frozen=True)
class ChunkingConfig:
    """Chunk sizing controls for LLM-friendly markdown blocks."""

    target_tokens: int = 1500
    min_tokens: int = 900
    max_tokens: int = 1850


@dataclass(frozen=True)
class ParserConfig:
    """Global parser configuration."""

    raw_root: Path = Path("guidelines/raw")
    parsed_root: Path = Path("guidelines/parsed")
    strict_validation: bool = True
    strip_rules: StripRuleConfig = field(default_factory=StripRuleConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)


FORBIDDEN_OUTPUT_PATTERNS: tuple[str, ...] = (
    "PLEASE NOTE that use of this NCCN Content is governed by the End-User License Agreement",
    "MAY NOT distribute this Content",
    "NCCN Guidelines Version",
    "National Comprehensive Cancer Network",
    "All rights reserved",
    "Printed by",
)
