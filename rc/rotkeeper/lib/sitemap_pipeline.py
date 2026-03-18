from pathlib import Path
import yaml
import frontmatter
import re
from ..config import CONFIG
import logging

logger = logging.getLogger("rotkeeper.commands.sitemap_pipeline")

def _parse_nav_token(token: str):
    """Parse numeric prefix if present, fallback to 9999."""
    match = re.match(r"^(\d+)[_\- ]+(.*)$", token)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return 9999, token.strip()

class SitemapPipeline:
    def __init__(self, ctx=None):
        self.ctx = ctx
        self.content_dir = CONFIG.CONTENT_DIR
        self.reports_dir = CONFIG.BONES / "reports"
        self.output_file = self.reports_dir / "sitemap_pipeline.yaml"
        self.pages = []
        self.metadata = {"tags": {}, "authors": {}, "dates": {}, "rotkeeper_nav": {}}

    def load_existing(self):
        if self.output_file.exists():
            try:
                data = yaml.safe_load(self.output_file.read_text(encoding="utf-8"))
                self.pages = data.get("pages", [])
            except Exception as e:
                logger.warning(f"Failed to load existing sitemap_pipeline.yaml: {e}")

    def collect_pages(self):
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
                label = token
                if label not in current:
                    current[label] = {"__children__": {}, "__pages__": []}
                current = current[label]["__children__"]
            current.setdefault("__pages__", []).append(page)

    def write_yaml(self):
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        if self.ctx and getattr(self.ctx, "dry_run", False):
            logger.info(f"[dry-run] Would write unified sitemap to {self.output_file}")
            return
        data = {
            "pages": self.pages,
            "tags": self.metadata["tags"],
            "authors": self.metadata["authors"],
            "dates": self.metadata["dates"],
            "rotkeeper_nav": self.metadata["rotkeeper_nav"]
        }
        self.output_file.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        logger.info(f"Wrote unified sitemap → {self.output_file}")

    def run(self):
        self.load_existing()
        self.collect_pages()
        self.build_metadata_trees()
        self.write_yaml()