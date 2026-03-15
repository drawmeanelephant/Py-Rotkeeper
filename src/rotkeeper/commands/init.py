from __future__ import annotations

import argparse
import logging

from pathlib import Path
from ..context import RunContext


def add_parser(subs: argparse._SubParsersAction) -> None:
    p = subs.add_parser("init", help="Initialize environment")
    p.add_argument("--force", action="store_true", help="Force rebuild/re-init")
    p.set_defaults(func=run)


def run(args: argparse.Namespace, ctx: RunContext) -> int:
    root = ctx.paths.root_dir
    home = root / "home"
    force = bool(getattr(args, "force", False))

    print(f"Initializing rotkeeper project in: {root}")

    # Directories to create under home
    directories = [
        home / "content",
        home / "bones" / "templates",
        home / "bones" / "assets" / "styles",
        home / "bones" / "config",
        home / "bones" / "reports",
    ]

    for directory in directories:
        if directory.exists() and not force:
            print(f"  - Skipping existing directory: {directory.relative_to(root)}")
        else:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created {directory.relative_to(root)}/")

    # Sample Markdown inside home/content
    sample_md = home / "content" / "sample.md"
    if not sample_md.exists() or force:
        sample_md.write_text("""---
title: Sample Document
author: Your Name
date: 2026-03-14
tags: [sample, getting-started]
---

# Welcome to Rotkeeper

This is a sample Markdown document to get you started.
""")
        print(f"  ✓ Created {sample_md.relative_to(root)}")
    else:
        print(f"  - Skipping existing file: {sample_md.relative_to(root)}")

    # Default HTML template with frontmatter, TOC, math, and CSS inside home/bones/templates
    default_template = home / "bones" / "templates" / "default.html"
    if not default_template.exists() or force:
        default_template.write_text("""---
title: "{{ title | default('Document') }}"
description: ""
keywords: []
---

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{{ title | default('Document') }}</title>
    <link rel="stylesheet" href="/assets/styles/main.css" />
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.4/dist/katex.min.js" defer></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.4/dist/katex.min.css" />
</head>
<body>
    <nav>
        <h1>{{ title | default('Document') }}</h1>
        {{ toc }}
    </nav>
    <main>
        {{ content }}
    </main>
</body>
</html>
""")
        print(f"  ✓ Created {default_template.relative_to(root)}")
    else:
        print(f"  - Skipping existing file: {default_template.relative_to(root)}")

    # SCSS files in home/bones/assets/styles
    scss_files = {
        "main.scss": """@use 'variables';
@use 'mixins';

body {
  font-family: variables.$font-sans;
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto;
  padding: variables.$spacing-lg;
  color: variables.$color-text;
  background-color: variables.$color-background;
}

h1, h2, h3 {
  color: variables.$color-heading;
}

a {
  color: variables.$color-link;
  text-decoration: none;
  &:hover { text-decoration: underline; }
}

code {
  @include mixins.code-style;
}

pre {
  @include mixins.code-style;
  padding: 1rem;
}
""",
        "_variables.scss": """$font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
$font-mono: "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;

$spacing-lg: 2rem;

$color-text: #222;
$color-background: #ffffff;
$color-heading: #111;
$color-link: #0a58ca;

$code-bg: #f5f5f5;
$code-border-radius: 4px;

$breakpoint-sm: 576px;
$breakpoint-md: 768px;
$breakpoint-lg: 992px;
$breakpoint-xl: 1200px;
""",
        "_mixins.scss": """@use 'variables';

@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

@mixin respond-to($breakpoint) {
  @if $breakpoint == sm { @media (min-width: variables.$breakpoint-sm) { @content; } }
  @else if $breakpoint == md { @media (min-width: variables.$breakpoint-md) { @content; } }
  @else if $breakpoint == lg { @media (min-width: variables.$breakpoint-lg) { @content; } }
  @else if $breakpoint == xl { @media (min-width: variables.$breakpoint-xl) { @content; } }
}

@mixin code-style {
  background: variables.$code-bg;
  border-radius: variables.$code-border-radius;
  padding: 0.2rem 0.4rem;
  font-family: variables.$font-mono;
  overflow-x: auto;
}
"""
    }

    for filename, content in scss_files.items():
        scss_path = home / "bones" / "assets" / "styles" / filename
        if not scss_path.exists() or force:
            scss_path.write_text(content)
            print(f"  ✓ Created {scss_path.relative_to(root)}")
        else:
            print(f"  - Skipping existing file: {scss_path.relative_to(root)}")

    # render-flags.yaml inside home/bones/config
    render_flags = home / "bones" / "config" / "render-flags.yaml"
    if not render_flags.exists() or force:
        render_flags.write_text("""# Rotkeeper Render Configuration
default_template: default
output_dir: output
markdown_extensions:
  - tables
  - fenced_code
  - codehilite
  - toc
  - attr_list
  - def_list
  - admonition
  - smarty
  - mathjax
render_options:
  generate_toc: true
  code_theme: default
  output_extension: .html
  pretty_html: true
manifest:
  enabled: true
  filename: manifest.json
  include_hashes: true
watch:
  watch_dirs:
    - content
    - bones/templates
    - bones/config
    - bones/assets/styles
  patterns:
    - "*.md"
    - "*.html"
    - "*.yaml"
    - "*.scss"
  debounce_ms: 500
""")
        print(f"  ✓ Created {render_flags.relative_to(root)}")
    else:
        print(f"  - Skipping existing file: {render_flags.relative_to(root)}")

    # Reports README inside home/bones/reports
    reports_readme = home / "bones" / "reports" / "README.md"
    if not reports_readme.exists() or force:
        reports_readme.write_text("# Render Reports\n\nThis folder contains manifests and logs generated by Rotkeeper.")
        print(f"  ✓ Created {reports_readme.relative_to(root)}")
    else:
        print(f"  - Skipping existing file: {reports_readme.relative_to(root)}")

    # .gitignore in root
    gitignore = root / ".gitignore"
    if not gitignore.exists() or force:
        gitignore.write_text("""output/
*.html
!home/bones/templates/*.html
home/bones/assets/styles/*.css
__pycache__/
*.py[cod]
.venv/
env/
*.swp
.DS_Store
""")
        print(f"  ✓ Created {gitignore.relative_to(root)}")
    else:
        print(f"  - Skipping existing file: {gitignore.relative_to(root)}")

    print("\n✨ Rotkeeper project initialized successfully!")
    print("Next steps:")
    print("  1. Edit home/content/sample.md or add new Markdown files")
    print("  2. Customize home/bones/templates/default.html and home/bones/assets/styles/*.scss")
    print("  3. Run 'rotkeeper render' to generate output")
    print("  4. Check home/bones/reports/ for rendering manifests\n")

    return 0
