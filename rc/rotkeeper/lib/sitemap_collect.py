from __future__ import annotations

import argparse
import logging
import yaml
from pathlib import Path
import re
from datetime import date as datetype

from ..config import CONFIG
from ..context import RunContext

logger = logging.getLogger(__name__)

# ── tiny helpers (extracted from old sitemap_pipeline.py) ─────────────────────
def parse_nav_token(token: str):
    match = re.match(r"(\d+)[.\-\s]+(.*)", token)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return 9999, token.strip()

def sort_nav_tree(node: dict) -> None:
    if "pages" in node:
        node["pages"].sort(key=lambda p: p.get("title", ""))
    children = node.get("children", {})
    if children:
        sorted_items = sorted(children.items(), key=lambda item: parse_nav_token(item[0]))
        node["children"] = {k: v for k, v in sorted_items}
        for child in node["children"].values():
            sort_nav_tree(child)

def coerce_date(val) -> str | None:
    if val is None:
        return None
    if isinstance(val, datetype):
        return val.isoformat()
    return str(val) or None

def add_parser(subparsers):
    p = subparsers.add_parser("sitemap-collect",
        help="Collect pages + build metadata + write sitemap_pipeline.yaml")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=run)

def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    cfg = ctx.config if (ctx and ctx.config) else CONFIG
    dry_run = getattr(args, "dry_run", False) or getattr(ctx, "dry_run", False)
    verbose = getattr(args, "verbose", False) or getattr(ctx, "verbose", False)
    if verbose:
        logger.setLevel(logging.DEBUG)

    # collect_pages
    pages = []
    skipped = 0
    content_dir = cfg.CONTENT_DIR
    if not content_dir.exists() or not content_dir.is_dir():
        logger.warning("content directory not found at %s", content_dir)
        return 0

    for md in sorted(content_dir.rglob("*.md")):
        relpath = md.relative_to(content_dir)
        if relpath.name.startswith("_") or any(p.startswith(".") for p in relpath.parts):
            skipped += 1
            continue
        try:
            import frontmatter
            post = frontmatter.load(md)
        except Exception as e:
            logger.warning("Failed to load frontmatter from %s: %s", md, e)
            skipped += 1
            continue
        if post.get("draft", False) or not post.get("published", True):
            skipped += 1
            continue
        page_data = {
            "title":        post.get("title", relpath.stem),
            "path":         relpath.with_suffix(".html").as_posix(),
            "source":       relpath.as_posix(),
            "author":       post.get("author", "Misc"),
            "tags":         post.get("tags", []) or [],
            "keywords":     post.get("keywords", []) or [],
            "date":         coerce_date(post.get("date")),
            "rotkeepernav": post.get("rotkeepernav", []) or [],
            "show_in_nav":  post.get("show_in_nav", True),
            "description":  post.get("description", ""),
        }
        if any(p["path"] == page_data["path"] for p in pages):
            logger.warning("Duplicate output path skipped: %s", page_data["path"])
            skipped += 1
            continue
        pages.append(page_data)

    logger.info("Collected %d pages, skipped %d", len(pages), skipped)

    # build_metadata_trees
    metadata = {"tags": {}, "authors": {}, "dates": {}, "rotkeepernav": {}}
    for page in pages:
        author = page["author"]
        metadata["authors"].setdefault(author, {"pages": []})
        metadata["authors"][author]["pages"].append(page)
        for tag in page.get("tags", []):
            metadata["tags"].setdefault(tag, {"pages": []})
            metadata["tags"][tag]["pages"].append(page)
        date = page.get("date") or "Misc"
        metadata["dates"].setdefault(date, {"pages": []})
        metadata["dates"][date]["pages"].append(page)
        if not page.get("show_in_nav", True):
            continue
        current = metadata["rotkeepernav"]
        tokens = page.get("rotkeepernav") or ["Misc"]
        for token in tokens:
            _, label = parse_nav_token(token)
            current.setdefault(label, {"children": {}, "pages": []})
            current = current[label]["children"]
        current.setdefault("pages", []).append(page)
    sort_nav_tree(metadata["rotkeepernav"])

    if dry_run:
        logger.info("[dry-run] would write sitemap_pipeline.yaml")
        return 0

    reports_dir = cfg.REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "pages": pages,
        "tags": metadata["tags"],
        "authors": metadata["authors"],
        "dates": metadata["dates"],
        "rotkeepernav": metadata["rotkeepernav"],
    }
    (reports_dir / "sitemap_pipeline.yaml").write_text(
        yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    logger.info("Wrote sitemap_pipeline.yaml")
    return 0