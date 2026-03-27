---
title: "Utilities"
slug: utilities-index
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - utilities
  - nav
  - cleanup
  - book
  - reference
description: "Overview of Rotkeeper utility commands: nav, cleanup_bones, and book."
toc: false
rotkeeper_nav:
  - "40_Utilities"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "utilities/index.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Utilities

Utility commands handle tasks that sit outside the core build pipeline — nav rendering, output cleanup, and book/scriptbook export.  
They are typically run selectively rather than as part of every build.

---

## Utility Commands

| Command | What it does |
|---|---|
| [`rc nav`](nav.md) | Renders the navigation structure into templates |
| [`rc cleanup_bones`](cleanup_bones.md) | Removes stale files from `output/` without touching source |
| [`rc book`](book.md) | Exports content as a combined book or scriptbook artifact |

---

## When to Use Each

**`rc nav`** — run when nav structure has changed (new pages, reordered tokens) but you don't need a full render. Useful for iterating on nav layout without rebuilding all HTML.

**`rc cleanup_bones`** — run before a clean build to remove orphaned output files (pages that were deleted from source but still exist in `output/`). Safe to run at any time; it does not touch `home/`.

**`rc book`** — run when you want a single combined output (e.g. a PDF-ready or single-HTML artifact). Typically a one-off rather than part of the standard build loop.

---

## Pages in This Section

- [nav](nav.md) — render nav structure into templates
- [cleanup_bones](cleanup_bones.md) — remove stale output files
- [book](book.md) — export content as a combined book artifact
