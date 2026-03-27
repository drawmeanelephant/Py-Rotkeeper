---
title: "Rotkeeper Scriptbook (Full)"
subtitle: "All Python source files under rc/ with path markers"
generated: "2026-03-24"
---

<!-- START: rc/rotkeeper/__init__.py -->

__all__ = ["__version__"]

__version__ = "0.1.0"

<!-- END: rc/rotkeeper/__init__.py -->

<!-- START: rc/rotkeeper/__main__.py -->

from .rc import main


if __name__ == "__main__":
    raise SystemExit(main())
<!-- END: rc/rotkeeper/__main__.py -->

<!-- START: rc/rotkeeper/config.py -->

# rc/rotkeeper/config.py
from pathlib import Path
import logging
import yaml

logger = logging.getLogger(__name__)


class Config:
    """Central configuration singleton for Rotkeeper.

    Holds paths, flags, scenario info, and dependencies.
    Scripts query this instead of hardcoding anything.
    """

    def __init__(self):
        self.ROOT_DIR = Path(__file__).resolve().parent.parent.parent
        self.BASE_DIR = Path.cwd()
        self.BONES    = self.BASE_DIR / "bones"
        self.HOME     = self.BASE_DIR / "home"
        self.CONTENT_DIR = self.HOME / "content"
        self.OUTPUT_DIR  = self.HOME / "output"
        self.default_template = None
        self.SCENARIO = "default"
        self.DEPENDENCIES = {
            "pandoc": {"check": ["pandoc", "--version"], "required": True},
            "sass":   {"check": ["sass",   "--version"], "required": False},
            "node":   {"check": ["node",   "--version"], "required": False},
        }

        user_config_path = self.BONES / "config" / "user-config.yaml"
        if user_config_path.exists():
            try:
                with open(user_config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                self._apply(data)
            except yaml.YAMLError as e:
                logger.error(
                    "user-config.yaml is malformed and will be ignored: %s", e
                )

    # ------------------------------------------------------------------
    # Overridable output paths (set via _apply / load)
    # ------------------------------------------------------------------

    @property
    def REPORTS_DIR(self) -> Path:
        return getattr(self, "_reports_dir", self.BONES / "reports")

    @property
    def GENERATED_CONTENT_DIR(self) -> Path:
        return getattr(self, "_generated_content_dir", self.CONTENT_DIR / "generated")

    # ROOTDIR alias for any legacy references
    @property
    def ROOTDIR(self) -> Path:
        return self.ROOT_DIR

    # ------------------------------------------------------------------

    def _apply(self, data: dict) -> None:
        """Apply a config dict, overriding current values."""
        if not data:
            return

        known = {
            "HOME", "CONTENT_DIR", "OUTPUT_DIR", "default_template",
            "SCENARIO", "REPORTS_DIR", "GENERATED_CONTENT_DIR",
        }
        unknown = set(data.keys()) - known
        if unknown:
            logger.warning(
                "Unrecognized keys in config (typo?): %s", sorted(unknown)
            )

        if "HOME" in data:
            self.HOME = (self.BASE_DIR / data["HOME"]).resolve()
        if "CONTENT_DIR" in data:
            self.CONTENT_DIR = (self.BASE_DIR / data["CONTENT_DIR"]).resolve()
        if "OUTPUT_DIR" in data:
            self.OUTPUT_DIR = (self.BASE_DIR / data["OUTPUT_DIR"]).resolve()
        if "default_template" in data:
            self.default_template = data["default_template"]
        if "SCENARIO" in data:
            self.SCENARIO = data["SCENARIO"]
        if "REPORTS_DIR" in data:
            self._reports_dir = (self.BASE_DIR / data["REPORTS_DIR"]).resolve()
        if "GENERATED_CONTENT_DIR" in data:
            self._generated_content_dir = (
                self.BASE_DIR / data["GENERATED_CONTENT_DIR"]
            ).resolve()

    def load(self, path: Path) -> None:
        """Load configuration overrides from a YAML file.

        When a config file is explicitly loaded, BASE_DIR is rebound to the
        project root inferred from the config file's location. This supports
        running rotkeeper from outside the project directory, e.g.:

            rotkeeper --config /sites/site-a/bones/config/user-config.yaml render

        Assumes the config file lives at <project_root>/bones/config/*.yaml,
        so project root = config_file.parent.parent.parent.
        If the file is not in that structure, BASE_DIR stays as Path.cwd().
        """
        if not path.exists():
            logger.warning(
                "Config path not found: %s — running with defaults", path
            )
            return

        inferred_root = path.resolve().parent.parent.parent
        if inferred_root.exists():
            self.BASE_DIR = inferred_root
            self.BONES    = self.BASE_DIR / "bones"
            self.HOME     = self.BASE_DIR / "home"
            self.CONTENT_DIR = self.HOME / "content"
            self.OUTPUT_DIR  = self.HOME / "output"
            logger.debug("Config: BASE_DIR rebound to %s", self.BASE_DIR)
        else:
            logger.warning(
                "Could not infer project root from config path %s — "
                "expected <root>/bones/config/<file>.yaml layout. "
                "Keeping BASE_DIR=%s",
                path, self.BASE_DIR,
            )

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(
                "Invalid YAML in config %s: %s — running with defaults", path, e
            )
            return

        self._apply(data)

    # ------------------------------------------------------------------

    def output_path(self, filename: str) -> Path:
        """Compute output path for a given file under the current scenario."""
        return self.OUTPUT_DIR / self.SCENARIO / filename


CONFIG = Config()
<!-- END: rc/rotkeeper/config.py -->

<!-- START: rc/rotkeeper/context.py -->

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunContext:
    dry_run: bool
    verbose: bool
    log_file: Path | None
    config: object | None = None
    # sitemap-pipeline stage flags
    index_only: bool = False
    metadata_only: bool = False
    write_only: bool = False
<!-- END: rc/rotkeeper/context.py -->

<!-- START: rc/rotkeeper/deps.py -->

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass

from .exec import run


class MissingDependencyError(RuntimeError):
    pass


@dataclass(frozen=True)
class PandocInfo:
    path: str
    version: str | None


def require_bins(*names: str) -> None:
    missing = [n for n in names if shutil.which(n) is None]
    if missing:
        raise MissingDependencyError(f"Missing required dependencies: {', '.join(missing)}")


def get_pandoc_info() -> PandocInfo:
    require_bins("pandoc")
    pandoc_path = shutil.which("pandoc")
    assert pandoc_path is not None

    version = None
    try:
        res = run(["pandoc", "--version"], check=False)
        first = (res.stdout.splitlines() or [""])[0]
        m = re.search(r"\b(\d+\.\d+(?:\.\d+)?)\b", first)
        version = m.group(1) if m else None
    except Exception:
        version = None

    return PandocInfo(path=pandoc_path, version=version)


def try_import_pypandoc() -> bool:
    try:
        import pypandoc  # noqa: F401
    except Exception:
        return False
    return True

<!-- END: rc/rotkeeper/deps.py -->

<!-- START: rc/rotkeeper/exec.py -->

from __future__ import annotations

import logging
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class ExecResult:
    returncode: int
    stdout: str
    stderr: str
    success: bool = False

    def __post_init__(self):
        object.__setattr__(self, 'success', self.returncode == 0)


class ExecError(RuntimeError):
    def __init__(self, message: str, *, result: ExecResult | None = None) -> None:
        super().__init__(message)
        self.result = result


def _format_cmd(cmd: Sequence[str] | str) -> str:
    if isinstance(cmd, str):
        return cmd
    return " ".join(shlex.quote(p) for p in cmd)


def run(
    cmd: Sequence[str] | str,
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    dry_run: bool = False,
    verbose: bool = False,
    check: bool = True,
    default_cwd: Path | None = None,
) -> ExecResult:
    """
    Execute a subprocess command.

    Stub-friendly contract: always returns an ExecResult; raises ExecError on failure if check=True.
    """
    rendered = _format_cmd(cmd)
    if dry_run:
        return ExecResult(returncode=0, stdout=f"[DRY-RUN] {rendered}\n", stderr="")

    if verbose:
        logging.info(f"[exec] {rendered}")

    actual_cwd = cwd if cwd is not None else default_cwd

    completed = subprocess.run(
        cmd,
        cwd=str(actual_cwd) if actual_cwd is not None else None,
        env=env,
        text=True,
        capture_output=True,
        shell=isinstance(cmd, str),
    )
    result = ExecResult(
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )
    if check and result.returncode != 0:
        raise ExecError(f"Command failed ({result.returncode}): {rendered}", result=result)
    return result
<!-- END: rc/rotkeeper/exec.py -->

<!-- START: rc/rotkeeper/frontend_deps.py -->

import shutil
import logging

logger = logging.getLogger(__name__)

class MissingFrontendDependencyError(Exception):
    pass

def require_frontend_bins(*bins: str):
    missing_bins = []
    for bin_name in bins:
        if shutil.which(bin_name) is None:
            missing_bins.append(bin_name)

    if missing_bins:
        for bin_name in missing_bins:
            logger.error(f"Required frontend binary '{bin_name}' not found in PATH.")
        raise MissingFrontendDependencyError(f"Missing frontend dependencies: {', '.join(missing_bins)}")

def check_node():
    require_frontend_bins('node')

def check_sass():
    # Sass can be 'sass' (Dart Sass) or 'node-sass'
    if shutil.which('sass') is None and shutil.which('node-sass') is None:
        logger.error("Neither 'sass' nor 'node-sass' found in PATH.")
        raise MissingFrontendDependencyError("Missing frontend dependency: 'sass' or 'node-sass'")
<!-- END: rc/rotkeeper/frontend_deps.py -->

<!-- START: rc/rotkeeper/lib/__init__.py -->

from __future__ import annotations
import importlib
import pkgutil
from pathlib import Path

def get_commands():
    """
    Dynamically discover all lib modules that expose add_parser().
    """
    package_dir = Path(__file__).parent
    commands = []
    for finder, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        module = importlib.import_module(f".{module_name}", package=__name__)
        if hasattr(module, "add_parser"):
            commands.append((module_name, module.add_parser))
    return commands
<!-- END: rc/rotkeeper/lib/__init__.py -->

<!-- START: rc/rotkeeper/lib/assets.py -->

# rc/rotkeeper/lib/assets.py
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

    cfg = ctx.config if (ctx and ctx.config) else CONFIG  # respect --config

    assets_dir  = cfg.BONES / "assets"
    report_path = cfg.REPORTS_DIR / "assets.yaml"          # ← was cfg.BONES / "reports" / "assets.yaml"

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

    global_asset_paths = {rel for rel, _ in global_assets}
    content_dir = cfg.CONTENT_DIR  # respect --config

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
<!-- END: rc/rotkeeper/lib/assets.py -->

<!-- START: rc/rotkeeper/lib/book.py -->

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

def _scriptbook_full(reports: Path, strip: bool, cfg=CONFIG) -> None:
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


def _docbook(reports: Path, strip: bool, cfg=CONFIG) -> None:
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


def _docbook_clean(reports: Path, strip: bool, cfg=CONFIG) -> None:
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


def _configbook(reports: Path, strip: bool, cfg=CONFIG) -> None:
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


def _contentbook(reports: Path, strip: bool, cfg=CONFIG) -> None:
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


def _contentmeta(reports: Path, strip: bool, cfg=CONFIG) -> None:
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


def _collapse(reports: Path, strip: bool, cfg=CONFIG) -> None:
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
<!-- END: rc/rotkeeper/lib/book.py -->

<!-- START: rc/rotkeeper/lib/cleanup_bones.py -->

from __future__ import annotations

import argparse
import logging

from ..context import RunContext


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("cleanup-bones", help="Backup and prune bones/ (stub)")
    p.add_argument("--days", type=int, default=30, help="Retention window in days (stub)")
    p.add_argument("--yes", action="store_true", help="Skip confirmation (stub)")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext) -> int:
    logging.info("cleanup-bones (stub)")
    logging.debug("days=%s yes=%s", args.days, args.yes)
    return 0

