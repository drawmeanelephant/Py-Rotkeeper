import yaml
import frontmatter
import re
import textwrap
from datetime import date as date_type
from ..config import CONFIG
import logging
from dataclasses import replace
import pprint

logger = logging.getLogger("rotkeeper.sitemap_pipeline")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_nav_token(token: str):
    """Parse numeric prefix if present, fallback to 9999."""
    match = re.match(r"^(\d+)[_\- ]+(.*)$", token)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return 9999, token.strip()

def _sort_nav_tree(node: dict) -> None:
    """Recursively sort nav tree nodes by numeric prefix, then title."""
    if "__pages__" in node:
        node["__pages__"].sort(key=lambda p: p.get("title", ""))
    children = node.get("__children__", {})
    if children:
        sorted_items = sorted(
            children.items(),
            key=lambda item: _parse_nav_token(item[0]),
        )
        node["__children__"] = {k: v for k, v in sorted_items}
        for child in node["__children__"].values():
            _sort_nav_tree(child)

def _nav_tree_to_markdown(node: dict, depth: int = 0) -> list[str]:
    """
    Recursively render a nav tree node to a nested Markdown list.
    Returns a list of lines.
    Labels are always clean (stripped of numeric prefix) because
    build_metadata_trees() inserts using the label from _parse_nav_token().
    """
    lines = []
    indent = "  " * depth
    for label, child in node.get("__children__", {}).items():
        pages = child.get("__pages__", [])
        sub = child.get("__children__", {})
        if pages:
            # Use the first page as the section link, rest as sub-items
            first = pages[0]
            lines.append(f"{indent}- [{label}]({first['path']})")
            for page in pages[1:]:
                lines.append(f"{indent}  - [{page['title']}]({page['path']})")
        else:
            lines.append(f"{indent}- {label}")
        if sub:
            lines.extend(_nav_tree_to_markdown(child, depth + 1))
    return lines

