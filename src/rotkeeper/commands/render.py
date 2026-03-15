from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any
import re
import yaml
import time
import subprocess

from ..context import RunContext


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
            return {}
        return data
    except Exception:
        return {}


def save_render_state(path: Path, state: dict[str, dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("render", help="Render markdown to HTML via pandoc (stub)")
    p.add_argument("--config", type=str, default=None, help="Path to render-flags.yaml (stub)")
    p.set_defaults(func=run)


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


def _is_hidden_or_private(rel: Path) -> bool:
    return any(part.startswith(".") or part.startswith("_") for part in rel.parts)


def _build_pandoc_args(config: dict[str, Any], ctx: RunContext) -> tuple[str | None, list[str]]:
    fmt = None
    if "from" in config:
        fmt = str(config["from"])
    elif "format" in config:
        fmt = str(config["format"])

    args: list[str] = []

    template = config.get("template")
    if template:
        template_path = Path(template)
        if not template_path.is_absolute():
            template_path = ctx.paths.root_dir / template_path
        if not template_path.exists():
            logging.warning("[render] Template not found: %s", template_path)
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


def _get_frontmatter_template(md_path: Path) -> str | None:
    """Parse YAML frontmatter for template override"""
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return None
    fm = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not fm:
        return None
    data = yaml.safe_load(fm.group(1))
    if isinstance(data, dict):
        return data.get("template")
    return None


def file_needs_render(src: Path, dest: Path, template_path: Path | None, prev_state: dict[str, float]) -> bool:
    # If dest does not exist, we must render
    if not dest.exists():
        return True
    src_mtime = compute_file_mtime(src)
    template_mtime = compute_file_mtime(template_path) if template_path else None
    prev_src_mtime = prev_state.get("src_mtime")
    prev_template_mtime = prev_state.get("template_mtime")
    if src_mtime is None:
        return True
    if prev_src_mtime != src_mtime:
        return True
    if template_mtime is not None and prev_template_mtime != template_mtime:
        return True
    return False


def run(args: argparse.Namespace, ctx: RunContext) -> int:
    logging.debug("root=%s", ctx.paths.root_dir)
    logging.debug("config=%s", getattr(args, "config", None))

    content_dir = ctx.paths.content_dir
    output_dir = ctx.paths.output_dir
    manifest_path = ctx.paths.reports_dir / "render-manifest.yaml"
    build_manifest_path = ctx.paths.reports_dir / "build-manifest.yaml"
    render_state_path = ctx.paths.reports_dir / "render-state.yaml"

    if not content_dir.exists() or not content_dir.is_dir():
        logging.info("No content directory found at %s", content_dir)
        markdown_files: list[Path] = []
    else:
        markdown_files = []
        for path in content_dir.rglob("*.md"):
            if not path.is_file():
                continue
            rel = path.relative_to(content_dir)
            if _is_hidden_or_private(rel):
                logging.debug("Skipping hidden/private file: %s", rel.as_posix())
                continue
            markdown_files.append(path)
        markdown_files.sort(key=lambda path: path.relative_to(content_dir).as_posix())
        logging.info("Found %d markdown files under %s", len(markdown_files), content_dir)

    config_path = None
    render_config: dict[str, Any] = {}
    if args.config:
        config_path = Path(args.config).expanduser()
        if not config_path.is_absolute():
            config_path = ctx.paths.root_dir / config_path
        if not config_path.exists():
            logging.error("Render config not found: %s", config_path)
            return 2
        try:
            render_config = _load_render_config(config_path)
        except Exception as exc:
            logging.error("Failed to load render config %s: %s", config_path, exc)
            return 2
        logging.info("Loaded render config: %s", config_path)

    pandoc_format, pandoc_args = _build_pandoc_args(render_config, ctx)
    if pandoc_format:
        logging.debug("Pandoc format: %s", pandoc_format)
    if pandoc_args:
        logging.debug("Pandoc args: %s", pandoc_args)

    if not ctx.dry_run and markdown_files:
        try:
            import pypandoc
        except ImportError:
            logging.error("pypandoc is required for render. Install with: pip install rotkeeper[pandoc]")
            return 2
    else:
        pypandoc = None

    # Load persistent render state
    render_state = load_render_state(render_state_path)

    manifest_items: list[dict[str, str]] = []
    build_pages: list[dict[str, str]] = []
    failures = 0
    total = len(markdown_files)
    successes = 0
    skipped = 0

    for src in markdown_files:
        rel = src.relative_to(content_dir)
        dest_rel = rel.with_suffix(".html")
        dest = output_dir / dest_rel

        # Determine template for this document
        fm_template = _get_frontmatter_template(src)
        if fm_template:
            template_path = Path(fm_template)
            if not template_path.is_absolute():
                # resolve relative to bones/templates folder
                template_path = ctx.paths.assets_dir / "templates" / template_path
            if not template_path.exists():
                logging.warning("Frontmatter template not found for %s: %s", src, template_path)
        elif render_config.get("template"):
            template_path = Path(render_config["template"])
            if not template_path.is_absolute():
                template_path = ctx.paths.root_dir / template_path
            if not template_path.exists():
                logging.warning("[render] Template not found: %s", template_path)
        else:
            # use default system template from bones/templates
            template_path = ctx.paths.bones_dir / "templates" / "default.html"
            if not template_path.exists():
                logging.warning("Default system template not found: %s", template_path)

        # Compute mtimes and previous state
        state_key = rel.as_posix()
        prev_state = render_state.get(state_key, {})
        needs_render = file_needs_render(src, dest, template_path, prev_state)
        src_mtime = compute_file_mtime(src)
        template_mtime = compute_file_mtime(template_path) if template_path else None

        manifest_items.append(
            {"input": rel.as_posix(), "output": dest_rel.as_posix()}
        )
        build_pages.append(
            {
                "source": src.relative_to(ctx.paths.root_dir).as_posix(),
                "output": dest.relative_to(ctx.paths.root_dir).as_posix(),
            }
        )

        if ctx.dry_run:
            logging.info("[dry-run] render %s -> %s (needs_render=%s)", src, dest, needs_render)
            successes += 1
            continue

        if not needs_render:
            logging.debug("Skipping unchanged file: %s", src)
            skipped += 1
            continue

        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            pypandoc.convert_file(
                str(src),
                "html",
                format=pandoc_format,
                outputfile=str(dest),
                extra_args=[f"--template={template_path}"],
            )
            logging.info("Rendered %s -> %s", src, dest)
            successes += 1
            # Update render state
            render_state[state_key] = {
                "src_mtime": src_mtime if src_mtime is not None else time.time(),
                "template_mtime": template_mtime if template_mtime is not None else 0,
            }
            save_render_state(render_state_path, render_state)
        except Exception as exc:
            failures += 1
            logging.error("Failed to render %s: %s", src, exc)

    manifest_obj = {"render": manifest_items}
    build_manifest_obj = {"pages": build_pages}

    if ctx.dry_run:
        logging.info("[dry-run] would write render manifest: %s", manifest_path)
        logging.info("[dry-run] would write build manifest: %s", build_manifest_path)
        logging.info("[dry-run] render summary: %d files would render, %d failures", successes, failures)
        return 0

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        yaml.safe_dump(manifest_obj, sort_keys=False),
        encoding="utf-8",
    )
    logging.info("Wrote render manifest: %s", manifest_path)
    build_manifest_path.write_text(
        yaml.safe_dump(build_manifest_obj, sort_keys=False),
        encoding="utf-8",
    )
    logging.info("Wrote build manifest: %s", build_manifest_path)

    logging.info("Render summary: %d files rendered successfully, %d files skipped, %d failures", successes, skipped, failures)
    if failures:
        logging.error("Render completed with %d failure(s).", failures)
        return 2

    # Compile SCSS → CSS automatically after render
    build_sass(ctx)
    return 0


# --- Sass build helper ---
def build_sass(ctx: RunContext, scss_file: Path | None = None, output_file: Path | None = None):
    """Compile SCSS to CSS using sass CLI."""
    if scss_file is None:
        scss_file = ctx.paths.assets_dir / "styles" / "main.scss"
    if output_file is None:
        output_file = ctx.paths.output_dir / "css" / "main.css"
    if not scss_file.exists():
        logging.warning("SCSS file not found: %s", scss_file)
        return
    output_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["sass", "--style=compressed", "--no-source-map", str(scss_file), str(output_file)],
            check=True
        )
        logging.info("Compiled SCSS -> CSS: %s", output_file)
    except FileNotFoundError:
        logging.error("Sass CLI not installed. Run 'npm install -D sass' or install system sass")
    except subprocess.CalledProcessError as e:
        logging.error("Sass compilation failed: %s", e)
