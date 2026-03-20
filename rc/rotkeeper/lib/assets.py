from __future__ import annotations

import argparse
import hashlib
import logging
from pathlib import Path

from ..context import RunContext
from ..config import CONFIG


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("assets", help="Catalog static assets and write an assets.yaml report")
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
        and value not in {
            "null", "Null", "NULL",
            "true", "True", "TRUE",
            "false", "False", "FALSE",
        }
    )
    if safe:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _format_assets_yaml(assets: list[dict[str, str]]) -> str:
    if not assets:
        return "[]\n"
    lines: list[str] = []
    for item in assets:
        lines.append("- path: " + _yaml_quote(item["path"]))
        lines.append("  sha256: " + _yaml_quote(item["sha256"]))
        lines.append("  origin: " + _yaml_quote(item["origin"]))
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    dry_run = ctx.dry_run if ctx is not None else getattr(args, "dry_run", False)
    verbose = ctx.verbose if ctx is not None else getattr(args, "verbose", False)

    if verbose:
        logging.getLogger().setLevel(logging.INFO)

    assets_dir = CONFIG.BONES / "assets"
    report_path = CONFIG.BONES / "reports" / "assets.yaml"

    # --- Global assets (bones/assets/) ---
    if not assets_dir.exists():
        logging.info("No assets directory found at %s", assets_dir)
        global_assets: list[tuple[str, Path]] = []
    else:
        global_assets = [
            (src.relative_to(assets_dir).as_posix(), src)
            for src in assets_dir.rglob("*")
            if src.is_file()
            and not src.name.startswith(".")
            and src.suffix.lower() != ".scss"
        ]
        global_assets.sort(key=lambda item: item[0])
        logging.info("Found %d assets under %s", len(global_assets), assets_dir)

    assets: list[dict[str, str]] = []

    for rel, src in global_assets:
        if dry_run:
            logging.info("[dry-run] catalog %s", src)
        else:
            logging.info("Cataloged asset: %s", rel)
            sha = _sha256_file(src)
            assets.append({"path": rel, "sha256": sha, "origin": "global"})

    # --- Page-local assets (home/content/, i.e. CONFIG.CONTENT_DIR) ---
    global_asset_paths = {rel for rel, _ in global_assets}
    content_dir = CONFIG.CONTENT_DIR  # was incorrectly CONFIG.BONES / "content"

    if content_dir.exists():
        for md_path in content_dir.rglob("*.md"):
            for local_asset in md_path.parent.iterdir():
                if not local_asset.is_file():
                    continue
                if local_asset.name.startswith("."):
                    continue
                if local_asset.suffix.lower() in {".md", ".scss"}:
                    continue
                local_asset_rel = local_asset.relative_to(content_dir).as_posix()
                if local_asset_rel in global_asset_paths:
                    continue
                if dry_run:
                    logging.info("[dry-run] catalog page-local asset %s", local_asset)
                else:
                    logging.info(
                        "Cataloged page-local asset: %s (for page %s)",
                        local_asset_rel,
                        md_path.relative_to(content_dir),
                    )
                    sha = _sha256_file(local_asset)
                    assets.append({"path": local_asset_rel, "sha256": sha, "origin": "page-local"})

    if dry_run:
        logging.info("[dry-run] would write report: %s", report_path)
        return 0

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_format_assets_yaml(assets), encoding="utf-8")
    logging.info("Wrote asset report: %s", report_path)
    return 0
