from __future__ import annotations

from jinja2 import Environment, FileSystemLoader
import argparse
import logging
import re
import time
from pathlib import Path
from typing import Any, Generator

import yaml

from ..config import CONFIG
from ..context import RunContext

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper: iter_markdown_files
# ---------------------------------------------------------------------------

def iter_markdown_files(cfg) -> Generator[Path, None, None]:
    """Yield sorted renderable .md files under cfg.CONTENTDIR, skipping hidden/private paths."""
    content_dir = cfg.CONTENTDIR
    if not content_dir.exists() or not content_dir.is_dir():
        return
    paths = []
    for path in content_dir.rglob("*.md"):
        if not path.is_file():
            continue
        rel = path.relative_to(content_dir)
        if _is_hidden_or_private(rel):
            logger.debug("Skipping hidden/private file %s", rel.as_posix())
            continue
        paths.append(path)
    paths.sort(key=lambda p: p.relative_to(content_dir).as_posix())
    yield from paths


def _is_hidden_or_private(rel: Path) -> bool:
    return any(part.startswith(".") or part.startswith("_") for part in rel.parts)


# ---------------------------------------------------------------------------
# Helper: read_frontmatter_and_body
# ---------------------------------------------------------------------------

def read_frontmatter_and_body(path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter + body from a .md file."""
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            body_md = parts[2]
            return fm, body_md
    return {}, raw


# ---------------------------------------------------------------------------
# Helper: merge_sidecar
# ---------------------------------------------------------------------------

def merge_sidecar(fm: dict, sidecar_path: Path) -> dict:
    """Load .rk.yaml sidecar, merge over fm; return new dict, never mutate fm."""
    if not sidecar_path.exists():
        return dict(fm)
    try:
        sidecar_data = yaml.safe_load(sidecar_path.read_text(encoding="utf-8")) or {}
    except Exception as sc_exc:
        logger.warning("Could not read sidecar %s: %s", sidecar_path, sc_exc)
        return dict(fm)
    return {**fm, **sidecar_data}


# ---------------------------------------------------------------------------
# Helper: render_page
# ---------------------------------------------------------------------------

def render_page(
    *,
    src: Path,
    dest: Path,
    fm: dict,
    body_md: str,
    pandoc_format: str,
    pandoc_args: list[str],
    jinja_env: Environment,
    render_config: dict[str, Any],
    templates_dir: Path,
    assets_dir: Path,
    pypandoc: Any,
) -> bool:
    """Run pypandoc → HTML, Jinja2 template render, write to dest. Returns True on success."""
    try:
        file_args = [a for a in pandoc_args if not a.startswith("--template") and not a.startswith("--include-before-body")]
        body_html = pypandoc.convert_text(
            body_md, "html",
            format=pandoc_format or "markdown",
            extra_args=file_args,
        )

        template_name = fm.get("template") or render_config.get("template") or "default.html"
        try:
            tmpl = jinja_env.get_template(str(template_name))
        except Exception:
            logger.warning("Template not found in Jinja2 env %s, falling back to default.html", template_name)
            tmpl = jinja_env.get_template("default.html")

        html = tmpl.render(
            title=fm.get("title", ""),
            author=fm.get("author", ""),
            date=str(fm.get("date", "")),
            description=fm.get("description", ""),
            version=fm.get("version", ""),
            tags=fm.get("tags", []),
            toc="",
            body=body_html,
        )
        dest.write_text(html, encoding="utf-8")
        logger.info("Rendered %s -> %s", src, dest)
        return True
    except Exception as exc:
        logger.error("Failed to render %s: %s", src, exc)
        return False


# ---------------------------------------------------------------------------
# Internal helpers (unchanged from original)
# ---------------------------------------------------------------------------

def _make_jinja_env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,
    )


def _compute_file_mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except Exception:
        return None


def _load_render_state(path: Path) -> dict[str, dict[str, float]]:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            logger.warning("render-state.yaml has unexpected structure; starting fresh")
            return {}
        return data
    except Exception as e:
        logger.warning("Could not read render-state.yaml: %s; starting fresh", e)
        return {}


def _save_render_state(path: Path, state: dict[str, dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")


def _load_render_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("render config must be a mapping")
    return data


def _normalize_css(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(value).strip()] if str(value).strip() else []


def _normalize_extra_args(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [value]
    return [str(value)]


def _is_hidden_or_private_path(rel: Path) -> bool:
    return any(part.startswith(".") or part.startswith("_") for part in rel.parts)


def _get_frontmatter_template(md_path: Path) -> str | None:
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return None
    fm = re.match(r"---(.+?)---", text, re.DOTALL)
    if not fm:
        return None
    data = yaml.safe_load(fm.group(1))
    if isinstance(data, dict):
        return data.get("template")
    return None


def _resolve_template(name: str, templates_dir: Path, assets_dir: Path) -> Path | None:
    for candidate in [templates_dir / name, assets_dir / "templates" / name]:
        if candidate.exists():
            return candidate
    return None


def _file_needs_render(
    src: Path,
    dest: Path,
    template_path: Path | None,
    prev_state: dict[str, float],
) -> bool:
    if not dest.exists():
        return True
    src_mtime = _compute_file_mtime(src)
    template_mtime = _compute_file_mtime(template_path) if template_path else None
    if src_mtime is None:
        return True
    if prev_state.get("src_mtime") != src_mtime:
        return True
    if template_mtime is not None and prev_state.get("template_mtime") != template_mtime:
        return True
    return False


def _build_pandoc_args(render_config: dict[str, Any]) -> tuple[str, list[str]]:
    pandoc_format = render_config.get("from", "markdown")
    extra_args = _normalize_extra_args(render_config.get("extra_args"))
    css_files = _normalize_css(render_config.get("css"))
    args = list(extra_args)
    for css in css_files:
        args += ["--css", css]
    return pandoc_format, args


# ---------------------------------------------------------------------------
# run()  — locked signature, fail-fast guard (Task 1 + Task 2)
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace, ctx: RunContext) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    cfg = ctx.config if ctx is not None and getattr(ctx, "config", None) is not None else CONFIG
    content_dir = cfg.CONTENTDIR
    output_dir = cfg.OUTPUTDIR
    templates_dir = cfg.BONES / "templates"
    assets_dir = cfg.BONES / "assets"
    reports_dir = cfg.REPORTSDIR
    base_dir = cfg.BASEDIR

    manifest_path = reports_dir / "render-manifest.yaml"
    build_manifest_path = reports_dir / "build-manifest.yaml"
    render_state_path = reports_dir / "render-state.yaml"

    logger.debug("render root %s", cfg.BASEDIR)
    logger.debug("render config arg %s", getattr(args, "config", None))

    if not ctx.dry_run:
        for d in [output_dir, templates_dir, assets_dir, reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

    # Load render config (render-flags.yaml)
    render_config: dict[str, Any] = {}
    if getattr(args, "config", None):
        config_path = Path(args.config).expanduser()
        if not config_path.is_absolute():
            config_path = cfg.ROOTDIR / config_path
        if not config_path.exists():
            logger.error("Render config not found: %s", config_path)
            return 2
        try:
            render_config = _load_render_config(config_path)
        except Exception as exc:
            logger.error("Failed to load render config %s: %s", config_path, exc)
            return 2
        logger.info("Loaded render config %s", config_path)

    pandoc_format, pandoc_args = _build_pandoc_args(render_config)

    pypandoc = None
    if not ctx.dry_run:
        try:
            import pypandoc as pypandoc  # type: ignore
        except ImportError:
            logger.error("pypandoc is required for render. Install with pip install rotkeeper[pandoc]")
            return 2

    jinja_env = _make_jinja_env(templates_dir)
    render_state = _load_render_state(render_state_path)
    render_state_dirty = False
    manifest_items: list[dict[str, str]] = []
    build_pages: list[dict[str, str]] = []
    failures = 0
    successes = 0
    skipped = 0
    dry_run_count = 0

    for src in iter_markdown_files(cfg):
        rel = src.relative_to(content_dir)
        dest = output_dir / rel.with_suffix(".html")
        dest_rel = rel.with_suffix(".html")

        fm, body_md = read_frontmatter_and_body(src)
        fm = merge_sidecar(fm, src.with_suffix(".rk.yaml"))

        # Resolve template path for mtime tracking
        fm_template = fm.get("template")
        if fm_template:
            if Path(fm_template).is_absolute():
                template_path = Path(fm_template) if Path(fm_template).exists() else None
            else:
                template_path = _resolve_template(fm_template, templates_dir, assets_dir)
            if template_path is None:
                logger.warning("Frontmatter template not found for %s: %s", src, fm_template)
        elif render_config.get("template"):
            name = str(render_config["template"])
            if Path(name).is_absolute():
                template_path = Path(name) if Path(name).exists() else None
            else:
                template_path = _resolve_template(name, templates_dir, assets_dir)
            if template_path is None:
                logger.warning("render Template not found: %s", name)
        else:
            default = templates_dir / "default.html"
            template_path = default if default.exists() else None

        state_key = rel.as_posix()
        prev_state = render_state.get(state_key, {})
        needs_render = getattr(args, "force", False) or _file_needs_render(src, dest, template_path, prev_state)

        src_mtime = _compute_file_mtime(src)
        template_mtime = _compute_file_mtime(template_path) if template_path else None

        try:
            manifest_items.append({"input": rel.as_posix(), "output": dest_rel.as_posix()})
            build_pages.append({
                "source": src.relative_to(base_dir).as_posix(),
                "output": dest.relative_to(base_dir).as_posix(),
            })
        except ValueError as exc:
            logger.warning("Could not make path relative for build manifest: %s", exc)

        if ctx.dry_run:
            logger.info("dry-run render %s -> %s (needs_render=%s)", src, dest, needs_render)
            dry_run_count += 1
            continue

        if not needs_render:
            logger.info("Skipping unchanged file %s", src)
            skipped += 1
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)

        ok = render_page(
            src=src,
            dest=dest,
            fm=fm,
            body_md=body_md,
            pandoc_format=pandoc_format,
            pandoc_args=pandoc_args,
            jinja_env=jinja_env,
            render_config=render_config,
            templates_dir=templates_dir,
            assets_dir=assets_dir,
            pypandoc=pypandoc,
        )

        if ok:
            successes += 1
            render_state[state_key] = {
                "src_mtime": src_mtime if src_mtime is not None else time.time(),
                "template_mtime": template_mtime if template_mtime is not None else 0,
            }
            render_state_dirty = True
        else:
            failures += 1

    if render_state_dirty:
        _save_render_state(render_state_path, render_state)

    if ctx.dry_run:
        logger.info("dry-run would write render manifest %s", manifest_path)
        logger.info("dry-run would write build manifest %s", build_manifest_path)
        logger.info("dry-run render summary: %d files would be processed", dry_run_count)
        return 0

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump(manifest_items, sort_keys=False), encoding="utf-8")
    logger.info("Wrote render manifest %s", manifest_path)

    build_manifest_path.write_text(yaml.safe_dump(build_pages, sort_keys=False), encoding="utf-8")
    logger.info("Wrote build manifest %s", build_manifest_path)

    logger.info("Render summary: %d rendered, %d skipped, %d failed", successes, skipped, failures)
    if failures:
        logger.error("Render completed with %d failures.", failures)
        return 2
    return 0


# ---------------------------------------------------------------------------
# add_parser — unchanged: registers render subcommand, set_defaults(func=run)
# ---------------------------------------------------------------------------

def add_parser(subs: argparse.SubParsersAction) -> None:
    p = subs.add_parser("render", help="Render markdown to HTML via pandoc")
    p.add_argument("--config", type=str, default=None, help="Path to render-flags.yaml")
    p.add_argument("--force", action="store_true", help="Render all files regardless of modification times")
    p.set_defaults(func=run)
