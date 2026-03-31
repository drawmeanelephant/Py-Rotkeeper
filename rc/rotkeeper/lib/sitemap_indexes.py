from __future__ import annotations

import argparse
import logging
import yaml
import re
from pathlib import Path
from datetime import date as datetype

from ..config import CONFIG
from ..context import RunContext

logger = logging.getLogger(__name__)

def add_parser(subparsers):
    p = subparsers.add_parser("sitemap-indexes",
        help="Write generated index pages (tags/authors/dates/sitemap) – respects GENERATE_INDEXES")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=run)

def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    cfg = ctx.config if (ctx and ctx.config) else CONFIG
    if not cfg.GENERATE_INDEXES:
        logger.info("GENERATE_INDEXES=false → skipping index pages (no more generated/ diarrhea)")
        return 0

    sitemap_path = cfg.REPORTS_DIR / "sitemap_pipeline.yaml"
    if not sitemap_path.exists():
        logger.error("sitemap_pipeline.yaml missing – run sitemap-collect first")
        return 1

    data = yaml.safe_load(sitemap_path.read_text(encoding="utf-8"))
    pages = data["pages"]
    metadata = {k: data[k] for k in ["tags", "authors", "dates", "rotkeepernav"]}

    generated_dir = cfg.GENERATED_CONTENT_DIR
    if getattr(args, "dry_run", False) or getattr(ctx, "dry_run", False):
        logger.info("[dry-run] Would write index pages to %s", generated_dir)
        return 0

    generated_dir.mkdir(parents=True, exist_ok=True)
    today = datetype.today().isoformat()

    def write(rel: str, fm: dict, body_lines: list[str]):
        path = generated_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        fm.setdefault("generated_by", "rotkeeper/sitemap-indexes")
        fm.setdefault("generated_at", today)
        fm.setdefault("show_in_nav", False)
        header = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
        content = f"---\n{header}\n---\n" + "\n".join(body_lines)
        path.write_text(content, encoding="utf-8")
        logger.info("Wrote index page %s", path)

    # tags/index + per-tag pages
    tag_lines = ["# Tags\n"]
    for tag, data in sorted(metadata["tags"].items()):
        tag_lines.append(f"## {tag}")
        for page in data["pages"]:
            tag_lines.append(f"- {page['title']}")
        tag_lines.append("")
    write("tags/index.md", {"title": "Tags"}, tag_lines)

    for tag, data in sorted(metadata["tags"].items()):
        slug = re.sub(r"[^\w-]", "-", tag.lower().strip("-"))
        lines = [f"# {tag}\n"]
        for page in data["pages"]:
            desc = page.get("description", "")
            entry = f"- {page['title']}"
            if desc:
                entry += f"\n  {desc}"
            lines.append(entry)
        write(f"tags/{slug}.md", {"title": f"Tag: {tag}"}, lines)

    # authors, dates, sitemap
    author_lines = ["# Authors\n"]
    for author, data in sorted(metadata["authors"].items()):
        author_lines.append(f"## {author}")
        for page in data["pages"]:
            author_lines.append(f"- {page['title']}")
        author_lines.append("")
    write("authors/index.md", {"title": "Authors"}, author_lines)

    date_lines = ["# By Date\n"]
    for dt, data in sorted(metadata["dates"].items(), reverse=True):
        date_lines.append(f"## {dt}")
        for page in data["pages"]:
            date_lines.append(f"- {page['title']}")
        date_lines.append("")
    write("dates/index.md", {"title": "By Date"}, date_lines)

    sitemap_lines = ["# Sitemap\n"]
    for page in pages:
        sitemap_lines.append(f"- {page['title']}")
    write("sitemap.md", {"title": "Sitemap"}, sitemap_lines)

    logger.info("Index pages written to %s", generated_dir)
    return 0