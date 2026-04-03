"""Dataclasses shared across extraction, structure, chunking, and writing."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LineRecord:
    """A text line reconstructed from positioned PDF words."""

    text: str
    top: float
    bottom: float
    x0: float
    x1: float
    removed: bool = False
    removal_reason: str | None = None


@dataclass
class LinkRecord:
    """A PDF link annotation."""

    source_page: int
    kind: str
    target_page: int | None = None
    uri: str | None = None
    raw_dest: str | None = None


@dataclass
class TableRecord:
    """A table extracted from a page."""

    page_number: int
    table_index: int
    rows: list[list[str]]
    file_name: str


@dataclass
class FlowchartRecord:
    """Flowchart-like arrow text captured from a page."""

    page_number: int
    flowchart_index: int
    lines: list[str]
    nodes: list[str]
    edges: list[dict[str, str]]
    file_stem: str


@dataclass
class PageRecord:
    """Final cleaned data per page."""

    page_number: int
    text: str
    lines: list[LineRecord]
    removed_lines: list[LineRecord]
    references: list[str]
    links: list[LinkRecord]
    table_files: list[str] = field(default_factory=list)
    flowchart_files: list[str] = field(default_factory=list)


@dataclass
class SectionRecord:
    """Structured section built from outline/TOC."""

    section_id: str
    title: str
    parent_id: str | None
    level: int
    page_start: int
    page_end: int
    is_leaf: bool
    text: str
    references: list[str]
    table_files: list[str]
    flowchart_files: list[str]
    link_targets: list[str]


@dataclass
class ChunkRecord:
    """Chunked markdown block and metadata."""

    chunk_id: str
    section_id: str
    page_start: int
    page_end: int
    token_estimate: int
    text: str
    references: list[str]
    table_files: list[str]
    flowchart_files: list[str]
    link_targets: list[str]
