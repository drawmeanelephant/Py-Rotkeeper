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


def _is_external(ref: str) -> bool:
    ref = ref.lower()
    return ref.startswith("http") or ref.startswith("https") or ref.startswith("data")


def _strip_query_fragment(ref: str) -> str:
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
    htmlpath: Path,
    outputdir: Path,
    bonesassetsdir: Path,
    homeassetsdir: Path,
    homecontentdir: Path,
) -> tuple[Path, Path] | None:
    """Resolve a ref string to (src, dest) paths, or None if unresolvable.

    Resolution order for absolute /assets/... refs:
      1. bones/assets/<inner>   — global assets catalogued by the assets step
      2. home/assets/<inner>    — page-local assets under content dir

    For page-relative refs, resolve against the html file's directory and
    try to trace back to a source under bones/assets or home.
    """
    clean = _strip_query_fragment(ref).lstrip("/")

    if clean.startswith("assets/"):
        rel = Path(clean)
        inner = Path(*rel.parts[1:])
        # Try bones/assets first (global), then home/assets (page-local)
        for candidate_root in (bonesassetsdir, homeassetsdir):
            src = candidate_root / inner
            if src.exists() and src.is_file():
                dest = outputdir / rel
                return src, dest
        logging.warning("Global asset source missing: /%s (not found in bones/assets or home/assets)", clean)
        return None

    # Page-relative ref — resolve against the html file's parent directory
    destabs = (htmlpath.parent / clean).resolve()
    outputdirabs = outputdir.resolve()
    try:
        destrel = destabs.relative_to(outputdirabs)
    except ValueError:
        logging.warning("Skipping ref that escapes output dir: %s from %s", ref, htmlpath)
        return None

    dest = outputdirabs / destrel

    # Try to find the source: check if destrel is under output/assets/,
    # then trace back to bones/assets or home
    outputassetsabs = (outputdir / "assets").resolve()
    try:
        asset_inner = destabs.relative_to(outputassetsabs)
        for candidate_root in (bonesassetsdir, homeassetsdir):
            src = candidate_root / asset_inner
            if src.exists() and src.is_file():
                return src, dest
    except ValueError:
        pass

    # Fall back: assume page-relative asset lives next to the .md source
    src = homecontentdir / destrel
    if src.exists() and src.is_file():
        return src, dest

    logging.warning("Page-relative asset source missing: %s -> %s from %s", ref, src, htmlpath)
    return None


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    cfg = ctx.config if ctx is not None and ctx.config is not None else CONFIG
    outputdir = cfg.OUTPUTDIR
    bonesassetsdir = cfg.BONES / "assets"
    homeassetsdir = cfg.HOME / "assets"
    homecontentdir = cfg.HOME
    dry_run = ctx.dry_run if ctx is not None else False
    verbose = ctx.verbose if ctx is not None else False

    if verbose:
        logging.getLogger().setLevel(logging.INFO)

    if not outputdir.exists():
        logging.info("Output directory not found at %s", outputdir)
        return 0

    copied = 0
    skipped = 0

    for htmlpath in sorted(outputdir.rglob("*.html")):
        refs = collect_refs_from_html(htmlpath)
        for ref in refs:
            if _is_external(ref):
                continue
            result = resolve_ref(
                ref, htmlpath, outputdir,
                bonesassetsdir, homeassetsdir, homecontentdir,
            )
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
                logging.info("dry-run copy %s -> %s", src, dest)
                copied += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if verbose:
                logging.info("Copied %s -> %s", src, dest)
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
