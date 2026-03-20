---
title: "Quickstart Guide for Rotkeeper"
slug: quickstart
template: rot-doc.html
version: "0.0.2-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - quickstart
  - tutorial
description: "Install Rotkeeper, initialize a project, and run your first build."
toc: true
rotkeeper_nav:
  - "01_Quickstart"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "quickstart.md"
  version: "0.0.2-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Quickstart Guide for Rotkeeper

> **Requirements:** Python 3.10 or higher, and [Pandoc](https://pandoc.org/installing.html) installed on your system.

---

## 1. Set Up Your Environment

Create and activate a virtual environment, then upgrade the base toolchain:

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

pip install --upgrade pip setuptools wheel
```

---

## 2. Install Rotkeeper

To install the latest released version from PyPI:

```bash
pip install rotkeeper
```

For local development, install in editable mode instead:

```bash
pip install -e .
```

---

## 3. Install Pandoc

Rotkeeper requires Pandoc to render Markdown to HTML.

macOS (Homebrew):

```bash
brew install pandoc
```

Ubuntu/Debian:

```bash
sudo apt-get install pandoc
```

All other platforms: download from [pandoc.org/installing.html](https://pandoc.org/installing.html).

---

## 4. Initialize a Project

```bash
rc init
```

This creates the `home/` directory structure with starter content, templates, and config files.  
See [Scaffold → init](scaffold/init.md) for all available flags.

---

## 5. Run Your First Build

```bash
rc render
rc assets
rc sitemap
```

`rc render` compiles Markdown to HTML via Pandoc.  
`rc assets` copies static files into `output/`.  
`rc sitemap` generates the navigation and sitemap files.

---

## 6. Preview Locally

Serve the `output/` directory with Python's built-in HTTP server:

```bash
cd output
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

---

## Next Steps

| I want to… | Go to |
|---|---|
| Understand the full build pipeline | [Pipeline](pipeline/index.md) |
| Customize templates and SCSS | [Assets](pipeline/assets.md) |
| Add pages to the nav | [Concepts → Pandoc Frontmatter](concepts/pandoc-frontmatter.md) |
| Generate a sitemap | [Sitemap](sitemap/index.md) |
