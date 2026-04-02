#!/usr/bin/env python3
"""rc/rotkeeper/lib/configbook.py"""
from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from rotkeeper.config import CONFIG
from rotkeeper.context import RunContext

_DEFAULT_EXCLUDED: frozenset[str] = frozenset([
    "rotkeeper-scriptbook-full.md",
    "rotkeeper-docbook.md",
    "rotkeeper-docbook-clean.md",
])
_BONES_EXTS: frozenset[str] = frozenset({".md", ".yaml", ".yml", ".css", ".html"})
_FENCE_START = "||> FILE: {rel}"
_FENCE_END   = "||> END: {rel}"
_EXT_LANG: dict[str, str] = {
    ".yaml": "yaml", ".yml": "yaml", ".css": "css", ".html": "html", ".md": "markdown",
}


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "configbook",
        help="Bundle bones/ config assets (.md/.yaml/.css/.html) into a configbook report",
    )
    p.add_argument("--include-reports", action="store_true", default=False)
    p.add_argument("--dry-run",  action="store_true", default=False)
    p.add_argument("--verbose",  action="store_true", default=False)
    p.set_defaults(func=run)
    return p


def _write_header(out: Path, title: str, subtitle: str) -> None:
    today = date.today().isoformat()
    out.write_text(
        f'---\ntitle: "{title}"\nsubtitle: "{subtitle}"\ngenerated: "{today}"\n---\n\n',
        encoding="utf-8",
    )


def _append_file_block(out: Path, rel: str, content: str) -> None:
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
    bones_dir: Path, out_path: Path, exclude_names: frozenset[str]
) -> list[Path]:
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
        if f.as_posix().endswith("bones/reports/assets.yaml"):
            continue
        found.append(f)
    return found


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    # ctx is the boss — no fallback two-step
    dry             = ctx.dry_run if ctx is not None else False
    verbose         = ctx.verbose if ctx is not None else False
    include_reports = bool(getattr(args, "include_reports", False))

    cfg     = ctx.config if (ctx is not None and ctx.config is not None) else CONFIG
    reports = cfg.BONES / "reports"
    out     = reports / "rotkeeper-configbook.md"

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    exclude = frozenset() if include_reports else _DEFAULT_EXCLUDED
    files   = _collect_bones_files(cfg.BONES, out, exclude)

    if dry:
        logging.info("DRY-RUN: would write configbook (%d files) -> %s", len(files), out)
        for f in files:
            logging.info("  + %s", f.relative_to(cfg.BASEDIR))
        return 0

    reports.mkdir(parents=True, exist_ok=True)
    subtitle = (
        "All bones/ assets (md/yaml/css/html) — generated reports INCLUDED"
        if include_reports
        else "All bones/ assets (md/yaml/css/html); generated reports excluded by default"
    )
    _write_header(out, "Rotkeeper Configbook", subtitle)

    for f in files:
        rel = str(f.relative_to(cfg.BASEDIR))
        _append_file_block(out, rel, f.read_text(encoding="utf-8"))

    logging.info("configbook -> %s (%d files)", out, len(files))
    return 0