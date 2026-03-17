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
    pages: list[dict[str, object]] = []
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
                try:
                    text = src.read_text(encoding="utf-8")
                except OSError as exc:
                    logging.warning("[sitemap] Failed to read file %s: %s", src, exc)
                    skipped += 1
                    continue
                frontmatter = {}
                if text.startswith("---"):
                    parts = text.split("---", 2)
                    if len(parts) >= 3:
                        try:
                            frontmatter = yaml.safe_load(parts[1]) or {}
                        except yaml.YAMLError as exc:
                            logging.warning("[sitemap] Failed to parse frontmatter in %s: %s", src, exc)
                            frontmatter = {}
                if frontmatter.get("draft", False) is True or frontmatter.get("published", True) is False:
                    skipped += 1
                    continue
                title = frontmatter.get("title")
                if not title:
                    title = rel_path.stem
                keywords = frontmatter.get("keywords", [])
                if not isinstance(keywords, list):
                    keywords = []
                show_in_nav = frontmatter.get("show_in_nav", True)
                html_path = rel_path.with_suffix(".html").as_posix()

                # Extract frontmatter fields with defaults if missing
                author = frontmatter.get("author", "rotkeeper")
                date = frontmatter.get("date")
                tags = frontmatter.get("tags", [])
                if not isinstance(tags, list):
                    tags = []
                rotkeeper_nav = frontmatter.get("rotkeeper_nav", [])
                if not isinstance(rotkeeper_nav, list):
                    rotkeeper_nav = []

                # Add the page entry to pages list
                pages.append({
                    "path": html_path,
                    "title": title,
                    "author": author,
                    "date": date,
                    "keywords": keywords,
                    "tags": tags,
                    "rotkeeper_nav": rotkeeper_nav,
                    "show_in_nav": show_in_nav,
                })

        # Sort pages by rotkeeper_nav with numeric prefixes; fallback to alphabetical
        import re
        def nav_sort_key(nav_list, title):
            key = []
            for item in nav_list:
                match = re.match(r'^(\d+)_+(.*)$', item)
                if match:
                    key.append((int(match.group(1)), match.group(2).lower()))
                else:
                    key.append((float('inf'), item.lower()))
            key.append((float('inf'), title.lower()))
            return tuple(key)

        pages.sort(key=lambda p: nav_sort_key(p.get("rotkeeper_nav", []), p["title"]))

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
