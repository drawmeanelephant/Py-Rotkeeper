#!/usr/bin/env python3
"""rc/rotkeeper/lib/scriptbook.py"""
from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from rotkeeper.config import CONFIG
from rotkeeper.context import RunContext


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "scriptbook",
        help="Bundle all Python source files under rc/ into a Markdown report",
    )
    p.add_argument("--dry-run", action="store_true", default=False)
    p.add_argument("--verbose", action="store_true", default=False)
    p.set_defaults(func=run)
    return p


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


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    # ctx is the boss
    dry     = ctx.dry_run if ctx is not None else False
    verbose = ctx.verbose if ctx is not None else False

    cfg = ctx.config if (ctx is not None and ctx.config is not None) else CONFIG

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    reports  = cfg.BONES / "reports"
    src_root = cfg.ROOT_DIR / "rc"

    if dry:
        logging.info("DRY-RUN: would write scriptbook-full -> %s/rotkeeper-scriptbook-full.md", reports)
        return 0

    reports.mkdir(parents=True, exist_ok=True)
    out = reports / "rotkeeper-scriptbook-full.md"
    _write_header(out, "Rotkeeper Scriptbook (Full)", "All Python source files under rc/ with path markers")

    if not src_root.exists():
        logging.warning("scriptbook: src dir not found: %s", src_root)
        return 0

    for f in sorted(src_root.rglob("*.py")):
        rel = str(f.relative_to(cfg.ROOT_DIR))
        _append_file_block(out, rel, f.read_text(encoding="utf-8"))

    logging.info("scriptbook -> %s", out)
    return 0