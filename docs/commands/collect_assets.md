---
title: "Collect Assets Command"
author: "rotkeeper"
date: "2026-03-16"
lang: "en-US"
toc: true
numbersections: true
geometry: "margin=1in"
fontsize: "12pt"
keywords: [collect_assets, rotkeeper, cli]
tags: [commands, assets]
rotkeeper_nav: ["01_Docs", "Commands", "Collect Assets"]
show_in_nav: true
template: "rot-doc.html"
---


# Collect Assets Command

## Concept

The `collect_assets` command gathers all static asset files, including images, stylesheets, scripts, and other media, from various sources in a Rotkeeper project into a centralized directory. This ensures consistent handling of assets during builds and simplifies deployment.

## Usage

```bash
rotkeeper collect_assets [--output <dir>] [--dry-run] [--verbose]
```

- `--output <dir>`: Specify a custom directory to collect assets into. Defaults to the standard build output.  
- `--dry-run`: Show what would be collected without making changes.  
- `--verbose`: Display detailed logs during the asset collection process.

## Example

```bash
rotkeeper collect_assets --verbose --output ./build/assets
```

Collects all assets with detailed logging and places them into `./build/assets`.

## Future Goals

- Implement automatic optimization for images, CSS, and JS files.  
- Support asset deduplication and hash-based caching.  
- Enable filtering options to include or exclude specific file types or directories.  
- Integrate with deployment pipelines or CDNs for automated distribution.
