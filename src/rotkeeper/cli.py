from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

from . import __version__
from .context import RunContext
from .paths import Paths, RootNotFoundError, discover_root


def _configure_logging(*, verbose: bool, quiet: bool, log_file: Path | None) -> None:
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(level=level, handlers=handlers, format="%(asctime)s %(levelname)-7s %(message)s")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rotkeeper", description="Rotkeeper (Python rewrite)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--root", type=Path, default=None, help="Project root directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing/executing")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress non-error output")
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Optional log file path (defaults to stderr only)",
    )

    subs = parser.add_subparsers(dest="command", required=True)

    from .commands.assets import add_parser as add_assets
    from .commands.book import add_parser as add_book
    from .commands.cleanup_bones import add_parser as add_cleanup_bones
    from .commands.collect_assets import add_parser as add_collect_assets
    from .commands.init import add_parser as add_init
    from .commands.render import add_parser as add_render
    from .commands.reseed import add_parser as add_reseed
    from .commands.sitemap import add_parser as add_sitemap
    from .commands.nav import add_nav

    add_init(subs)
    add_render(subs)
    add_assets(subs)
    add_collect_assets(subs)
    add_book(subs)
    add_reseed(subs)
    add_sitemap(subs)
    add_cleanup_bones(subs)
    add_nav(subs)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    log_file = args.log_file.expanduser().resolve() if args.log_file else None
    _configure_logging(verbose=bool(args.verbose), quiet=bool(args.quiet), log_file=log_file)

    try:
        root_dir = discover_root(args.root)
    except RootNotFoundError as e:
        logging.error(str(e))
        return 2

    start_time = time.perf_counter()
    ctx = RunContext(
        paths=Paths.from_root(root_dir),
        dry_run=bool(args.dry_run),
        verbose=bool(args.verbose),
        log_file=log_file,
    )

    try:
        result = args.func(args, ctx)

        duration = time.perf_counter() - start_time
        logging.info("Completed in %.2fs", duration)

        return int(result) if result is not None else 0

    except KeyboardInterrupt:
        logging.error("Interrupted.")
        return 130

    except Exception as e:
        duration = time.perf_counter() - start_time
        logging.error(str(e))
        logging.debug("Command failed after %.2fs", duration)
        if args.verbose:
            raise
        return 1
