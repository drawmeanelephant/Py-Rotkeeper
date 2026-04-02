from __future__ import annotations
import argparse
import logging
import re
import yaml
from datetime import date as date_type
from pathlib import Path
from ..config import CONFIG
from ..context import RunContext
from .page import Page

logger = logging.getLogger(__name__)


def parse_nav_token(token: str) -> tuple[int, str]:
    match = re.match(r"^(\d+)[.\-_\s](.*)", token)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return 9999, token.strip()


def coerce_date(val) -> str | None:
    if val is None:
        return None
    if isinstance(val, date_type):
        return val.isoformat()
    return str(val) or None


def add_parser(subparsers: argparse.SubParsersAction) -> None:
    p = subparsers.add_parser("sitemap-collect", help="Collect pages, build metadata, write sitemappipeline.yaml")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    cfg = ctx.config if ctx is not None and ctx.config is not None else CONFIG
    dry_run = getattr(args, "dry_run", False)
    verbose = getattr(args, "verbose", False)
    if ctx is not None:
        dry_run = ctx.dry_run or dry_run
        verbose = ctx.verbose or verbose
    if verbose:
        logger.setLevel(logging.DEBUG)

    content_dir = cfg.CONTENT_DIR
    if not content_dir.exists() or not content_dir.is_dir():
        logger.warning("content directory not found at %s", content_dir)
        return 0

    pages: list[Page] = []
    skipped = 0

    for md in sorted(content_dir.rglob("*.md")):
        rel_path = md.relative_to(content_dir)
        if rel_path.name.startswith("_") or any(p.startswith(".") for p in rel_path.parts):
            skipped += 1
            continue
        try:
            import frontmatter as fmlib
            post = fmlib.load(md)
        except Exception as e:
            logger.warning("Failed to load frontmatter from %s: %s", md, e)
            skipped += 1
            continue

        if post.get("draft", False) or not post.get("published", True):
            skipped += 1
            continue

        page = Page(
            title=post.get("title", rel_path.stem),
            path=str(rel_path.with_suffix(".html").as_posix()),
            source=str(rel_path.as_posix()),
            author=post.get("author", "Misc"),
            date=coerce_date(post.get("date")),
            tags=post.get("tags") or [],
            keywords=post.get("keywords") or [],
            rotkeeper_nav=post.get("rotkeeper_nav") or [],
            show_in_nav=post.get("show_in_nav", True),
            description=post.get("description", ""),
        )

        if any(p.path == page.path for p in pages):
            logger.warning("Duplicate output path, skipped: %s", page.path)
            skipped += 1
            continue

        pages.append(page)

    logger.info("Collected %d pages, skipped %d", len(pages), skipped)

    metadata: dict = {"tags": {}, "authors": {}, "dates": {}, "rotkeeper_nav": {}}
    for page in pages:
        author = page.author
        metadata["authors"].setdefault(author, {"pages": []})
        metadata["authors"][author]["pages"].append(page.to_dict())
        for tag in page.tags:
            metadata["tags"].setdefault(tag, {"pages": []})
            metadata["tags"][tag]["pages"].append(page.to_dict())
        d = page.date or "Misc"
        metadata["dates"].setdefault(d, {"pages": []})
        metadata["dates"][d]["pages"].append(page.to_dict())

    if dry_run:
        logger.info("dry-run: would write sitemappipeline.yaml")
        return 0

    reports_dir = cfg.REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    data = {"pages": [p.to_dict() for p in pages], "metadata": metadata}
    (reports_dir / "sitemappipeline.yaml").write_text(
        yaml.dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    logger.info("Wrote sitemappipeline.yaml (%d pages)", len(pages))
    return 0
