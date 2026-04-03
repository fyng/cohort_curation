#!/usr/bin/env python3
"""CLI for parsing large clinical guideline PDFs into LLM-friendly artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import ParserConfig
from .pipeline import parse_guidelines_batch, parse_single_guideline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse guideline PDFs into structured markdown outputs.")
    parser.add_argument(
        "--raw-root",
        default="guidelines/raw",
        help="Input directory containing raw PDF guidelines (default: guidelines/raw)",
    )
    parser.add_argument(
        "--parsed-root",
        default="guidelines/parsed",
        help="Output directory for parsed artifacts (default: guidelines/parsed)",
    )
    parser.add_argument(
        "--pdf",
        default=None,
        help="Optional single PDF file name under raw-root to parse (default: parse all PDFs)",
    )
    parser.add_argument(
        "--strict-validation",
        action="store_true",
        help="Enable strict validation hard-fail behavior (default: enabled)",
    )
    parser.add_argument(
        "--no-strict-validation",
        action="store_true",
        help="Disable strict validation and keep reports as warnings",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    strict = True
    if args.no_strict_validation:
        strict = False
    elif args.strict_validation:
        strict = True

    config = ParserConfig(
        raw_root=Path(args.raw_root),
        parsed_root=Path(args.parsed_root),
        strict_validation=strict,
    )

    if args.pdf:
        pdf_path = config.raw_root / args.pdf
        summary = parse_single_guideline(pdf_path=pdf_path, config=config)
        print(json.dumps(summary, indent=2, ensure_ascii=True))
        return

    batch = parse_guidelines_batch(config=config)
    print(json.dumps(batch, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
