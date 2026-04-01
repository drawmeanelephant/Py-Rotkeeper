from __future__ import annotations

import argparse
import hashlib
import logging
from pathlib import Path

from ..context import RunContext
from ..config import CONFIG


def add_parser(subs: argparse.SubParsersAction) -> None:
    p = subs.add_parser("assets", help="Catalog static assets and write an assets.yaml report")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done without copying")
    p.add_argument("--verbose", action="store_true", help="Enable detailed logging")
    p.set_defaults(func=run)


def sha256file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def yaml_quote(value: str) -> str:
    safe = (
        value
        and value == value
        and all(ch.isalnum() or ch in "-_." for ch in value)
        and value not in ("null", "Null", "NULL", "true", "True", "TRUE", "false", "False", "FALSE")
    )
    if safe:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def format_assets_yaml(assets: list[dict[str, str]]) -> str:
    if not assets:
        return ""
    lines: list[str] = []
    for item in assets:
        lines.append(f"- path: {yaml_quote(item['path'])}")
        lines.append(f"  sha256: {yaml_quote(item['sha256'])}")
        lines.append(f"  origin: {yaml_quote(item['origin'])}")
    return "\n".join(lines)


ALLOWED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".css", ".js",
    ".mp4", ".mp3", ".ogg", ".wav", ".webm",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
}


def is_asset_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name.startswith("."):
        return False
    if path.suffix.lower() in {".md", ".yaml", ".yml", ".html", ".htm", ".scss"}:
        return False
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False
    return True


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    # Normalize args/ctx in case they were passed in swapped order
    if ctx is None or not hasattr(ctx, "dryrun"):
        args, ctx = ctx, args
    dryrun = getattr(ctx, "dryrun", getattr(args, "dry_run", False))
    verbose = getattr(ctx, "verbose", getattr(args, "verbose", False))
    if verbose:
        logging.getLogger().setLevel(logging.INFO)

    cfg = ctx.config if ctx and ctx.config else CONFIG  # respect --config

    # Global assets live at bones/assets/ — paths catalogued as assets/<rel>
    # so that collect-assets can locate sources at cfg.HOME / "assets" / <rel>.
    bones_assets_dir = cfg.BONES / "assets"
    report_path = cfg.BONES / "reports" / "assets.yaml"

    # ------------------------------------------------------------------ #
    # 1. Global assets — bones/assets/**                                   #
    #    Catalog path as  assets/<rel-to-bones-assets-dir>                 #
    #    Source on disk:  bones/assets/<rel>                               #
    #    collect-assets:  src = cfg.HOME / "assets" / <rel>               #
    #                     dest = output/assets/<rel>                       #
    # ------------------------------------------------------------------ #
    global_assets: list[tuple[str, Path]] = []
    if bones_assets_dir.exists():
        global_assets = [
            (src.relative_to(bones_assets_dir).as_posix(), src)
            for src in bones_assets_dir.rglob("*")
            if is_asset_file(src)
        ]
        global_assets.sort(key=lambda item: item[0])
        logging.info("Found %d assets under %s", len(global_assets), bones_assets_dir)
    else:
        logging.info("No assets directory found at %s", bones_assets_dir)

    assets: list[dict[str, str]] = []

    for rel, src in global_assets:
        # path field: "assets/<rel>" — collect-assets strips "assets/" prefix
        # to find src at cfg.HOME / "assets" / rel, then writes to output/assets/<rel>
        full_rel = f"assets/{rel}"
        if dryrun:
            logging.info("dry-run catalog %s", src)
        else:
            logging.info("Cataloged asset %s", full_rel)
        sha = sha256file(src)
        assets.append({"path": full_rel, "sha256": sha, "origin": "global"})

    global_asset_paths = {f"assets/{rel}" for rel, _ in global_assets}

    # ------------------------------------------------------------------ #
    # 2. Page-local assets — home/ (content dir)                          #
    #    Catalog path as  content/<rel-to-contentdir>                     #
    #    collect-assets resolves src from page context via assets.yaml    #
    # ------------------------------------------------------------------ #
    content_dir = cfg.CONTENT_DIR  # respect --config
    if content_dir.exists():
        for path in content_dir.rglob("*"):
            if not is_asset_file(path):
                continue
            rel_path = path.relative_to(content_dir).as_posix()
            full_rel_path = f"content/{rel_path}"
            if full_rel_path in global_asset_paths:
                continue
            if dryrun:
                logging.info("dry-run catalog page-local asset %s", path)
            else:
                logging.info("Cataloged page-local asset %s", full_rel_path)
            sha = sha256file(path)
            assets.append({"path": full_rel_path, "sha256": sha, "origin": "page-local"})

    if dryrun:
        logging.info("dry-run would write report %s", report_path)
        return 0

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(format_assets_yaml(assets), encoding="utf-8")
    logging.info("Wrote asset report %s", report_path)
    return 0
