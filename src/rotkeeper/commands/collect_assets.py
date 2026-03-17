from __future__ import annotations

import argparse
import logging
import shutil
from html.parser import HTMLParser
from pathlib import Path

from ..context import RunContext


class _ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._maybe_add(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._maybe_add(tag, attrs)

    def _maybe_add(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            key = "src"
        elif tag == "script":
            key = "src"
        elif tag == "link":
            key = "href"
        else:
            return

        for attr, value in attrs:
            if attr == key and value:
                self.refs.append(value)


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser(
        "collect-assets",
        help="Collect referenced assets into output/assets",
    )
    p.add_argument("--dry-run", action="store_true", help="Show what would be done without copying")
    p.add_argument("--verbose", action="store_true", help="Enable detailed logging")
    p.set_defaults(func=run)


def _is_external(ref: str) -> bool:
    ref = ref.lower()
    return ref.startswith("http://") or ref.startswith("https://") or ref.startswith("data:")


def _strip_query_fragment(ref: str) -> str:
    ref = ref.split("#", 1)[0]
    ref = ref.split("?", 1)[0]
    return ref


def _collect_refs_from_html(path: Path) -> list[str]:
    parser = _ResourceParser()
    html = path.read_text(encoding="utf-8", errors="ignore")
    parser.feed(html)
    return parser.refs


def _resolve_asset(
    ref_rel: Path,
    *,
    md_dir: Path,
    resources_dir: Path,
    bones_assets_dir: Path,
) -> tuple[Path, str, Path] | None:
    candidates = (
        ("markdown", md_dir),
        ("resources", resources_dir),
        ("bones", bones_assets_dir),
    )
    for label, root in candidates:
        root_resolved = root.resolve()
        src = (root / ref_rel).resolve()
        if not src.is_relative_to(root_resolved):
            logging.warning("Skipping asset outside %s dir: %s", label, ref_rel.as_posix())
            continue
        if src.exists() and src.is_file():
            return src, label, root_resolved
    return None


def run(args: argparse.Namespace, ctx: RunContext) -> int:
    import yaml
    import hashlib

    output_dir = ctx.paths.output_dir
    output_assets_dir = output_dir / "assets"
    bones_reports_dir = ctx.paths.bones_dir / "reports"
    assets_report_path = bones_reports_dir / "assets.yaml"
    home_assets_dir = ctx.paths.home_dir / "assets"
    # Markdown root for page-local assets
    home_content_dir = ctx.paths.home_dir / "content"

    dry_run = getattr(args, "dry_run", False)
    verbose = getattr(args, "verbose", False)
    if verbose:
        logging.getLogger().setLevel(logging.INFO)

    if not output_dir.exists():
        logging.info("Output directory not found at %s", output_dir)
        return 0

    if not assets_report_path.exists():
        logging.error("assets.yaml report not found at %s", assets_report_path)
        return 1

    try:
        with assets_report_path.open("r", encoding="utf-8") as f:
            assets_report = yaml.safe_load(f)
    except Exception as e:
        logging.error("Failed to load assets.yaml: %s", e)
        return 1

    if not isinstance(assets_report, list):
        logging.error("assets.yaml report is not a list")
        return 1

    # Helper: compute sha256 of a file
    def sha256sum(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    # For each asset in the report, copy to output_dir in the correct spot
    for asset in assets_report:
        # asset: dict with at least keys: path, hash, [origin], [page_html], [page_md]
        asset_path = asset.get("path")
        asset_hash = asset.get("hash") or asset.get("sha256")
        asset_origin = asset.get("origin")  # "global" or "page-local" or possibly "home/assets" or "markdown"
        asset_abs = asset.get("abs")  # Not always present
        page_html = asset.get("page_html")  # for page-local
        page_md = asset.get("page_md")

        if not asset_path or not asset_hash:
            logging.warning("Asset report entry missing path or hash: %r", asset)
            continue

        # Skip hidden files and .scss files
        path_obj = Path(asset_path)
        if path_obj.name.startswith('.') or path_obj.suffix.lower() == ".scss":
            if verbose:
                logging.info("Skipping hidden or SCSS file: %s", asset_path)
            continue

        # Try to find the source file
        # If abs is present, use it, else try to reconstruct
        src = None
        if asset_abs:
            src = Path(asset_abs)
        else:
            # Try home/assets for global, or markdown dir for page-local
            if asset_origin == "global" or (asset_origin and "home/assets" in asset_origin):
                src = home_assets_dir / asset_path
            elif asset_origin == "page-local" or (asset_origin and "markdown" in asset_origin):
                if page_md:
                    src = Path(page_md).parent / Path(asset_path).name
                elif page_html:
                    # Try reconstruct from html path
                    md_dir = Path(page_html).with_suffix(".md").parent
                    src = md_dir / Path(asset_path).name
                else:
                    src = home_content_dir / asset_path
            else:
                # Fallback: try home/assets first, then home/content
                candidate1 = home_assets_dir / asset_path
                candidate2 = home_content_dir / asset_path
                if candidate1.exists():
                    src = candidate1
                elif candidate2.exists():
                    src = candidate2
                else:
                    src = Path(asset_path)
        if not src.exists():
            logging.warning("Asset source file missing: %s", src)
            continue

        # Determine destination
        if asset_origin == "global" or (asset_origin and "home/assets" in asset_origin):
            # Global asset: output/assets/<relative_path>
            dest = output_assets_dir / asset_path
            dest_info = f"{src} -> {dest}"
        elif asset_origin == "page-local" or (asset_origin and "markdown" in asset_origin):
            # Page-local: output/<html_dir>/<filename>
            if page_html:
                html_path = output_dir / page_html
                dest = html_path.parent / Path(asset_path).name
            elif page_md:
                html_path = output_dir / Path(page_md).with_suffix(".html")
                dest = html_path.parent / Path(asset_path).name
            else:
                # fallback: put in output_dir
                dest = output_dir / Path(asset_path).name
            dest_info = f"page-local asset {src} -> {dest}"
        else:
            # Fallback: treat as global
            dest = output_assets_dir / asset_path
            dest_info = f"{src} -> {dest}"

        # If file exists and hash matches, skip
        if dest.exists():
            try:
                dest_hash = sha256sum(dest)
                if dest_hash == asset_hash:
                    if verbose:
                        logging.info("Asset already up-to-date: %s", dest)
                    continue
                else:
                    if verbose:
                        logging.info("Asset at %s hash mismatch (have %s, want %s), will overwrite", dest, dest_hash, asset_hash)
            except Exception as e:
                logging.warning("Failed to compute hash for %s: %s", dest, e)
                # Will overwrite

        if dry_run:
            logging.info("[dry-run] copy %s", dest_info)
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

        # Verify hash
        try:
            copied_hash = sha256sum(dest)
            if copied_hash != asset_hash:
                logging.error("Copied asset %s hash mismatch (got %s, expected %s)", dest, copied_hash, asset_hash)
                continue
            if verbose:
                logging.info("Copied and verified asset: %s", dest_info)
            else:
                logging.info("Copied asset: %s", asset_path)
        except Exception as e:
            logging.error("Failed to verify hash for %s: %s", dest, e)

    return 0
