from __future__ import annotations

import argparse
import logging

from ..context import RunContext


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("reseed", help="Reconstruct files from bound books (stub)")
    p.add_argument("--input",  type=str,          default=None,  help="Input markdown file (stub)")
    p.add_argument("--all",    action="store_true",               help="Reseed from all known books (stub)")
    p.add_argument("--force",  action="store_true",               help="Allow overwriting files (stub)")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")
    logging.info("reseed (stub)")
    logging.debug("input=%s all=%s force=%s", args.input, getattr(args, "all", False), args.force)
    return 0
