from __future__ import annotations

import argparse
import hashlib
import logging
from pathlib import Path

from ..context import RunContext


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("assets", help="Copy static assets and write an assets.yaml report")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done without copying")
    p.add_argument("--verbose", action="store_true", help="Enable detailed logging")
    p.set_defaults(func=run)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _yaml_quote(value: str) -> str:
    """
    Minimal YAML quoting for scalars in our report.

    Keep unquoted values when they are plainly safe; otherwise use JSON-style
    quoting which is also valid in YAML.
    """
    safe = (
        value != ""
        and all(ch.isalnum() or ch in "._/-" for ch in value)
        and value
        not in {
            "null",
            "Null",
            "NULL",
            "true",
            "True",
            "TRUE",
            "false",
            "False",
            "FALSE",
        }
    )
    if safe:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _format_assets_yaml(assets: list[dict[str, str]]) -> str:
    # Always produce a list of dicts at top level, even if empty
    if not assets:
        return "[]\n"
    lines: list[str] = []
    for item in assets:
        lines.append("- path: " + _yaml_quote(item["path"]))
        lines.append("  sha256: " + _yaml_quote(item["sha256"]))
        lines.append("  origin: " + _yaml_quote(item["origin"]))
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace, ctx: RunContext) -> int:
    dry_run = getattr(args, "dry_run", False)
    verbose = getattr(args, "verbose", False)
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
    del args  # unused (kept for the CLI contract)

    assets_dir = ctx.paths.assets_dir
    output_assets_dir = ctx.paths.output_dir / "assets"
    report_path = ctx.paths.reports_dir / "assets.yaml"

    if not assets_dir.exists():
        logging.info("No assets directory found at %s", assets_dir)
        global_assets: list[tuple[str, Path]] = []
    else:
        global_assets = []
        for src in assets_dir.rglob("*"):
            # Skip hidden files and .scss files
            if src.is_file() and not src.name.startswith('.') and src.suffix.lower() != ".scss":
                rel = src.relative_to(assets_dir).as_posix()
                global_assets.append((rel, src))
        global_assets.sort(key=lambda item: item[0])
        logging.info("Found %d assets under %s", len(global_assets), assets_dir)

    assets: list[dict[str, str]] = []

    # Catalog global assets without copying
    for rel, src in global_assets:
        if dry_run:
            logging.info("[dry-run] catalog %s", src)
        else:
            logging.info("Cataloged asset: %s", rel)
        sha = _sha256_file(src)
        assets.append({"path": rel, "sha256": sha, "origin": "global"})

    # Prepare set of global asset relative paths for quick lookup
    global_asset_paths = {rel for rel, _ in global_assets}

    # Catalog page-local assets without copying
    content_dir = ctx.paths.content_dir
    if content_dir.exists():
        for md_path in content_dir.rglob("*.md"):
            md_dir = md_path.parent
            # Determine the output directory for this markdown file's rendered HTML
            # We assume the output HTML will be placed preserving the relative path from content_dir,
            # but with .html extension instead of .md
            rel_md_dir = md_dir.relative_to(content_dir)
            output_page_dir = ctx.paths.output_dir / rel_md_dir

            # Scan for non-markdown files in the same directory
            for local_asset in md_dir.iterdir():
                # Skip hidden files, .md files, and .scss files
                if local_asset.is_file() and not local_asset.name.startswith('.') and local_asset.suffix.lower() not in [".md", ".scss"]:
                    # Compute relative path of the local asset relative to content_dir
                    local_asset_rel = local_asset.relative_to(content_dir).as_posix()
                    # Skip if already included as a global asset
                    if local_asset_rel in global_asset_paths:
                        continue
                    if dry_run:
                        logging.info("[dry-run] catalog page-local asset %s", local_asset)
                    else:
                        logging.info("Cataloged page-local asset: %s (for page %s)", local_asset_rel, md_path.relative_to(content_dir))
                    sha = _sha256_file(local_asset)
                    assets.append({"path": local_asset_rel, "sha256": sha, "origin": "page-local"})

    # Note: JS, fonts, and other future asset types may be added to the include list later

    if dry_run:
        logging.info("[dry-run] would write report: %s", report_path)
        return 0

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _format_assets_yaml(assets),
        encoding="utf-8",
    )
    logging.info("Wrote asset report: %s", report_path)
    return 0
