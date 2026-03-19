from __future__ import annotations

import argparse
import logging

from ..context import RunContext
from ..config import CONFIG


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("book", help="Bind reports/books (stub)")
    p.add_argument(
        "--mode",
        type=str,
        default="all",
        choices=[
            "all",
            "scriptbook-full",
            "docbook",
            "docbook-clean",
            "configbook",
            "contentbook",
            "contentmeta",
            "collapse",
        ],
        help="Which book/report to generate (stub)",
    )
    p.add_argument("--dry-run", action="store_true", help="(Alias) show what would be done")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    logging.info("book (stub)")
    effective_dry = bool(getattr(args, "dry_run", False)) or (ctx.dry_run if ctx else False)
    logging.debug("mode=%s dry_run=%s reports_dir=%s", args.mode, effective_dry, CONFIG.BONES / "reports")
    return 0
