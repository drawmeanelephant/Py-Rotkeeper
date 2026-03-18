from __future__ import annotations

import argparse
import logging
from pathlib import Path
import yaml
import frontmatter
import re

from ..config import CONFIG

logger = logging.getLogger("rotkeeper.commands.sitemap")


def _parse_nav_token(token: str):
    """01_Docs → (1, 'Docs'). No prefix → (9999, token)"""
    match = re.match(r"^(\d+)[_\- ]+(.*)$", token)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return 9999, token.strip()


class SitemapPipeline:
    def __init__(self, ctx=None):
        self.ctx = ctx
        config = ctx.config if ctx else CONFIG
        self.content_dir = config.CONTENT_DIR
        self.reports_dir = config.BONES / "reports"
        self.pages: list[dict] = []
        self.dry_run = getattr(ctx, "dry_run", False) if ctx else False
        self.verbose = getattr(ctx, "verbose", False) if ctx else False

    def collect_pages(self):
        pages = []
        skipped = 0

        for path in self.content_dir.rglob("*.md"):
            rel_path = path.relative_to(self.content_dir)

            # Skip _files or hidden dirs
            if rel_path.name.startswith("_") or any(p.startswith(".") for p in rel_path.parts):
                skipped += 1
                continue

            try:
                post = frontmatter.load(path)
            except Exception as exc:
                logger.warning("[sitemap] Failed to load frontmatter from %s: %s", path, exc)
                skipped += 1
                continue

            # Skip drafts or unpublished
            if post.get("draft", False) or not post.get("published", True):
                skipped += 1
                continue

            html_path = rel_path.with_suffix(".html").as_posix()
            title = post.get("title") or rel_path.stem
            keywords = post.get("keywords", []) or []
            tags = post.get("tags", []) or []
            rotkeeper_nav = post.get("rotkeeper_nav", []) or []
            show_in_nav = post.get("show_in_nav", True)
            author = post.get("author", "rotkeeper")
            date = post.get("date")

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

        # Sort pages by rotkeeper_nav numeric prefix; fallback to title
        def nav_sort_key(nav_list, title):
            key = []
            for item in nav_list:
                match = re.match(r'^(\d+)[_\- ]+(.*)$', item)
                if match:
                    key.append((int(match.group(1)), match.group(2).lower()))
                else:
                    key.append((float('inf'), item.lower()))
            key.append((float('inf'), title.lower()))
            return tuple(key)

        pages.sort(key=lambda p: nav_sort_key(p.get("rotkeeper_nav", []), p["title"]))

        logger.info(f"[sitemap] Collected {len(pages)} pages, skipped {skipped}")
        self.pages = pages
        return pages

    def build_nav(self, pages=None):
        if pages is None:
            pages = self.pages
        root = {}
        for page in pages:
            if not page.get("show_in_nav", True):
                continue
            nav_path = page.get("rotkeeper_nav") or []
            if not nav_path:
                continue

            current = root
            for i, raw_token in enumerate(nav_path):
                order, label = _parse_nav_token(raw_token)
                if label not in current:
                    current[label] = {"_order": order, "_children": {}, "_page": None}
                node = current[label]
                if i == len(nav_path) - 1:
                    node["_page"] = page["path"]
                current = node["_children"]

        return self._sort_nav(root)

    def _sort_nav(self, node):
        if not node:
            return {}
        sorted_items = sorted(node.items(), key=lambda x: x[1]["_order"])
        result = {}
        for label, data in sorted_items:
            result[label] = {
                "page": data["_page"],
                "children": self._sort_nav(data["_children"]),
            }
        return result

    def write_yaml(self, path: Path, data: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    def run(self):
        pages = self.collect_pages()

        sitemap_path = self.reports_dir / "sitemap.yaml"

        if self.dry_run:
            logger.info(f"[dry-run] Would write sitemap.yaml to {self.reports_dir}")
            return

        self.write_yaml(sitemap_path, {"pages": pages})
        logger.info(f"Wrote sitemap.yaml → {sitemap_path}")


# ---------------------- CLI integration ----------------------
def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("sitemap", help="Generate sitemap.yaml + nav.yaml")
    p.add_argument("--dry-run", action="store_true", help="Do not write files, just log actions")
    p.set_defaults(func=run_command)


from dataclasses import replace

def run_command(args: argparse.Namespace, ctx=None) -> int:
    if ctx:
        ctx = replace(
            ctx,
            dry_run=getattr(args, "dry_run", False),
            verbose=getattr(args, "verbose", False),
        )
    pipeline = SitemapPipeline(ctx=ctx)
    pipeline.run()
    return 0
