from __future__ import annotations

import argparse
import logging
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml

from ..config import CONFIG
from ..context import RunContext

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
            return {}
        return data
    except Exception:
        return {}

def save_render_state(path: Path, state: dict[str, dict[str, float]]) -> None:
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

def _is_hidden_or_private(rel: Path) -> bool:
    return any(part.startswith(".") or part.startswith("_") for part in rel.parts)

def _resolve_template(name: str, templates_dir: Path, assets_dir: Path) -> Path | None:
    """Search the two standard template locations; return resolved Path or None."""
    for candidate in [templates_dir / name, assets_dir / "templates" / name]:
        if candidate.exists():
            return candidate
    return None

def _build_pandoc_args(config: dict[str, Any], templates_dir: Path, assets_dir: Path) -> tuple[str | None, list[str]]:
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
            logging.warning("[render] Template not found: %s", template_name)
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
    """Return the template name from YAML frontmatter, or None."""
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

# ---------------------------------------------------------------------------
# Sass helper
# ---------------------------------------------------------------------------

def build_sass(scss_file: Path | None = None, output_file: Path | None = None) -> None:
    """Compile SCSS to CSS using the sass CLI."""
    if scss_file is None:
        scss_file = CONFIG.BONES / "assets" / "styles" / "main.scss"
    if output_file is None:
        output_file = CONFIG.OUTPUT_DIR / "css" / "main.css"
    if not scss_file.exists():
        logging.warning("SCSS file not found: %s", scss_file)
        return
    output_file.parent.mkdir(parents=True, exist_ok=True)
    node_modules_path = (CONFIG.ROOT_DIR / "node_modules").resolve()
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
        logging.info("Compiled SCSS -> CSS: %s", output_file)
    except FileNotFoundError:
        logging.error("Sass CLI not installed. Run 'npm install -D sass' or install system sass.")
    except subprocess.CalledProcessError as exc:
        logging.error("Sass compilation failed: %s", exc)

# ---------------------------------------------------------------------------
# Public render helper (used by render_sitemap and other lib modules)
# ---------------------------------------------------------------------------

def render_template(
    src: Path,
    dest: Path,
    template_path: Path | None = None,
    extra_args: list[str] | None = None,
    pandoc_format: str | None = None,
) -> None:
    """
    Render a single Markdown file to HTML via pypandoc.

    Args:
        src: Source .md file path.
        dest: Destination .html file path.
        template_path: Optional Pandoc HTML template.
        extra_args: Additional Pandoc CLI arguments.
        pandoc_format: Input format string passed to pypandoc (e.g. "markdown").
    """
    import pypandoc  # type: ignore

    args: list[str] = list(extra_args or [])
    if template_path is not None and template_path.exists():
        args = [f"--template={template_path}"] + [a for a in args if not a.startswith("--template=")]

    dest.parent.mkdir(parents=True, exist_ok=True)
    pypandoc.convert_file(
        str(src),
        "html",
        format=pandoc_format,
        outputfile=str(dest),
        extra_args=args,
    )
    logging.info("render_template: %s -> %s", src, dest)

# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("render", help="Render markdown to HTML via pandoc")
    p.add_argument("--config", type=str, default=None, help="Path to render-flags.yaml")
    p.add_argument(
        "--force",
        action="store_true",
        help="Render all files regardless of modification times",
    )
    p.set_defaults(func=run)

# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace, ctx: RunContext) -> int:
    logging.debug("root=%s", CONFIG.ROOT_DIR)
    logging.debug("config=%s", getattr(args, "config", None))

    content_dir = CONFIG.CONTENT_DIR
    output_dir = CONFIG.OUTPUT_DIR
    templates_dir = CONFIG.BONES / "templates"
    assets_dir = CONFIG.BONES / "assets"
    reports_dir = CONFIG.BONES / "reports"
    manifest_path = reports_dir / "render-manifest.yaml"
    build_manifest_path = reports_dir / "build-manifest.yaml"
    render_state_path = reports_dir / "render-state.yaml"
    base_dir = Path.cwd()

    for d in [output_dir, templates_dir, assets_dir, reports_dir]:
        if not ctx.dry_run:
            d.mkdir(parents=True, exist_ok=True)

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
        markdown_files.sort(key=lambda p: p.relative_to(content_dir).as_posix())
        logging.info("Found %d markdown files under %s", len(markdown_files), content_dir)

    render_config: dict[str, Any] = {}
    if args.config:
        config_path = Path(args.config).expanduser()
        if not config_path.is_absolute():
            config_path = CONFIG.ROOT_DIR / config_path
        if not config_path.exists():
            logging.error("Render config not found: %s", config_path)
            return 2
        try:
            render_config = _load_render_config(config_path)
        except Exception as exc:
            logging.error("Failed to load render config %s: %s", config_path, exc)
            return 2
        logging.info("Loaded render config: %s", config_path)

    pandoc_format, pandoc_args = _build_pandoc_args(render_config, templates_dir, assets_dir)
    if pandoc_format:
        logging.debug("Pandoc format: %s", pandoc_format)
    if pandoc_args:
        logging.debug("Pandoc args: %s", pandoc_args)

    pypandoc = None
    if not ctx.dry_run and markdown_files:
        try:
            import pypandoc as _pypandoc  # type: ignore
            pypandoc = _pypandoc
        except ImportError:
            logging.error("pypandoc is required for render. Install with: pip install rotkeeper[pandoc]")
            return 2

    render_state = load_render_state(render_state_path)
    render_state_dirty = False

    manifest_items: list[dict[str, str]] = []
    build_pages: list[dict[str, str]] = []
    failures = 0
    successes = 0
    skipped = 0
    dry_run_count = 0

    for src in markdown_files:
        rel = src.relative_to(content_dir)
        dest_rel = rel.with_suffix(".html")
        dest = output_dir / dest_rel

        fm_template = _get_frontmatter_template(src)
        template_path: Path | None = None
        if fm_template:
            if Path(fm_template).is_absolute():
                candidate = Path(fm_template)
                template_path = candidate if candidate.exists() else None
            else:
                template_path = _resolve_template(fm_template, templates_dir, assets_dir)
            if template_path is None:
                logging.warning("Frontmatter template not found for %s: %s", src, fm_template)
        elif render_config.get("template"):
            name = str(render_config["template"])
            if Path(name).is_absolute():
                candidate = Path(name)
                template_path = candidate if candidate.exists() else None
            else:
                template_path = _resolve_template(name, templates_dir, assets_dir)
            if template_path is None:
                logging.warning("[render] Template not found: %s", name)
        else:
            default = templates_dir / "default.html"
            if default.exists():
                template_path = default
            else:
                logging.warning("Default system template not found: %s", default)

        state_key = rel.as_posix()
        prev_state = render_state.get(state_key, {})
        needs_render = getattr(args, "force", False) or file_needs_render(src, dest, template_path, prev_state)

        src_mtime = compute_file_mtime(src)
        template_mtime = compute_file_mtime(template_path) if template_path else None

        try:
            manifest_items.append({"input": rel.as_posix(), "output": dest_rel.as_posix()})
            build_pages.append({
                "source": src.relative_to(base_dir).as_posix(),
                "output": dest.relative_to(base_dir).as_posix(),
            })
        except ValueError as exc:
            logging.warning("Could not make path relative to cwd for build manifest: %s", exc)

        if ctx.dry_run:
            logging.info("[dry-run] render %s -> %s (needs_render=%s)", src, dest, needs_render)
            dry_run_count += 1
            continue

        if not needs_render:
            logging.info("Skipping unchanged file: %s", src)
            skipped += 1
            continue

        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            file_args = [a for a in pandoc_args if not a.startswith("--template=")]
            if template_path is not None and template_path.exists():
                file_args = [f"--template={template_path}"] + file_args

            sidecar_path = src.with_suffix(".rk.yaml")
            if sidecar_path.exists():
                file_args += [f"--metadata-file={sidecar_path}"]

            nav_partial = CONFIG.REPORTS_DIR / "nav_partial.md"
            if nav_partial.exists():
                file_args += [f"--include-before-body={nav_partial}"]

            pypandoc.convert_file(
                str(src),
                "html",
                format=pandoc_format,
                outputfile=str(dest),
                extra_args=file_args,
            )
            logging.info("Rendered %s -> %s", src, dest)
            successes += 1
            render_state[state_key] = {
                "src_mtime": src_mtime if src_mtime is not None else time.time(),
                "template_mtime": template_mtime if template_mtime is not None else 0,
            }
            render_state_dirty = True
        except Exception as exc:
            failures += 1
            logging.error("Failed to render %s: %s", src, exc)

    if render_state_dirty:
        save_render_state(render_state_path, render_state)

    manifest_obj = {"render": manifest_items}
    build_manifest_obj = {"pages": build_pages}

    if ctx.dry_run:
        logging.info("[dry-run] would write render manifest: %s", manifest_path)
        logging.info("[dry-run] would write build manifest: %s", build_manifest_path)
        logging.info("[dry-run] render summary: %d files would be processed", dry_run_count)
        return 0

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump(manifest_obj, sort_keys=False), encoding="utf-8")
    logging.info("Wrote render manifest: %s", manifest_path)

    build_manifest_path.write_text(yaml.safe_dump(build_manifest_obj, sort_keys=False), encoding="utf-8")
    logging.info("Wrote build manifest: %s", build_manifest_path)

    build_sass()

    logging.info(
        "Render summary: %d rendered, %d skipped, %d failed",
        successes, skipped, failures,
    )

    if failures:
        logging.error("Render completed with %d failure(s).", failures)
        return 2
    return 0
