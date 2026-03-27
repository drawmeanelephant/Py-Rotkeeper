---
title: 'Tag: reference'
draft: false
generated_by: rotkeeper/sitemap_pipeline
generated_at: '2026-03-26'
show_in_nav: false
---
# reference

- Changelog
  Release history and notable changes for Rotkeeper.
- Pandoc Frontmatter in Rotkeeper
  How Rotkeeper reads and uses YAML frontmatter fields, and how they map to Pandoc metadata.
- Rotkeeper Documentation
  Landing page and navigation guide for Rotkeeper documentation.
- rc assets
  Catalogs static assets from bones/assets/ and page-local files, writing assets.yaml for use by collect_assets.
- rc collect-assets
  Copies cataloged assets from source into output/, using SHA-256 hashes to skip unchanged files.
- Pipeline
  Overview of the Rotkeeper build pipeline: render, assets, and collect_assets.
- rc render
  Compiles Markdown to HTML via Pandoc, applies templates, and compiles SCSS.
- Scaffold
  Overview of Rotkeeper scaffold commands: init and reseed.
- rc init
  Initializes a new Rotkeeper project, creating the full home/ directory structure with starter content, templates, and config.
- rc reseed
  Restores missing scaffold files from a book archive without overwriting existing content.
- Sitemap
  Overview of Rotkeeper sitemap commands: sitemap, sitemap_pipeline, and render_sitemap.
- rc sitemap-pipeline
  Full sitemap pipeline: collects pages, builds metadata trees, writes index pages, nav partial, sidecar metadata, and a unified YAML report.
- rc render-sitemap
  Stub: renders the sitemap data into final HTML nav and XML output.
- rc sitemap
  Scans content frontmatter and writes sitemap.yaml — the page catalog used by nav and sitemap-pipeline.
- rc book
  Packages Rotkeeper content, config, and scripts into portable archive files for migration, backup, or import to another installation.
- rc cleanup-bones
  Backup and prune stale files from bones/ based on a configurable retention window.
- Utilities
  Overview of Rotkeeper utility commands: nav, cleanup_bones, and book.
- rc nav
  Reads sitemap.yaml and writes nav.yaml — a structured navigation tree grouped by rotkeeper_nav, author, date, and tags.