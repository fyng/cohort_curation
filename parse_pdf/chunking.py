"""Section chunking utilities for LLM-friendly output sizes."""

from __future__ import annotations

import re
from itertools import count

from .config import ChunkingConfig
from .models import ChunkRecord, SectionRecord
from .utils import estimate_tokens

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _split_large_paragraph(paragraph: str, max_tokens: int) -> list[str]:
    if estimate_tokens(paragraph) <= max_tokens:
        return [paragraph]

    sentences = [part.strip() for part in _SENTENCE_SPLIT_RE.split(paragraph) if part.strip()]
    if not sentences:
        return [paragraph]

    parts: list[str] = []
    current: list[str] = []
    for sentence in sentences:
        candidate = " ".join([*current, sentence]).strip()
        if current and estimate_tokens(candidate) > max_tokens:
            parts.append(" ".join(current).strip())
            current = [sentence]
        else:
            current.append(sentence)

    if current:
        parts.append(" ".join(current).strip())

    return [part for part in parts if part]


def _split_into_blocks(text: str, max_tokens: int) -> list[str]:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    blocks: list[str] = []
    for paragraph in paragraphs:
        blocks.extend(_split_large_paragraph(paragraph, max_tokens=max_tokens))
    return blocks


def build_chunks(sections: list[SectionRecord], config: ChunkingConfig) -> list[ChunkRecord]:
    """Chunk leaf section text near the configured token target."""
    chunk_list: list[ChunkRecord] = []
    sequence = count(1)

    for section in sections:
        if not section.is_leaf:
            continue
        if not section.text.strip():
            continue

        blocks = _split_into_blocks(section.text, max_tokens=config.max_tokens)
        current_blocks: list[str] = []

        for block in blocks:
            candidate_text = "\n\n".join([*current_blocks, block]).strip()
            if current_blocks and estimate_tokens(candidate_text) > config.max_tokens:
                chunk_text = "\n\n".join(current_blocks).strip()
                chunk_number = next(sequence)
                chunk_list.append(
                    ChunkRecord(
                        chunk_id=f"chunk_{chunk_number:04d}",
                        section_id=section.section_id,
                        page_start=section.page_start,
                        page_end=section.page_end,
                        token_estimate=estimate_tokens(chunk_text),
                        text=chunk_text,
                        references=section.references,
                        table_files=section.table_files,
                        flowchart_files=section.flowchart_files,
                        link_targets=section.link_targets,
                    )
                )
                current_blocks = [block]
            else:
                current_blocks.append(block)

        if current_blocks:
            chunk_text = "\n\n".join(current_blocks).strip()
            chunk_number = next(sequence)
            chunk_list.append(
                ChunkRecord(
                    chunk_id=f"chunk_{chunk_number:04d}",
                    section_id=section.section_id,
                    page_start=section.page_start,
                    page_end=section.page_end,
                    token_estimate=estimate_tokens(chunk_text),
                    text=chunk_text,
                    references=section.references,
                    table_files=section.table_files,
                    flowchart_files=section.flowchart_files,
                    link_targets=section.link_targets,
                )
            )

    return chunk_list
