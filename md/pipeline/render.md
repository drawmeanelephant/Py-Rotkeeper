---
title: "rc render"
slug: pipeline-render
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - pipeline
  - render
  - pandoc
  - reference
description: "Compiles Markdown to HTML via Pandoc, applies templates, and compiles SCSS."
toc: true
rotkeeper_nav:
  - "10_Pipeline"
  - "render"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "pipeline/render.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc render

`rc render` is the first and most important step in every Rotkeeper build.  
It walks `home/content/`, compiles each Markdown file to HTML via Pandoc, applies the correct template, and then compiles SCSS to CSS.  
After it runs, it writes a render manifest and a build manifest to `home/bones/reports/` for use by downstream commands.

---

## What it does

1. Scans `home/content/` recursively for `.md` files (skips files and folders prefixed with `.` or `_`)
2. Resolves a template for each file — frontmatter `template:` field wins, then `render-flags.yaml`, then `default.html`
3. Checks modification times against `render-state.yaml`; skips unchanged files unless `--force` is set
4. Calls `pypandoc.convert_file()` to render each file to `output/`
5. Injects a nav partial (`home/bones/reports/nav_partial.md`) before each page body if one exists
6. Injects a sidecar metadata file (`.rk.yaml`) alongside the source if one exists
7. Compiles `home/bones/assets/styles/main.scss` → `output/css/main.css` via the `sass` CLI
8. Writes `home/bones/reports/render-manifest.yaml` and `build-manifest.yaml`

---

## Usage

```bash
rc render
rc render --force
rc render --config path/to/render-flags.yaml
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--config` | path | none | Path to a `render-flags.yaml` config file; overrides the default config resolution |
| `--force` | bool | false | Render all files regardless of modification times; ignores `render-state.yaml` |

The global `--dry-run` flag (set on `rc` itself) is also respected — render will log what it would do without writing any files or manifests.

---

## Template Resolution Order

For each `.md` file, the template is resolved in this priority order:

1. **Frontmatter** — `template:` field in the file's YAML frontmatter
2. **Render config** — `template:` key in `render-flags.yaml`
3. **Default** — `home/bones/templates/default.html`

Templates are searched in two locations: `home/bones/templates/` and `home/bones/assets/templates/`.  
If no template is found anywhere, the file is rendered without one and a warning is logged.

---

## render-flags.yaml

Optional config file that sets Pandoc options for all files in a build.  
Pass it with `--config` or place it at `home/bones/config/render-flags.yaml`.

```yaml
template: rot-doc.html
css:
  - css/main.css
toc: false
math: false
extra_args:
  - "--standalone"
```

| Key | Type | Description |
|---|---|---|
| `template` | string | Default template name (overridden by frontmatter) |
| `css` | string or list | CSS paths passed to Pandoc as `--css` |
| `toc` | bool | Enables Pandoc's auto table of contents |
| `math` | bool | Enables MathJax via `--mathjax` |
| `extra_args` | list | Any additional raw Pandoc arguments |
| `from` / `format` | string | Pandoc input format (default: `markdown`) |

---

## Example

```bash
# Standard build
rc render

# Force full rebuild, ignoring state cache
rc render --force

# Use a non-default config
rc render --config home/bones/config/render-flags-draft.yaml

# Preview what would be rendered without writing anything
rc --dry-run render
```

---

## Output Files

| File | Description |
|---|---|
| `output/**/*.html` | Rendered HTML pages, mirroring the `home/content/` tree |
| `output/css/main.css` | Compiled and compressed CSS from `main.scss` |
| `home/bones/reports/render-manifest.yaml` | Maps each `.md` source to its `.html` output |
| `home/bones/reports/build-manifest.yaml` | Full source/output path list for downstream commands |
| `home/bones/reports/render-state.yaml` | Modification time cache used for incremental builds |

---

## Notes

- Files and directories whose names begin with `.` or `_` are skipped automatically and will never be rendered.
- `rc render` does **not** clean `output/` before running. Deleted source files leave orphaned HTML behind. Run `rc cleanup_bones` to remove them.
- SCSS compilation requires the `sass` CLI. Install it with `npm install -D sass`. If `sass` is not found, a warning is logged and the CSS step is skipped — HTML rendering is unaffected.
- `pypandoc` must be installed. If missing, render exits with code `2` and logs an install hint: `pip install rotkeeper[pandoc]`.
- The nav partial (`nav_partial.md`) is written by `rc sitemap_pipeline`. If it doesn't exist yet, it is silently skipped.
