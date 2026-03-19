---
title: "Rotkeeper Documentation Index"
slug: scripts-index
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-14"
description: "Directory index for Rotkeeper. Explains each file's purpose and project structure."
tags:
  - rotkeeper
  - reference
  - file-structure
asset_meta:
  name: "scripts-index.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
status: published
---

# 📖 Rotkeeper Project Reference

Welcome to Rotkeeper, your command-line necropolis for managing static site rituals.  
This document explains the **purpose of each file and folder** in the project, following the "rules" established in the old Rotkeeper.

> 🕯️ Every file has a reason. Understanding it keeps your rituals tidy.

---

## 📁 Project Structure & File Purpose

### 1. **Root**
- `README.md` — high-level project description, getting started guide, and license info.  
- `LICENSE` — MIT license for the project.  
- `pyproject.toml` — Python packaging, dependencies, and entry points.  
- `package.json` / `package-lock.json` — Node dependencies for SCSS compilation.  
- `node_modules/` — local Node modules (ignored in Git).  
- `output/` — rendered HTML/CSS output (ignored in Git).  
- `home/` — main content, templates, and assets for Rotkeeper.  
- `src/rotkeeper/` — Python code for CLI and commands.

---

### 2. **Home Folder**
- `home/content/` — Markdown source files for docs and tutorials.  
- `home/bones/templates/` — HTML templates (e.g., `default.html`) for rendering pages.  
- `home/bones/assets/styles/` — SCSS files (`main.scss`, `_variables.scss`, `_mixins.scss`) for site styling.  
- `home/bones/config/` — configuration files like `render-flags.yaml`.  
- `home/bones/reports/` — logs, manifests, or audit reports.  
- `home/test_assets/` — sample posts or images for testing renders.

---

### 3. **Python Source (`src/rotkeeper`)**
- `__init__.py` — package initializer.  
- `__main__.py` — entry point for `python -m rotkeeper`.  
- `cli.py` — parses command-line arguments.  
- `commands/` — individual CLI commands:
  - `init.py` / `rotkeeper_init.py` — initialize a new project.  
  - `render.py` — compile Markdown to HTML, build SCSS.  
  - `book.py` — scriptbook/book utilities.  
  - `assets.py` / `collect_assets.py` — copy and manage static assets.  
  - `reseed.py` — reseed content or scripts.  
  - `sitemap.py` — generate navigation info.  
  - `cleanup_bones.py` — remove old output or temporary files.  
- `context.py` — runtime context and path management.  
- `paths.py` — filesystem path helpers.  
- `deps.py` — external dependency checks (Pandoc, Sass).  
- `exec.py` — helper to run subprocesses safely.

---

### 4. **Tests**
- `src/tests/` — Python unit tests for command utilities, asset collection, and pipelines.

---

### 5. **Docs / Guides**
- `home/content/docs/index.md` — this file; overview and rules for the project.  
- Other Markdown files in `docs/` explain workflows, CLI usage, templates, configuration, and troubleshooting.

---

### 6. **Rules for File Usage**
1. **Every script should have metadata** (`version`, `author`, `tracked`) in frontmatter.  
2. **Incremental builds only touch modified files**, using manifests in `reports/`.  
3. **Assets (images, CSS, templates) live in `bones/assets/`** — do not mix with content Markdown.  
4. **SCSS modularity**: `_variables.scss` → `_mixins.scss` → `main.scss` → compiled CSS.  
5. **Logs and audit reports** are read-only for reference; never edit them manually.  

---

> With these rules, Rotkeeper keeps your static site rituals orderly and predictable.