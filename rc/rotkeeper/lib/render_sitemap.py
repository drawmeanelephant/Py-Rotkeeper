import os
import sys
import yaml
import logging
import click
from collections import defaultdict
from .render import render_template

logger = logging.getLogger("rotkeeper.commands.render_sitemap")
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def load_sitemap_yaml(path):
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        logger.debug(f"Loaded sitemap YAML from {path}")
        return data
    except Exception as e:
        logger.error(f"Failed to load sitemap YAML from {path}: {e}")
        sys.exit(1)


def build_tree(pages):
    """
    Build a nested dictionary tree from pages list.
    Each page has a 'path' like 'dir/subdir/page.md'.
    Pages with 'show_in_nav: false' are excluded.
    """
    tree = {}

    def insert_path(tree, parts, page):
        if not parts:
            return
        head = parts[0]
        if len(parts) == 1:
            # Leaf node: store page info
            tree.setdefault(head, {})["_page"] = page
        else:
            tree.setdefault(head, {})
            insert_path(tree[head], parts[1:], page)

    for page in pages:
        if page.get("show_in_nav") is False:
            logger.debug(f"Skipping page {page.get('path')} due to show_in_nav: false")
            continue
        path = page.get("path", "")
        if not path:
            logger.debug(f"Skipping page with missing path: {page}")
            continue
        parts = path.strip("/").split("/")
        logger.debug(f"Inserting page {path} into tree at parts: {parts}")
        insert_path(tree, parts, page)

    return tree


def render_tree(tree, level=0):
    """
    Recursively render HTML <ul>/<li> from tree structure.
    Leaf nodes have '_page' key with page info.
    """
    if not tree:
        return ""

    indent = "  " * level
    html = f"{indent}<ul>\n"
    for key in sorted(tree.keys()):
        if key == "_page":
            # Leaf node page
            page = tree["_page"]
            title = page.get("title") or os.path.splitext(os.path.basename(page.get("path", "")))[0]
            url = page.get("url") or page.get("path", "#")
            html += f'{indent}  <li><a href="{url}">{title}</a></li>\n'
        else:
            # Directory node
            # Check if this node has a page directly under '_page'
            page = tree[key].get("_page")
            if page:
                title = page.get("title") or key
                url = page.get("url") or page.get("path", "#")
                html += f'{indent}  <li><a href="{url}">{title}</a>\n'
            else:
                html += f'{indent}  <li>{key}\n'
            # Recurse into subtree excluding '_page'
            subtree = {k: v for k, v in tree[key].items() if k != "_page"}
            html += render_tree(subtree, level + 2)
            html += f'{indent}  </li>\n'
    html += f"{indent}</ul>\n"
    return html


@click.command("render-sitemap")
@click.option(
    "--sitemap-yaml",
    default="sitemap.yaml",
    show_default=True,
    help="Path to sitemap YAML file.",
)
@click.option(
    "--output",
    default="output/sitemap.html",
    show_default=True,
    help="Path to output sitemap HTML file.",
)
@click.option(
    "--template",
    default="default.html.j2",
    show_default=True,
    help="Template file to use for rendering sitemap.",
)
@click.option(
    "--dry-run/--no-dry-run",
    default=False,
    help="Do not write output file, just show what would be done.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (use -v, -vv for more).",
)
@click.option(
    "--minimal/--no-minimal",
    default=False,
    help="Render minimal sitemap without extra decorations.",
)
def render_sitemap(sitemap_yaml, output, template, dry_run, verbose, minimal):
    """
    Render the sitemap HTML page from a sitemap YAML file using pages.
    """

    # Set logging level based on verbosity
    if verbose == 1:
        logger.setLevel(logging.DEBUG)
    elif verbose >= 2:
        logger.setLevel(logging.NOTSET)

    logger.info(f"Rendering sitemap from {sitemap_yaml} to {output} using template {template}")
    if dry_run:
        logger.info("Dry run mode - no files will be written.")

    # Load sitemap YAML
    sitemap_data = load_sitemap_yaml(sitemap_yaml)

    if not isinstance(sitemap_data, dict):
        logger.error("Sitemap YAML root must be a dictionary.")
        sys.exit(1)

    pages = sitemap_data.get("pages")
    if not isinstance(pages, list):
        logger.error("Sitemap YAML must contain a 'pages' list.")
        sys.exit(1)

    logger.debug(f"Loaded {len(pages)} pages from sitemap.yaml")

    # Build nested tree from pages
    tree = build_tree(pages)
    logger.debug("Built nested tree structure for sitemap")

    # Generate navigation HTML
    nav_html = render_tree(tree)
    logger.debug("Generated navigation HTML")

    # Prepare template context
    context = {
        "nav_html": nav_html,
        "minimal": minimal,
        "title": sitemap_data.get("title", "Sitemap"),
    }

    # Render template
    try:
        rendered_html = render_template(template, **context)
    except Exception as e:
        logger.error(f"Failed to render sitemap template: {e}")
        sys.exit(1)

    if dry_run:
        logger.info("Rendered HTML preview:\n" + rendered_html)
    else:
        # Ensure output directory exists
        output_dir = os.path.dirname(output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.debug(f"Created output directory {output_dir}")

        # Write to output file
        try:
            with open(output, "w", encoding="utf-8") as f:
                f.write(rendered_html)
            logger.info(f"Sitemap written to {output}")
        except Exception as e:
            logger.error(f"Failed to write sitemap to {output}: {e}")
            sys.exit(1)
