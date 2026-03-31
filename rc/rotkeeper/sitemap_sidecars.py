<!-- START: rc/rotkeeper/lib/sitemap_sidecars.py -->
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

# helper (same as in sitemap_collect)
def parse_nav_token(token: str):
    import re
    match = re.match(r"(\d+)[.\-\s]+(.*)", token)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return 9999, token.strip()

def add_parser(subparsers):
    p = subparsers.add_parser("sitemap-sidecars",
        help="Write .rk.yaml sidecar metadata files next to each .md")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=run)

def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    cfg = ctx.config if (ctx and ctx.config) else CONFIG
    dry_run = getattr(args, "dry_run", False) or getattr(ctx, "dry_run", False)

    sitemap_path = cfg.REPORTS_DIR / "sitemap_pipeline.yaml"
    if not sitemap_path.exists():
        logger.error("sitemap_pipeline.yaml missing – run sitemap-collect first")
        return 1

    data = yaml.safe_load(sitemap_path.read_text(encoding="utf-8"))
    pages = data["pages"]
    tag_index = data["tags"]

    today = datetype.today().isoformat()

    for page in pages:
        source_path = cfg.CONTENT_DIR / page["source"]
        sidecar_path = source_path.with_suffix(".rk.yaml")

        # related pages by tag
        related: list = []
        seen: set = set()
        for tag in page.get("tags", []):
            for candidate in tag_index.get(tag, {}).get("pages", []):
                if candidate["path"] != page["path"] and candidate["path"] not in seen:
                    related.append({
                        "title": candidate["title"],
                        "path": candidate["path"],
                        "description": candidate.get("description", ""),
                    })
                    seen.add(candidate["path"])
                if len(related) >= 5:
                    break
            if len(related) >= 5:
                break

        # breadcrumb
        breadcrumb = []
        for token in page.get("rotkeepernav", []):
            _, label = parse_nav_token(token)
            breadcrumb.append(label)
        breadcrumb.append(page["title"])

        sidecar = {
            "rotkeeper": {
                "generated_at": today,
                "source": page["source"],
                "breadcrumb": breadcrumb,
                "related_pages": related,
                "tag_pages": [
                    {
                        "tag": tag,
                        "url": f"/generated/tags/{re.sub(r'[^\\w-]', '-', tag.lower().strip('-'))}.html",
                    }
                    for tag in page.get("tags", [])
                ],
                "author_page": "/generated/authors/index.html",
            }
        }

        if dry_run:
            logger.info("[dry-run] Would write sidecar %s", sidecar_path)
            continue

        sidecar_path.write_text(
            yaml.dump(sidecar, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        logger.debug("Wrote sidecar %s", sidecar_path)

    logger.info("Sidecar metadata written for %d pages", len(pages))
    return 0
<!-- END: rc/rotkeeper/lib/sitemap_sidecars.py -->