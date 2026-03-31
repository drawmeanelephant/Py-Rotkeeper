#!/usr/bin/env python3
"""
rotkeeper flow — full site build pipeline
Defaults to incremental; pass --force to rebuild everything.
"""
import argparse
import logging
import sys
from pathlib import Path

from rotkeeper.config import CONFIG
from rotkeeper.context import RunContext

# NEW modular sitemap steps
import rotkeeper.lib.sitemap_collect as sitemap_collect
import rotkeeper.lib.sitemap_indexes as sitemap_indexes
import rotkeeper.lib.sitemap_nav_partial as sitemap_nav_partial
import rotkeeper.lib.sitemap_sidecars as sitemap_sidecars

import rotkeeper.lib.assets          as assets
import rotkeeper.lib.render          as render
import rotkeeper.lib.collect_assets  as collect
import rotkeeper.lib.nav             as nav

if not hasattr(nav, 'navcommand'):
    def navcommand(*args, **kwargs):
        pass
    nav.navcommand = navcommand

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def add_parser(subparsers):
    parser = subparsers.add_parser("flow", help="Run full Rotkeeper site pipeline")
    parser.add_argument("--force",   action="store_true", help="Re-render all files")
    parser.add_argument("--dry-run", action="store_true", dest="dryrun")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--config",  type=str, default=None, help="Path to user-config.yaml")
    parser.set_defaults(func=run_flow)

def run_flow(args, ctx):
    steps = [
        ("sitemap-collect",     lambda: sitemap_collect.run(   _ns(dryrun=args.dryrun, verbose=args.verbose), ctx)),
        ("sitemap-indexes",     lambda: sitemap_indexes.run(   _ns(dryrun=args.dryrun, verbose=args.verbose), ctx)),
        ("sitemap-nav-partial", lambda: sitemap_nav_partial.run(_ns(dryrun=args.dryrun, verbose=args.verbose), ctx)),
        ("sitemap-sidecars",    lambda: sitemap_sidecars.run(  _ns(dryrun=args.dryrun, verbose=args.verbose), ctx)),
        ("assets",              lambda: assets.run(            _ns(dryrun=args.dryrun, verbose=args.verbose), ctx)),
        ("render",              lambda: render.run(            _ns(config=None, force=args.force, dryrun=args.dryrun), ctx)),
        ("collect-assets",      lambda: collect.run(           _ns(dryrun=args.dryrun, verbose=args.verbose), ctx)),
        ("nav",                 lambda: nav.navcommand(        _ns(output=None, dryrun=args.dryrun, verbose=args.verbose), ctx)),
    ]

    total = len(steps)
    for i, (name, fn) in enumerate(steps, 1):
        print(f"==> [{i}/{total}] {name}")
        try:
            rc = fn()
            if rc and rc != 0:
                print(f"    FAILED (exit {rc})", file=sys.stderr)
                sys.exit(rc)
        except Exception as e:
            print(f"    ERROR during {name}: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)

    print("==> Build complete.")

def _ns(**kw):
    """Quick argparse.Namespace factory."""
    import argparse
    return argparse.Namespace(**kw)