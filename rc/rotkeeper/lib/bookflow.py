#!/usr/bin/env python3
"""
rc/rotkeeper/lib/bookflow.py
Combined runner for all binder (book) rituals.
Mirrors the style of flow.py — runs each book step in sequence,
printing progress, and short-circuits on failure.

Modes
-----
    scriptbook      rc/rotkeeper/lib/scriptbook.py   → rotkeeper-scriptbook-full.md
    docbook         rc/rotkeeper/lib/docbook.py       → rotkeeper-docbook.md + docbook-clean.md
    configbook      rc/rotkeeper/lib/configbook.py    → rotkeeper-configbook.md
    all (default)   runs all three in order

Usage:
    rotkeeper bookflow [--mode scriptbook|docbook|configbook|all]
                       [--include-reports]
                       [--strip-frontmatter]
                       [--dry-run] [--verbose]

    # Full backup (include big generated reports in configbook):
    rotkeeper bookflow --mode all --include-reports
"""
from __future__ import annotations

import argparse
import logging
import sys

import rotkeeper.lib.scriptbook as scriptbook
import rotkeeper.lib.docbook    as docbook
import rotkeeper.lib.configbook as configbook

from rotkeeper.config  import CONFIG
from rotkeeper.context import RunContext


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "bookflow",
        help="Run binder rituals: scriptbook, docbook, and/or configbook in sequence",
    )
    p.add_argument(
        "--mode",
        choices=["scriptbook", "docbook", "configbook", "all"],
        default="all",
        help="Which book(s) to produce (default: all)",
    )
    p.add_argument(
        "--include-reports",
        action="store_true",
        default=False,
        help=(
            "Pass to configbook: include large generated reports for a full backup "
            "(scriptbook-full, docbook, docbook-clean)"
        ),
    )
    p.add_argument(
        "--strip-frontmatter",
        action="store_true",
        default=False,
        help="Pass to docbook: strip YAML frontmatter from included Markdown files",
    )
    p.add_argument("--dry-run",  action="store_true", default=False)
    p.add_argument("--verbose",  action="store_true", default=False)
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to user-config.yaml (overrides default)",
    )
    p.set_defaults(func=run_bookflow)
    return p


# ── helpers ───────────────────────────────────────────────────────────────────

def _ns(**kw) -> argparse.Namespace:
    return argparse.Namespace(**kw)


# ── entry point ───────────────────────────────────────────────────────────────

def run_bookflow(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    dry     = bool(getattr(args, "dry_run", False))
    verbose = bool(getattr(args, "verbose", False))
    mode    = getattr(args, "mode", "all")
    include = bool(getattr(args, "include_reports", False))
    strip   = bool(getattr(args, "strip_frontmatter", False))

    if ctx is None:
        ctx = RunContext(dry_run=dry, verbose=verbose, log_file=None, config=CONFIG)

    # Build the ordered step list
    all_steps: list[tuple[str, object]] = [
        (
            "scriptbook",
            lambda: scriptbook.run(
                _ns(dry_run=dry, verbose=verbose), ctx
            ),
        ),
        (
            "docbook",
            lambda: docbook.run(
                _ns(dry_run=dry, verbose=verbose, mode="both",
                    strip_frontmatter=strip),
                ctx,
            ),
        ),
        (
            "configbook",
            lambda: configbook.run(
                _ns(dry_run=dry, verbose=verbose, include_reports=include), ctx
            ),
        ),
    ]

    steps = (
        all_steps
        if mode == "all"
        else [(name, fn) for name, fn in all_steps if name == mode]
    )

    total = len(steps)
    for i, (name, fn) in enumerate(steps, 1):
        print(f"==> [{i}/{total}] {name}")
        try:
            rc = fn()
            if rc and rc != 0:
                print(f"    FAILED (exit {rc})", file=sys.stderr)
                return rc
        except Exception as e:
            print(f"    ERROR during {name}: {e}", file=sys.stderr)
            if verbose:
                import traceback
                traceback.print_exc()
            return 1

    print("==> Book rituals complete.")
    return 0
