from __future__ import annotations
import argparse
import logging
import re
from datetime import date
from pathlib import Path

from rotkeeper.config import CONFIG
from rotkeeper.context import RunContext


def add_parser(subparsers):
    p = subparsers.add_parser("book", help="Binder ritual: bundle scripts, docs, configs, content")
    p.add_argument(
        "--mode",
        choices=[
            "scriptbook-full", "docbook", "docbook-clean",
            "configbook", "contentbook", "contentmeta",
            "collapse", "all",
        ],
        default="all",
    )
    p.add_argument("--dry-run", action="store_true", default=False)
    p.add_argument("--strip-frontmatter", action="store_true", default=False)
    p.set_defaults(func=run)
    return p


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    dry   = bool(getattr(args, "dry_run", False)) or (ctx.dry_run if ctx else False)
    strip = bool(getattr(args, "strip_frontmatter", False))
    cfg   = ctx.config if (ctx and ctx.config) else CONFIG  # respect --config
    reports = cfg.BONES / "reports"
    mode  = args.mode

    logging.debug("book: mode=%s reports=%s dry=%s", mode, reports, dry)

    if not dry:
        reports.mkdir(parents=True, exist_ok=True)

    dispatch = {
        "scriptbook-full": _scriptbook_full,
        "docbook":         _docbook,
        "docbook-clean":   _docbook_clean,
        "configbook":      _configbook,
        "contentbook":     _contentbook,
        "contentmeta":     _contentmeta,
        "collapse":        _collapse,
    }

    if mode == "all":
        targets = ["scriptbook-full", "docbook", "docbook-clean"]
    else:
        targets = [mode]

    for m in targets:
        if dry:
            logging.info("DRY-RUN: would run book mode=%s -> %s", m, reports)
        else:
            dispatch[m](reports, strip, cfg)

    return 0


# ── helpers ───────────────────────────────────────────────────────────────────

