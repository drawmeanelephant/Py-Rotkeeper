#!/usr/bin/env python3
"""
rc/rotkeeper/lib/configbook.py
Binder ritual: bundle bones/ config assets (Markdown, YAML, CSS, HTML)
into a single annotated Markdown for archival / backup.

Default behaviour
-----------------
Collects every .md, .yaml/.yml, .css, and .html file found anywhere under
bones/, EXCLUDING the three large generated reports:

    bones/reports/rotkeeper-scriptbook-full.md
    bones/reports/rotkeeper-docbook.md
    bones/reports/rotkeeper-docbook-clean.md

Pass --include-reports to lift those exclusions for a complete backup.

Delimiter format
----------------
configbook uses a DIFFERENT fence style from scriptbook/docbook on purpose.
scriptbook/docbook use HTML comment fences:

    <!-- START: path -->
    <!-- END: path -->

configbook uses pipe-bang fences so they never collide when configbook
ingests the generated reports under --include-reports:

    ||> FILE: path/to/file.yaml
    ...content...
    ||> END: path/to/file.yaml

Content is additionally wrapped in a typed Markdown code fence (```yaml,
```css, etc.) so that inner backticks in the source files don't escape
the outer block, and syntax-aware tools can highlight correctly.

Usage (standalone):
    rotkeeper configbook [--include-reports] [--dry-run] [--verbose]

Produced report:
    bones/reports/rotkeeper-configbook.md
"""
from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from rotkeeper.config import CONFIG
from rotkeeper.context import RunContext


# Reports excluded by default (matched against f.name)
_DEFAULT_EXCLUDED: frozenset[str] = frozenset(
    [
        "rotkeeper-scriptbook-full.md",
        "rotkeeper-docbook.md",
        "rotkeeper-docbook-clean.md",
    ]
)

# Extensions captured from bones/
_BONES_EXTS: frozenset[str] = frozenset({".md", ".yaml", ".yml", ".css", ".html"})

# Fence format — deliberately distinct from scriptbook's <!-- START/END --> markers
# Using ||> prefix: unambiguous, no special meaning in Markdown, YAML, HTML, or Python
_FENCE_START = "||> FILE: {rel}"
_FENCE_END   = "||> END: {rel}"

# Extension -> code fence language tag
_EXT_LANG: dict[str, str] = {
    ".yaml": "yaml",
    ".yml":  "yaml",
    ".css":  "css",
    ".html": "html",
    ".md":   "markdown",
}


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "configbook",
        help=(
            "Bundle bones/ config assets (.md/.yaml/.css/.html) into a "
            "configbook report; large generated reports are excluded by default"
        ),
    )
    p.add_argument(
        "--include-reports",
        action="store_true",
        default=False,
        help=(
            "Include the normally-excluded generated reports "
            "(scriptbook-full, docbook, docbook-clean) for a complete backup. "
            "Safe: configbook uses its own ||> FILE/END fences, "
            "not the HTML comment fences used by those reports."
        ),
    )
    p.add_argument("--dry-run",  action="store_true", default=False)
    p.add_argument("--verbose",  action="store_true", default=False)
    p.set_defaults(func=run)
    return p


# ── helpers ───────────────────────────────────────────────────────────────────

def _write_header(out: Path, title: str, subtitle: str) -> None:
    today = date.today().isoformat()
    out.write_text(
        f'---\ntitle: "{title}"\nsubtitle: "{subtitle}"\ngenerated: "{today}"\n---\n\n',
        encoding="utf-8",
    )


def _append_file_block(out: Path, rel: str, content: str) -> None:
    """
    Write one file block using ||> fences with a typed inner code fence.

    The inner ```lang fence means:
      - content's own backtick sequences can't escape the outer block
      - syntax-aware renderers highlight correctly
      - the ||> outer markers remain unambiguously parseable regardless
        of what the content contains
    """
    lang = _EXT_LANG.get(Path(rel).suffix.lower(), "text")

    with out.open("a", encoding="utf-8") as f:
        f.write(_FENCE_START.format(rel=rel) + "\n\n")
        f.write(f"```{lang}\n")
        f.write(content)
        if not content.endswith("\n"):
            f.write("\n")
        f.write("```\n\n")
        f.write(_FENCE_END.format(rel=rel) + "\n\n")


def _collect_bones_files(
    bones_dir: Path,
    out_path: Path,
    exclude_names: frozenset[str],
) -> list[Path]:
    """
    Walk bones/ and return sorted files matching _BONES_EXTS,
    skipping the output file itself and any name in exclude_names.
    """
    found: list[Path] = []
    for f in sorted(bones_dir.rglob("*")):
        if not f.is_file():
            continue
        if f.suffix.lower() not in _BONES_EXTS:
            continue
        if f == out_path:
            continue
        if f.name in exclude_names:
            continue
        # Exclude workflow asset index (too large / not useful for configbook)
        if f.as_posix().endswith("bones/reports/assets.yaml"):
            continue
        found.append(f)
    return found


# ── entry point ───────────────────────────────────────────────────────────────

def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    dry             = bool(getattr(args, "dry_run", False)) or (ctx.dry_run if ctx else False)
    verbose         = bool(getattr(args, "verbose", False)) or (ctx.verbose if ctx else False)
    include_reports = bool(getattr(args, "include_reports", False))
    cfg             = ctx.config if (ctx and ctx.config) else CONFIG
    reports         = cfg.BONES / "reports"
    out             = reports / "rotkeeper-configbook.md"

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    exclude = frozenset() if include_reports else _DEFAULT_EXCLUDED
    files   = _collect_bones_files(cfg.BONES, out, exclude)

    if dry:
        logging.info(
            "DRY-RUN: would write configbook (%d files) -> %s", len(files), out
        )
        for f in files:
            logging.info("  + %s", f.relative_to(cfg.BASE_DIR))
        return 0

    reports.mkdir(parents=True, exist_ok=True)
    subtitle = (
        "All bones/ assets (md/yaml/css/html) — generated reports INCLUDED"
        if include_reports
        else "All bones/ assets (md/yaml/css/html); generated reports excluded by default"
    )
    _write_header(out, "Rotkeeper Configbook", subtitle)

    for f in files:
        rel = str(f.relative_to(cfg.BASE_DIR))
        _append_file_block(out, rel, f.read_text(encoding="utf-8"))

    logging.info("configbook -> %s (%d files)", out, len(files))
    return 0
