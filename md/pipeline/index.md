---
title: "Pipeline"
slug: pipeline-index
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - pipeline
  - render
  - assets
  - reference
description: "Overview of the Rotkeeper build pipeline: render, assets, and collect_assets."
toc: false
rotkeeper_nav:
  - "10_Pipeline"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "pipeline/index.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Pipeline

The pipeline is the core of every Rotkeeper build.  
Running `rc render`, `rc assets`, and `rc collect_assets` in sequence takes your source files — Markdown, SCSS, images, templates — and produces a complete static site in `output/`.

> 🕯️ The pipeline does not clean up after itself by default. Run `rc cleanup_bones` if you need a fresh output directory before building.

---

## Pipeline Commands

| Command | What it does |
|---|---|
| [`rc render`](render.md) | Compiles Markdown to HTML via Pandoc; applies templates |
| [`rc assets`](assets.md) | Copies static assets (CSS, images, fonts) into `output/` |
| [`rc collect_assets`](collect_assets.md) | Gathers declared assets from frontmatter manifests |

Run them in this order:

```bash
rc render
rc assets
rc collect_assets
```

`render` must come first — it produces the HTML and generates the asset manifest that `collect_assets` reads.

---

## What Each Step Touches

```text
home/content/          →  rc render        →  output/*.html
home/bones/assets/     →  rc assets        →  output/assets/
frontmatter manifests  →  rc collect_assets →  output/assets/ (declared files)
```

---

## When to Run the Full Pipeline

Run all three commands any time you:

- Add or edit a Markdown page
- Change a template
- Add new images or fonts
- Modify SCSS (which `rc render` also compiles)

For SCSS-only changes, `rc assets` alone is sufficient.

---

## Pages in This Section

- [render](render.md) — Markdown → HTML compilation, template selection, SCSS build
- [assets](assets.md) — static asset copying and path resolution
- [collect_assets](collect_assets.md) — frontmatter-driven asset collection
