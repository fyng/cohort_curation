"""Build section hierarchy from PDF outlines with TOC-style fallbacks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from .models import PageRecord, SectionRecord
from .utils import slugify


@dataclass
class OutlineEntry:
    """Intermediate representation of a bookmark node."""

    section_id: str
    title: str
    parent_id: str | None
    level: int
    path_titles: list[str]
    page_start: int | None
    page_end: int | None = None
    is_leaf: bool = True


def _safe_outline_title(item: Any) -> str:
    title = getattr(item, "title", None)
    if title is None:
        return str(item)
    value = str(title).strip()
    return value or "Untitled"


def _safe_outline_page_number(reader: PdfReader, item: Any) -> int | None:
    try:
        page_index = reader.get_destination_page_number(item)
    except Exception:
        return None
    if page_index is None:
        return None
    if int(page_index) < 0:
        return None
    return int(page_index) + 1


def _walk_outline_items(
    items: list[Any],
    reader: PdfReader,
    level: int,
    parent_id: str | None,
    parent_titles: list[str],
    sequence: list[int],
    entries: list[OutlineEntry],
) -> None:
    index = 0
    previous_entry: OutlineEntry | None = None

    while index < len(items):
        item = items[index]
        if isinstance(item, list):
            if previous_entry is None:
                _walk_outline_items(
                    item,
                    reader=reader,
                    level=level,
                    parent_id=parent_id,
                    parent_titles=parent_titles,
                    sequence=sequence,
                    entries=entries,
                )
            else:
                _walk_outline_items(
                    item,
                    reader=reader,
                    level=level + 1,
                    parent_id=previous_entry.section_id,
                    parent_titles=previous_entry.path_titles,
                    sequence=sequence,
                    entries=entries,
                )
                previous_entry.is_leaf = False
            index += 1
            continue

        sequence[0] += 1
        title = _safe_outline_title(item)
        section_id = f"sec_{sequence[0]:04d}_{slugify(title)[:40]}"
        path_titles = [*parent_titles, title]
        page_start = _safe_outline_page_number(reader, item)
        previous_entry = OutlineEntry(
            section_id=section_id,
            title=title,
            parent_id=parent_id,
            level=level,
            path_titles=path_titles,
            page_start=page_start,
        )
        entries.append(previous_entry)
        index += 1


def _compute_page_ranges(entries: list[OutlineEntry], total_pages: int) -> list[OutlineEntry]:
    for i, entry in enumerate(entries):
        if entry.page_start is None:
            continue
        page_end = total_pages
        for following in entries[i + 1 :]:
            if following.page_start is None:
                continue
            if following.page_start <= entry.page_start:
                continue
            if following.level <= entry.level:
                page_end = following.page_start - 1
                break
        entry.page_end = max(entry.page_start, page_end)

    return entries


def _fallback_sections(total_pages: int) -> list[OutlineEntry]:
    entries: list[OutlineEntry] = []
    sequence = 1
    span = 8
    for start in range(1, total_pages + 1, span):
        end = min(total_pages, start + span - 1)
        title = f"Pages {start}-{end}"
        section_id = f"sec_{sequence:04d}_{slugify(title)}"
        entries.append(
            OutlineEntry(
                section_id=section_id,
                title=title,
                parent_id=None,
                level=1,
                path_titles=[title],
                page_start=start,
                page_end=end,
                is_leaf=True,
            )
        )
        sequence += 1
    return entries


def extract_outline_entries(reader: PdfReader, total_pages: int) -> list[OutlineEntry]:
    """Extract and normalize PDF outline entries with page ranges."""
    try:
        raw_outline = reader.outline
    except Exception:
        raw_outline = []

    entries: list[OutlineEntry] = []
    _walk_outline_items(
        raw_outline if isinstance(raw_outline, list) else [],
        reader=reader,
        level=1,
        parent_id=None,
        parent_titles=[],
        sequence=[0],
        entries=entries,
    )

    entries = [entry for entry in entries if entry.page_start is not None]
    if not entries:
        return _fallback_sections(total_pages=total_pages)

    return _compute_page_ranges(entries, total_pages=total_pages)


def _page_to_leaf_section(entries: list[OutlineEntry], total_pages: int) -> dict[int, str]:
    mapping: dict[int, str] = {}
    for entry in entries:
        if not entry.is_leaf:
            continue
        if entry.page_start is None or entry.page_end is None:
            continue
        for page_number in range(entry.page_start, entry.page_end + 1):
            mapping.setdefault(page_number, entry.section_id)

    # Ensure complete coverage even if outline has gaps.
    if mapping:
        last_seen = None
        for page_number in range(1, total_pages + 1):
            if page_number in mapping:
                last_seen = mapping[page_number]
                continue
            if last_seen is not None:
                mapping[page_number] = last_seen

    return mapping


def build_sections(
    entries: list[OutlineEntry],
    pages: list[PageRecord],
) -> tuple[list[SectionRecord], dict[int, str]]:
    """Create section records with text payload for leaf sections."""
    by_page = {record.page_number: record for record in pages}
    total_pages = len(pages)
    page_to_leaf = _page_to_leaf_section(entries, total_pages=total_pages)

    sections: list[SectionRecord] = []

    for entry in entries:
        if entry.page_start is None or entry.page_end is None:
            continue

        references: set[str] = set()
        table_files: set[str] = set()
        flowchart_files: set[str] = set()
        link_targets: set[str] = set()
        text_parts: list[str] = []

        for page_number in range(entry.page_start, entry.page_end + 1):
            page = by_page.get(page_number)
            if page is None:
                continue
            references.update(page.references)
            table_files.update(page.table_files)
            flowchart_files.update(page.flowchart_files)
            for link in page.links:
                if link.kind == "external" and link.uri:
                    link_targets.add(link.uri)
                elif link.target_page is not None:
                    target_section_id = page_to_leaf.get(link.target_page)
                    if target_section_id is not None:
                        link_targets.add(f"sections/{target_section_id}.md")
                    else:
                        link_targets.add(f"pages/page_{link.target_page:04d}.md")
            if entry.is_leaf and page.text.strip():
                text_parts.append(page.text.strip())

        section_text = "\n\n".join(text_parts).strip() if entry.is_leaf else ""
        sections.append(
            SectionRecord(
                section_id=entry.section_id,
                title=entry.title,
                parent_id=entry.parent_id,
                level=entry.level,
                page_start=entry.page_start,
                page_end=entry.page_end,
                is_leaf=entry.is_leaf,
                text=section_text,
                references=sorted(references),
                table_files=sorted(table_files),
                flowchart_files=sorted(flowchart_files),
                link_targets=sorted(link_targets),
            )
        )

    return sections, page_to_leaf
