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
    del args  # unused (kept for the CLI contract)

    output_dir = ctx.paths.output_dir
    output_assets_dir = output_dir / "assets"
    resources_dir = ctx.paths.home_dir / "resources"
    bones_assets_dir = ctx.paths.assets_dir

    if not output_dir.exists():
        logging.info("Output directory not found at %s", output_dir)
        return 0

    html_files = sorted(output_dir.rglob("*.html"))
    if not html_files:
        logging.info("No HTML files found under %s", output_dir)
        return 0

    seen: set[str] = set()

    for html_path in html_files:
        html_rel = html_path.relative_to(output_dir)
        md_path = ctx.paths.home_dir / html_rel.with_suffix(".md")
        md_dir = md_path.parent
        for ref in _collect_refs_from_html(html_path):
            ref = ref.strip()
            if not ref or _is_external(ref) or ref.startswith("//"):
                continue

            ref_path = _strip_query_fragment(ref).strip()
            if not ref_path:
                continue

            rel = Path(ref_path.lstrip("/"))
            resolved = _resolve_asset(
                rel,
                md_dir=md_dir,
                resources_dir=resources_dir,
                bones_assets_dir=bones_assets_dir,
            )
            if resolved is None:
                logging.warning("Missing asset for reference %s", ref)
                continue

            src, origin, root_resolved = resolved

            if origin == "markdown":
                # namespace using the markdown page directory
                page_dir = md_path.stem
                dest_rel = Path(page_dir) / src.name
            else:
                dest_rel = src.relative_to(root_resolved)

            rel_key = dest_rel.as_posix()
            if rel_key in seen:
                continue
            seen.add(rel_key)

            dest = output_assets_dir / dest_rel
            if ctx.dry_run:
                logging.info("[dry-run] copy %s -> %s", src, dest)
                continue

            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            logging.info("Copied asset: %s", rel_key)

    return 0
