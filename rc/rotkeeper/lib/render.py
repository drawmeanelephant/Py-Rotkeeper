from __future__ import annotations
from jinja2 import Environment, FileSystemLoader
import argparse
import logging
import re
import time
from pathlib import Path
from typing import Any
import yaml
from ..config import CONFIG
from ..context import RunContext
from .page import Page

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def iter_markdown_files(cfg) -> list[Path]:
    content_dir = cfg.CONTENT_DIR
    if not content_dir.exists() or not content_dir.is_dir():
        return []
    files = []
    for path in content_dir.rglob("*.md"):
        if not path.is_file():
            continue
        rel = path.relative_to(content_dir)
        if _is_hidden_or_private(rel):
            continue
        files.append(path)
    files.sort(key=lambda p: p.relative_to(content_dir).as_posix())
    return files


def read_frontmatter_and_body(src: Path) -> tuple[dict, str]:
    raw = src.read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        fm = yaml.safe_load(parts[1]) or {} if len(parts) >= 2 else {}
        body = parts[2] if len(parts) >= 3 else raw
    else:
        fm = {}
        body = raw
    return fm, body


def merge_sidecar(fm: dict, sidecar_path: Path) -> dict:
    """Merge only the rotkeeper: sub-key from a sidecar, never clobber user top-level keys."""
    if not sidecar_path.exists():
        return dict(fm)
    try:
        sidecar_data = yaml.safe_load(sidecar_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        logger.warning("Could not read sidecar %s: %s", sidecar_path, exc)
        return dict(fm)
    # Only merge the rotkeeper: sub-key
    rk = sidecar_data.get("rotkeeper", {})
    return {**fm, **rk}


def render_page(
    src: Path,
    dest: Path,
    jinja_env: Environment,
    cfg,
    pandoc_format: str | None,
    pandoc_args: list[str],
    dry_run: bool,
) -> None:
    """Render a single Markdown page to HTML using Pandoc + Jinja2."""
    import pypandoc

    fm_raw, body_md = read_frontmatter_and_body(src)
    sidecar_path = src.with_suffix(".rk.yaml")
    fm = merge_sidecar(fm_raw, sidecar_path)

    # Build a typed Page for template context
    page = Page(
        title=fm.get("title", src.stem),
        path=str(src.relative_to(cfg.CONTENT_DIR).with_suffix(".html").as_posix()),
        source=str(src.relative_to(cfg.CONTENT_DIR).as_posix()),
        author=fm.get("author", "Misc"),
        date=str(fm.get("date", "")) or None,
        tags=fm.get("tags") or [],
        keywords=fm.get("keywords") or [],
        rotkeeper_nav=fm.get("rotkeeper_nav") or [],
        show_in_nav=fm.get("show_in_nav", True),
        description=fm.get("description", ""),
    )

    # Determine template
    template_name = fm.get("template") or cfg.defaulttemplate
    template_obj = None
    if template_name:
        try:
            template_obj = jinja_env.get_template(template_name)
        except Exception:
            logger.warning("Jinja2 template not found: %s — falling back to default", template_name)

    if template_obj is None:
        try:
            template_obj = jinja_env.get_template("default.html")
        except Exception:
            logger.warning("No default.html template found; writing raw Pandoc output")

    # Pandoc render
    file_args = [a for a in pandoc_args if not a.startswith("--template") and not a.startswith("--include-before-body")]
    body_html = pypandoc.convert_text(
        body_md,
        "html",
        format=pandoc_format or "markdown",
        extra_args=file_args,
    )

    if template_obj is not None:
        rendered = template_obj.render(
            page=page,
            body=body_html,
            title=page.title,
            author=page.author,
            date=page.date,
            tags=page.tags,
            keywords=page.keywords,
            rotkeeper_nav=page.rotkeeper_nav,
            description=page.description,
            breadcrumb=fm.get("breadcrumb", []),
            related_pages=fm.get("related_pages", []),
        )
    else:
        rendered = body_html

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered, encoding="utf-8")


# ---------------------------------------------------------------------------
# Internal utilities
# ---------------------------------------------------------------------------

def _is_hidden_or_private(rel: Path) -> bool:
    return any(part.startswith(".") or part.startswith("_") for part in rel.parts)


def _resolve_template(name: str, templates_dir: Path, assets_dir: Path) -> Path | None:
    for candidate in [templates_dir / name, assets_dir / "templates" / name]:
        if candidate.exists():
            return candidate
    return None


def _get_frontmatter_template(md_path: Path) -> str | None:
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return None
    fm = re.match(r"^---(.+?)---", text, re.DOTALL)
    if not fm:
        return None
    data = yaml.safe_load(fm.group(1))
    if isinstance(data, dict):
        return data.get("template")
    return None


