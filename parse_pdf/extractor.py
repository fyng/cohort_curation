"""Low-level PDF extraction with strict header/footer sanitization."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any

import pdfplumber
from pypdf import PdfReader

from .config import StripRuleConfig
from .models import FlowchartRecord, LineRecord, LinkRecord, PageRecord, TableRecord

_LINE_Y_TOLERANCE = 2.5
_ARROW_RE = re.compile(r"(->|-->|=>|<-|→|←|↔|⟶)")
_ARROW_SPLIT_RE = re.compile(r"\s*(?:->|-->|=>|<-|→|←|↔|⟶)\s*")
_DATE_RE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
_TIME_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
_REFERENCE_RE = re.compile(r"\[[0-9,\- ]+\]|[\u00B9\u00B2\u00B3\u2070-\u2079]+|[\*\u2020\u2021\u00A7\u00B6]")
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_PANEL_CODE_RE = re.compile(r"\b[A-Z]{2,8}-[A-Z0-9]{1,4}\b")


def _normalize_cell(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\x17", " - ")
    text = _CONTROL_CHAR_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _join_words(words: list[dict[str, Any]]) -> str:
    parts = [str(word.get("text", "")).strip() for word in words]
    parts = [part for part in parts if part]
    text = " ".join(parts).strip()
    text = text.replace("\x17", " - ")
    text = _CONTROL_CHAR_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _words_to_lines(words: list[dict[str, Any]]) -> list[LineRecord]:
    if not words:
        return []

    sorted_words = sorted(words, key=lambda item: (float(item["top"]), float(item["x0"])))
    buckets: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_top: float | None = None

    for word in sorted_words:
        top = float(word["top"])
        if current_top is None:
            current = [word]
            current_top = top
            continue
        if abs(top - current_top) <= _LINE_Y_TOLERANCE:
            current.append(word)
            current_top = (current_top + top) / 2.0
        else:
            buckets.append(current)
            current = [word]
            current_top = top

    if current:
        buckets.append(current)

    lines: list[LineRecord] = []
    for bucket in buckets:
        ordered = sorted(bucket, key=lambda item: float(item["x0"]))
        text = _join_words(ordered)
        if not text:
            continue
        tops = [float(item["top"]) for item in ordered]
        bottoms = [float(item["bottom"]) for item in ordered]
        x0s = [float(item["x0"]) for item in ordered]
        x1s = [float(item["x1"]) for item in ordered]
        lines.append(
            LineRecord(
                text=text,
                top=min(tops),
                bottom=max(bottoms),
                x0=min(x0s),
                x1=max(x1s),
            )
        )

    return lines


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(phrase.casefold() in lowered for phrase in phrases)


def _remove_line_reason(line: LineRecord, page_height: float, rules: StripRuleConfig) -> str | None:
    top_limit = page_height * rules.top_band_ratio
    bottom_limit = page_height * (1.0 - rules.bottom_band_ratio)
    in_header_zone = line.top <= top_limit
    in_footer_zone = line.bottom >= bottom_limit
    text = line.text.strip()

    if _contains_any(text, rules.always_strip_phrases):
        return "global_disclaimer_phrase"

    if in_header_zone:
        if _contains_any(text, rules.header_phrases):
            return "header_phrase"
        lowered = text.casefold()
        if "printed by" in lowered:
            return "header_identity"
        if "printed" in lowered and _DATE_RE.search(text) and _TIME_RE.search(text):
            return "header_identity"

    if in_footer_zone:
        if _contains_any(text, rules.footer_phrases):
            return "footer_phrase"

    return None


def _extract_references(text: str) -> list[str]:
    found = {match.group(0).strip() for match in _REFERENCE_RE.finditer(text)}
    return sorted(marker for marker in found if marker)


def _extract_tables(page: Any, page_number: int) -> list[TableRecord]:
    tables_raw = page.extract_tables() or []
    tables: list[TableRecord] = []
    for index, raw_table in enumerate(tables_raw, start=1):
        if not raw_table:
            continue
        rows = [[_normalize_cell(cell) for cell in row] for row in raw_table]
        if all(not any(cell for cell in row) for row in rows):
            continue
        file_name = f"table_p{page_number:04d}_t{index:02d}.md"
        tables.append(TableRecord(page_number=page_number, table_index=index, rows=rows, file_name=file_name))
    return tables


def _build_flowchart(lines: list[str], page_number: int, index: int) -> FlowchartRecord:
    edges: list[dict[str, str]] = []
    nodes: set[str] = set()

    for line in lines:
        parts = [part.strip() for part in _ARROW_SPLIT_RE.split(line) if part.strip()]
        if len(parts) < 2:
            continue
        for node in parts:
            nodes.add(node)
        for left, right in zip(parts, parts[1:]):
            edges.append({"from": left, "to": right})

    node_list = sorted(nodes)

    if not edges and len(lines) >= 2:
        sequence_nodes = [line.strip() for line in lines if line.strip()]
        for node in sequence_nodes:
            nodes.add(node)
        for left, right in zip(sequence_nodes, sequence_nodes[1:]):
            edges.append({"from": left, "to": right})
        node_list = sorted(nodes)

    file_stem = f"flowchart_p{page_number:04d}_f{index:02d}"
    return FlowchartRecord(
        page_number=page_number,
        flowchart_index=index,
        lines=lines,
        nodes=node_list,
        edges=edges,
        file_stem=file_stem,
    )


def _extract_flowcharts(
    lines: list[LineRecord],
    page_number: int,
    links: list[LinkRecord],
) -> list[FlowchartRecord]:
    groups: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        text = line.text.strip()
        if not text:
            continue
        if _ARROW_RE.search(text):
            current.append(text)
            continue
        if current:
            groups.append(current)
            current = []

    if current:
        groups.append(current)

    if not groups:
        internal_links = sum(1 for link in links if link.kind == "internal")
        if internal_links >= 5:
            panel_lines = [
                line.text.strip()
                for line in lines
                if line.text.strip() and len(line.text.strip()) <= 160 and _PANEL_CODE_RE.search(line.text)
            ]
            if len(panel_lines) >= 4:
                groups.append(panel_lines[:32])

    flowcharts: list[FlowchartRecord] = []
    for idx, group in enumerate(groups, start=1):
        flowcharts.append(_build_flowchart(group, page_number=page_number, index=idx))

    return flowcharts


def _resolve_dest_page(dest: Any, page_ref_to_number: dict[int, int], reader: PdfReader) -> int | None:
    if dest is None:
        return None

    if hasattr(dest, "get_object"):
        try:
            dest = dest.get_object()
        except Exception:
            return None

    if isinstance(dest, str):
        try:
            named = reader.named_destinations.get(dest)
            if named is not None:
                page_index = reader.get_destination_page_number(named)
                if page_index is None:
                    return None
                return int(page_index) + 1
        except Exception:
            return None

    if isinstance(dest, (list, tuple)) and dest:
        first = dest[0]
        if hasattr(first, "idnum"):
            return page_ref_to_number.get(int(first.idnum))
        if hasattr(first, "get_object"):
            try:
                resolved = first.get_object()
            except Exception:
                resolved = None
            if resolved is not None and hasattr(resolved, "idnum"):
                return page_ref_to_number.get(int(resolved.idnum))

    if hasattr(dest, "title") or hasattr(dest, "page"):
        try:
            page_index = reader.get_destination_page_number(dest)  # type: ignore[arg-type]
            if page_index is None:
                return None
            return int(page_index) + 1
        except Exception:
            return None

    return None


def extract_links(reader: PdfReader) -> dict[int, list[LinkRecord]]:
    """Extract PDF link annotations grouped by source page."""
    page_ref_to_number: dict[int, int] = {}
    for page_number, page in enumerate(reader.pages, start=1):
        reference = getattr(page, "indirect_reference", None)
        if reference is not None and hasattr(reference, "idnum"):
            page_ref_to_number[int(reference.idnum)] = page_number

    links_by_page: dict[int, list[LinkRecord]] = defaultdict(list)

    for source_page, page in enumerate(reader.pages, start=1):
        annots = page.get("/Annots")
        if annots is None:
            continue
        if hasattr(annots, "get_object"):
            annots = annots.get_object()
        if annots is None:
            continue

        for annot in annots:
            try:
                obj = annot.get_object()
            except Exception:
                continue
            if obj.get("/Subtype") != "/Link":
                continue

            action = obj.get("/A")
            uri = None
            kind = "internal"
            if action is not None:
                try:
                    uri_value = action.get("/URI")
                except Exception:
                    uri_value = None
                if uri_value:
                    kind = "external"
                    uri = str(uri_value)

            dest = obj.get("/Dest")
            if dest is None and action is not None:
                try:
                    dest = action.get("/D")
                except Exception:
                    dest = None

            target_page = _resolve_dest_page(dest, page_ref_to_number, reader)
            raw_dest = str(dest) if dest is not None else None
            links_by_page[source_page].append(
                LinkRecord(
                    source_page=source_page,
                    kind=kind,
                    target_page=target_page,
                    uri=uri,
                    raw_dest=raw_dest,
                )
            )

    return links_by_page


def extract_pdf_content(pdf_path: Path, rules: StripRuleConfig) -> tuple[PdfReader, list[PageRecord], list[TableRecord], list[FlowchartRecord]]:
    """Extract cleaned pages plus table and flowchart artifacts."""
    reader = PdfReader(str(pdf_path))
    links_by_page = extract_links(reader)

    pages: list[PageRecord] = []
    tables: list[TableRecord] = []
    flowcharts: list[FlowchartRecord] = []

    with pdfplumber.open(pdf_path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(use_text_flow=True, keep_blank_chars=False) or []
            lines = _words_to_lines(words)

            cleaned_lines: list[LineRecord] = []
            removed_lines: list[LineRecord] = []
            for line in lines:
                reason = _remove_line_reason(line, float(page.height), rules)
                if reason is not None:
                    removed_lines.append(replace(line, removed=True, removal_reason=reason))
                else:
                    cleaned_lines.append(line)

            text = "\n".join(line.text for line in cleaned_lines if line.text.strip()).strip()

            page_tables = _extract_tables(page, page_number=index)
            tables.extend(page_tables)

            links = links_by_page.get(index, [])
            page_flowcharts = _extract_flowcharts(cleaned_lines, page_number=index, links=links)
            flowcharts.extend(page_flowcharts)

            references = _extract_references(text)

            pages.append(
                PageRecord(
                    page_number=index,
                    text=text,
                    lines=cleaned_lines,
                    removed_lines=removed_lines,
                    references=references,
                    links=links,
                    table_files=[table.file_name for table in page_tables],
                    flowchart_files=[f"{flow.file_stem}.md" for flow in page_flowcharts],
                )
            )

    return reader, pages, tables, flowcharts
