def generate_dynamic_nav(nav_list):
    """
    From a full nav_list, generate dynamic pages for templates:
    - by_author
    - by_tag
    - by_keyword
    - by_date (year/month/day)
    Returns a dict of virtual pages.
    """
    dynamic_pages = {
        "by_author": {},
        "by_tag": {},
        "by_keyword": {},
        "by_date": {}
    }

    def collect_pages(entry):
        # Collect pages recursively
        pages = []
        if "pages" in entry:
            for p in entry["pages"]:
                if isinstance(p, dict) and "title" in p and "path" in p:
                    pages.append(p)
                elif isinstance(p, dict) and "group" in p:
                    pages.extend(collect_pages(p))
        return pages

    all_pages = []
    for top in nav_list:
        all_pages.extend(collect_pages(top))

    for page in all_pages:
        # Author
        author = page.get("author") or "Misc"
        dynamic_pages["by_author"].setdefault(author, []).append(page)
        # Tags
        for tag in page.get("tags", []):
            dynamic_pages["by_tag"].setdefault(tag, []).append(page)
        # Keywords
        for kw in page.get("keywords", []):
            dynamic_pages["by_keyword"].setdefault(kw, []).append(page)
        # Date
        date = page.get("date")
        if date:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(date)
                y, m, d = str(dt.year), f"{dt.month:02}", f"{dt.day:02}"
            except:
                y = m = d = "Misc"
        else:
            y = m = d = "Misc"
        dynamic_pages["by_date"].setdefault(y, {}).setdefault(m, {}).setdefault(d, []).append(page)

    return dynamic_pages


if __name__ == "__main__":
    import argparse
    import yaml
    from pprint import pprint

    parser = argparse.ArgumentParser(description="Generate dynamic nav pages for templates")
    parser.add_argument("--input", default="bones/reports/nav.yaml", help="Path to nav.yaml")
    parser.add_argument("--output", default="bones/reports/dynamic_nav.yaml", help="Path to output YAML")
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing file")
    parser.add_argument("--verbose", action="store_true", help="Pretty-print output")
    args = parser.parse_args()

    # Load nav.yaml
    with open(args.input, "r", encoding="utf-8") as f:
        nav_list = yaml.safe_load(f)

    # Generate dynamic pages
    dynamic_pages = generate_dynamic_nav(nav_list)

    if args.verbose:
        pprint(dynamic_pages)

    if args.dry_run:
        import json
        print(json.dumps(dynamic_pages, indent=2))
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            yaml.safe_dump(dynamic_pages, f, sort_keys=False)
        if args.verbose:
            print(f"Dynamic nav written to {args.output}")
