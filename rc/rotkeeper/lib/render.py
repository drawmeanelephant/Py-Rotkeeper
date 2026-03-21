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
