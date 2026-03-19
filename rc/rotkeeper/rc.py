# rc.py skeleton

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from types import SimpleNamespace
from dataclasses import replace

from .config import CONFIG  # Assuming a CONFIG module exists for configuration
from .context import RunContext
from .lib import get_commands  # Dynamic command discovery from lib
from .lib import sitemap as sitemap_command_module
from .lib import nav as nav_command_module


def _configure_logging(verbose: bool = False, quiet: bool = False, log_file: Path | None = None) -> None:
    """Configure logging based on verbosity, quiet mode, and optional log file."""
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
    """Build the top-level argument parser and register commands dynamically."""
    parser = argparse.ArgumentParser(prog="rotkeeper", description="Rotkeeper CLI")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without making changes",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose debug output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Optional log file path",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to configuration file",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Dynamically register commands from lib, scenario-aware
    for cmd_name, add_parser_func in get_commands():
        add_parser_func(subparsers)

    # Explicitly register sitemap command (temporary until fully integrated into dynamic loader)
    if hasattr(sitemap_command_module, "add_parser"):
        sitemap_command_module.add_parser(subparsers)
        # Add --dry-run and --verbose if missing
        sitemap_parser = None
        for action in subparsers.choices.get("sitemap", [])._actions if "sitemap" in subparsers.choices else []:
            pass
        sitemap_parser = subparsers.choices.get("sitemap")
        if sitemap_parser:
            if not any(a.dest == "dry_run" for a in sitemap_parser._actions):
                sitemap_parser.add_argument(
                    "--dry-run",
                    action="store_true",
                    help="Preview actions without making changes",
                )
            if not any(a.dest == "verbose" for a in sitemap_parser._actions):
                sitemap_parser.add_argument(
                    "--verbose",
                    action="store_true",
                    help="Enable verbose debug output",
                )

            def run(args, ctx):
                from .lib.sitemap import SitemapPipeline
                mutable_ctx = replace(
                    ctx,
                    dry_run=getattr(args, "dry_run", False),
                    verbose=getattr(args, "verbose", False)
                )
                if getattr(mutable_ctx, "verbose", False):
                    import logging
                    logging.basicConfig(level=logging.INFO)
                pipeline = SitemapPipeline(ctx=mutable_ctx)
                pipeline.run()

            sitemap_parser.set_defaults(func=run)

    if hasattr(nav_command_module, "add_parser"):
        nav_command_module.add_parser(subparsers)
        nav_parser = subparsers.choices.get("nav")
        if nav_parser:
            if not any(a.dest == "dry_run" for a in nav_parser._actions):
                nav_parser.add_argument(
                    "--dry-run",
                    action="store_true",
                    help="Preview actions without making changes",
                )
            if not any(a.dest == "verbose" for a in nav_parser._actions):
                nav_parser.add_argument(
                    "--verbose",
                    action="store_true",
                    help="Enable verbose debug output",
                )

            def run(args, ctx):
                from .lib.nav import NavPipeline
                mutable_ctx = replace(
                    ctx,
                    dry_run=getattr(args, "dry_run", False),
                    verbose=getattr(args, "verbose", False)
                )
                if getattr(mutable_ctx, "verbose", False):
                    import logging
                    logging.basicConfig(level=logging.INFO)
                pipeline = NavPipeline(ctx=mutable_ctx)
                pipeline.run()

            nav_parser.set_defaults(func=run)

    # Unified SitemapPipeline CLI registration
    from .lib.sitemap_pipeline import SitemapPipeline as UnifiedSitemapPipeline

    def add_sitemap_pipeline_command(subparsers):
        parser = subparsers.add_parser(
            "sitemap_pipeline",
            help="Collect Markdown pages, build metadata trees, and write sitemap_pipeline.yaml"
        )
        parser.add_argument(
            "--index-only",
            action="store_true",
            help="Collect pages but do not build metadata"
        )
        parser.add_argument(
            "--metadata-only",
            action="store_true",
            help="Build tags/author/date trees only"
        )
        parser.add_argument(
            "--write-only",
            action="store_true",
            help="Write YAML only"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate actions without writing files"
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print detailed logs"
        )

        def run(args, ctx):
            # Extract staged flags locally
            index_only = getattr(args, "index_only", False)
            metadata_only = getattr(args, "metadata_only", False)
            write_only = getattr(args, "write_only", False)

            # Keep RunContext clean (only dry_run and verbose)
            mutable_ctx = replace(
                ctx,
                dry_run=getattr(args, "dry_run", False),
                verbose=getattr(args, "verbose", False)
            )

            if getattr(mutable_ctx, "verbose", False):
                import logging
                logging.basicConfig(level=logging.INFO)

            # Instantiate pipeline
            from .lib.sitemap_pipeline import SitemapPipeline as UnifiedSitemapPipeline
            pipeline = UnifiedSitemapPipeline(ctx=mutable_ctx)

            # Manually assign staged flags to the pipeline
            pipeline.index_only = index_only
            pipeline.metadata_only = metadata_only
            pipeline.write_only = write_only

            # Run the pipeline
            pipeline.run()

        parser.set_defaults(func=run)

    # Register the new command
    add_sitemap_pipeline_command(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Load config if specified
    if args.config:
        CONFIG.load(args.config)

    _configure_logging(verbose=args.verbose, quiet=args.quiet, log_file=args.log_file)

    paths = SimpleNamespace(root_dir=Path.cwd())

    ctx = RunContext(
        paths=paths,
        dry_run=args.dry_run,
        verbose=args.verbose,
        log_file=args.log_file,
        config=CONFIG,
    )

    try:
        # Dispatch to the selected command function
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
