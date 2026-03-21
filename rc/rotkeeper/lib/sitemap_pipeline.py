# rc/rotkeeper/lib/sitemap_pipeline.py
from __future__ import annotations

import pprint
import re
import textwrap
from dataclasses import replace
from datetime import date as datetype
from pathlib import Path

import frontmatter
import yaml

from ..config import CONFIG
import logging

logger = logging.getLogger("rotkeeper.sitemap_pipeline")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_nav_token(token: str):
    """Parse numeric prefix if present, fallback to 9999."""
    match = re.match(r"(\d+)[.\-\s]+(.*)", token)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return 9999, token.strip()


def sort_nav_tree(node: dict) -> None:
    """Recursively sort nav tree nodes by numeric prefix, then title."""
    if "pages" in node:
        node["pages"].sort(key=lambda p: p.get("title", ""))
    children = node.get("children", {})
    if children:
        sorted_items = sorted(children.items(), key=lambda item: parse_nav_token(item[0]))
        node["children"] = {k: v for k, v in sorted_items}
        for child in node["children"].values():
            sort_nav_tree(child)


def nav_tree_to_markdown(node: dict, depth: int = 0) -> list[str]:
    """Recursively render a nav tree node to a nested Markdown list."""
    lines = []
    indent = "  " * depth
    for label, child in node.get("children", {}).items():
        pages = child.get("pages", [])
        sub = child.get("children", {})
        if pages:
            first = pages[0]
            lines.append(f"{indent}- [{label}]({first.get('path', '#')})")
            for page in pages[1:]:
                lines.append(f"{indent}  - [{page.get('title', '')}]({page.get('path', '#')})")
        else:
            lines.append(f"{indent}- {label}")
        if sub:
            lines.extend(nav_tree_to_markdown(child, depth + 1))
    return lines


def coerce_date(val) -> str | None:
    """Coerce datetime.date or other date-like objects to ISO string."""
    if val is None:
        return None
    if isinstance(val, datetype):
        return val.isoformat()
    return str(val) or None


# ---------------------------------------------------------------------------
# Pipeline class
# ---------------------------------------------------------------------------

