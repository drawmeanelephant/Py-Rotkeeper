from __future__ import annotations

import argparse
import logging
import re
import yaml
from datetime import date as datetype
from pathlib import Path

from ..config  import CONFIG
from ..context import RunContext

logger = logging.getLogger(__name__)


def _parse_nav_token(token: str) -> tuple[int, str]:
    match = re.match(r"(\d+)[\.\-\s]+(.*)", token)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return 9999, token.strip()


def _coerce_date(val) -> str | None:
    if val is None:
        return None
    if isinstance(val, datetype):
        return val.isoformat()
    return str(val) or None


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "sitemap-collect",
        help="Collect pages + build metadata + write sitemap_pipeline.yaml",
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    cfg     = ctx.config if (ctx is not None and ctx.config is not None) else CONFIG
    dry_run = ctx.dry_run if ctx is not None else False
    verbose = ctx.verbose if ctx is not None else False

    if verbose:
        logger.setLevel(logging.DEBUG)

    content_dir = cfg.CONTENT_DIR
    if not content_dir.exists() or not content_dir.is_dir():
        logger.warning("content directory not found at %s", content_dir)
        return 0

    pages: list[dict] = []
    skipped = 0

    for md in sorted(content_dir.rglob("*.md")):
        relpath = md.relative_to(content_dir)
        if relpath.name.startswith("_") or any(p.startswith(".") for p in relpath.parts):
            skipped += 1
            continue
        try:
            import frontmatter as fm_lib
            post = fm_lib.load(md)
        except Exception as e:
            logger.warning("Failed to load frontmatter from %s: %s", md, e)
            skipped += 1
            continue
        if post.get("draft", False) or not post.get("published", True):
            skipped += 1
            continue
        page_data = {
            "title":         post.get("title", relpath.stem),
            "path":          relpath.with_suffix(".html").as_posix(),
            "source":        relpath.as_posix(),
            "author":        post.get("author", "Misc"),
            "tags":          post.get("tags", []) or [],
            "keywords":      post.get("keywords", []) or [],
            "date":          _coerce_date(post.get("date")),
            "rotkeeper_nav": post.get("rotkeeper_nav", []) or [],
            "show_in_nav":   post.get("show_in_nav", True),
            "description":   post.get("description", ""),
        }
        if any(p["path"] == page_data["path"] for p in pages):
            logger.warning("Duplicate output path skipped: %s", page_data["path"])
            skipped += 1
            continue
        pages.append(page_data)

    logger.info("Collected %d pages, skipped %d", len(pages), skipped)

    metadata: dict = {"tags": {}, "authors": {}, "dates": {}, "rotkeeper_nav": {}}
    for page in pages:
        author = page["author"]
        metadata["authors"].setdefault(author, {"pages": []})["pages"].append(page)
        for tag in page.get("tags", []):
            metadata["tags"].setdefault(tag, {"pages": []})["pages"].append(page)
        d = page.get("date") or "Misc"
        metadata["dates"].setdefault(d, {"pages": []})["pages"].append(page)

    if dry_run:
        logger.info("[dry-run] would write sitemap_pipeline.yaml")
        return 0

    reports_dir = cfg.REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    data = {"pages": pages, **metadata}
    (reports_dir / "sitemap_pipeline.yaml").write_text(
        yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    logger.info("Wrote sitemap_pipeline.yaml (%d pages)", len(pages))
    return 0