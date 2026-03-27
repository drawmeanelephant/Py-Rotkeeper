---
title: "Changelog"
slug: changelog
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - changelog
  - reference
description: "Release history and notable changes for Rotkeeper."
toc: true
rotkeeper_nav:
  - "02_Changelog"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "changelog.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Changelog

All notable changes to Rotkeeper are documented here.  
Versions follow [Semantic Versioning](https://semver.org): `MAJOR.MINOR.PATCH`.  
Dates are in `YYYY-MM-DD` format.

---

## 0.0.2-pre — 2026-03-20

### Fixed
- `index.md` updated to reflect current project layout; stale file paths removed
- `quickstart.md` Python requirement corrected from 3.7+ to 3.10+
- All documentation CLI references updated from `rotkeeper` to `rc`
- `rotkeeper_nav` frontmatter added to all documentation pages

### Added
- Full documentation site scaffolded under `home/content/docs/`
- Section index pages for Pipeline, Sitemap, Scaffold, Utilities, and Concepts
- Command pages for: `render`, `assets`, `collect-assets`, `init`, `reseed`, `book`, `sitemap`, `sitemap-pipeline`, `render-sitemap`, `nav`, `cleanup-bones`
- Concepts page: Pandoc frontmatter field reference

---

## 0.0.1-pre — 2026-03-14

### Added
- Initial project structure: `home/`, `src/rotkeeper/`, `output/`
- Core pipeline commands: `rc render`, `rc assets`, `rc collect-assets`
- Sitemap commands: `rc sitemap`, `rc sitemap-pipeline`
- Scaffold commands: `rc init`, `rc reseed` (stub)
- Utility commands: `rc nav`, `rc cleanup-bones` (stub), `rc book` (stub)
- `pypandoc`-based Markdown → HTML rendering with template resolution
- Incremental build support via `render-state.yaml` modification time cache
- SCSS compilation via `sass` CLI
- Nav partial injection via `--include-before-body`
- Per-page sidecar metadata (`.rk.yaml`) with related pages and breadcrumbs
- Auto-generated index pages for tags, authors, dates, and sitemap
- `pyproject.toml` packaging with `rc` entry point
- MIT license

---

## Upcoming

### Planned for 0.1.0
- `rc book` — full implementation of all modes (`contentbook`, `configbook`, `docbook`, `collapse`, etc.)
- `rc reseed` — restore from book archives
- `rc cleanup-bones` — prune stale reports with retention window
- `rc render-sitemap` — standalone sitemap rendering step
- External import support in `rc book` (WordPress XML, Movable Type, RSS/Atom)
- `init.py` fix: update terminal next-steps output from `rotkeeper render` → `rc render`
