from __future__ import annotations

import argparse
import logging
import yaml
from pathlib import Path

from ..config import CONFIG
from ..context import RunContext

logger = logging.getLogger(__name__)

def add_parser(subparsers):
    p = subparsers.add_parser("sitemap-nav-partial",
        help="Write HTML nav partial for Pandoc --include-before-body")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=run)

def run(args: argparse.Namespace, ctx: RunContext | None = None) -> int:
    cfg = ctx.config if (ctx and ctx.config) else CONFIG
    dry_run = getattr(args, "dry_run", False) or getattr(ctx, "dry_run", False)

    sitemap_path = cfg.REPORTS_DIR / "sitemap_pipeline.yaml"
    if not sitemap_path.exists():
        logger.error("sitemap_pipeline.yaml missing – run sitemap-collect first")
        return 1

    data = yaml.safe_load(sitemap_path.read_text(encoding="utf-8"))
    nav_tree = data.get("rotkeepernav", {})

    if dry_run:
        logger.info("[dry-run] Would write nav_partial.html")
        return 0

    output_file = cfg.REPORTS_DIR / "nav_partial.html"
    cfg.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

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
    html_lines = ['<nav class="site-nav">']
    html_lines.append("  <ul>")
    html_lines.extend(items)
    html_lines.append("  </ul>")
    html_lines.append("</nav>")

    output_file.write_text("\n".join(html_lines) + "\n", encoding="utf-8")
    logger.info("Wrote nav partial %s", output_file)
    return 0