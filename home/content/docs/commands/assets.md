---
title: "Assets Command"
author: "Your Name Here"
date: "2026-03-16"
lang: "en-US"
toc: true
numbersections: true
geometry: "margin=1in"
fontsize: "12pt"
keywords: [assets, rotkeeper, cli]
tags: [commands, assets]
rotkeeper_nav: ["01_Docs", "Commands", "Assets"]
show_in_nav: true
template: "rot-doc.html"
---

# Assets Command

The `assets` command manages and processes asset files used within Rotkeeper projects, ensuring they are correctly handled during rendering.

## Concept

The `assets` command is designed to handle all static asset files such as images, stylesheets, and scripts that are part of a Rotkeeper project. It ensures these assets are properly copied, optimized, and linked during the site generation process. This command helps maintain the integrity and availability of assets across different environments and output formats.

## Usage

```bash
rotkeeper assets [OPTIONS]
```

### Options

- `--dry-run`  
  Simulate the asset processing without making any changes to the output directories. Useful for testing what would happen.

- `--verbose`  
  Output detailed logs of the asset processing steps for debugging and monitoring purposes.

- `--output <dir>`  
  Specify a custom output directory where the processed assets should be placed. Defaults to the standard build directory.

### Example

```bash
rotkeeper assets --verbose --output ./build/assets
```

This command processes all assets with detailed logging and places them into the `./build/assets` directory.

## Future Goals

- Implement automatic optimization for images and other media to reduce file sizes without quality loss.
- Add support for asset versioning and cache busting to improve browser caching behavior.
- Integrate with CDN deployment workflows to streamline asset distribution.
- Provide more granular filtering options to include or exclude specific asset types or directories.
- Enhance error reporting and recovery mechanisms during asset processing.
