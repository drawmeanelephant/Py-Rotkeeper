from pathlib import Path
import yaml
import frontmatter
import re
from ..config import CONFIG
import logging
from dataclasses import replace
import pprint

logger = logging.getLogger("rotkeeper.commands.sitemap")

def _parse_nav_token(token: str):
    """Parse numeric prefix if present, fallback to 9999."""
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
        self.pages = []
        self.metadata = {"tags": {}, "authors": {}, "dates": {}, "rotkeeper_nav": {}}
        self.dry_run = getattr(ctx, "dry_run", False) if ctx else False
        self.verbose = getattr(ctx, "verbose", False) if ctx else False
        self.index_only = getattr(ctx, "index_only", False) if ctx else False
        self.metadata_only = getattr(ctx, "metadata_only", False) if ctx else False
        self.write_only = getattr(ctx, "write_only", False) if ctx else False

    def collect_pages(self):
        # ensure clean state per run
        self.pages = []
        skipped = 0
        for md in self.content_dir.rglob("*.md"):
            rel_path = md.relative_to(self.content_dir)
            if rel_path.name.startswith("_") or any(p.startswith(".") for p in rel_path.parts):
                skipped += 1
                continue
            try:
                post = frontmatter.load(md)
            except Exception as e:
                logger.warning(f"Failed to load frontmatter from {md}: {e}")
                skipped += 1
                continue
            if post.get("draft", False) or not post.get("published", True):
                skipped += 1
                continue

            page_data = {
                "title": post.get("title", rel_path.stem),
                "path": rel_path.with_suffix(".html").as_posix(),
                "author": post.get("author", "Misc"),
                "tags": post.get("tags", []) or [],
                "keywords": post.get("keywords", []) or [],
                "date": post.get("date"),
                "rotkeeper_nav": post.get("rotkeeper_nav", []) or [],
                "show_in_nav": post.get("show_in_nav", True)
            }
            # dedupe by path
            if any(p["path"] == page_data["path"] for p in self.pages):
                continue
            self.pages.append(page_data)
        logger.info(f"Collected {len(self.pages)} pages, skipped {skipped}")

    def build_metadata_trees(self):
        # Reset
        self.metadata = {"tags": {}, "authors": {}, "dates": {}, "rotkeeper_nav": {}}

        for page in self.pages:
            if not page.get("show_in_nav", True):
                continue

            # Authors
            self.metadata["authors"].setdefault(page["author"], {"pages": []})
            self.metadata["authors"][page["author"]]["pages"].append(page)

            # Tags
            for tag in page.get("tags", []):
                self.metadata["tags"].setdefault(tag, {"pages": []})
                self.metadata["tags"][tag]["pages"].append(page)

            # Dates
            date = page.get("date") or "Misc"
            self.metadata["dates"].setdefault(date, {"pages": []})
            self.metadata["dates"][date]["pages"].append(page)

            # rotkeeper_nav
            current = self.metadata["rotkeeper_nav"]
            for token in page.get("rotkeeper_nav", ["Misc"]):
                _, label = _parse_nav_token(token)
                if label not in current:
                    current[label] = {"__children__": {}, "__pages__": []}
                current = current[label]["__children__"]
            current.setdefault("__pages__", []).append(page)

        def sort_nav_tree(node):
            # Sort __pages__ alphabetically by title
            if "__pages__" in node:
                node["__pages__"].sort(key=lambda p: p.get("title", ""))

            # Sort children by numeric prefix and then label
            children = node.get("__children__", {})
            if children:
                sorted_items = sorted(
                    children.items(),
                    key=lambda item: _parse_nav_token(item[0])
                )
                # Rebuild dict to maintain order
                node["__children__"] = {k: v for k, v in sorted_items}
                # Recursively sort children
                for child in node["__children__"].values():
                    sort_nav_tree(child)

        sort_nav_tree(self.metadata["rotkeeper_nav"])

    def write_yaml(self):
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        if self.dry_run:
            logger.info(f"[dry-run] Would write unified sitemap to {self.reports_dir / 'sitemap_pipeline.yaml'}")
            return
        data = {
            "pages": self.pages,
            "tags": self.metadata["tags"],
            "authors": self.metadata["authors"],
            "dates": self.metadata["dates"],
            "rotkeeper_nav": self.metadata["rotkeeper_nav"]
        }
        output_file = self.reports_dir / "sitemap_pipeline.yaml"
        output_file.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        logger.info(f"Wrote unified sitemap → {output_file}")

    def run(self):
        """
        Run the sitemap pipeline in stages. Supports:
        - index: collect pages only
        - metadata: build tag/author/date/keywords/nav trees
        - write: write YAML
        Defaults to full run if no stage flags are set.
        Respects self.dry_run and self.verbose.
        """
        if self.index_only:
            if self.verbose:
                logger.info("Stage: index-only")
            self.collect_pages()
            return

        if self.metadata_only:
            if self.verbose:
                logger.info("Stage: metadata-only")
            self.collect_pages()
            self.build_metadata_trees()
            if self.verbose:
                pprint.pprint(self.metadata)
            return

        if self.write_only:
            if self.verbose:
                logger.info("Stage: write-only")
            self.write_yaml()
            return

        # default: full pipeline
        if self.verbose:
            logger.info("Stage: full pipeline")
        self.collect_pages()
        self.build_metadata_trees()
        self.write_yaml()

def run_command(args, ctx=None):
    if ctx:
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