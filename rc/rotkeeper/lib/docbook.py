#!/usr/bin/env python3
"""rc/rotkeeper/lib/docbook.py"""
from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from rotkeeper.config import CONFIG
from rotkeeper.context import RunContext


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "docbook",
        help="Bundle Markdown documentation into docbook / docbook-clean reports",
    )
    p.add_argument("--mode", choices=["docbook", "docbook-clean", "both"], default="both")
    p.add_argument("--strip-frontmatter", action="store_true", default=False)
    p.add_argument("--dry-run",  action="store_true", default=False)
    p.add_argument("--verbose",  action="store_true", default=False)
    p.set_defaults(func=run)
    return p


def _frontmatter_and_body(path: Path) -> tuple[dict[str, str], str]:
    text  = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].startswith("---"):
        return {}, text
    end = next((i for i, l in enumerate(lines[1:], 1) if l.startswith("---")), None)
    if end is None:
        return {}, text
    fm_lines = lines[1:end]
    body     = "".join(lines[end + 1:])
    fm: dict[str, str] = {}
    for l in fm_lines:
        if ":" in l:
            k, _, v = l.partition(":")
            fm[k.strip()] = v.strip().strip('"')
    return fm, body


def _write_header(out: Path, title: str, subtitle: str) -> None:
    today = date.today().isoformat()
    out.write_text(
        f'---\ntitle: "{title}"\nsubtitle: "{subtitle}"\ngenerated: "{today}"\n---\n\n',
        encoding="utf-8",
    )


def _append_file_block(out: Path, rel: str, content: str) -> None:
    with out.open("a", encoding="utf-8") as f:
        f.write(f"<!-- START: {rel} -->\n\n")
        f.write(content)
        if not content.endswith("\n"):
            f.write("\n")
        f.write(f"<!-- END: {rel} -->\n\n")


def _run_docbook(reports: Path, strip: bool, cfg) -> None:
    out      = reports / "rotkeeper-docbook.md"
    docs_dir = cfg.CONTENT_DIR / "docs"
    _write_header(out, "Rotkeeper Docbook", "All markdown documentation in home/content/docs/ with path markers")
    if not docs_dir.exists():
        logging.debug("docbook: docs dir not found: %s", docs_dir)
        return
    for f in sorted(docs_dir.rglob("*.md")):
        rel      = str(f.relative_to(cfg.HOME))
        fm, body = _frontmatter_and_body(f)
        content  = body if strip else f.read_text(encoding="utf-8")
        _append_file_block(out, rel, content)
    logging.info("docbook -> %s", out)


def _run_docbook_clean(reports: Path, cfg) -> None:
    out      = reports / "rotkeeper-docbook-clean.md"
    docs_dir = cfg.CONTENT_DIR / "docs"
    _write_header(out, "Home Content (Cleaned)", "Frontmatter-stripped, collapse-friendly version")
    if not docs_dir.exists():
        logging.debug("docbook-clean: docs dir not found: %s", docs_dir)
        return
    with out.open("a", encoding="utf-8") as fh:
        for f in sorted(docs_dir.rglob("*.md")):
            fm, body = _frontmatter_and_body(f)
            title    = fm.get("title") or f.stem
            fh.write(f"## {title}\n\n")
            fh.write(body.lstrip("\n"))
            fh.write("\n\n")
    logging.info("docbook-clean -> %s", out)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    # ctx is the boss
    dry     = ctx.dry_run if ctx is not None else False
    verbose = ctx.verbose if ctx is not None else False
    strip   = bool(getattr(args, "strip_frontmatter", False))

    cfg     = ctx.config if (ctx is not None and ctx.config is not None) else CONFIG
    mode    = getattr(args, "mode", "both")
    reports = cfg.BONES / "reports"

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    targets = ["docbook", "docbook-clean"] if mode == "both" else [mode]

    if dry:
        for t in targets:
            logging.info("DRY-RUN: would write %s -> %s", t, reports)
        return 0

    reports.mkdir(parents=True, exist_ok=True)
    if "docbook" in targets:
        _run_docbook(reports, strip, cfg)
    if "docbook-clean" in targets:
        _run_docbook_clean(reports, cfg)
    return 0