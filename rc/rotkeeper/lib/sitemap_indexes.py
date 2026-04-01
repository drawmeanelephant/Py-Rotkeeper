from __future__ import annotations

import argparse
import logging
import yaml
from datetime import date as datetype
from pathlib import Path

from ..config  import CONFIG
from ..context import RunContext

logger = logging.getLogger(__name__)


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "sitemap-indexes",
        help="Write generated index pages — respects GENERATE_INDEXES",
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    cfg     = ctx.config if (ctx is not None and ctx.config is not None) else CONFIG
    dry_run = ctx.dry_run if ctx is not None else False

    if not cfg.GENERATE_INDEXES:
        logger.info("GENERATE_INDEXES=false → skipping index pages")
        return 0

    sitemap_path = cfg.REPORTS_DIR / "sitemap_pipeline.yaml"
    if not sitemap_path.exists():
        logger.error("sitemap_pipeline.yaml missing — run sitemap-collect first")
        return 1

    data          = yaml.safe_load(sitemap_path.read_text(encoding="utf-8"))
    tag_meta      = data.get("tags", {})
    author_meta   = data.get("authors", {})
    generated_dir = cfg.GENERATED_CONTENT_DIR

    if dry_run:
        logger.info("[dry-run] Would write index pages to %s", generated_dir)
        return 0

    generated_dir.mkdir(parents=True, exist_ok=True)
    today = datetype.today().isoformat()

    def write(rel: str, fm: dict, bodylines: list[str]) -> None:
        path = generated_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        fm.setdefault("generated_by", "rotkeeper/sitemap-indexes")
        fm.setdefault("generated_at", today)
        fm.setdefault("show_in_nav",  False)
        fm.setdefault("published",    True)
        header  = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
        content = f"---\n{header}\n---\n" + "".join(bodylines)
        path.write_text(content, encoding="utf-8")
        logger.info("Wrote index page %s", path)

    for tag, tag_data in tag_meta.items():
        tag_pages = tag_data.get("pages", [])
        lines = [f"- [{p['title']}](/{p['path']})\n" for p in tag_pages]
        write(f"tags/{tag}.md", {"title": f"Tag: {tag}", "tag": tag}, lines)

    for author, auth_data in author_meta.items():
        auth_pages = auth_data.get("pages", [])
        lines = [f"- [{p['title']}](/{p['path']})\n" for p in auth_pages]
        write(f"authors/{author}.md", {"title": f"Author: {author}", "author": author}, lines)

    return 0