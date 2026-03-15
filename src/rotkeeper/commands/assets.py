from __future__ import annotations

import argparse
import hashlib
import logging
import shutil
from pathlib import Path

from ..context import RunContext


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("assets", help="Copy static assets and write an assets.yaml report")
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
    if not assets:
        return "assets: []\n"
    lines: list[str] = ["assets:"]
    for item in assets:
        lines.append(f"  - path: {_yaml_quote(item['path'])}")
        lines.append(f"    sha256: {_yaml_quote(item['sha256'])}")
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace, ctx: RunContext) -> int:
    del args  # unused (kept for the CLI contract)

    assets_dir = ctx.paths.assets_dir
    output_assets_dir = ctx.paths.output_dir / "assets"
    report_path = ctx.paths.reports_dir / "assets.yaml"

    if not assets_dir.exists():
        logging.info("No assets directory found at %s", assets_dir)
        assets: list[dict[str, str]] = []
    else:
        discovered: list[tuple[str, Path]] = []
        for src in assets_dir.rglob("*"):
            if src.is_file():
                rel = src.relative_to(assets_dir).as_posix()
                discovered.append((rel, src))
        discovered.sort(key=lambda item: item[0])
        logging.info("Found %d assets under %s", len(discovered), assets_dir)

        assets = []
        for rel, src in discovered:
            dest = output_assets_dir / rel
            if ctx.dry_run:
                logging.info("[dry-run] copy %s -> %s", src, dest)
                sha = _sha256_file(src)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                logging.info("Copied asset: %s", rel)
                sha = _sha256_file(dest)
            assets.append({"path": rel, "sha256": sha})

    report_obj = {"assets": assets}

    if ctx.dry_run:
        logging.info("[dry-run] would ensure directory exists: %s", output_assets_dir)
        logging.info("[dry-run] would write report: %s", report_path)
        return 0

    output_assets_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _format_assets_yaml(report_obj["assets"]),
        encoding="utf-8",
    )
    logging.info("Wrote asset report: %s", report_path)
    return 0
