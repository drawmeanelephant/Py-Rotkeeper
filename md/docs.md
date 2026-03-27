---
title: "Py-Rotkeeper Full Documentation"
slug: docs
template: rot-doc.html
version: "0.0.3-pre"
updated: "2026-03-27"
description: "Complete reference for Rotkeeper: pipeline, scaffold, utilities, concepts, and sitemap."
tags:
  - rotkeeper
  - reference
  - full-docs
rotkeeper_nav:
  - "00_Home"
show_in_nav: true
draft: false
published: true
author: "Filed Systems"
---

# 🐘 Py-Rotkeeper Full Documentation

This page contains all the sections of the Rotkeeper docs in one place. Use the links below to jump to any topic.

---

## Quickstart
Install, initialize, and run your first build.

- [Quickstart Guide](quickstart.html)
- Steps:
  1. Install Python dependencies
  2. Initialize project
  3. Run first render

---

## Pipeline
Core commands and workflow.

- `render` – convert Markdown to HTML  
- `assets` – collect and organize assets  
- `collect-assets` – gather files for deployment

Refer to [Pipeline Docs](pipeline/index.html) for full details.

---

## Scaffold
Project setup and reseed commands.

- [Scaffold Index](scaffold/index.html)
- Commands:
  - `init` – initialize project
  - `reseed` – reset project structure

---

## Utilities
Helper scripts for navigation, cleanup, and book formatting.

- [Utilities Overview](utils/index.html)
- Examples:
  - `nav` – generate nav links
  - `cleanup_bones` – clean intermediate files
  - `book` – assemble chapters

---

## Concepts
Rotkeeper architecture and frontmatter concepts.

- [Frontmatter & Metadata](concepts/pandoc-frontmatter.html)
- How Rotkeeper reads Markdown metadata

---

## Sitemap
Navigation structure and generated sitemaps.

- [Sitemap Overview](sitemap/index.html)
- [Generated Tags](generated/tags/index.html)
- [Authors](generated/authors/index.html)
- [Dates](generated/dates/index.html)

---

> 🔗 Tip: Start at Quickstart if you're new, then explore Pipeline and Utilities for deeper control.