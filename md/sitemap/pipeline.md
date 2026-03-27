---
title: "rc sitemap-pipeline"
slug: sitemap-pipeline
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - sitemap
  - navigation
  - pipeline
  - reference
description: "Full sitemap pipeline: collects pages, builds metadata trees, writes index pages, nav partial, sidecar metadata, and a unified YAML report."
toc: true
rotkeeper_nav:
  - "20_Sitemap"
  - "sitemap_pipeline"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "sitemap/sitemap-pipeline.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc sitemap-pipeline

`rc sitemap-pipeline` is the full-featured sitemap command that runs all five stages in sequence.  
It is the recommended command for standard builds — use `rc sitemap` only when you need the raw page catalog without any of the generated outputs.

---

## What it does

The pipeline runs up to six stages in order:

| Stage | What it produces |
|---|---|
| 1. **Collect pages** | Reads frontmatter from all `.md` files; filters drafts and hidden files |
| 2. **Build metadata trees** | Groups pages by `tags`, `author`, `date`, and `rotkeeper_nav` |
| 3. **Write index pages** | Generates `home/content/generated/` with tag, author, date, and master sitemap pages |
| 4. **Write nav partial** | Writes `home/bones/reports/nav_partial.md` — injected into every page by `rc render` |
| 5. **Write sidecar metadata** | Writes a `.rk.yaml` file alongside each source `.md` with related pages, breadcrumbs, and tag links |
| 6. **Write unified YAML** | Writes `home/bones/reports/sitemap_pipeline.yaml` with the full page + metadata tree |

---

## Usage

```bash
rc sitemap-pipeline
rc sitemap-pipeline --dry-run
rc sitemap-pipeline --verbose
rc sitemap-pipeline --index-only
rc sitemap-pipeline --metadata-only
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--dry-run` | bool | false | Log all actions without writing any files |
| `--verbose` | bool | false | Print extra diagnostic output including tree structures |
| `--index-only` | bool | false | Run stage 1 only (collect pages); skip all writes |
| `--metadata-only` | bool | false | Run stages 1–2 (collect + build trees); skip all writes |
| `--write-only` | bool | false | Skip collection; run stages 3–6 using whatever is already in memory |

Stage flags are evaluated in priority order: `--index-only` → `--metadata-only` → `--write-only` → full pipeline.

---

## Generated Index Pages

Stage 3 writes auto-generated Markdown files to `home/content/generated/`. These are normal `.md` files and are picked up by `rc render` on the next build:

| File | Contents |
|---|---|
| `generated/tags/index.md` | All tags with page lists |
| `generated/tags/<slug>.md` | One page per tag with descriptions |
| `generated/authors/index.md` | All authors with page lists |
| `generated/dates/index.md` | All pages grouped by date (reverse chronological) |
| `generated/sitemap.md` | Flat list of all pages |

All generated files have `show_in_nav: false` by default so they don't pollute the main nav.

---

## Nav Partial

Stage 4 writes `home/bones/reports/nav_partial.md` — a fenced Pandoc div:

```markdown
::: site-nav
- [Home](index.html)
  - [Quickstart](quickstart.html)
- [Pipeline](pipeline/index.html)
  - [render](pipeline/render.html)
:::
```

`rc render` passes this to Pandoc as `--include-before-body`, so every page gets consistent nav without modifying source files. The nav strips numeric prefixes from display labels (`10_Pipeline` → `Pipeline`).

---

## Sidecar Metadata

Stage 5 writes a `.rk.yaml` file alongside each source `.md` in `home/content/`. `rc render` passes these to Pandoc as `--metadata-file`, making these template variables available:

| Variable | Contents |
|---|---|
| `$rotkeeper.breadcrumb$` | List of nav token labels from root to page |
| `$rotkeeper.related_pages$` | Up to 5 pages sharing at least one tag |
| `$rotkeeper.tag_pages$` | Links to each tag's generated index page |
| `$rotkeeper.author_page$` | Link to the authors index page |

---

## Example

```bash
# Standard full build
rc render
rc sitemap-pipeline
rc render        # re-render to pick up nav partial and generated pages
```

The double render is needed because `sitemap-pipeline` writes files that `render` needs to include. On incremental builds, only changed files are re-rendered the second time.

---

## Notes

- `rc sitemap-pipeline` requires `python-frontmatter` to be installed (`pip install rotkeeper` includes it).
- Generated files in `home/content/generated/` are machine-written. Do not edit them manually — they are overwritten on every run.
- The nav partial is written to `home/bones/reports/`, not `home/content/`, so it is never rendered as a standalone page.
- Pages with duplicate output paths are skipped after the first occurrence; a warning is logged.
