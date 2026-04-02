from __future__ import annotations
import argparse
import logging
import yaml
from pathlib import Path
from ..config import CONFIG
from ..context import RunContext

logger = logging.getLogger(__name__)


def add_parser(subparsers: argparse.SubParsersAction) -> None:
    p = subparsers.add_parser(
        "sitemap-nav-partial",
        help="Write HTML nav partial for Pandoc --include-before-body",
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    if ctx is not None and not isinstance(ctx, RunContext):
        raise TypeError(f"ctx must be a RunContext or None, got {type(ctx)!r}")

    cfg = ctx.config if ctx is not None and ctx.config is not None else CONFIG
    dry_run = ctx.dry_run if ctx is not None else False

    sitemap_path = cfg.REPORTS_DIR / "sitemappipeline.yaml"
    if not sitemap_path.exists():
        logger.error("sitemappipeline.yaml missing — run sitemap-collect first")
        return 1

    data = yaml.safe_load(sitemap_path.read_text(encoding="utf-8"))
    nav_tree = data.get("rotkeeper_nav", {})

    if dry_run:
        logger.info("dry-run: Would write navpartial.html")
        return 0

    cfg.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = cfg.REPORTS_DIR / "navpartial.html"

    def render_items(tree: dict, depth: int = 0) -> list[str]:
        lines: list[str] = []
        indent = " " * (depth * 2)
        for group_name, group_data in tree.items():
            if group_name in ("pages", "children") or not isinstance(group_data, dict):
                continue
            lines.append(f'{indent}<li class="nav-group">')
            lines.append(f'{indent}  <span>{group_name}</span>')
            lines.append(f'{indent}  <ul>')
            for page in group_data.get("pages", []):
                title = page.get("title", "Untitled")
                path = page.get("path", "")
                lines.append(f'{indent}    <li><a href="{path}">{title}</a></li>')
            lines.extend(render_items(group_data.get("children", {}), depth + 2))
            lines.append(f'{indent}  </ul>')
            lines.append(f'{indent}</li>')
        return lines

    html_lines = ['<nav class="site-nav">', '  <ul>']
    html_lines.extend(render_items(nav_tree))
    html_lines += ['  </ul>', '</nav>']
    output_file.write_text("\n".join(html_lines) + "\n", encoding="utf-8")
    logger.info("Wrote nav partial %s", output_file)
    return 0