<!-- END: rc/rotkeeper/lib/cleanup_bones.py -->

<!-- START: rc/rotkeeper/lib/collect_assets.py -->

# rc/rotkeeper/lib/collect_assets.py
from __future__ import annotations

import argparse
import logging
import shutil
from html.parser import HTMLParser
from pathlib import Path

from ..config import CONFIG


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


def run(args: argparse.Namespace, ctx=None) -> int:
    import yaml
    import hashlib

    cfg = ctx.config if (ctx and ctx.config) else CONFIG  # respect --config

    output_dir         = cfg.OUTPUT_DIR
    output_assets_dir  = output_dir / "assets"
    bones_reports_dir  = cfg.REPORTS_DIR                    # ← was cfg.BONES / "reports"
    assets_report_path = cfg.REPORTS_DIR / "assets.yaml"   # ← was bones_reports_dir / "assets.yaml"
    home_assets_dir    = cfg.HOME / "assets"
    home_content_dir   = cfg.CONTENT_DIR

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

    def sha256sum(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    for asset in assets_report:
        # ← new guard: skip malformed entries gracefully
        if not isinstance(asset, dict):
            logging.warning("Skipping malformed asset entry: %r", asset)
            continue

        asset_path   = asset.get("path")
        asset_hash   = asset.get("hash") or asset.get("sha256")
        asset_origin = asset.get("origin", "global")
        asset_abs    = asset.get("abs")
        page_html    = asset.get("page_html")
        page_md      = asset.get("page_md")

        if not asset_path or not asset_hash:
            logging.warning("Asset report entry missing path or hash: %r", asset)
            continue

        path_obj = Path(asset_path)
        if path_obj.name.startswith('.') or path_obj.suffix.lower() == ".scss":
            if verbose:
                logging.info("Skipping hidden or SCSS file: %s", asset_path)
            continue

        src = None
        if asset_abs:
            src = Path(asset_abs)
        else:
            if asset_origin == "global" or (asset_origin and "home/assets" in asset_origin):
                src = home_assets_dir / asset_path
            elif asset_origin == "page-local" or (asset_origin and "markdown" in asset_origin):
                if page_md:
                    src = Path(page_md).parent / Path(asset_path).name
                elif page_html:
                    md_dir = Path(page_html).with_suffix(".md").parent
                    src = md_dir / Path(asset_path).name
                else:
                    src = home_content_dir / asset_path
            else:
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

        if asset_origin == "global" or (asset_origin and "home/assets" in asset_origin):
            dest = output_assets_dir / asset_path
            dest_info = f"{src} -> {dest}"
        elif asset_origin == "page-local" or (asset_origin and "markdown" in asset_origin):
            if page_html:
                html_path = output_dir / page_html
                dest = html_path.parent / Path(asset_path).name
            elif page_md:
                html_path = output_dir / Path(page_md).with_suffix(".html")
                dest = html_path.parent / Path(asset_path).name
            else:
                dest = output_dir / Path(asset_path).name
            dest_info = f"page-local asset {src} -> {dest}"
        else:
            dest = output_assets_dir / asset_path
            dest_info = f"{src} -> {dest}"

        if dest.exists():
            try:
                dest_hash = sha256sum(dest)
                if dest_hash == asset_hash:
                    if verbose:
                        logging.info("Asset already up-to-date: %s", dest)
                    continue
                else:
                    if verbose:
                        logging.info(
                            "Asset at %s hash mismatch (have %s, want %s), will overwrite",
                            dest, dest_hash, asset_hash,
                        )
            except Exception as e:
                logging.warning("Failed to compute hash for %s: %s", dest, e)

        if dry_run:
            logging.info("[dry-run] copy %s", dest_info)
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

        try:
            copied_hash = sha256sum(dest)
            if copied_hash != asset_hash:
                logging.error(
                    "Copied asset %s hash mismatch (got %s, expected %s)",
                    dest, copied_hash, asset_hash,
                )
                continue
            if verbose:
                logging.info("Copied and verified asset: %s", dest_info)
            else:
                logging.info("Copied asset: %s", asset_path)
        except Exception as e:
            logging.error("Failed to verify hash for %s: %s", dest, e)

    return 0
<!-- END: rc/rotkeeper/lib/collect_assets.py -->

<!-- START: rc/rotkeeper/lib/init.py -->

# rc/rotkeeper/lib/init.py
from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path

from ..context import RunContext
from ..config import CONFIG

logger = logging.getLogger(__name__)

SKIP_FILES = {".dsstore", ".gitkeep", "thumbs.db", "desktop.ini"}


def add_parser(subs: argparse.SubParsersAction) -> None:
    p = subs.add_parser("init", help="Initialize a Rotkeeper project environment")
    p.add_argument("--force", action="store_true", help="Force rebuild/re-init of existing files")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    cfg = ctx.config if (ctx is not None and ctx.config is not None) else CONFIG

    base_dir = cfg.BASE_DIR
    home     = cfg.HOME
    bones    = cfg.BONES
    force    = bool(getattr(args, "force", False))

    logger.info("Initializing rotkeeper project at: %s", base_dir)
    print(f"Initializing rotkeeper project in {base_dir}")

    directories = [
        cfg.CONTENT_DIR,
        bones / "templates",
        bones / "assets" / "styles",
        bones / "assets" / "images",
        bones / "config",
        bones / "reports",
    ]
    for directory in directories:
        if directory.exists() and not force:
            print(f"  - Skipping existing directory {directory.relative_to(base_dir)}")
        else:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  Created {directory.relative_to(base_dir)}")

    user_config = bones / "config" / "user-config.yaml"
    if not user_config.exists() or force:
        home_rel    = str(home.relative_to(base_dir))
        content_rel = str(cfg.CONTENT_DIR.relative_to(base_dir))
        output_rel  = str(cfg.OUTPUT_DIR.relative_to(base_dir))
        cfg_text = (
            "HOME: " + home_rel + "\n"
            + "CONTENT_DIR: " + content_rel + "\n"
            + "OUTPUT_DIR: " + output_rel + "\n"
            + "# REPORTS_DIR: bones/reports   # optional: override reports output location\n"  # ← new hint
            + "default_template: default\n"
        )
        user_config.write_text(cfg_text, encoding="utf-8")
        print(f"  Created {user_config.relative_to(base_dir)}")
    else:
        print(f"  - Skipping existing file {user_config.relative_to(base_dir)}")

    SOURCES_DIR = Path(__file__).parent.parent / "sources"

    content_src_dir = SOURCES_DIR / "content"
    if content_src_dir.exists():
        for src in content_src_dir.rglob("*"):
            if not src.is_file() or src.name.lower() in SKIP_FILES:
                continue
            rel = src.relative_to(content_src_dir)
            dst = cfg.CONTENT_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists() or force:
                shutil.copy2(src, dst)
                print(f"  Created {dst.relative_to(base_dir)}")
            else:
                print(f"  - Skipping existing file {dst.relative_to(base_dir)}")

    templates_src_dir = SOURCES_DIR / "templates"
    templates_dst_dir = bones / "templates"
    if templates_src_dir.exists():
        for src in templates_src_dir.iterdir():
            if not src.is_file() or src.name.lower() in SKIP_FILES:
                continue
            dst = templates_dst_dir / src.name
            if not dst.exists() or force:
                shutil.copy2(src, dst)
                print(f"  Created {dst.relative_to(base_dir)}")
            else:
                print(f"  - Skipping existing file {dst.relative_to(base_dir)}")

    styles_src_dir = SOURCES_DIR / "styles"
    styles_dst_dir = bones / "assets" / "styles"
    if styles_src_dir.exists():
        for src in styles_src_dir.iterdir():
            if not src.is_file() or src.name.lower() in SKIP_FILES:
                continue
            dst = styles_dst_dir / src.name
            if not dst.exists() or force:
                shutil.copy2(src, dst)
                print(f"  Created {dst.relative_to(base_dir)}")
            else:
                print(f"  - Skipping existing file {dst.relative_to(base_dir)}")

    mascot_src = SOURCES_DIR / "images" / "mascot.png"
    mascot_dst = bones / "assets" / "images" / "mascot.png"
    if mascot_src.exists():
        if not mascot_dst.exists() or force:
            shutil.copy2(mascot_src, mascot_dst)
            print(f"  Created {mascot_dst.relative_to(base_dir)}")
        else:
            print(f"  - Skipping existing file {mascot_dst.relative_to(base_dir)}")

    reports_readme = bones / "reports" / "README.md"
    if not reports_readme.exists() or force:
        reports_readme.write_text(
            "Render Reports - contains manifests and logs generated by Rotkeeper.\n",
            encoding="utf-8",
        )
        print(f"  Created {reports_readme.relative_to(base_dir)}")
    else:
        print(f"  - Skipping existing file {reports_readme.relative_to(base_dir)}")

    gitignore = base_dir / ".gitignore"
    if not gitignore.exists() or force:
        gitignore_text = (
            "output/**/*.html\n"
            "!bones/templates/*.html\n"
            "bones/assets/styles/*.css\n"
            "__pycache__/\n"
            "*.pyc\n"
            ".od\n"
            ".venv/\n"
            "env/\n"
            "*.swp\n"
            ".DS_Store\n"
        )
        gitignore.write_text(gitignore_text, encoding="utf-8")
        print(f"  Created {gitignore.relative_to(base_dir)}")
    else:
        print(f"  - Skipping existing file {gitignore.relative_to(base_dir)}")

    print("Rotkeeper project initialized successfully!")
    print("Next steps:")
    print("  1. Edit " + str(cfg.CONTENT_DIR.relative_to(base_dir)) + "/index.md or add new Markdown files")
    print("  2. Customize " + str((bones / "templates" / "default.html").relative_to(base_dir)))
    print("  3. Run: rotkeeper sitemap-pipeline")
    print("  4. Run: rotkeeper render")
    print("  5. Check " + str((bones / "reports").relative_to(base_dir)) + " for rendering manifests")
    return 0
<!-- END: rc/rotkeeper/lib/init.py -->

<!-- START: rc/rotkeeper/lib/nav.py -->

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

import yaml

from ..config import CONFIG

logger = logging.getLogger(__name__)


def parse_nav_label(label):
    """Parse a label to extract numeric prefix for sorting."""
    if label is None:
        return (float('inf'), '')
    match = re.match(r'^(\d+)_+(.*)$', label)
    if match:
        return (int(match.group(1)), match.group(2).strip().lower())
    return (float('inf'), label.lower())


def nav_command(args, ctx=None):
    cfg = ctx.config if (ctx is not None and ctx.config is not None) else CONFIG

    sitemap_path = cfg.BONES / "reports" / "sitemap_pipeline.yaml"
    if not sitemap_path.exists():
        logger.error("Sitemap file not found at %s", sitemap_path)
        logger.error("Run 'rotkeeper sitemap-pipeline' first to generate it.")
        return 1

    try:
        with sitemap_path.open("r", encoding="utf-8") as f:
            sitemap = yaml.safe_load(f)
    except Exception as e:
        logger.error("Failed to load sitemap_pipeline.yaml: %s", e)
        return 1

    if isinstance(sitemap, dict) and "pages" in sitemap:
        pages_list = sitemap["pages"]
    elif isinstance(sitemap, list):
        pages_list = sitemap
    else:
        logger.error("sitemap_pipeline.yaml structure not recognized")
        return 1

    # Normalize and prepare pages
    pages = []
    for p in pages_list:
        if not isinstance(p, dict) or not p.get("show_in_nav", True):
            continue
        nav_path = p.get("rotkeeper_nav")
        if not isinstance(nav_path, list) or not nav_path:
            nav_path = ["Misc"]
        else:
            nav_path = [str(item) for item in nav_path]
        pages.append({**p, "rotkeeper_nav": nav_path})

    # Build metadata-first nav structure
    metadata_groups = ["author", "date", "tags", "keywords", "rotkeeper_nav"]
    nav_tree = {key: {} for key in metadata_groups}

    for page in pages:
        author = page.get("author") or "Misc"
        date   = page.get("date")   or "Misc"
        tags   = page.get("tags")   or ["Misc"]
        keywords = page.get("keywords") or ["Misc"]
        rot_nav  = page.get("rotkeeper_nav") or ["Misc"]

        nav_tree["author"].setdefault(author, {"pages": []})
        nav_tree["author"][author]["pages"].append(page)

        for tag in tags:
            nav_tree["tags"].setdefault(tag, {"pages": []})
            nav_tree["tags"][tag]["pages"].append(page)

        for kw in keywords:
            nav_tree["keywords"].setdefault(kw, {"pages": []})
            nav_tree["keywords"][kw]["pages"].append(page)

        current = nav_tree["rotkeeper_nav"]
        for part in rot_nav:
            if part not in current or not isinstance(current.get(part), dict):
                current[part] = {"__children__": {}, "__pages__": []}
            current = current[part]["__children__"]
        current.setdefault("__pages__", []).append(page)

        try:
            from datetime import datetime
            dt = datetime.fromisoformat(str(date))
            year, month, day = str(dt.year), f"{dt.month:02}", f"{dt.day:02}"
        except Exception:
            year = month = day = "Misc"
        nav_tree["date"].setdefault(year, {}).setdefault(month, {}).setdefault(day, {"pages": []})
        nav_tree["date"][year][month][day]["pages"].append(page)

    def convert_rot_nav_tree(tree):
        nav_list = []
        for orig_key, group_dict in sorted(tree.items(), key=lambda x: parse_nav_label(x[0])):
            if not isinstance(group_dict, dict):
                continue
            display = re.sub(r'^\d+_+', '', orig_key).strip() if orig_key else "Misc"
            entry = {"group": display, "pages": []}
            children = convert_rot_nav_tree(group_dict.get("__children__", {}))
            if children:
                entry["pages"].extend(children)
            for p in group_dict.get("__pages__", []):
                page_data = {k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")}
                entry["pages"].append(page_data)
            nav_list.append(entry)
        return nav_list

    final_nav = {}

    authors = []
    for author, data in sorted(nav_tree["author"].items(), key=lambda x: x[0].lower()):
        pages_out = [{k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")} for p in data["pages"]]
        authors.append({"group": author, "pages": pages_out})
    final_nav["author"] = authors

    dates = []
    for year in sorted(nav_tree["date"].keys()):
        months_list = []
        for month in sorted(nav_tree["date"][year].keys()):
            days_list = []
            for day in sorted(nav_tree["date"][year][month].keys()):
                pages_out = [{k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")} for p in nav_tree["date"][year][month][day]["pages"]]
                days_list.append({"group": day, "pages": pages_out})
            months_list.append({"group": month, "pages": days_list})
        dates.append({"group": year, "pages": months_list})
    final_nav["date"] = dates

    tags_list = []
    for tag, data in sorted(nav_tree["tags"].items(), key=lambda x: x[0].lower()):
        pages_out = [{k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")} for p in data["pages"]]
        tags_list.append({"group": tag, "pages": pages_out})
    final_nav["tags"] = tags_list

    keywords_list = []
    for kw, data in sorted(nav_tree["keywords"].items(), key=lambda x: x[0].lower()):
        pages_out = [{k: p.get(k) for k in ("title", "path", "author", "date", "tags", "keywords", "rotkeeper_nav", "show_in_nav")} for p in data["pages"]]
        keywords_list.append({"group": kw, "pages": pages_out})
    final_nav["keywords"] = keywords_list

    final_nav["rotkeeper_nav"] = convert_rot_nav_tree(nav_tree["rotkeeper_nav"])

    output_path = Path(args.output) if args.output else cfg.BONES / "reports" / "nav.yaml"

    if args.dry_run:
        print("Dry run enabled, navigation would be:")
        print(yaml.safe_dump(final_nav, sort_keys=False))
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(final_nav, f, sort_keys=False)
        if args.verbose:
            print(f"Wrote navigation to {output_path}")
            for group_key in final_nav:
                print(f"Top-level group: {group_key}")
                for subgroup in final_nav[group_key]:
                    print(f"  Group: {subgroup['group']}")
                    for page in subgroup.get("pages", []):
                        if isinstance(page, dict) and "title" in page:
                            print(f"    - Title: {page.get('title')}, Path: {page.get('path')}, Author: {page.get('author')}")

    return 0


def add_parser(subs):
    parser = subs.add_parser("nav", help="Generate navigation YAML from sitemap-pipeline output")
    parser.add_argument(
        "--output",
        type=str,
        help="Output path for navigation YAML (default: CONFIG.BONES / reports / nav.yaml)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write output, just print it")
    parser.add_argument("--verbose", action="store_true", help="Print additional information")
    parser.set_defaults(func=nav_command)
<!-- END: rc/rotkeeper/lib/nav.py -->

<!-- START: rc/rotkeeper/lib/page.py -->

# rc/rotkeeper/page.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class Page:
    title: str
    path: str              # output-relative .html path
    source: str            # content-relative .md path
    author: str = "Misc"
    date: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    rotkeeper_nav: list[str] = field(default_factory=list)
    show_in_nav: bool = True
    description: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "Page":
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})
<!-- END: rc/rotkeeper/lib/page.py -->

<!-- START: rc/rotkeeper/lib/render.py -->

# rc/rotkeeper/lib/render.py
from __future__ import annotations

import argparse
import logging
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml

from ..config import CONFIG
from ..context import RunContext

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def compute_file_mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except Exception:
        return None


def load_render_state(path: Path) -> dict[str, dict[str, float]]:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            logger.warning("render-state.yaml has unexpected structure; starting fresh")
            return {}
        return data
    except Exception as e:
        logger.warning("Could not read render-state.yaml (%s); starting fresh", e)
        return {}


def save_render_state(path: Path, state: dict[str, dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")


def load_render_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("render config must be a mapping")
    return data


def normalize_css(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(value).strip()] if str(value).strip() else []


def normalize_extra_args(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [value]
    return [str(value)]


def is_hidden_or_private(rel: Path) -> bool:
    return any(part.startswith(".") or part.startswith("_") for part in rel.parts)


def resolve_template(name: str, templates_dir: Path, assets_dir: Path) -> Path | None:
    """Search the two standard template locations; return resolved Path or None."""
    for candidate in [templates_dir / name, assets_dir / "templates" / name]:
        if candidate.exists():
            return candidate
    return None


def get_frontmatter_template(md_path: Path) -> str | None:
    """Return the template name from YAML frontmatter, or None."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return None
    fm = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not fm:
        return None
    data = yaml.safe_load(fm.group(1))
    if isinstance(data, dict):
        return data.get("template")
    return None


def file_needs_render(
    src: Path,
    dest: Path,
    template_path: Path | None,
    prev_state: dict[str, float],
) -> bool:
    if not dest.exists():
        return True
    src_mtime = compute_file_mtime(src)
    template_mtime = compute_file_mtime(template_path) if template_path else None
    if src_mtime is None:
        return True
    if prev_state.get("src_mtime") != src_mtime:
        return True
    if template_mtime is not None and prev_state.get("template_mtime") != template_mtime:
        return True
    return False


def build_pandoc_args(
    config: dict[str, Any],
    templates_dir: Path,
    assets_dir: Path,
) -> tuple[str | None, list[str]]:
    fmt: str | None = None
    if "from" in config:
        fmt = str(config["from"])
    elif "format" in config:
        fmt = str(config["format"])
    args: list[str] = []
    template_name = config.get("template")
    if template_name:
        template_path = resolve_template(str(template_name), templates_dir, assets_dir)
        if template_path is None:
            logger.warning("render: Template not found: %s", template_name)
        else:
            args.append(f"--template={template_path}")
    for css in normalize_css(config.get("css")):
        args.append(f"--css={css}")
    if config.get("toc"):
        args.append("--toc")
    if config.get("math"):
        args.append("--mathjax")
    args.extend(normalize_extra_args(config.get("extra_args")))
    return fmt, args


def build_sass(
    cfg,
    dry_run: bool = False,
    scss_file: Path | None = None,
    output_file: Path | None = None,
) -> None:
    """Compile SCSS to CSS using the sass CLI. Respects dry_run."""
    if scss_file is None:
        scss_file = cfg.BONES / "assets" / "styles" / "main.scss"
    if output_file is None:
        output_file = cfg.OUTPUT_DIR / "css" / "main.css"
    if not scss_file.exists():
        logger.warning("SCSS file not found: %s", scss_file)
        return
    if dry_run:
        logger.info("dry-run: Would compile SCSS %s -> %s", scss_file, output_file)
        return
    output_file.parent.mkdir(parents=True, exist_ok=True)
    node_modules_path = cfg.ROOT_DIR / "node_modules"
    cmd = [
        "sass",
        "--style=compressed",
        "--no-source-map",
        f"--load-path={node_modules_path}",
        str(scss_file),
        str(output_file),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        logger.info("Compiled SCSS -> CSS %s", output_file)
    except FileNotFoundError:
        logger.error("Sass CLI not installed. Run: npm install -D sass")
    except subprocess.CalledProcessError as exc:
        logger.error("Sass compilation failed: %s", exc)
    # Copy Bootstrap JS if available
    js_src = node_modules_path / "bootstrap" / "dist" / "js" / "bootstrap.bundle.min.js"
    js_dest = cfg.OUTPUT_DIR / "js" / "bootstrap.bundle.min.js"
    if js_src.exists():
        js_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(js_src, js_dest)
        logger.info("Copied Bootstrap JS -> %s", js_dest)
    else:
        logger.warning("Bootstrap JS not found in node_modules: %s", js_src)


# ---------------------------------------------------------------------------
# Main render entry point
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace, ctx: RunContext) -> int:
    # Resolve config from ctx — this is the key fix.
    # Previously this used global CONFIG and Path.cwd() which broke --config.
    cfg = ctx.config if (ctx is not None and getattr(ctx, "config", None) is not None) else CONFIG

    content_dir  = cfg.CONTENT_DIR
    output_dir   = cfg.OUTPUT_DIR
    templates_dir = cfg.BONES / "templates"
    assets_dir   = cfg.BONES / "assets"
    reports_dir  = cfg.REPORTS_DIR
    base_dir     = cfg.BASE_DIR

    manifest_path      = reports_dir / "render-manifest.yaml"
    build_manifest_path = reports_dir / "build-manifest.yaml"
    render_state_path  = reports_dir / "render-state.yaml"

    logger.debug("render root: %s", cfg.BASE_DIR)
    logger.debug("render config arg: %s", getattr(args, "config", None))

    if not ctx.dry_run:
        for d in [output_dir, templates_dir, assets_dir, reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

    # Collect markdown files
    if not content_dir.exists() or not content_dir.is_dir():
        logger.info("No content directory found at %s", content_dir)
        markdown_files: list[Path] = []
    else:
        markdown_files = []
        for path in content_dir.rglob("*.md"):
            if not path.is_file():
                continue
            rel = path.relative_to(content_dir)
            if is_hidden_or_private(rel):
                logger.debug("Skipping hidden/private file: %s", rel.as_posix())
                continue
            markdown_files.append(path)
        markdown_files.sort(key=lambda p: p.relative_to(content_dir).as_posix())
        logger.info("Found %d markdown files under %s", len(markdown_files), content_dir)

    # Load render-flags config
    render_config: dict[str, Any] = {}
    if getattr(args, "config", None):
        config_path = Path(args.config).expanduser()
        if not config_path.is_absolute():
            config_path = cfg.ROOT_DIR / config_path
        if not config_path.exists():
            logger.error("Render config not found: %s", config_path)
            return 2
        try:
            render_config = load_render_config(config_path)
        except Exception as exc:
            logger.error("Failed to load render config %s: %s", config_path, exc)
            return 2
        logger.info("Loaded render config %s", config_path)

    pandoc_format, pandoc_args = build_pandoc_args(render_config, templates_dir, assets_dir)
    if pandoc_format:
        logger.debug("Pandoc format: %s", pandoc_format)
    if pandoc_args:
        logger.debug("Pandoc args: %s", pandoc_args)

    # Import pypandoc only if we'll actually render
    pypandoc = None
    if not ctx.dry_run and markdown_files:
        try:
            import pypandoc as _pypandoc  # type: ignore
            pypandoc = _pypandoc
        except ImportError:
            logger.error("pypandoc is required for render. Install with: pip install rotkeeper[pandoc]")
            return 2

    render_state = load_render_state(render_state_path)
    render_state_dirty = False
    manifest_items: list[dict[str, str]] = []
    build_pages: list[dict[str, str]] = []
    failures = 0
    successes = 0
    skipped = 0
    dryrun_count = 0

    for src in markdown_files:
        rel = src.relative_to(content_dir)
        dest_rel = rel.with_suffix(".html")
        dest = output_dir / dest_rel

        # Resolve template: frontmatter > render-flags config > default
        fm_template = get_frontmatter_template(src)
        if fm_template:
            if Path(fm_template).is_absolute():
                template_path = Path(fm_template) if Path(fm_template).exists() else None
            else:
                template_path = resolve_template(fm_template, templates_dir, assets_dir)
            if template_path is None:
                logger.warning("Frontmatter template not found for %s: %s", src, fm_template)
        elif render_config.get("template"):
            name = str(render_config["template"])
            if Path(name).is_absolute():
                template_path = Path(name) if Path(name).exists() else None
            else:
                template_path = resolve_template(name, templates_dir, assets_dir)
            if template_path is None:
                logger.warning("render: Template not found: %s", name)
        else:
            default = templates_dir / "default.html"
            template_path = default if default.exists() else None
            if template_path is None:
                logger.warning("Default system template not found: %s", default)

        state_key = rel.as_posix()
        prev_state = render_state.get(state_key, {})
        needs_render = getattr(args, "force", False) or file_needs_render(
            src, dest, template_path, prev_state
        )

        src_mtime = compute_file_mtime(src)
        template_mtime = compute_file_mtime(template_path) if template_path else None

        try:
            manifest_items.append({"input": rel.as_posix(), "output": dest_rel.as_posix()})
            build_pages.append({
                "source": src.relative_to(base_dir).as_posix(),
                "output": dest.relative_to(base_dir).as_posix(),
            })
        except ValueError as exc:
            logger.warning("Could not make path relative for build manifest: %s", exc)

        if ctx.dry_run:
            logger.info("dry-run: render %s -> %s (needs_render=%s)", src, dest, needs_render)
            dryrun_count += 1
            continue

        if not needs_render:
            logger.info("Skipping unchanged file: %s", src)
            skipped += 1
            continue

        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            file_args = [a for a in pandoc_args if not a.startswith("--template")]
            if template_path is not None and template_path.exists():
                file_args += [f"--template={template_path}"]
            sidecar_path = src.with_suffix(".rk.yaml")
            if sidecar_path.exists():
                file_args += [f"--metadata-file={sidecar_path}"]
            # nav partial — use cfg.REPORTS_DIR so --config overrides are respected
            nav_partial = cfg.REPORTS_DIR / "nav_partial.html"
            if nav_partial.exists():
                file_args += [f"--include-before-body={nav_partial}"]
            pypandoc.convert_file(
                str(src),
                "html",
                format=pandoc_format,
                outputfile=str(dest),
                extra_args=file_args,
            )
            logger.info("Rendered %s -> %s", src, dest)
            successes += 1
            render_state[state_key] = {
                "src_mtime":      src_mtime if src_mtime is not None else time.time(),
                "template_mtime": template_mtime if template_mtime is not None else 0,
            }
            render_state_dirty = True
        except Exception as exc:
            failures += 1
            logger.error("Failed to render %s: %s", src, exc)

    if render_state_dirty:
        save_render_state(render_state_path, render_state)

    manifest_obj  = {"render": manifest_items}
    build_manifest_obj = {"pages": build_pages}

    if ctx.dry_run:
        logger.info("dry-run: would write render manifest %s", manifest_path)
        logger.info("dry-run: would write build manifest %s", build_manifest_path)
        logger.info("dry-run: render summary — %d files would be processed", dryrun_count)
        return 0

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump(manifest_obj, sort_keys=False), encoding="utf-8")
    logger.info("Wrote render manifest %s", manifest_path)
    build_manifest_path.write_text(yaml.safe_dump(build_manifest_obj, sort_keys=False), encoding="utf-8")
    logger.info("Wrote build manifest %s", build_manifest_path)

    # Compile SCSS — now dry_run aware
    build_sass(cfg, dry_run=ctx.dry_run)

    logger.info(
        "Render summary: %d rendered, %d skipped, %d failed",
        successes, skipped, failures,
    )
    if failures:
        logger.error("Render completed with %d failures.", failures)
        return 2
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def add_parser(subs: argparse.SubParsersAction) -> None:
    p = subs.add_parser("render", help="Render markdown to HTML via pandoc")
    p.add_argument("--config", type=str, default=None, help="Path to render-flags.yaml")
    p.add_argument("--force", action="store_true", help="Render all files regardless of modification times")
    p.set_defaults(func=run)
<!-- END: rc/rotkeeper/lib/render.py -->

<!-- START: rc/rotkeeper/lib/reseed.py -->

from __future__ import annotations

import argparse
import logging

from ..context import RunContext


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("reseed", help="Reconstruct files from bound books (stub)")
    p.add_argument("--input", type=str, default=None, help="Input markdown file (stub)")
    p.add_argument("--all", action="store_true", help="Reseed from all known books (stub)")
    p.add_argument("--force", action="store_true", help="Allow overwriting files (stub)")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext) -> int:
    logging.info("reseed (stub)")
    logging.debug("input=%s all=%s force=%s", args.input, args.all, args.force)
    return 0

<!-- END: rc/rotkeeper/lib/reseed.py -->

<!-- START: rc/rotkeeper/lib/sitemap_pipeline.py -->

# rc/rotkeeper/lib/sitemap_pipeline.py
from __future__ import annotations

import pprint
import re
import textwrap
from dataclasses import replace
from datetime import date as datetype
from pathlib import Path

import frontmatter
import yaml

from ..config import CONFIG
import logging

logger = logging.getLogger("rotkeeper.sitemap_pipeline")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_nav_token(token: str):
    """Parse numeric prefix if present, fallback to 9999."""
    match = re.match(r"(\d+)[.\-\s]+(.*)", token)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return 9999, token.strip()


def sort_nav_tree(node: dict) -> None:
    """Recursively sort nav tree nodes by numeric prefix, then title."""
    if "pages" in node:
        node["pages"].sort(key=lambda p: p.get("title", ""))
    children = node.get("children", {})
    if children:
        sorted_items = sorted(children.items(), key=lambda item: parse_nav_token(item[0]))
        node["children"] = {k: v for k, v in sorted_items}
        for child in node["children"].values():
            sort_nav_tree(child)


def nav_tree_to_markdown(node: dict, depth: int = 0) -> list[str]:
    """Recursively render a nav tree node to a nested Markdown list."""
    lines = []
    indent = "  " * depth
    for label, child in node.get("children", {}).items():
        pages = child.get("pages", [])
        sub = child.get("children", {})
        if pages:
            first = pages[0]
            lines.append(f"{indent}- [{label}]({first.get('path', '#')})")
            for page in pages[1:]:
                lines.append(f"{indent}  - [{page.get('title', '')}]({page.get('path', '#')})")
        else:
            lines.append(f"{indent}- {label}")
        if sub:
            lines.extend(nav_tree_to_markdown(child, depth + 1))
    return lines


def coerce_date(val) -> str | None:
    """Coerce datetime.date or other date-like objects to ISO string."""
    if val is None:
        return None
    if isinstance(val, datetype):
        return val.isoformat()
    return str(val) or None


# ---------------------------------------------------------------------------
# Pipeline class
# ---------------------------------------------------------------------------

class SitemapPipeline:

    def __init__(self, ctx=None):
        self.ctx = ctx
        config = ctx.config if ctx else CONFIG
        self.content_dir   = config.CONTENT_DIR
        self.reports_dir   = config.REPORTS_DIR   # use REPORTS_DIR so overrides are respected
        self.pages: list   = []
        self.metadata: dict = {"tags": {}, "authors": {}, "dates": {}, "rotkeepernav": {}}
        self.dry_run       = getattr(ctx, "dry_run",       False) if ctx else False
        self.verbose       = getattr(ctx, "verbose",       False) if ctx else False
        self.index_only    = getattr(ctx, "index_only",    False) if ctx else False
        self.metadata_only = getattr(ctx, "metadata_only", False) if ctx else False
        self.write_only    = getattr(ctx, "write_only",    False) if ctx else False

    # ------------------------------------------------------------------

    def collect_pages(self) -> None:
        """Walk content_dir, load frontmatter, filter drafts and hidden files."""
        self.pages = []
        skipped = 0

        if not self.content_dir.exists() or not self.content_dir.is_dir():
            logger.warning(
                "collect_pages: content directory not found at %s — "
                "run 'rotkeeper init' first",
                self.content_dir,
            )
            return

        for md in sorted(self.content_dir.rglob("*.md")):
            relpath = md.relative_to(self.content_dir)
            if relpath.name.startswith("_") or any(p.startswith(".") for p in relpath.parts):
                skipped += 1
                continue
            try:
                post = frontmatter.load(md)
            except Exception as e:
                logger.warning("Failed to load frontmatter from %s: %s", md, e)
                skipped += 1
                continue
            if post.get("draft", False) or not post.get("published", True):
                skipped += 1
                continue
            page_data = {
                "title":        post.get("title", relpath.stem),
                "path":         relpath.with_suffix(".html").as_posix(),
                "source":       relpath.as_posix(),
                "author":       post.get("author", "Misc"),
                "tags":         post.get("tags",     []) or [],
                "keywords":     post.get("keywords", []) or [],
                "date":         coerce_date(post.get("date")),
                "rotkeepernav": post.get("rotkeepernav", []) or [],
                "show_in_nav":  post.get("show_in_nav", True),
                "description":  post.get("description", ""),
            }
            if any(p["path"] == page_data["path"] for p in self.pages):
                logger.warning("Duplicate output path skipped: %s", page_data["path"])
                skipped += 1
                continue
            self.pages.append(page_data)
        logger.info("Collected %d pages, skipped %d", len(self.pages), skipped)

    # ------------------------------------------------------------------

    def build_metadata_trees(self) -> None:
        """Build tag, author, date, and nav trees from self.pages."""
        if not self.pages:
            logger.warning("build_metadata_trees called with no pages; run collect_pages first")
        self.metadata = {"tags": {}, "authors": {}, "dates": {}, "rotkeepernav": {}}
        for page in self.pages:
            author = page["author"]
            self.metadata["authors"].setdefault(author, {"pages": []})
            self.metadata["authors"][author]["pages"].append(page)
            for tag in page.get("tags", []):
                self.metadata["tags"].setdefault(tag, {"pages": []})
                self.metadata["tags"][tag]["pages"].append(page)
            date = page.get("date") or "Misc"
            self.metadata["dates"].setdefault(date, {"pages": []})
            self.metadata["dates"][date]["pages"].append(page)
            if not page.get("show_in_nav", True):
                continue
            current = self.metadata["rotkeepernav"]
            tokens = page.get("rotkeepernav") or ["Misc"]
            for token in tokens:
                _, label = parse_nav_token(token)
                current.setdefault(label, {"children": {}, "pages": []})
                current = current[label]["children"]
            current.setdefault("pages", []).append(page)
        sort_nav_tree(self.metadata["rotkeepernav"])
        logger.info(
            "Built metadata trees: %d tags, %d authors, %d dates",
            len(self.metadata["tags"]),
            len(self.metadata["authors"]),
            len(self.metadata["dates"]),
        )

    # ------------------------------------------------------------------

    def write_index_pages(self) -> None:
        """Emit auto-generated Markdown index pages for tags, authors, dates, and sitemap."""
        generated_dir = self.content_dir / "generated"
        if self.dry_run:
            logger.info("dry-run: Would write index pages to %s", generated_dir)
            return
        generated_dir.mkdir(parents=True, exist_ok=True)
        today = datetype.today().isoformat()

        def write(rel: str, fm: dict, body_lines: list[str]):
            path = generated_dir / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            fm.setdefault("generated_by", "rotkeeper/sitemap_pipeline")
            fm.setdefault("generated_at", today)
            fm.setdefault("show_in_nav", False)
            header = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
            content = f"---\n{header}\n---\n" + "\n".join(body_lines)
            path.write_text(content, encoding="utf-8")
            logger.info("Wrote index page %s", path)

        tag_lines = ["# Tags\n"]
        for tag, data in sorted(self.metadata["tags"].items()):
            tag_lines.append(f"## {tag}")
            for page in data["pages"]:
                tag_lines.append(f"- {page['title']}")
            tag_lines.append("")
        write("tags/index.md", {"title": "Tags", "draft": False}, tag_lines)

        for tag, data in sorted(self.metadata["tags"].items()):
            slug = re.sub(r"[^\w-]", "-", tag.lower().strip("-"))
            lines = [f"# {tag}\n"]
            for page in data["pages"]:
                desc = page.get("description", "")
                entry = f"- {page['title']}"
                if desc:
                    entry += f"\n  {desc}"
                lines.append(entry)
            write(f"tags/{slug}.md", {"title": f"Tag: {tag}", "draft": False}, lines)

        author_lines = ["# Authors\n"]
        for author, data in sorted(self.metadata["authors"].items()):
            author_lines.append(f"## {author}")
            for page in data["pages"]:
                author_lines.append(f"- {page['title']}")
            author_lines.append("")
        write("authors/index.md", {"title": "Authors", "draft": False}, author_lines)

        date_lines = ["# By Date\n"]
        for dt, data in sorted(self.metadata["dates"].items(), reverse=True):
            date_lines.append(f"## {dt}")
            for page in data["pages"]:
                date_lines.append(f"- {page['title']}")
            date_lines.append("")
        write("dates/index.md", {"title": "By Date", "draft": False}, date_lines)

        sitemap_lines = ["# Sitemap\n"]
        for page in self.pages:
            sitemap_lines.append(f"- {page['title']}")
        write("sitemap.md", {"title": "Sitemap", "draft": False}, sitemap_lines)

        logger.info("Index pages written to %s", generated_dir)

    # ------------------------------------------------------------------

    def write_nav_partial(self) -> None:
        """Write an HTML nav block to reports_dir/nav_partial.html.

        Render passes this to Pandoc via --include-before-body so every page
        gets consistent nav without modifying source files.

        NOTE: must be .html not .md — Pandoc's --include-before-body inserts
        the file verbatim; it does not parse Markdown.
        """
        output_file = self.reports_dir / "nav_partial.html"

        if self.dry_run:
            logger.info("dry-run: Would write nav partial to %s", output_file)
            return

        self.reports_dir.mkdir(parents=True, exist_ok=True)

        nav_tree = self.metadata.get("rotkeepernav", {})

        def render_items(node: dict, depth: int = 0) -> list[str]:
            lines = []
            indent = "  " * (depth + 2)
            for label, child in node.get("children", {}).items():
                pages = child.get("pages", [])
                sub_children = child.get("children", {})
                if pages:
                    first = pages[0]
                    href = "/" + first.get("path", "#")
                    lines.append(f'{indent}<li><a href="{href}">{label}</a>')
                    if len(pages) > 1 or sub_children:
                        lines.append(f"{indent}  <ul>")
                        for page in pages[1:]:
                            phref = "/" + page.get("path", "#")
                            ptitle = page.get("title", "")
                            lines.append(f'{indent}    <li><a href="{phref}">{ptitle}</a></li>')
                        if sub_children:
                            lines.extend(render_items(child, depth + 2))
                        lines.append(f"{indent}  </ul>")
                    lines.append(f"{indent}</li>")
                else:
                    lines.append(f"{indent}<li>{label}")
                    if sub_children:
                        lines.append(f"{indent}  <ul>")
                        lines.extend(render_items(child, depth + 2))
                        lines.append(f"{indent}  </ul>")
                    lines.append(f"{indent}</li>")
            return lines

        items = render_items(nav_tree)

        if not items:
            logger.warning("write_nav_partial: nav tree is empty, writing empty nav")

        html_lines = ['<nav class="site-nav">']
        html_lines.append("  <ul>")
        html_lines.extend(items)
        html_lines.append("  </ul>")
        html_lines.append("</nav>")

        output_file.write_text("\n".join(html_lines) + "\n", encoding="utf-8")
        logger.info("Wrote nav partial %s", output_file)

    # ------------------------------------------------------------------

    def write_sidecar_metadata(self) -> None:
        """Write .rk.yaml sidecar files alongside each source .md."""
        if not self.pages:
            logger.warning("write_sidecar_metadata called with no pages")
            return
        today = datetype.today().isoformat()
        tag_index = self.metadata["tags"]
        for page in self.pages:
            source_path = self.content_dir / page["source"]
            sidecar_path = source_path.with_suffix(".rk.yaml")
            related: list = []
            seen: set = set()
            for tag in page.get("tags", []):
                for candidate in tag_index.get(tag, {}).get("pages", []):
                    if candidate["path"] != page["path"] and candidate["path"] not in seen:
                        related.append({
                            "title":       candidate["title"],
                            "path":        candidate["path"],
                            "description": candidate.get("description", ""),
                        })
                        seen.add(candidate["path"])
                    if len(related) >= 5:
                        break
                if len(related) >= 5:
                    break
            breadcrumb = []
            for token in page.get("rotkeepernav", []):
                _, label = parse_nav_token(token)
                breadcrumb.append(label)
            breadcrumb.append(page["title"])
            sidecar = {
                "rotkeeper": {
                    "generated_at": today,
                    "source":       page["source"],
                    "breadcrumb":   breadcrumb,
                    "related_pages": related,
                    "tag_pages": [
                        {
                            "tag": tag,
                            "url": f"/generated/tags/{re.sub(r'[^\\w-]', '-', tag.lower().strip('-'))}.html",
                        }
                        for tag in page.get("tags", [])
                    ],
                    "author_page": "/generated/authors/index.html",
                }
            }
            if self.dry_run:
                logger.info("dry-run: Would write sidecar %s", sidecar_path)
                continue
            sidecar_path.write_text(
                yaml.dump(sidecar, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            logger.debug("Wrote sidecar %s", sidecar_path)
        logger.info("Sidecar metadata written for %d pages", len(self.pages))

    # ------------------------------------------------------------------

    def write_yaml(self) -> None:
        """Write the unified sitemap YAML to reports_dir."""
        if not self.pages:
            logger.warning("write_yaml called with no pages; output will be empty")
        output_file = self.reports_dir / "sitemap_pipeline.yaml"
        if self.dry_run:
            logger.info("dry-run: Would write unified sitemap to %s", output_file)
            return
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "pages":        self.pages,
            "tags":         self.metadata["tags"],
            "authors":      self.metadata["authors"],
            "dates":        self.metadata["dates"],
            "rotkeepernav": self.metadata["rotkeepernav"],
        }
        output_file.write_text(
            yaml.dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        logger.info("Wrote unified sitemap %s", output_file)

    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run the sitemap pipeline."""
        if self.index_only:
            logger.info("Stage: index-only")
            self.collect_pages()
            if self.verbose:
                pprint.pprint([p["path"] for p in self.pages])
            return
        if self.metadata_only:
            logger.info("Stage: metadata-only")
            self.collect_pages()
            self.build_metadata_trees()
            if self.verbose:
                pprint.pprint(self.metadata)
            return
        if self.write_only:
            logger.info("Stage: write-only")
            self.write_index_pages()
            self.write_nav_partial()
            self.write_sidecar_metadata()
            self.write_yaml()
            return
        logger.info("Stage: full pipeline")
        self.collect_pages()
        self.build_metadata_trees()
        self.write_index_pages()
        self.write_nav_partial()
        self.write_sidecar_metadata()
        self.write_yaml()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def add_parser(subparsers):
    p = subparsers.add_parser(
        "sitemap-pipeline",
        help="Collect pages, build metadata trees, write index pages, nav partial, and sidecars",
    )
    p.add_argument("--dry-run",       action="store_true", help="Print actions without writing files")
    p.add_argument("--verbose",       action="store_true", help="Print extra diagnostic output")
    p.add_argument("--index-only",    action="store_true", help="Collect pages only")
    p.add_argument("--metadata-only", action="store_true", help="Collect + build trees only")
    p.add_argument("--write-only",    action="store_true", help="Skip collection, write from memory")
    p.set_defaults(func=run_command)
    return p


def run_command(args, ctx=None):
    if ctx is None:
        raise ValueError("sitemap-pipeline requires a RunContext; ctx was None")
    ctx = replace(
        ctx,
        dry_run       = getattr(args, "dry_run",       False),
        verbose       = getattr(args, "verbose",       False),
        index_only    = getattr(args, "index_only",    False),
        metadata_only = getattr(args, "metadata_only", False),
        write_only    = getattr(args, "write_only",    False),
    )
    pipeline = SitemapPipeline(ctx=ctx)
    pipeline.run()
    return 0
<!-- END: rc/rotkeeper/lib/sitemap_pipeline.py -->

<!-- START: rc/rotkeeper/rc.py -->

# rc/rc.py
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from dataclasses import replace

from .config import CONFIG
from .context import RunContext
from .lib import get_commands


def _configure_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_file: Path | None = None,
) -> None:
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(message)s",
        handlers=handlers,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rotkeeper", description="Rotkeeper CLI")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without making changes")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress non-error output")
    parser.add_argument("--log-file", type=Path, default=None, help="Optional log file path")
    parser.add_argument("--config", type=Path, default=None, help="Path to configuration file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Dynamic discovery — lib modules expose add_parser(subparsers).
    # sitemap, nav, render, sitemap-pipeline are all discovered here;
    # no manual re-registration needed.
    for _cmd_name, add_parser_func in get_commands():
        add_parser_func(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.config:
        CONFIG.load(args.config)

    _configure_logging(
        verbose=args.verbose,
        quiet=args.quiet,
        log_file=args.log_file,
    )

    ctx = RunContext(
        dry_run=args.dry_run,
        verbose=args.verbose,
        log_file=args.log_file,
        config=CONFIG,
    )

    try:
        return args.func(args, ctx) or 0
    except KeyboardInterrupt:
        logging.error("Execution interrupted by user.")
        return 130
    except Exception as exc:
        if args.verbose:
            logging.exception("An unexpected error occurred:")
        else:
            logging.error("Error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
<!-- END: rc/rotkeeper/rc.py -->

