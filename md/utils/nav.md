---
title: "rc nav"
slug: utilities-nav
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - utilities
  - navigation
  - reference
description: "Reads sitemap.yaml and writes nav.yaml — a structured navigation tree grouped by rotkeeper_nav, author, date, and tags."
toc: true
rotkeeper_nav:
  - "40_Utilities"
  - "nav"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "utilities/nav.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc nav

`rc nav` reads `home/bones/reports/sitemap.yaml` and produces `home/bones/reports/nav.yaml` — a fully structured navigation tree organized by `rotkeeper_nav` section, author, date, and tags.  
Use it when you need the nav data file updated without running the full `sitemap-pipeline`.

---

## What it does

1. Reads `home/bones/reports/sitemap.yaml` (exits with error if not found)
2. Filters out pages where `show_in_nav` is false
3. Builds five parallel navigation trees from the page list:
   - **`rotkeeper_nav`** — hierarchical tree from nav tokens, sorted by numeric prefix
   - **`author`** — pages grouped alphabetically by author
   - **`date`** — pages nested by year → month → day
   - **`tags`** — pages grouped alphabetically by tag
   - **`keywords`** — pages grouped alphabetically by keyword
4. Writes the combined structure to `home/bones/reports/nav.yaml`

Numeric prefixes are stripped from display labels in the output (`10_Pipeline` → `Pipeline`).

---

## Usage

```bash
rc nav
rc nav --dry-run
rc nav --verbose
rc nav --output path/to/custom-nav.yaml
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--output` | path | `home/bones/reports/nav.yaml` | Custom output path for the nav YAML |
| `--dry-run` | bool | false | Print the nav YAML to stdout without writing any file |
| `--verbose` | bool | false | Print top-level groups and page titles after writing |

---

## nav.yaml structure

```yaml
rotkeeper_nav:
  - group: Home
    pages:
      - title: "Rotkeeper Documentation"
        path: index.html
        ...
  - group: Pipeline
    pages:
      - group: render
        pages: [...]

author:
  - group: "Filed Systems"
    pages: [...]

date:
  - group: "2026"
    pages:
      - group: "03"
        pages:
          - group: "20"
            pages: [...]

tags:
  - group: pipeline
    pages: [...]

keywords:
  - group: pandoc
    pages: [...]
```

---

## Example

```bash
rc sitemap
rc nav
rc nav --dry-run    # inspect nav structure without writing
```

---

## Notes

- `rc nav` requires `sitemap.yaml` to exist. Run `rc sitemap` or `rc sitemap-pipeline` first.
- Pages without any `rotkeeper_nav` tokens are placed in a `Misc` group.
- Pages without a valid ISO date string in the `date` field are placed in a `Misc` group in the date tree.
- `rc nav` does **not** write a nav partial for injection into rendered pages — that is done by `rc sitemap-pipeline` stage 4. `rc nav` produces a data file only.
