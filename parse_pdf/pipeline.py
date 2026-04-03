"""End-to-end parsing pipeline for clinical guideline PDFs."""

from __future__ import annotations

import shutil
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .chunking import build_chunks
from .config import FORBIDDEN_OUTPUT_PATTERNS, ParserConfig
from .extractor import extract_pdf_content
from .structure import build_sections, extract_outline_entries
from .validate import validate_guideline_outputs
from .writers import (
    ensure_output_layout,
    write_chunk_artifacts,
    write_flowchart_artifacts,
    write_manifest,
    write_page_artifacts,
    write_report,
    write_section_artifacts,
    write_table_artifacts,
)


def _sanitize_summary(pages: list[Any]) -> dict[str, Any]:
    reason_counter: Counter[str] = Counter()
    reason_pages: dict[str, list[int]] = defaultdict(list)

    for page in pages:
        for line in page.removed_lines:
            reason = line.removal_reason or "unknown"
            reason_counter[reason] += 1
            if page.page_number not in reason_pages[reason]:
                reason_pages[reason].append(page.page_number)

    return {
        "total_removed_lines": int(sum(reason_counter.values())),
        "reason_counts": dict(reason_counter),
        "reason_pages": {reason: sorted(numbers) for reason, numbers in reason_pages.items()},
    }


def parse_single_guideline(pdf_path: Path, config: ParserConfig) -> dict[str, Any]:
    """Parse one PDF into markdown-first, validated outputs."""
    guideline_slug = pdf_path.stem
    guideline_dir = config.parsed_root / guideline_slug

    if guideline_dir.exists():
        shutil.rmtree(guideline_dir)

    dirs = ensure_output_layout(guideline_dir)

    reader, pages, tables, flowcharts = extract_pdf_content(pdf_path, rules=config.strip_rules)
    outline_entries = extract_outline_entries(reader, total_pages=len(pages))
    sections, _ = build_sections(outline_entries, pages=pages)
    chunks = build_chunks(sections, config=config.chunking)

    write_page_artifacts(dirs["pages"], pages)
    write_table_artifacts(dirs["tables"], tables)
    write_flowchart_artifacts(dirs["flowcharts"], flowcharts)
    write_section_artifacts(dirs["sections"], sections)
    write_chunk_artifacts(dirs["chunks"], chunks)

    write_manifest(
        guideline_dir,
        source_pdf=pdf_path,
        page_count=len(pages),
        section_count=len(sections),
        chunk_count=len(chunks),
        table_count=len(tables),
        flowchart_count=len(flowcharts),
    )

    sanitize_summary = _sanitize_summary(pages)
    write_report(dirs["reports"], "sanitization_summary", sanitize_summary)

    validation = validate_guideline_outputs(
        guideline_dir,
        pages=pages,
        sections=sections,
        chunks=chunks,
        forbidden_patterns=FORBIDDEN_OUTPUT_PATTERNS,
        chunking=config.chunking,
    )
    write_report(dirs["reports"], "validation", validation)

    if config.strict_validation and not validation["passed"]:
        raise RuntimeError(f"Validation failed for {pdf_path.name}: {validation['checks']}")

    summary = {
        "guideline": guideline_slug,
        "source_pdf": pdf_path.as_posix(),
        "output_dir": guideline_dir.as_posix(),
        "page_count": len(pages),
        "section_count": len(sections),
        "chunk_count": len(chunks),
        "table_count": len(tables),
        "flowchart_count": len(flowcharts),
        "validation_passed": validation["passed"],
        "validation_checks": validation["checks"],
        "sanitization_summary": sanitize_summary,
    }
    write_report(dirs["reports"], "summary", summary)
    return summary


def parse_guidelines_batch(config: ParserConfig | None = None) -> dict[str, Any]:
    """Parse all PDFs in the configured raw guideline folder."""
    cfg = config or ParserConfig()
    raw_root = cfg.raw_root.resolve()
    parsed_root = cfg.parsed_root.resolve()
    parsed_root.mkdir(parents=True, exist_ok=True)

    pdf_paths = sorted(raw_root.glob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found under {raw_root}")

    started_at = datetime.now(timezone.utc)
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for pdf_path in pdf_paths:
        try:
            result = parse_single_guideline(pdf_path, config=cfg)
            results.append(result)
        except Exception as exc:
            failure = {
                "guideline": pdf_path.stem,
                "source_pdf": pdf_path.as_posix(),
                "error": str(exc),
            }
            failures.append(failure)

    batch_report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "started_at_utc": started_at.isoformat(),
        "raw_root": raw_root.as_posix(),
        "parsed_root": parsed_root.as_posix(),
        "strict_validation": cfg.strict_validation,
        "guideline_count": len(pdf_paths),
        "success_count": len(results),
        "failure_count": len(failures),
        "results": results,
        "failures": failures,
    }

    report_path = parsed_root / "batch_report.json"
    report_path.write_text(
        __import__("json").dumps(batch_report, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    if cfg.strict_validation and failures:
        joined = "; ".join(f"{item['guideline']}: {item['error']}" for item in failures)
        raise RuntimeError(f"Batch parsing failed in strict mode: {joined}")

    return batch_report