def _coerce_date(val) -> str | None:
    """Coerce datetime.date or other date-like objects to ISO string."""
    if val is None:
        return None
    if isinstance(val, date_type):
        return val.isoformat()
    return str(val) or None

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class SitemapPipeline:
    def __init__(self, ctx=None):
        self.ctx = ctx
        config = ctx.config if ctx else CONFIG
        self.content_dir = config.CONTENT_DIR
        self.reports_dir = config.BONES / "reports"
        self.pages = []
        self.metadata = {"tags": {}, "authors": {}, "dates": {}, "rotkeeper_nav": {}}
        self.dry_run = getattr(ctx, "dry_run", False) if ctx else False
        self.verbose = getattr(ctx, "verbose", False) if ctx else False
        self.index_only = getattr(ctx, "index_only", False) if ctx else False
        self.metadata_only = getattr(ctx, "metadata_only", False) if ctx else False
        self.write_only = getattr(ctx, "write_only", False) if ctx else False

    # ------------------------------------------------------------------
    # Stage 1: collect
    # ------------------------------------------------------------------

    def collect_pages(self):
        """Walk content_dir, load frontmatter, filter drafts and hidden files."""
        self.pages = []
        skipped = 0

        for md in sorted(self.content_dir.rglob("*.md")):
            rel_path = md.relative_to(self.content_dir)

            if rel_path.name.startswith("_") or any(
                p.startswith(".") for p in rel_path.parts
            ):
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
                "title": post.get("title", rel_path.stem),
                "path": rel_path.with_suffix(".html").as_posix(),
                "source": rel_path.as_posix(),
                "author": post.get("author", "Misc"),
                "tags": post.get("tags", []) or [],
                "keywords": post.get("keywords", []) or [],
                "date": _coerce_date(post.get("date")),
                "rotkeeper_nav": post.get("rotkeeper_nav", []) or [],
                "show_in_nav": post.get("show_in_nav", True),
                "description": post.get("description", ""),
            }

            if any(p["path"] == page_data["path"] for p in self.pages):
                logger.warning("Duplicate output path skipped: %s", page_data["path"])
                skipped += 1
                continue

            self.pages.append(page_data)

        logger.info("Collected %d pages, skipped %d", len(self.pages), skipped)

    # ------------------------------------------------------------------
    # Stage 2: build metadata trees
    # ------------------------------------------------------------------

    def build_metadata_trees(self):
        """Build tag, author, date, and nav trees from self.pages."""
        if not self.pages:
            logger.warning("build_metadata_trees called with no pages; run collect_pages first")

        self.metadata = {"tags": {}, "authors": {}, "dates": {}, "rotkeeper_nav": {}}

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
            current = self.metadata["rotkeeper_nav"]
            tokens = page.get("rotkeeper_nav") or ["Misc"]
            for token in tokens:
                # _parse_nav_token strips numeric prefix; label is always clean
                _, label = _parse_nav_token(token)
                current.setdefault(label, {"__children__": {}, "__pages__": []})
                current = current[label]["__children__"]
            current.setdefault("__pages__", []).append(page)

        _sort_nav_tree(self.metadata["rotkeeper_nav"])
        logger.info(
            "Built metadata trees: %d tags, %d authors, %d dates",
            len(self.metadata["tags"]),
            len(self.metadata["authors"]),
            len(self.metadata["dates"]),
        )

    # ------------------------------------------------------------------
    # Stage 3: write generated index pages into content_dir
    # ------------------------------------------------------------------

    def write_index_pages(self):
        """
        Emit auto-generated Markdown index pages for tags, keywords,
        authors, dates, and a master sitemap page.

        Pages are written to content_dir/generated/ with an underscore
        prefix on the frontmatter so render knows they're machine-made.
        They are normal .md files and will be picked up by render's
        standard rglob pass.
        """
        generated_dir = self.content_dir / "generated"

        if self.dry_run:
            logger.info("[dry-run] Would write index pages to %s", generated_dir)
            return

        generated_dir.mkdir(parents=True, exist_ok=True)

        today = date_type.today().isoformat()

        def _write(rel: str, fm: dict, body_lines: list[str]):
            path = generated_dir / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            fm.setdefault("generated_by", "rotkeeper/sitemap_pipeline")
            fm.setdefault("generated_at", today)
            fm.setdefault("show_in_nav", False)
            header = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
            content = "---\n" + header + "\n---\n\n" + "\n".join(body_lines) + "\n"
            path.write_text(content, encoding="utf-8")
            logger.info("Wrote index page → %s", path)

        # --- tags ---
        tag_lines = ["# Tags\n"]
        for tag, data in sorted(self.metadata["tags"].items()):
            tag_lines.append(f"## {tag}\n")
            for page in data["pages"]:
                tag_lines.append(f"- [{page['title']}]({'../' + page['path']})")
            tag_lines.append("")
        _write("tags/index.md", {"title": "Tags", "draft": False}, tag_lines)

        for tag, data in sorted(self.metadata["tags"].items()):
            slug = re.sub(r"[^\w-]", "-", tag.lower()).strip("-")
            lines = [f"# {tag}\n"]
            for page in data["pages"]:
                desc = page.get("description", "")
                entry = f"- [{page['title']}]({'../../' + page['path']})"
                if desc:
                    entry += f" — {desc}"
                lines.append(entry)
            _write(f"tags/{slug}.md", {"title": f"Tag: {tag}", "draft": False}, lines)

        # --- authors ---
        author_lines = ["# Authors\n"]
        for author, data in sorted(self.metadata["authors"].items()):
            author_lines.append(f"## {author}\n")
            for page in data["pages"]:
                author_lines.append(f"- [{page['title']}]({'../' + page['path']})")
            author_lines.append("")
        _write("authors/index.md", {"title": "Authors", "draft": False}, author_lines)

        # --- dates ---
        date_lines = ["# By Date\n"]
        for dt, data in sorted(self.metadata["dates"].items(), reverse=True):
            date_lines.append(f"## {dt}\n")
            for page in data["pages"]:
                date_lines.append(f"- [{page['title']}]({'../' + page['path']})")
            date_lines.append("")
        _write("dates/index.md", {"title": "By Date", "draft": False}, date_lines)

        # --- master sitemap ---
        sitemap_lines = ["# Sitemap\n"]
        for page in self.pages:
            sitemap_lines.append(f"- [{page['title']}]({page['path']})")
        _write("sitemap.md", {"title": "Sitemap", "draft": False}, sitemap_lines)

        logger.info("Index pages written to %s", generated_dir)

    # ------------------------------------------------------------------
    # Stage 4: write nav partial for --include-before-body
    # ------------------------------------------------------------------

    def write_nav_partial(self):
        """
        Write a Markdown nav block to reports_dir/nav_partial.md.
        Render passes this to Pandoc via --include-before-body so every
        page gets consistent nav without modifying source files.

        The output is a fenced div so CSS can target div.site-nav:
        ::: site-nav
        - [Home](index.html)
        ...
        :::
        """
        output_file = self.reports_dir / "nav_partial.md"

        if self.dry_run:
            logger.info("[dry-run] Would write nav partial to %s", output_file)
            return

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        lines = ["::: site-nav", ""]
        lines.extend(_nav_tree_to_markdown(self.metadata["rotkeeper_nav"]))
        lines += ["", ":::"]
        output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        logger.info("Wrote nav partial → %s", output_file)

    # ------------------------------------------------------------------
    # Stage 5: write per-page sidecar metadata files
    # ------------------------------------------------------------------

    def write_sidecar_metadata(self):
        """
        For each collected page, write a companion .rk.yaml file containing
        Rotkeeper-managed metadata (related pages, tag links, breadcrumb path).

        Render passes these to Pandoc as --metadata-file so template variables
        like $rotkeeper.related_pages$ are available without touching source files.

        Sidecar files live alongside their source .md in content_dir.
        """
        if not self.pages:
            logger.warning("write_sidecar_metadata called with no pages")
            return

        today = date_type.today().isoformat()
        tag_index = self.metadata["tags"]

        for page in self.pages:
            source_path = self.content_dir / page["source"]
            sidecar_path = source_path.with_suffix(".rk.yaml")

            # Related pages: share at least one tag, exclude self, cap at 5
            related = []
            seen = set()
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

            # Breadcrumb from rotkeeper_nav tokens (labels already clean)
            breadcrumb = []
            for token in page.get("rotkeeper_nav", []):
                _, label = _parse_nav_token(token)
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
                            "url": f"generated/tags/{re.sub(r'[^\w-]', '-', tag.lower()).strip('-')}.html",
                        }
                        for tag in page.get("tags", [])
                    ],
                    "author_page": "generated/authors/index.html",
                }
            }

            if self.dry_run:
                logger.info("[dry-run] Would write sidecar %s", sidecar_path)
                continue

            sidecar_path.write_text(
                yaml.dump(sidecar, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            logger.debug("Wrote sidecar → %s", sidecar_path)

        logger.info("Sidecar metadata written for %d pages", len(self.pages))

    # ------------------------------------------------------------------
    # Stage 6: write unified report YAML
    # ------------------------------------------------------------------

    def write_yaml(self):
        """Write the unified sitemap YAML to reports_dir."""
        if not self.pages:
            logger.warning("write_yaml called with no pages — output will be empty")

        output_file = self.reports_dir / "sitemap_pipeline.yaml"

        if self.dry_run:
            logger.info("[dry-run] Would write unified sitemap to %s", output_file)
            return

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "pages": self.pages,
            "tags": self.metadata["tags"],
            "authors": self.metadata["authors"],
            "dates": self.metadata["dates"],
            "rotkeeper_nav": self.metadata["rotkeeper_nav"],
        }
        output_file.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        logger.info("Wrote unified sitemap → %s", output_file)

    # ------------------------------------------------------------------
    # Pipeline orchestration
    # ------------------------------------------------------------------

    def run(self):
        """
        Run the sitemap pipeline.

        Stage flags (checked in priority order):
          --index-only    collect pages only, print paths if verbose
          --metadata-only collect + build trees, print if verbose
          --write-only    skip collection, write whatever is in memory
          Default:        full pipeline — collect → build → index pages →
                          nav partial → sidecars → YAML report
        """
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
# CLI wiring
# ---------------------------------------------------------------------------

def add_parser(subparsers):
    p = subparsers.add_parser(
        "sitemap-pipeline",
        help="Collect pages, build metadata trees, write index pages, nav partial, and sidecars",
    )
    p.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    p.add_argument("--verbose", action="store_true", help="Print extra diagnostic output")
    p.add_argument("--index-only", action="store_true", help="Collect pages only")
    p.add_argument("--metadata-only", action="store_true", help="Collect + build trees only")
    p.add_argument("--write-only", action="store_true", help="Skip collection; write from memory")
    p.set_defaults(func=run_command)
    return p

def run_command(args, ctx=None):
    if ctx is None:
        raise ValueError("sitemap-pipeline requires a RunContext; ctx was None")

    ctx = replace(
        ctx,
        dry_run=getattr(args, "dry_run", False),
        verbose=getattr(args, "verbose", False),
        index_only=getattr(args, "index_only", False),
        metadata_only=getattr(args, "metadata_only", False),
        write_only=getattr(args, "write_only", False),
    )

    pipeline = SitemapPipeline(ctx=ctx)
    pipeline.run()
    return 0
