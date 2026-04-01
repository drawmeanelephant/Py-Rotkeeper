from __future__ import annotations

import argparse
import logging
import shutil
from html.parser import HTMLParser
from pathlib import Path

from ..config import CONFIG
from ..context import RunContext


class ResourceParser(HTMLParser):
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


def add_parser(subs: argparse.SubParsersAction) -> None:
    p = subs.add_parser("collect-assets", help="Collect referenced assets into output/assets")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done without copying")
    p.add_argument("--verbose", action="store_true", help="Enable detailed logging")
    p.set_defaults(func=run)


def is_external(ref: str) -> bool:
    ref = ref.lower()
    return ref.startswith("http") or ref.startswith("https") or ref.startswith("data:")


def strip_query_fragment(ref: str) -> str:
    ref = ref.split("#", 1)[0]
    ref = ref.split("?", 1)[0]
    return ref


def collect_refs_from_html(path: Path) -> list[str]:
    parser = ResourceParser()
    html = path.read_text(encoding="utf-8", errors="ignore")
    parser.feed(html)
    return parser.refs


def resolve_ref(
    ref: str,
    html_path: Path,
    outputdir: Path,
    home_assets_dir: Path,
    home_content_dir: Path,
) -> tuple[Path, Path] | None:
    clean = strip_query_fragment(ref).lstrip("/")

    if clean.startswith("assets/"):
        rel = Path(clean)
        inner = Path(*rel.parts[1:])
        src = home_assets_dir / inner
        dest = outputdir / rel
        if src.exists() and src.is_file():
            return src, dest
        logging.warning("Global asset source missing: %s (resolved to %s)", ref, src)
        return None

    dest_abs = (html_path.parent / clean).resolve()
    outputdir_abs = outputdir.resolve()

    try:
        dest_rel = dest_abs.relative_to(outputdir_abs)
    except ValueError:
        logging.warning("Skipping ref that escapes output dir: %s (from %s)", ref, html_path)
        return None

    dest = outputdir_abs / dest_rel
    outputassets_abs = (outputdir / "assets").resolve()

    try:
        asset_inner = dest_abs.relative_to(outputassets_abs)
        src = home_assets_dir / asset_inner
    except ValueError:
        src = home_content_dir / dest_rel

    if src.exists() and src.is_file():
        return src, dest

    logging.warning("Page-relative asset source missing: %s -> %s (from %s)", ref, src, html_path)
    return None


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    cfg = ctx.config if (ctx is not None and ctx.config is not None) else CONFIG
    outputdir = cfg.OUTPUT_DIR
    home_assets_dir = cfg.HOME / "assets"
    home_content_dir = cfg.CONTENT_DIR

    dry_run = getattr(args, "dry_run", False)
    verbose = getattr(args, "verbose", False)
    if ctx is not None:
        dry_run = ctx.dry_run
        verbose = ctx.verbose

    if verbose:
        logging.getLogger().setLevel(logging.INFO)

    if not outputdir.exists():
        logging.info("Output directory not found at %s", outputdir)
        return 0

    copied = 0
    skipped = 0

    for html_path in sorted(outputdir.rglob("*.html")):
        refs = collect_refs_from_html(html_path)
        for ref in refs:
            if is_external(ref):
                continue
            result = resolve_ref(ref, html_path, outputdir, home_assets_dir, home_content_dir)
            if result is None:
                skipped += 1
                continue
            src, dest = result
            if dest.exists():
                try:
                    if _sha256(src) == _sha256(dest):
                        if verbose:
                            logging.info("Already up-to-date: %s", dest)
                        skipped += 1
                        continue
                except Exception as e:
                    logging.warning("Hash check failed for %s: %s", dest, e)
            if dry_run:
                logging.info("dry-run copy: %s -> %s", src, dest)
                copied += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if verbose:
                logging.info("Copied: %s -> %s", src, dest)
            copied += 1

    logging.info("collect-assets: %d copied, %d skipped/up-to-date", copied, skipped)
    return 0


def _sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
