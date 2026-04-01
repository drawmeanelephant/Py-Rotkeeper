from __future__ import annotations

import argparse
import logging

from ..context import RunContext


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("cleanup-bones", help="Backup and prune bones/ (stub)")
    p.add_argument("--days",  type=int, default=30, help="Retention window in days (stub)")
    p.add_argument("--yes",   action="store_true",  help="Skip confirmation (stub)")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")
    logging.info("cleanup-bones (stub)")
    logging.debug("days=%s yes=%s", args.days, args.yes)
    return 0
