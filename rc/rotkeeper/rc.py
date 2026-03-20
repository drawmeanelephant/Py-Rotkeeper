# rc/rc.py
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from dataclasses import replace

from .config import CONFIG
from .context import RunContext
from .lib import get_commands


def _configure_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_file: Path | None = None,
) -> None:
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(message)s",
        handlers=handlers,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rotkeeper", description="Rotkeeper CLI")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without making changes")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress non-error output")
    parser.add_argument("--log-file", type=Path, default=None, help="Optional log file path")
    parser.add_argument("--config", type=Path, default=None, help="Path to configuration file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Dynamic discovery — lib modules expose add_parser(subparsers).
    # sitemap, nav, render, sitemap-pipeline are all discovered here;
    # no manual re-registration needed.
    for _cmd_name, add_parser_func in get_commands():
        add_parser_func(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.config:
        CONFIG.load(args.config)

    _configure_logging(
        verbose=args.verbose,
        quiet=args.quiet,
        log_file=args.log_file,
    )

    ctx = RunContext(
        dry_run=args.dry_run,
        verbose=args.verbose,
        log_file=args.log_file,
        config=CONFIG,
    )

    try:
        return args.func(args, ctx) or 0
    except KeyboardInterrupt:
        logging.error("Execution interrupted by user.")
        return 130
    except Exception as exc:
        if args.verbose:
            logging.exception("An unexpected error occurred:")
        else:
            logging.error("Error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