class SitemapPipeline:

    def __init__(self, ctx=None):
        self.ctx = ctx
        config = ctx.config if ctx else CONFIG
        self.content_dir   = config.CONTENT_DIR
        self.reports_dir   = config.REPORTS_DIR   # use REPORTS_DIR so overrides are respected
        self.pages: list   = []
        self.metadata: dict = {"tags": {}, "authors": {}, "dates": {}, "rotkeepernav": {}}
        self.dry_run       = getattr(ctx, "dry_run",       False) if ctx else False
        self.verbose       = getattr(ctx, "verbose",       False) if ctx else False
        self.index_only    = getattr(ctx, "index_only",    False) if ctx else False
        self.metadata_only = getattr(ctx, "metadata_only", False) if ctx else False
        self.write_only    = getattr(ctx, "write_only",    False) if ctx else False

    # ------------------------------------------------------------------

    def collect_pages(self) -> None:
        """Walk content_dir, load frontmatter, filter drafts and hidden files."""
        self.pages = []
        skipped = 0

        if not self.content_dir.exists() or not self.content_dir.is_dir():
            logger.warning(
                "collect_pages: content directory not found at %s — "
                "run 'rotkeeper init' first",
                self.content_dir,
            )
            return

        for md in sorted(self.content_dir.rglob("*.md")):
            relpath = md.relative_to(self.content_dir)
            if relpath.name.startswith("_") or any(p.startswith(".") for p in relpath.parts):
                skipped += 1
                continue
            try:
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
                "tags":         post.get("tags",     []) or [],
                "keywords":     post.get("keywords", []) or [],
                "date":         coerce_date(post.get("date")),
                "rotkeepernav": post.get("rotkeepernav", []) or [],
                "show_in_nav":  post.get("show_in_nav", True),
                "description":  post.get("description", ""),
            }
            if any(p["path"] == page_data["path"] for p in self.pages):
                logger.warning("Duplicate output path skipped: %s", page_data["path"])
                skipped += 1
                continue
            self.pages.append(page_data)
        logger.info("Collected %d pages, skipped %d", len(self.pages), skipped)

    # ------------------------------------------------------------------

    def build_metadata_trees(self) -> None:
        """Build tag, author, date, and nav trees from self.pages."""
        if not self.pages:
            logger.warning("build_metadata_trees called with no pages; run collect_pages first")
        self.metadata = {"tags": {}, "authors": {}, "dates": {}, "rotkeepernav": {}}
        for page in self.pages:
            author = page["author"]
            self.metadata["authors"].setdefault(author, {"pages": []})
            self.metadata["authors"][author]["pages"].append(page)
            for tag in page.get("tags", []):
                self.metadata["tags"].setdefault(tag, {"pages": []})
                self.metadata["tags"][tag]["pages"].append(page)
            date = page.get("date") or "Misc"
            self.metadata["dates"].setdefault(date, {"pages": []})
            self.metadata["dates"][date]["pages"].append(page)
            if not page.get("show_in_nav", True):
                continue
            current = self.metadata["rotkeepernav"]
            tokens = page.get("rotkeepernav") or ["Misc"]
            for token in tokens:
                _, label = parse_nav_token(token)
                current.setdefault(label, {"children": {}, "pages": []})
                current = current[label]["children"]
            current.setdefault("pages", []).append(page)
        sort_nav_tree(self.metadata["rotkeepernav"])
        logger.info(
            "Built metadata trees: %d tags, %d authors, %d dates",
            len(self.metadata["tags"]),
            len(self.metadata["authors"]),
            len(self.metadata["dates"]),
        )

    # ------------------------------------------------------------------

    def write_index_pages(self) -> None:
        """Emit auto-generated Markdown index pages for tags, authors, dates, and sitemap."""
        generated_dir = self.content_dir / "generated"
        if self.dry_run:
            logger.info("dry-run: Would write index pages to %s", generated_dir)
            return
        generated_dir.mkdir(parents=True, exist_ok=True)
        today = datetype.today().isoformat()

        def write(rel: str, fm: dict, body_lines: list[str]):
            path = generated_dir / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            fm.setdefault("generated_by", "rotkeeper/sitemap_pipeline")
            fm.setdefault("generated_at", today)
            fm.setdefault("show_in_nav", False)
            header = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
            content = f"---\n{header}\n---\n" + "\n".join(body_lines)
            path.write_text(content, encoding="utf-8")
            logger.info("Wrote index page %s", path)

        tag_lines = ["# Tags\n"]
        for tag, data in sorted(self.metadata["tags"].items()):
            tag_lines.append(f"## {tag}")
            for page in data["pages"]:
                tag_lines.append(f"- {page['title']}")
            tag_lines.append("")
        write("tags/index.md", {"title": "Tags", "draft": False}, tag_lines)

        for tag, data in sorted(self.metadata["tags"].items()):
            slug = re.sub(r"[^\w-]", "-", tag.lower().strip("-"))
            lines = [f"# {tag}\n"]
            for page in data["pages"]:
                desc = page.get("description", "")
                entry = f"- {page['title']}"
                if desc:
                    entry += f"\n  {desc}"
                lines.append(entry)
            write(f"tags/{slug}.md", {"title": f"Tag: {tag}", "draft": False}, lines)

        author_lines = ["# Authors\n"]
        for author, data in sorted(self.metadata["authors"].items()):
            author_lines.append(f"## {author}")
            for page in data["pages"]:
                author_lines.append(f"- {page['title']}")
            author_lines.append("")
        write("authors/index.md", {"title": "Authors", "draft": False}, author_lines)

        date_lines = ["# By Date\n"]
        for dt, data in sorted(self.metadata["dates"].items(), reverse=True):
            date_lines.append(f"## {dt}")
            for page in data["pages"]:
                date_lines.append(f"- {page['title']}")
            date_lines.append("")
        write("dates/index.md", {"title": "By Date", "draft": False}, date_lines)

        sitemap_lines = ["# Sitemap\n"]
        for page in self.pages:
            sitemap_lines.append(f"- {page['title']}")
        write("sitemap.md", {"title": "Sitemap", "draft": False}, sitemap_lines)

        logger.info("Index pages written to %s", generated_dir)

    # ------------------------------------------------------------------

    def write_nav_partial(self) -> None:
        """Write an HTML nav block to reports_dir/nav_partial.html.

        Render passes this to Pandoc via --include-before-body so every page
        gets consistent nav without modifying source files.

        NOTE: must be .html not .md — Pandoc's --include-before-body inserts
        the file verbatim; it does not parse Markdown.
        """
        output_file = self.reports_dir / "nav_partial.html"

        if self.dry_run:
            logger.info("dry-run: Would write nav partial to %s", output_file)
            return

        self.reports_dir.mkdir(parents=True, exist_ok=True)

        nav_tree = self.metadata.get("rotkeepernav", {})

        def render_items(node: dict, depth: int = 0) -> list[str]:
            lines = []
            indent = "  " * (depth + 2)
            for label, child in node.get("children", {}).items():
                pages = child.get("pages", [])
                sub_children = child.get("children", {})
                if pages:
                    first = pages[0]
                    href = "/" + first.get("path", "#")
                    lines.append(f'{indent}<li><a href="{href}">{label}</a>')
                    if len(pages) > 1 or sub_children:
                        lines.append(f"{indent}  <ul>")
                        for page in pages[1:]:
                            phref = "/" + page.get("path", "#")
                            ptitle = page.get("title", "")
                            lines.append(f'{indent}    <li><a href="{phref}">{ptitle}</a></li>')
                        if sub_children:
                            lines.extend(render_items(child, depth + 2))
                        lines.append(f"{indent}  </ul>")
                    lines.append(f"{indent}</li>")
                else:
                    lines.append(f"{indent}<li>{label}")
                    if sub_children:
                        lines.append(f"{indent}  <ul>")
                        lines.extend(render_items(child, depth + 2))
                        lines.append(f"{indent}  </ul>")
                    lines.append(f"{indent}</li>")
            return lines

        items = render_items(nav_tree)

        if not items:
            logger.warning("write_nav_partial: nav tree is empty, writing empty nav")

        html_lines = ['<nav class="site-nav">']
        html_lines.append("  <ul>")
        html_lines.extend(items)
        html_lines.append("  </ul>")
        html_lines.append("</nav>")

        output_file.write_text("\n".join(html_lines) + "\n", encoding="utf-8")
        logger.info("Wrote nav partial %s", output_file)

    # ------------------------------------------------------------------

    def write_sidecar_metadata(self) -> None:
        """Write .rk.yaml sidecar files alongside each source .md."""
        if not self.pages:
            logger.warning("write_sidecar_metadata called with no pages")
            return
        today = datetype.today().isoformat()
        tag_index = self.metadata["tags"]
        for page in self.pages:
            source_path = self.content_dir / page["source"]
            sidecar_path = source_path.with_suffix(".rk.yaml")
            related: list = []
            seen: set = set()
            for tag in page.get("tags", []):
                for candidate in tag_index.get(tag, {}).get("pages", []):
                    if candidate["path"] != page["path"] and candidate["path"] not in seen:
                        related.append({
                            "title":       candidate["title"],
                            "path":        candidate["path"],
                            "description": candidate.get("description", ""),
                        })
                        seen.add(candidate["path"])
                    if len(related) >= 5:
                        break
                if len(related) >= 5:
                    break
            breadcrumb = []
            for token in page.get("rotkeepernav", []):
                _, label = parse_nav_token(token)
                breadcrumb.append(label)
            breadcrumb.append(page["title"])
            sidecar = {
                "rotkeeper": {
                    "generated_at": today,
                    "source":       page["source"],
                    "breadcrumb":   breadcrumb,
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
            if self.dry_run:
                logger.info("dry-run: Would write sidecar %s", sidecar_path)
                continue
            sidecar_path.write_text(
                yaml.dump(sidecar, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            logger.debug("Wrote sidecar %s", sidecar_path)
        logger.info("Sidecar metadata written for %d pages", len(self.pages))

    # ------------------------------------------------------------------

    def write_yaml(self) -> None:
        """Write the unified sitemap YAML to reports_dir."""
        if not self.pages:
            logger.warning("write_yaml called with no pages; output will be empty")
        output_file = self.reports_dir / "sitemap_pipeline.yaml"
        if self.dry_run:
            logger.info("dry-run: Would write unified sitemap to %s", output_file)
            return
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "pages":        self.pages,
            "tags":         self.metadata["tags"],
            "authors":      self.metadata["authors"],
            "dates":        self.metadata["dates"],
            "rotkeepernav": self.metadata["rotkeepernav"],
        }
        output_file.write_text(
            yaml.dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        logger.info("Wrote unified sitemap %s", output_file)

    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run the sitemap pipeline."""
        if self.index_only:
            logger.info("Stage: index-only")
            self.collect_pages()
            if self.verbose:
                pprint.pprint([p["path"] for p in self.pages])
            return
        if self.metadata_only:
            logger.info("Stage: metadata-only")
            self.collect_pages()
            self.build_metadata_trees()
            if self.verbose:
                pprint.pprint(self.metadata)
            return
        if self.write_only:
            logger.info("Stage: write-only")
            self.write_index_pages()
            self.write_nav_partial()
            self.write_sidecar_metadata()
            self.write_yaml()
            return
        logger.info("Stage: full pipeline")
        self.collect_pages()
        self.build_metadata_trees()
        self.write_index_pages()
        self.write_nav_partial()
        self.write_sidecar_metadata()
        self.write_yaml()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def add_parser(subparsers):
    p = subparsers.add_parser(
        "sitemap-pipeline",
        help="Collect pages, build metadata trees, write index pages, nav partial, and sidecars",
    )
    p.add_argument("--dry-run",       action="store_true", help="Print actions without writing files")
    p.add_argument("--verbose",       action="store_true", help="Print extra diagnostic output")
    p.add_argument("--index-only",    action="store_true", help="Collect pages only")
    p.add_argument("--metadata-only", action="store_true", help="Collect + build trees only")
    p.add_argument("--write-only",    action="store_true", help="Skip collection, write from memory")
    p.set_defaults(func=run_command)
    return p


def run_command(args, ctx=None):
    if ctx is None:
        raise ValueError("sitemap-pipeline requires a RunContext; ctx was None")
    ctx = replace(
        ctx,
        dry_run       = getattr(args, "dry_run",       False),
        verbose       = getattr(args, "verbose",       False),
        index_only    = getattr(args, "index_only",    False),
        metadata_only = getattr(args, "metadata_only", False),
        write_only    = getattr(args, "write_only",    False),
    )
    pipeline = SitemapPipeline(ctx=ctx)
    pipeline.run()
    return 0
