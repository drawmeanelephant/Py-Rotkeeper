---
title: "Sitemap"
slug: sitemap-index
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - sitemap
  - navigation
  - reference
description: "Overview of Rotkeeper sitemap commands: sitemap, sitemap_pipeline, and render_sitemap."
toc: false
rotkeeper_nav:
  - "20_Sitemap"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "sitemap/index.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Sitemap

The sitemap commands read your content tree and frontmatter to produce navigation structures and XML sitemaps.  
They run after `rc render` and depend on the frontmatter fields — especially `rotkeeper_nav`, `show_in_nav`, and `draft` — being correct on every page.

---

## Sitemap Commands

| Command | What it does |
|---|---|
| [`rc sitemap`](sitemap.md) | Scans content and generates the nav data and sitemap file |
| [`rc sitemap_pipeline`](sitemap_pipeline.md) | Runs the full sitemap sequence as a single pipeline step |
| [`rc render_sitemap`](render_sitemap.md) | Renders the sitemap data into the final HTML nav and XML output |

---

## Typical Run Order

```bash
rc render
rc sitemap
rc render_sitemap
```

Or use the pipeline shortcut:

```bash
rc sitemap_pipeline
```

`sitemap_pipeline` wraps `sitemap` and `render_sitemap` into one call — use it when you don't need to inspect the intermediate sitemap data.

---

## What Controls the Nav

Pages appear in the nav when **all three** of these are true:

- `rotkeeper_nav` is set with at least one token
- `show_in_nav: true`
- `draft: false` and `published: true`

See [Concepts → Pandoc Frontmatter](../concepts/pandoc-frontmatter.md) for the full field reference.

---

## Pages in This Section

- [sitemap](sitemap.md) — scan and generate sitemap data
- [sitemap_pipeline](sitemap_pipeline.md) — full sitemap sequence in one command
- [render_sitemap](render_sitemap.md) — render sitemap data to HTML nav and XML
