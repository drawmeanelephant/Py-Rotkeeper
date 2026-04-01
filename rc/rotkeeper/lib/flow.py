#!/usr/bin/env python3
# rotkeeper flow — full site build pipeline
from __future__ import annotations

import argparse
import logging
import sys
from typing import Callable

from rotkeeper.config import CONFIG
from rotkeeper.context import RunContext

import rotkeeper.lib.sitemap_collect as sitemap_collect
import rotkeeper.lib.sitemap_indexes as sitemap_indexes
import rotkeeper.lib.sitemap_nav_partial as sitemap_nav_partial
import rotkeeper.lib.sitemap_sidecars as sitemap_sidecars
import rotkeeper.lib.assets as assets
import rotkeeper.lib.render as render
import rotkeeper.lib.collect_assets as collect
import rotkeeper.lib.nav as nav  # available for future wiring; not in pipeline yet

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def add_parser(subparsers: argparse.SubParsersAction) -> None:
    parser = subparsers.add_parser("flow", help="Run full Rotkeeper site pipeline")
    parser.add_argument("--force", action="store_true", help="Re-render all files")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--config", type=str, default=None, help="Path to user-config.yaml")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    if ctx is None:
        raise RuntimeError(
            "flow.run() requires an explicit RunContext; ctx must not be None. "
            "Build a RunContext in the caller and pass it here."
        )

    steps: list[tuple[str, Callable[[], int]]] = [
        ("sitemap-collect",     lambda: sitemap_collect.run(args, ctx)),
        ("sitemap-indexes",     lambda: sitemap_indexes.run(args, ctx)),
        ("sitemap-nav-partial", lambda: sitemap_nav_partial.run(args, ctx)),
        ("sitemap-sidecars",    lambda: sitemap_sidecars.run(args, ctx)),
        ("assets",              lambda: assets.run(args, ctx)),
        ("render",              lambda: render.run(args, ctx)),
        ("collect-assets",      lambda: collect.run(args, ctx)),
        # nav step intentionally omitted: nav.py is a standalone tool,
        # not wired into the pipeline until nav.yaml has a consumer.
    ]

    total = len(steps)
    for i, (name, fn) in enumerate(steps, 1):
        print(f"{i}/{total} {name}")
        try:
            rc = fn()
            if rc and rc != 0:
                print(f"FAILED {name} exit {rc}", file=sys.stderr)
                sys.exit(rc)
        except Exception as e:
            print(f"ERROR during {name}: {e}", file=sys.stderr)
            if ctx.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)

    print("Build complete.")
    return 0
