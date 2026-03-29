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

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_jinja_env(templates_dir: Path) -> "Environment":
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,
    )


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
    for candidate in [templates_dir / name, assets_dir / "templates" / name]:
        if candidate.exists():
            return candidate
    return None


def get_frontmatter_template(md_path: Path) -> str | None:
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


# ---------------------------------------------------------------------------
# Main render entry point
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace, ctx: RunContext) -> int:
    cfg = ctx.config if (ctx is not None and getattr(ctx, "config", None) is not None) else CONFIG

    content_dir   = cfg.CONTENT_DIR
    output_dir    = cfg.OUTPUT_DIR
    templates_dir = cfg.BONES / "templates"
    assets_dir    = cfg.BONES / "assets"
    reports_dir   = cfg.REPORTS_DIR
    base_dir      = cfg.BASE_DIR

    manifest_path       = reports_dir / "render-manifest.yaml"
    build_manifest_path = reports_dir / "build-manifest.yaml"
    render_state_path   = reports_dir / "render-state.yaml"

    logger.debug("render root: %s", cfg.BASE_DIR)
    logger.debug("render config arg: %s", getattr(args, "config", None))

    if not ctx.dry_run:
        for d in [output_dir, templates_dir, assets_dir, reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

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

            raw = src.read_text(encoding="utf-8")
            if raw.startswith("---"):
                parts = raw.split("---", 2)
                fm_meta = yaml.safe_load(parts[1]) or {} if len(parts) >= 3 else {}
                body_md = parts[2] if len(parts) >= 3 else raw
            else:
                fm_meta = {}
                body_md = raw

            sidecar_path = src.with_suffix(".rk.yaml")
            if sidecar_path.exists():
                try:
                    sidecar_data = yaml.safe_load(sidecar_path.read_text(encoding="utf-8")) or {}
                    fm_meta = {**sidecar_data, **fm_meta}
                except Exception as sc_exc:
                    logger.warning("Could not read sidecar %s: %s", sidecar_path, sc_exc)

            file_args = [a for a in pandoc_args
                         if not a.startswith("--template") and not a.startswith("--include-before-body")]
            body_html = pypandoc.convert_text(
                body_md,
                "html",
                format=pandoc_format or "markdown",
                extra_args=file_args,
            )

            jinja_env = _make_jinja_env(templates_dir)
            template_name = (fm_meta.get("template") or
                             render_config.get("template") or
                             "default.html")
            try:
                tmpl = jinja_env.get_template(str(template_name))
            except Exception:
                logger.warning("Template not found in Jinja2 env: %s, falling back to default.html", template_name)
                tmpl = jinja_env.get_template("default.html")

            html = tmpl.render(
                title=fm_meta.get("title", ""),
                author=fm_meta.get("author", ""),
                date=str(fm_meta.get("date", "")),
                description=fm_meta.get("description", ""),
                version=fm_meta.get("version", ""),
                tags=fm_meta.get("tags", []),
                toc="",
                body=body_html,
            )
            dest.write_text(html, encoding="utf-8")
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

    if ctx.dry_run:
        logger.info("dry-run: would write render manifest %s", manifest_path)
        logger.info("dry-run: would write build manifest %s", build_manifest_path)
        logger.info("dry-run: render summary — %d files would be processed", dryrun_count)
        return 0

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump({"render": manifest_items}, sort_keys=False), encoding="utf-8")
    logger.info("Wrote render manifest %s", manifest_path)
    build_manifest_path.write_text(yaml.safe_dump({"pages": build_pages}, sort_keys=False), encoding="utf-8")
    logger.info("Wrote build manifest %s", build_manifest_path)

    logger.info("Render summary: %d rendered, %d skipped, %d failed", successes, skipped, failures)
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