def _frontmatter_and_body(path: Path) -> tuple[dict[str, str], str]:
    """Split a markdown file into a frontmatter dict and body text."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].startswith("---"):
        return {}, text
    end = next((i for i, l in enumerate(lines[1:], 1) if l.startswith("---")), None)
    if end is None:
        return {}, text
    fm_lines = lines[1:end]
    body = "".join(lines[end + 1:])
    fm: dict[str, str] = {}
    for l in fm_lines:
        if ":" in l:
            k, _, v = l.partition(":")
            fm[k.strip()] = v.strip().strip('"')
    return fm, body


def _write_header(out: Path, title: str, subtitle: str) -> None:
    today = date.today().isoformat()
    out.write_text(
        f'---\ntitle: "{title}"\nsubtitle: "{subtitle}"\ngenerated: "{today}"\n---\n\n',
        encoding="utf-8",
    )


def _append_file_block(out: Path, rel: str, content: str) -> None:
    with out.open("a", encoding="utf-8") as f:
        f.write(f"<!-- START: {rel} -->\n\n")
        f.write(content)
        if not content.endswith("\n"):
            f.write("\n")
        f.write(f"<!-- END: {rel} -->\n\n")


# ── modes ──────────────────────────────────────────────────────────────────────

def _scriptbook_full(reports: Path, strip: bool, cfg) -> None:
    out = reports / "rotkeeper-scriptbook-full.md"
    src_root = cfg.ROOT_DIR / "rc"
    _write_header(out, "Rotkeeper Scriptbook (Full)",
                  "All Python source files under rc/ with path markers")
    if not src_root.exists():
        logging.warning("book: scriptbook-full: src dir not found: %s", src_root)
        return
    for f in sorted(src_root.rglob("*.py")):
        rel = str(f.relative_to(cfg.ROOT_DIR))
        _append_file_block(out, rel, f.read_text(encoding="utf-8"))
    logging.info("book: scriptbook-full -> %s", out)


def _docbook(reports: Path, strip: bool, cfg) -> None:
    out = reports / "rotkeeper-docbook.md"
    _write_header(out, "Rotkeeper Docbook",
                  "All markdown documentation in home/content/docs/ with path markers")
    docs_dir = cfg.HOME / "content" / "docs"
    if not docs_dir.exists():
        logging.warning("book: docbook: docs dir not found: %s", docs_dir)
        return
    for f in sorted(docs_dir.rglob("*.md")):
        rel = str(f.relative_to(cfg.HOME))
        fm, body = _frontmatter_and_body(f)
        content = body if strip else f.read_text(encoding="utf-8")
        _append_file_block(out, rel, content)
    logging.info("book: docbook -> %s", out)


def _docbook_clean(reports: Path, strip: bool, cfg) -> None:
    out = reports / "rotkeeper-docbook-clean.md"
    _write_header(out, "Home Content (Cleaned)",
                  "Frontmatter-stripped, collapse-friendly version")
    docs_dir = cfg.HOME / "content" / "docs"
    if not docs_dir.exists():
        logging.warning("book: docbook-clean: docs dir not found: %s", docs_dir)
        return
    with out.open("a", encoding="utf-8") as fh:
        for f in sorted(docs_dir.rglob("*.md")):
            fm, body = _frontmatter_and_body(f)
            title = fm.get("title") or f.stem
            fh.write(f"## {title}\n\n")
            fh.write(body.lstrip("\n"))
            fh.write("\n\n")
    logging.info("book: docbook-clean -> %s", out)


def _configbook(reports: Path, strip: bool, cfg) -> None:
    out = reports / "rotkeeper-configbook.md"
    _write_header(out, "Rotkeeper Configbook",
                  "YAML configuration and templates used by rotkeeper")
    config_dir    = cfg.BONES / "config"
    templates_dir = cfg.BONES / "templates"
    globs = []
    for d in [config_dir, templates_dir]:
        if d.exists():
            globs += list(d.rglob("*.yaml"))
            globs += list(d.rglob("*.yml"))
            globs += list(d.rglob("*.tpl"))
            globs += list(d.rglob("*.html"))
    for f in sorted(globs, key=lambda p: str(p)):
        rel = str(f.relative_to(cfg.BASE_DIR))
        lines = [l for l in f.read_text(encoding="utf-8").splitlines(keepends=True)
                 if l.strip() != "```"]
        _append_file_block(out, rel, "".join(lines))
    logging.info("book: configbook -> %s", out)


def _contentbook(reports: Path, strip: bool, cfg) -> None:
    out = reports / "rotkeeper-contentbook.md"
    _write_header(out, "Rotkeeper Contentbook",
                  "All markdown in home/content/ with path markers")
    content_dir = cfg.HOME / "content"
    if not content_dir.exists():
        logging.warning("book: contentbook: content dir not found: %s", content_dir)
        return
    for f in sorted(content_dir.rglob("*.md")):
        rel = str(f.relative_to(cfg.HOME))
        fm, body = _frontmatter_and_body(f)
        content = body if strip else f.read_text(encoding="utf-8")
        _append_file_block(out, rel, content)
    logging.info("book: contentbook -> %s", out)


def _contentmeta(reports: Path, strip: bool, cfg) -> None:
    out = reports / "rotkeeper-contentmeta.yaml"
    content_dir = cfg.HOME / "content"
    if not content_dir.exists():
        logging.warning("book: contentmeta: content dir not found: %s", content_dir)
        return
    lines: list[str] = []
    for f in sorted(content_dir.rglob("*.md")):
        rel = str(f.relative_to(cfg.HOME))
        fm, _ = _frontmatter_and_body(f)
        lines.append(f'- path: "{rel}"')
        for k, v in fm.items():
            lines.append(f"  {k}: {v}")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    logging.info("book: contentmeta -> %s", out)


def _collapse(reports: Path, strip: bool, cfg) -> None:
    out = reports / "collapsed-content.yaml"
    entries: list[str] = []
    for f in sorted(reports.glob("rotkeeper-*.md")):
        logging.debug("book: collapse reading %s", f)
        fm, body = _frontmatter_and_body(f)
        title    = fm.get("title") or f.stem
        subtitle = fm.get("subtitle", "")
        indented_body = "\n".join("    " + l for l in body.splitlines())
        entries.append(
            f'- filename: "{f.name}"\n'
            f'  title: "{title}"\n'
            f'  subtitle: "{subtitle}"\n'
            f'  body: |\n'
            f'{indented_body}\n'
        )
    out.write_text("\n".join(entries) + "\n", encoding="utf-8")
    logging.info("book: collapse -> %s", out)
