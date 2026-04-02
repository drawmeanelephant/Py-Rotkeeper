from __future__ import annotations
import argparse
import logging
import re
from pathlib import Path
import yaml
from ..config import CONFIG
from .page import Page

logger = logging.getLogger(__name__)


def parse_nav_label(label):
    """Parse a label to extract numeric prefix for sorting."""
    if label is None:
        return float("inf"), ""
    match = re.match(r"^(\d+)[.\-_\s](.*)", label)
    if match:
        return int(match.group(1)), match.group(2).strip().lower()
    return float("inf"), label.lower()


def run(args, ctx=None):
    cfg = ctx.config if ctx is not None and ctx.config is not None else CONFIG

    sitemap_path = cfg.BONES / "reports" / "sitemappipeline.yaml"
    if not sitemap_path.exists():
        logger.error("Sitemap file not found at %s", sitemap_path)
        logger.error("Run rotkeeper sitemap-pipeline first to generate it.")
        return 1

    try:
        with sitemap_path.open("r", encoding="utf-8") as f:
            sitemap = yaml.safe_load(f)
    except Exception as e:
        logger.error("Failed to load sitemappipeline.yaml: %s", e)
        return 1

    if isinstance(sitemap, dict) and "pages" in sitemap:
        pages_list = sitemap["pages"]
    elif isinstance(sitemap, list):
        pages_list = sitemap
    else:
        logger.error("sitemappipeline.yaml structure not recognized")
        return 1

    # Construct Page objects via Page.from_dict()
    pages = []
    for p in pages_list:
        if not isinstance(p, dict):
            continue
        page = Page.from_dict(p)
        if not page.show_in_nav:
            continue
        nav_path = page.rotkeeper_nav
        if not isinstance(nav_path, list) or not nav_path:
            nav_path = ["Misc"]
        else:
            nav_path = [str(item) for item in nav_path]
        pages.append((page, nav_path))

    # Build nav tree using typed fields
    metadata_groups = ["author", "date", "tags", "keywords", "rotkeeper_nav"]
    nav_tree = {key: {} for key in metadata_groups}

    for page, rot_nav in pages:
        author = page.author or "Misc"
        date = page.date or "Misc"
        tags = page.tags or ["Misc"]
        keywords = page.keywords or ["Misc"]

        nav_tree["author"].setdefault(author, {"pages": []})
        nav_tree["author"][author]["pages"].append(page)

        for tag in tags:
            nav_tree["tags"].setdefault(tag, {"pages": []})
            nav_tree["tags"][tag]["pages"].append(page)

        for kw in keywords:
            nav_tree["keywords"].setdefault(kw, {"pages": []})
            nav_tree["keywords"][kw]["pages"].append(page)

        current = nav_tree["rotkeeper_nav"]
        for part in rot_nav:
            if part not in current or not isinstance(current.get(part), dict):
                current[part] = {"children": {}, "pages": []}
            current = current[part]["children"]
        current.setdefault("pages", []).append(page)

        try:
            from datetime import datetime
            dt = datetime.fromisoformat(str(date))
            year, month, day = str(dt.year), f"{dt.month:02}", f"{dt.day:02}"
        except Exception:
            year = month = day = "Misc"
        nav_tree["date"].setdefault(year, {}).setdefault(month, {}).setdefault(day, {"pages": []})
        nav_tree["date"][year][month][day]["pages"].append(page)

    def convert_rot_nav_tree(tree) -> list:
        nav_list = []
        for orig_key, group_dict in sorted(tree.items(), key=lambda x: parse_nav_label(x[0])):
            if orig_key in ("pages", "children") or not isinstance(group_dict, dict):
                continue
            display = re.sub(r"^\d+[.\-_\s]", "", orig_key).strip() if orig_key else "Misc"
            entry = {"group": display, "pages": []}
            children = convert_rot_nav_tree(group_dict.get("children", {}))
            if children:
                entry["pages"].extend(children)
            for p in group_dict.get("pages", []):
                if isinstance(p, Page):
                    page_data = p.to_dict()
                else:
                    page_data = {k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")}
                entry["pages"].append(page_data)
            nav_list.append(entry)
        return nav_list

    def pages_to_dicts(page_list):
        out = []
        for p in page_list:
            if isinstance(p, Page):
                out.append(p.to_dict())
            else:
                out.append({k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")})
        return out

    final_nav = {
        "author": [{"group": a, "pages": pages_to_dicts(d["pages"])} for a, d in sorted(nav_tree["author"].items(), key=lambda x: x[0].lower())],
        "date": [{"group": y, "pages": [{"group": m, "pages": [{"group": d, "pages": pages_to_dicts(v["pages"])} for d, v in sorted(months.items())]} for m, months in sorted(ydata.items())]} for y, ydata in sorted(nav_tree["date"].items())],
        "tags": [{"group": t, "pages": pages_to_dicts(d["pages"])} for t, d in sorted(nav_tree["tags"].items(), key=lambda x: x[0].lower())],
        "keywords": [{"group": kw, "pages": pages_to_dicts(d["pages"])} for kw, d in sorted(nav_tree["keywords"].items(), key=lambda x: x[0].lower())],
        "rotkeeper_nav": convert_rot_nav_tree(nav_tree["rotkeeper_nav"]),
    }

    output_path = Path(args.output) if getattr(args, "output", None) else cfg.BONES / "reports" / "nav.yaml"

    if getattr(args, "dry_run", False):
        print("Dry run enabled, navigation would be:")
        print(yaml.safe_dump(final_nav, sort_keys=False))
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(final_nav, f, sort_keys=False)

    if getattr(args, "verbose", False):
        print(f"Wrote navigation to {output_path}")

    return 0


def add_parser(subs):
    parser = subs.add_parser("nav", help="Generate navigation YAML from sitemap-pipeline output")
    parser.add_argument("--output", type=str, help=f"Output path for navigation YAML (default: CONFIG.BONES/reports/nav.yaml)")
    parser.add_argument("--dry-run", action="store_true", help="Do not write output, just print it")
    parser.add_argument("--verbose", action="store_true", help="Print additional information")
    parser.set_defaults(func=run)
