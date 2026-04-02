from __future__ import annotations
import argparse
import logging
import re
import yaml
from datetime import date as date_type
from pathlib import Path
from ..config import CONFIG
from ..context import RunContext

logger = logging.getLogger(__name__)


def parse_nav_token(token: str) -> tuple[int, str]:
    match = re.match(r"^(\d+)[.\-_\s](.*)", token)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return 9999, token.strip()


def write_sidecar(path: Path, rotkeeper_data: dict, dry_run: bool) -> None:
    """Write or merge-update a .rk.yaml sidecar. Never overwrites non-rotkeeper keys."""
    existing = {}
    if path.exists():
        try:
            existing = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            logger.warning("Could not read existing sidecar %s: %s", path, exc)
            existing = {}
    merged = {**existing, "rotkeeper": rotkeeper_data}
    if dry_run:
        logger.info("dry-run would write sidecar %s", path)
        return
    path.write_text(yaml.dump(merged, sort_keys=False, allow_unicode=True), encoding="utf-8")
    logger.debug("Wrote sidecar %s", path)


def add_parser(subparsers: argparse.SubParsersAction) -> None:
    p = subparsers.add_parser("sitemap-sidecars", help="Write .rk.yaml sidecar metadata files next to each .md")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    cfg = ctx.config if ctx is not None and ctx.config is not None else CONFIG
    dry_run = getattr(args, "dry_run", False)
    if ctx is not None:
        dry_run = ctx.dry_run or dry_run

    sitemap_path = cfg.REPORTS_DIR / "sitemappipeline.yaml"
    if not sitemap_path.exists():
        logger.error("sitemappipeline.yaml missing — run sitemap-collect first")
        return 1

    data = yaml.safe_load(sitemap_path.read_text(encoding="utf-8"))
    pages = data["pages"]
    tag_index = data.get("metadata", {}).get("tags", {})
    today = date_type.today().isoformat()

    for page in pages:
        page_source = page["source"]
        page_path = page["path"]
        page_title = page.get("title", "")
        source_path = cfg.CONTENT_DIR / page_source
        sidecar_path = source_path.with_suffix(".rk.yaml")

        related: list[dict] = []
        seen: set[str] = set()
        for tag in page.get("tags", []):
            for candidate in tag_index.get(tag, {}).get("pages", []):
                if candidate["path"] != page_path and candidate["path"] not in seen:
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

        breadcrumb: list[str] = []
        for token in page.get("rotkeeper_nav", []):
            _, label = parse_nav_token(token)
            breadcrumb.append(label)
        breadcrumb.append(page_title)

        rotkeeper_data = {
            "generated_at": today,
            "source": page_source,
            "breadcrumb": breadcrumb,
            "related_pages": related,
            "tag_pages": [
                {
                    "tag": tag,
                    "url": f"generated/tags/{re.sub(r'[^a-z0-9-]', '-', tag.lower().strip('-'))}.html",
                }
                for tag in page.get("tags", [])
            ],
            "author_page": "generated/authors/index.html",
        }

        write_sidecar(sidecar_path, rotkeeper_data, dry_run)

    logger.info("Sidecar metadata written for %d pages", len(pages))
    return 0