def _file_needs_render(
    src: Path, dest: Path, template_path: Path | None, prev_state: dict[str, float]
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
            logger.warning("render-state.yaml has unexpected structure, starting fresh")
            return {}
        return data
    except Exception as e:
        logger.warning("Could not read render-state.yaml: %s — starting fresh", e)
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


def _build_pandoc_args(
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
        template_path = _resolve_template(str(template_name), templates_dir, assets_dir)
        if template_path is None:
            logger.warning("render: Template not found: %s", template_name)
        else:
            args.append(f"--template={template_path}")
    for css in _normalize_css(config.get("css")):
        args.append(f"--css={css}")
    if config.get("toc"):
        args.append("--toc")
    if config.get("math"):
        args.append("--mathjax")
    args.extend(_normalize_extra_args(config.get("extra_args")))
    return fmt, args


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def add_parser(subparsers: argparse.SubParsersAction) -> None:
    p = subparsers.add_parser("render", help="Render Markdown content to HTML")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--force", action="store_true", help="Re-render all files")
    p.add_argument("--config", type=str, default=None, help="Path to render config YAML")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext) -> int:
    cfg = ctx.config if ctx is not None and getattr(ctx, "config", None) is not None else CONFIG
    content_dir = cfg.CONTENT_DIR
    output_dir = cfg.OUTPUTDIR
    templates_dir = cfg.BONES / "templates"
    assets_dir = cfg.BONES / "assets"
    reports_dir = cfg.REPORTS_DIR
    base_dir = cfg.BASEDIR

    manifest_path = reports_dir / "render-manifest.yaml"
    build_manifest_path = reports_dir / "build-manifest.yaml"
    render_state_path = reports_dir / "render-state.yaml"

    logger.debug("render root: %s", cfg.BASEDIR)
    logger.debug("render config arg: %s", getattr(args, "config", None))

    if not ctx.dry_run:
        for d in [output_dir, templates_dir, assets_dir, reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

    markdown_files = iter_markdown_files(cfg)
    logger.info("Found %d markdown files under %s", len(markdown_files), content_dir)

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
        logger.info("Loaded render config: %s", config_path)

    pandoc_format, pandoc_args = _build_pandoc_args(render_config, templates_dir, assets_dir)

    pypandoc = None
    if not ctx.dry_run and markdown_files:
        try:
            import pypandoc as pypandoc  # type: ignore
        except ImportError:
            logger.error("pypandoc is required for render. Install with: pip install rotkeeper[pandoc]")
            return 2

    render_state = _load_render_state(render_state_path)
    render_state_dirty = False
    manifest_items: list[dict[str, str]] = []
    build_pages: list[dict[str, str]] = []
    failures = 0
    successes = 0
    skipped = 0
    dry_run_count = 0

    # Task 7: construct jinja_env ONCE before the loop
    jinja_env = _make_jinja_env(templates_dir)

    for src in markdown_files:
        rel = src.relative_to(content_dir)
        dest_rel = rel.with_suffix(".html")
        dest = output_dir / dest_rel

        fm_raw, _ = read_frontmatter_and_body(src)
        fm_template = fm_raw.get("template")
        template_path: Path | None = None
        if fm_template:
            template_path = _resolve_template(fm_template, templates_dir, assets_dir)
            if template_path is None:
                logger.warning("Frontmatter template not found for %s: %s", src, fm_template)
        elif render_config.get("template"):
            name = str(render_config["template"])
            template_path = _resolve_template(name, templates_dir, assets_dir)
            if template_path is None:
                logger.warning("render: Template not found: %s", name)
        else:
            default = templates_dir / "default.html"
            template_path = default if default.exists() else None
            if template_path is None:
                logger.warning("Default system template not found: %s", default)

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
            logger.info("dry-run render: %s -> %s (needs_render=%s)", src, dest, needs_render)
            dry_run_count += 1
            continue

        if not needs_render:
            logger.info("Skipping unchanged file: %s", src)
            skipped += 1
            continue

        try:
            render_page(src, dest, jinja_env, cfg, pandoc_format, pandoc_args, ctx.dry_run)
            new_state: dict[str, float] = {}
            if src_mtime is not None:
                new_state["src_mtime"] = src_mtime
            if template_mtime is not None:
                new_state["template_mtime"] = template_mtime
            render_state[state_key] = new_state
            render_state_dirty = True
            successes += 1
            logger.debug("Rendered: %s -> %s", src, dest)
        except Exception as exc:
            logger.error("Failed to render %s: %s", src, exc)
            failures += 1

    if render_state_dirty and not ctx.dry_run:
        _save_render_state(render_state_path, render_state)

    if not ctx.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(yaml.safe_dump(manifest_items, sort_keys=False), encoding="utf-8")
        logger.info("Wrote render manifest: %s", manifest_path)
        build_manifest_path.write_text(yaml.safe_dump(build_pages, sort_keys=False), encoding="utf-8")
        logger.info("Wrote build manifest: %s", build_manifest_path)

    logger.info(
        "Render summary: %d rendered, %d skipped, %d failed",
        successes, skipped, failures,
    )
    if failures:
        logger.error("Render completed with %d failures.", failures)
        return 2
    return 0
