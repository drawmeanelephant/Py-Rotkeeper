from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

import yaml

from ..config import CONFIG

logger = logging.getLogger(__name__)


def parse_nav_label(label):
    """Parse a label to extract numeric prefix for sorting."""
    if label is None:
        return (float('inf'), '')
    match = re.match(r'^(\d+)_+(.*)$', label)
    if match:
        return (int(match.group(1)), match.group(2).strip().lower())
    return (float('inf'), label.lower())


def nav_command(args, ctx=None):
    cfg = ctx.config if (ctx is not None and ctx.config is not None) else CONFIG

    sitemap_path = cfg.BONES / "reports" / "sitemap_pipeline.yaml"
    if not sitemap_path.exists():
        logger.error("Sitemap file not found at %s", sitemap_path)
        logger.error("Run 'rotkeeper sitemap-pipeline' first to generate it.")
        return 1

    try:
        with sitemap_path.open("r", encoding="utf-8") as f:
            sitemap = yaml.safe_load(f)
    except Exception as e:
        logger.error("Failed to load sitemap_pipeline.yaml: %s", e)
        return 1

    if isinstance(sitemap, dict) and "pages" in sitemap:
        pages_list = sitemap["pages"]
    elif isinstance(sitemap, list):
        pages_list = sitemap
    else:
        logger.error("sitemap_pipeline.yaml structure not recognized")
        return 1

    # Normalize and prepare pages
    pages = []
    for p in pages_list:
        if not isinstance(p, dict) or not p.get("show_in_nav", True):
            continue
        nav_path = p.get("rotkeeper_nav")
        if not isinstance(nav_path, list) or not nav_path:
            nav_path = ["Misc"]
        else:
            nav_path = [str(item) for item in nav_path]
        pages.append({**p, "rotkeeper_nav": nav_path})

    # Build metadata-first nav structure
    metadata_groups = ["author", "date", "tags", "keywords", "rotkeeper_nav"]
    nav_tree = {key: {} for key in metadata_groups}

    for page in pages:
        author = page.get("author") or "Misc"
        date   = page.get("date")   or "Misc"
        tags   = page.get("tags")   or ["Misc"]
        keywords = page.get("keywords") or ["Misc"]
        rot_nav  = page.get("rotkeeper_nav") or ["Misc"]

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
                current[part] = {"__children__": {}, "__pages__": []}
            current = current[part]["__children__"]
        current.setdefault("__pages__", []).append(page)

        try:
            from datetime import datetime
            dt = datetime.fromisoformat(str(date))
            year, month, day = str(dt.year), f"{dt.month:02}", f"{dt.day:02}"
        except Exception:
            year = month = day = "Misc"
        nav_tree["date"].setdefault(year, {}).setdefault(month, {}).setdefault(day, {"pages": []})
        nav_tree["date"][year][month][day]["pages"].append(page)

    def convert_rot_nav_tree(tree):
        nav_list = []
        for orig_key, group_dict in sorted(tree.items(), key=lambda x: parse_nav_label(x[0])):
            if not isinstance(group_dict, dict):
                continue
            display = re.sub(r'^\d+_+', '', orig_key).strip() if orig_key else "Misc"
            entry = {"group": display, "pages": []}
            children = convert_rot_nav_tree(group_dict.get("__children__", {}))
            if children:
                entry["pages"].extend(children)
            for p in group_dict.get("__pages__", []):
                page_data = {k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")}
                entry["pages"].append(page_data)
            nav_list.append(entry)
        return nav_list

    final_nav = {}

    authors = []
    for author, data in sorted(nav_tree["author"].items(), key=lambda x: x[0].lower()):
        pages_out = [{k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")} for p in data["pages"]]
        authors.append({"group": author, "pages": pages_out})
    final_nav["author"] = authors

    dates = []
    for year in sorted(nav_tree["date"].keys()):
        months_list = []
        for month in sorted(nav_tree["date"][year].keys()):
            days_list = []
            for day in sorted(nav_tree["date"][year][month].keys()):
                pages_out = [{k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")} for p in nav_tree["date"][year][month][day]["pages"]]
                days_list.append({"group": day, "pages": pages_out})
            months_list.append({"group": month, "pages": days_list})
        dates.append({"group": year, "pages": months_list})
    final_nav["date"] = dates

    tags_list = []
    for tag, data in sorted(nav_tree["tags"].items(), key=lambda x: x[0].lower()):
        pages_out = [{k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")} for p in data["pages"]]
        tags_list.append({"group": tag, "pages": pages_out})
    final_nav["tags"] = tags_list

    keywords_list = []
    for kw, data in sorted(nav_tree["keywords"].items(), key=lambda x: x[0].lower()):
        pages_out = [{k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")} for p in data["pages"]]
        keywords_list.append({"group": kw, "pages": pages_out})
    final_nav["keywords"] = keywords_list

    final_nav["rotkeeper_nav"] = convert_rot_nav_tree(nav_tree["rotkeeper_nav"])

    output_path = Path(args.output) if args.output else cfg.BONES / "reports" / "nav.yaml"

    if args.dry_run:
        print("Dry run enabled, navigation would be:")
        print(yaml.safe_dump(final_nav, sort_keys=False))
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(final_nav, f, sort_keys=False)
        if args.verbose:
            print(f"Wrote navigation to {output_path}")
            for group_key in final_nav:
                print(f"Top-level group: {group_key}")
                for subgroup in final_nav[group_key]:
                    print(f"  Group: {subgroup['group']}")
                    for page in subgroup.get("pages", []):
                        if isinstance(page, dict) and "title" in page:
                            print(f"    - Title: {page.get('title')}, Path: {page.get('path')}, Author: {page.get('author')}")

    return 0


def add_parser(subs):
    parser = subs.add_parser("nav", help="Generate navigation YAML from sitemap-pipeline output")
    parser.add_argument(
        "--output",
        type=str,
        help="Output path for navigation YAML (default: CONFIG.BONES / reports / nav.yaml)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write output, just print it")
    parser.add_argument("--verbose", action="store_true", help="Print additional information")
    parser.set_defaults(func=nav_command)
