from __future__ import annotations

import argparse
import logging
from pathlib import Path

import yaml

from ..context import RunContext


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("sitemap", help="Generate site index/sitemap (stub)")
    p.add_argument("--output", type=str, default=None, help="Output path (stub)")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext) -> int:
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else ctx.paths.reports_dir / "sitemap.yaml"
    )

    content_dir = ctx.paths.content_dir
    pages: list[str] = []
    skipped = 0

    if not content_dir.exists() or not content_dir.is_dir():
        logging.info("[sitemap] No content directory found at %s", content_dir)
        logging.info("[sitemap] Skipped %d markdown files", skipped)
    else:
        for src in content_dir.rglob("*.md"):
            if src.is_file():
                rel_path = src.relative_to(content_dir)
                if rel_path.name.startswith("_"):
                    skipped += 1
                    continue
                if any(part.startswith(".") for part in rel_path.parts):
                    skipped += 1
                    continue
                rel = rel_path.as_posix()
                pages.append(rel)
        pages.sort()
        logging.info(
            "[sitemap] Found %d markdown files under %s",
            len(pages),
            content_dir,
        )
        logging.info("[sitemap] Skipped %d markdown files", skipped)

    report_obj = {"pages": pages}

    if ctx.dry_run:
        logging.info("[sitemap] Would write sitemap (dry-run) to %s", output_path)
        return 0

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            yaml.safe_dump(report_obj, sort_keys=False),
            encoding="utf-8",
        )
    except OSError as exc:
        logging.error("[sitemap] Failed to write sitemap: %s", exc)
        return 1
    logging.info("[sitemap] Wrote sitemap: %s", output_path)
    return 0
