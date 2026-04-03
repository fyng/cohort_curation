"""Validation checks for strict parsing quality and privacy stripping."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .config import ChunkingConfig
from .models import ChunkRecord, PageRecord, SectionRecord


def _scan_markdown_for_patterns(root: Path, patterns: tuple[str, ...]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    markdown_files = sorted(root.rglob("*.md"))

    for md_path in markdown_files:
        content = md_path.read_text(encoding="utf-8")
        for pattern in patterns:
            if pattern.casefold() in content.casefold():
                findings.append(
                    {
                        "file": md_path.as_posix(),
                        "pattern": pattern,
                    }
                )
    return findings


def _scan_markdown_for_identity(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    markdown_files = sorted(root.rglob("*.md"))
    identity_patterns = [
        re.compile(
            r"printed\s+by.*(?:\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{1,2}:\d{2}(?::\d{2})?\b)",
            re.IGNORECASE,
        ),
        re.compile(r"downloaded\s+by.*(?:\b\d{1,2}/\d{1,2}/\d{2,4}\b)", re.IGNORECASE),
    ]

    for md_path in markdown_files:
        content = md_path.read_text(encoding="utf-8")
        for regex in identity_patterns:
            for match in regex.finditer(content):
                findings.append(
                    {
                        "file": md_path.as_posix(),
                        "pattern": regex.pattern,
                        "match": match.group(0),
                    }
                )
    return findings


def validate_guideline_outputs(
    guideline_dir: Path,
    pages: list[PageRecord],
    sections: list[SectionRecord],
    chunks: list[ChunkRecord],
    forbidden_patterns: tuple[str, ...],
    chunking: ChunkingConfig,
) -> dict[str, Any]:
    """Validate sanitized and structured outputs, returning a detailed report."""
    forbidden_hits = _scan_markdown_for_patterns(guideline_dir, forbidden_patterns)
    identity_hits = _scan_markdown_for_identity(guideline_dir)

    leaf_sections = [section for section in sections if section.is_leaf]
    empty_leaf_sections = [section.section_id for section in leaf_sections if not section.text.strip()]
    oversized_chunks = [chunk.chunk_id for chunk in chunks if chunk.token_estimate > chunking.max_tokens]

    pages_without_removed_lines = [
        page.page_number for page in pages if page.page_number > 1 and not page.removed_lines
    ]
    eligible_pages = [page.page_number for page in pages if page.page_number > 1]
    stripped_ratio = 1.0
    if eligible_pages:
        stripped_ratio = 1.0 - (len(pages_without_removed_lines) / len(eligible_pages))

    checks = {
        "forbidden_pattern_hits": len(forbidden_hits) == 0,
        "identity_pattern_hits": len(identity_hits) == 0,
        "leaf_sections_non_empty": len(empty_leaf_sections) == 0,
        "chunk_size_max": len(oversized_chunks) == 0,
        "removed_lines_present": stripped_ratio >= 0.85,
    }

    passed = all(checks.values())
    return {
        "passed": passed,
        "checks": checks,
        "forbidden_hits": forbidden_hits,
        "identity_hits": identity_hits,
        "empty_leaf_sections": empty_leaf_sections,
        "oversized_chunks": oversized_chunks,
        "pages_without_removed_lines": pages_without_removed_lines,
        "stats": {
            "page_count": len(pages),
            "section_count": len(sections),
            "leaf_section_count": len(leaf_sections),
            "chunk_count": len(chunks),
            "total_removed_lines": sum(len(page.removed_lines) for page in pages),
            "stripped_page_ratio": stripped_ratio,
        },
    }
