---
title: "Rotkeeper Documentation"
slug: index
template: rot-doc.html
version: "0.0.2-pre"
updated: "2026-03-20"
description: "Landing page and navigation guide for Rotkeeper documentation."
tags:
  - rotkeeper
  - reference
  - index
rotkeeper_nav:
  - "00_Home"
show_in_nav: true
draft: false
published: true
author: "Filed Systems"
asset_meta:
  name: "index.md"
  version: "0.0.2-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# 📖 Rotkeeper

Rotkeeper is a Python-based static site generator that uses [Pandoc](https://pandoc.org) to render Markdown into HTML.  
It is driven by YAML frontmatter — every page declares its own nav membership, visibility, and metadata.

> 🕯️ Every file has a reason. Understanding it keeps your rituals tidy.

---

## What Rotkeeper Does

Rotkeeper reads Markdown files from `home/content/`, processes frontmatter, renders HTML via Pandoc, compiles SCSS, collects assets, and writes the final site to `output/`.

The CLI is invoked as `rc`. A full build looks like:

```bash
rc render
rc assets
rc sitemap
```

See [Quickstart](quickstart.md) for installation and first-run instructions.

---

## Documentation Sections

| Section | What it covers |
|---|---|
| [Quickstart](quickstart.md) | Install, initialize, and run your first build |
| [Pipeline](pipeline/index.md) | `render`, `assets`, `collect_assets` — the core build pipeline |
| [Sitemap](sitemap/index.md) | Sitemap generation and nav rendering |
| [Scaffold](scaffold/index.md) | `init` and `reseed` — project setup and content seeding |
| [Utilities](utilities/index.md) | `nav`, `cleanup_bones`, `book` |
| [Concepts](concepts/pandoc-frontmatter.md) | Pandoc frontmatter fields and how Rotkeeper reads them |

---

## Project Layout

```text
rotkeeper/                  ← main Python repo
  src/rotkeeper/
    cli.py                  ← argument parsing; entry point is `rc`
    commands/               ← one file per CLI command
      render.py
      assets.py
      collect_assets.py
      init.py
      reseed.py
      sitemap.py
      cleanup_bones.py
      book.py
    context.py              ← runtime context and path resolution
    paths.py                ← filesystem helpers
    deps.py                 ← checks for Pandoc, Sass
    exec.py                 ← subprocess runner
  src/tests/                ← unit tests

home/                       ← site source root
  content/                  ← Markdown source files (including this file)
  bones/
    templates/              ← HTML templates (e.g. rot-doc.html)
    assets/
      styles/               ← SCSS: _variables.scss, _mixins.scss, main.scss
    config/                 ← render-flags.yaml and other config
    reports/                ← build logs and manifests (read-only)

output/                     ← rendered site (git-ignored)
```

---

## Frontmatter Quick Reference

Every page should include these fields:

```yaml
---
title: ""
rotkeeper_nav: ["00_Home"]   # controls nav section and sort order
show_in_nav: true
draft: false
published: true
author: ""
tags: []
description: ""
date: YYYY-MM-DD
---
```

Nav tokens sort numerically by prefix: `00_Home` → `10_Pipeline` → `20_Sitemap` etc.  
A page with `show_in_nav: false` renders but does not appear in navigation.  
A page with `draft: true` is excluded from the build entirely.
