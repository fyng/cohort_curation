"""Writers for markdown-first parsed guideline artifacts."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import ChunkRecord, FlowchartRecord, PageRecord, SectionRecord, TableRecord
from .utils import markdown_escape


def ensure_output_layout(guideline_dir: Path) -> dict[str, Path]:
    """Create all sub-directories needed for parsed artifacts."""
    directories = {
        "pages": guideline_dir / "pages",
        "sections": guideline_dir / "sections",
        "tables": guideline_dir / "tables",
        "flowcharts": guideline_dir / "flowcharts",
        "chunks": guideline_dir / "chunks",
        "reports": guideline_dir / "reports",
    }
    guideline_dir.mkdir(parents=True, exist_ok=True)
    for path in directories.values():
        path.mkdir(parents=True, exist_ok=True)
    return directories


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _table_markdown(rows: list[list[str]]) -> str:
    if not rows:
        return "_No table rows extracted._\n"

    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]

    header = normalized[0]
    body = normalized[1:]

    escaped_header = [markdown_escape(cell) for cell in header]
    lines = ["| " + " | ".join(escaped_header) + " |"]
    lines.append("| " + " | ".join(["---"] * width) + " |")

    for row in body:
        escaped = [markdown_escape(cell) for cell in row]
        lines.append("| " + " | ".join(escaped) + " |")

    return "\n".join(lines) + "\n"


def write_page_artifacts(page_dir: Path, pages: list[PageRecord]) -> None:
    """Write page-level markdown and metadata JSON files."""
    for page in pages:
        md_path = page_dir / f"page_{page.page_number:04d}.md"
        json_path = page_dir / f"page_{page.page_number:04d}.json"

        body = page.text.strip() or "_No text extracted._"
        md = f"# Page {page.page_number:04d}\n\n{body}\n"
        md_path.write_text(md, encoding="utf-8")

        payload = {
            "page_number": page.page_number,
            "references": page.references,
            "links": [asdict(link) for link in page.links],
            "removed_lines": [
                {
                    "top": line.top,
                    "bottom": line.bottom,
                    "x0": line.x0,
                    "x1": line.x1,
                    "removal_reason": line.removal_reason,
                }
                for line in page.removed_lines
            ],
            "table_files": page.table_files,
            "flowchart_files": page.flowchart_files,
        }
        _write_json(json_path, payload)


def write_table_artifacts(table_dir: Path, tables: list[TableRecord]) -> None:
    """Write extracted tables as markdown plus an index JSON."""
    index_payload: list[dict[str, Any]] = []
    for table in tables:
        md_path = table_dir / table.file_name
        title = f"# Table page {table.page_number} index {table.table_index}\n\n"
        md_path.write_text(title + _table_markdown(table.rows), encoding="utf-8")
        index_payload.append(
            {
                "page_number": table.page_number,
                "table_index": table.table_index,
                "file": table.file_name,
                "row_count": len(table.rows),
                "column_count": max((len(row) for row in table.rows), default=0),
            }
        )

    _write_json(table_dir / "index.json", index_payload)


def write_flowchart_artifacts(flowchart_dir: Path, flowcharts: list[FlowchartRecord]) -> None:
    """Write flowchart-like text snippets and graph metadata."""
    index_payload: list[dict[str, Any]] = []
    for flowchart in flowcharts:
        md_path = flowchart_dir / f"{flowchart.file_stem}.md"
        json_path = flowchart_dir / f"{flowchart.file_stem}.json"

        line_block = "\n".join(f"- {line}" for line in flowchart.lines) or "- _No lines_"
        edge_block = "\n".join(
            f"- {edge['from']} -> {edge['to']}" for edge in flowchart.edges
        ) or "- _No edges resolved_"

        md = (
            f"# Flowchart page {flowchart.page_number} index {flowchart.flowchart_index}\n\n"
            "## Source Lines\n"
            f"{line_block}\n\n"
            "## Parsed Edges\n"
            f"{edge_block}\n"
        )
        md_path.write_text(md, encoding="utf-8")

        _write_json(json_path, asdict(flowchart))
        index_payload.append(
            {
                "page_number": flowchart.page_number,
                "flowchart_index": flowchart.flowchart_index,
                "file_markdown": md_path.name,
                "file_json": json_path.name,
                "node_count": len(flowchart.nodes),
                "edge_count": len(flowchart.edges),
            }
        )

    _write_json(flowchart_dir / "index.json", index_payload)


def write_section_artifacts(section_dir: Path, sections: list[SectionRecord]) -> None:
    """Write section markdown files, a TOC markdown, and a section index JSON."""
    toc_lines = ["# Table of Contents", ""]
    index_payload: list[dict[str, Any]] = []

    for section in sections:
        md_path = section_dir / f"{section.section_id}.md"
        indent = "  " * max(0, section.level - 1)
        toc_lines.append(
            f"{indent}- [{section.title}]({section.section_id}.md) (pages {section.page_start}-{section.page_end})"
        )

        metadata_lines = [
            f"- section_id: {section.section_id}",
            f"- parent_id: {section.parent_id or ''}",
            f"- level: {section.level}",
            f"- page_range: {section.page_start}-{section.page_end}",
            f"- is_leaf: {str(section.is_leaf).lower()}",
        ]

        text_block = section.text.strip() if section.is_leaf else "_Container section. See child sections._"
        md = (
            f"# {section.title}\n\n"
            "## Metadata\n"
            + "\n".join(metadata_lines)
            + "\n\n"
            "## Content\n"
            f"{text_block}\n"
        )
        md_path.write_text(md, encoding="utf-8")

        index_payload.append(
            {
                "section_id": section.section_id,
                "title": section.title,
                "parent_id": section.parent_id,
                "level": section.level,
                "page_start": section.page_start,
                "page_end": section.page_end,
                "is_leaf": section.is_leaf,
                "file": md_path.name,
                "reference_count": len(section.references),
                "table_file_count": len(section.table_files),
                "flowchart_file_count": len(section.flowchart_files),
                "link_target_count": len(section.link_targets),
            }
        )

    (section_dir / "toc.md").write_text("\n".join(toc_lines).strip() + "\n", encoding="utf-8")
    _write_json(section_dir / "index.json", index_payload)


def write_chunk_artifacts(chunk_dir: Path, chunks: list[ChunkRecord]) -> None:
    """Write chunk markdown files and index metadata."""
    index_payload: list[dict[str, Any]] = []
    for chunk in chunks:
        md_path = chunk_dir / f"{chunk.chunk_id}.md"
        metadata_lines = [
            f"- chunk_id: {chunk.chunk_id}",
            f"- section_id: {chunk.section_id}",
            f"- page_range: {chunk.page_start}-{chunk.page_end}",
            f"- token_estimate: {chunk.token_estimate}",
            f"- reference_count: {len(chunk.references)}",
            f"- table_refs: {', '.join(chunk.table_files)}",
            f"- flowchart_refs: {', '.join(chunk.flowchart_files)}",
            f"- link_target_count: {len(chunk.link_targets)}",
        ]

        md = (
            f"# {chunk.chunk_id}\n\n"
            "## Metadata\n"
            + "\n".join(metadata_lines)
            + "\n\n"
            "## Content\n"
            f"{chunk.text.strip()}\n"
        )
        md_path.write_text(md, encoding="utf-8")

        index_payload.append(
            {
                "chunk_id": chunk.chunk_id,
                "section_id": chunk.section_id,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "token_estimate": chunk.token_estimate,
                "file": md_path.name,
                "references": chunk.references,
                "table_files": chunk.table_files,
                "flowchart_files": chunk.flowchart_files,
                "link_targets": chunk.link_targets,
            }
        )

    _write_json(chunk_dir / "index.json", index_payload)


def write_manifest(
    guideline_dir: Path,
    source_pdf: Path,
    page_count: int,
    section_count: int,
    chunk_count: int,
    table_count: int,
    flowchart_count: int,
) -> None:
    """Write top-level manifest metadata."""
    payload = {
        "source_pdf": source_pdf.as_posix(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "page_count": page_count,
        "section_count": section_count,
        "chunk_count": chunk_count,
        "table_count": table_count,
        "flowchart_count": flowchart_count,
    }
    _write_json(guideline_dir / "manifest.json", payload)


def write_report(report_dir: Path, name: str, payload: Any) -> None:
    """Write report payload in JSON format."""
    _write_json(report_dir / f"{name}.json", payload)
