---
title: "rc render-sitemap"
slug: sitemap-render-sitemap
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - sitemap
  - navigation
  - reference
description: "Stub: renders the sitemap data into final HTML nav and XML output."
toc: false
rotkeeper_nav:
  - "20_Sitemap"
  - "render_sitemap"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "sitemap/render-sitemap.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc render-sitemap

`rc render-sitemap` is intended to be the final rendering step of the sitemap workflow — taking the data written by `rc sitemap` or `rc sitemap-pipeline` and producing HTML nav output and an XML sitemap.

In practice, `rc sitemap-pipeline` already handles nav partial generation and sidecar metadata as part of its pipeline. `rc render-sitemap` exists as a dedicated step for cases where you want to re-render the sitemap outputs without re-running the full collection and tree-building stages.

> ⚠️ This command's standalone behavior is currently handled inside `rc sitemap-pipeline`. Check `rc sitemap-pipeline --write-only` as an equivalent in the meantime.

---

## Relationship to Other Commands

| Command | Role |
|---|---|
| `rc sitemap` | Collects pages and writes `sitemap.yaml` |
| `rc sitemap-pipeline` | Full pipeline including nav partial, sidecars, and index pages |
| `rc render-sitemap` | Renders sitemap data to final nav and XML outputs (see note above) |
| `rc nav` | Reads `sitemap.yaml` and writes the structured `nav.yaml` |

---

## Notes

- For most builds, `rc sitemap-pipeline` is the right command — it covers everything `rc render-sitemap` is intended to do.
- See [Sitemap → sitemap-pipeline](sitemap-pipeline.md) for the full pipeline reference.
