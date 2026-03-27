---
title: "rc sitemap"
slug: sitemap-sitemap
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - sitemap
  - navigation
  - reference
description: "Scans content frontmatter and writes sitemap.yaml — the page catalog used by nav and sitemap-pipeline."
toc: true
rotkeeper_nav:
  - "20_Sitemap"
  - "sitemap"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "sitemap/sitemap.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc sitemap

`rc sitemap` walks `home/content/`, reads the frontmatter of every Markdown file, and writes a structured page catalog to `home/bones/reports/sitemap.yaml`.  
This catalog is the data source for `rc nav`, `rc sitemap-pipeline`, and `rc render_sitemap`.

---

## What it does

1. Recursively scans `home/content/` for `.md` files (skips files starting with `_` and any hidden directories)
2. Loads frontmatter from each file; skips files where `draft: true` or `published: false`
3. Extracts `title`, `path`, `author`, `date`, `keywords`, `tags`, `rotkeeper_nav`, and `show_in_nav` from each file
4. Sorts pages by `rotkeeper_nav` numeric prefix, falling back to title alphabetically
5. Writes the sorted list to `home/bones/reports/sitemap.yaml`

---

## Usage

```bash
rc sitemap
rc sitemap --dry-run
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--dry-run` | bool | false | Log what would be written without creating `sitemap.yaml` |

---

## sitemap.yaml format

```yaml
pages:
  - path: index.html
    title: "Rotkeeper Documentation"
    author: "Filed Systems"
    date: "2026-03-20"
    tags: [rotkeeper, reference]
    keywords: []
    rotkeeper_nav: ["00_Home"]
    show_in_nav: true
```

Each entry maps directly to the frontmatter fields read from the source file. Pages with `show_in_nav: false` are included in `sitemap.yaml` but will be excluded from rendered nav structures by downstream commands.

---

## Example

```bash
rc render
rc sitemap
rc nav
```

---

## Notes

- `rc sitemap` only reads files — it never writes to `home/content/` or `output/`.
- Files without a `title` field use the filename stem as the title.
- If frontmatter cannot be parsed for a file, that file is skipped with a warning logged.
- Pages with duplicate output paths (two `.md` files resolving to the same `.html`) are skipped after the first with a warning.
- For the full pipeline including nav partial and sidecar generation, use `rc sitemap-pipeline` instead.
