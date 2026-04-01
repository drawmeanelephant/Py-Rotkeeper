#!/usr/bin/env python3
"""
rc/rotkeeper/lib/degum.py
CLI tool for Rotkeeper to check markdown files for missing/None metadata
and dump a report.
"""
from __future__ import annotations

import glob
import os
import argparse
import yaml

from ..context import RunContext


def scan_md_files(source_dir: str, output_file: str) -> None:
    report: list[str] = []
    md_files = glob.glob(os.path.join(source_dir, "**/*.md"), recursive=True)
    for path in md_files:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if lines and lines[0].strip() == "---":
            end_idx = None
            for i, line in enumerate(lines[1:], start=1):
                if line.strip() == "---":
                    end_idx = i
                    break
            if end_idx is None:
                report.append(f"{path}: frontmatter not closed")
                continue
            frontmatter_text = "".join(lines[1:end_idx])
            try:
                data = yaml.safe_load(frontmatter_text)
            except yaml.YAMLError as e:
                report.append(f"{path}: YAML parse error: {e}")
                continue
            missing_fields = [
                field for field in ["title", "tags", "author", "date"]
                if not data or field not in data or data[field] is None
            ]
            if missing_fields:
                report.append(f"{path}: missing {', '.join(missing_fields)}")
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("\n".join(report) if report else "No issues found.\n")


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "degum-frontmatter",
        help="Check markdown files for missing/None frontmatter metadata and dump a report",
    )
    parser.add_argument("--source", required=True, help="Directory of markdown files")
    parser.add_argument("--output", required=True, help="Output report file")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")
    scan_md_files(args.source, args.output)
    print(f"Scan complete. Report written to {args.output}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Degum markdown frontmatter")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run(args, ctx=None)


if __name__ == "__main__":
    main()
