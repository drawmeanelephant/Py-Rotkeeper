---
title: "Getting Started"
description: "How to install and run Rotkeeper."
author: "Filed Systems"
date: "2026-02-10"
tags:
  - docs
  - setup
  - install
keywords:
  - getting started
  - installation
  - quickstart
template: rot-doc.html
show_in_nav: false
---

# Getting Started

## Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/drawmeanelephant/Py-Rotkeeper
cd Py-Rotkeeper
pip install -e .
npm install
```

## Basic Usage

Run the full pipeline from your site directory:

```bash
rotkeeper sitemap-pipeline
rotkeeper render
```

## Directory Structure

| Path | Purpose |
|---|---|
| `bones/` | Config, templates, assets |
| `home/content/` | Source Markdown files |
| `home/output/` | Rendered HTML output |
| `rc/` | Python package and CLI |

## Configuration

Override defaults in `bones/config/user-config.yaml`:

```yaml
CONTENT_DIR: home/content
OUTPUT_DIR: home/output
```

## Run Order

Every time you add or change content, run in this order:

1. `rotkeeper sitemap-pipeline` — rebuilds nav, metadata trees, and sidecars
2. `rotkeeper render` — renders all changed Markdown to HTML

Use `--force` on render to rebuild everything regardless of mtimes:

```bash
rotkeeper render --force
```
