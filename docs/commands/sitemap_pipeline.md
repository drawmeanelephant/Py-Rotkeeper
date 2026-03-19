---
title: "Sitemap and Navigation Pipeline"
author: "rotkeeper"
date: "2026-03-17"
lang: "en-US"
toc: true
numbersections: true
geometry: "margin=1in"
fontsize: "12pt"
keywords:
  - sitemap
  - navigation
  - rotkeeper
  - cli
tags:
  - commands
  - sitemap
  - nav
rotkeeper_nav:
  - "01_Docs"
  - "Commands"
  - "Sitemap & Navigation Pipeline"
show_in_nav: true
template: "rot-doc.html"
---

# sitemap_pipeline.md

# Sitemap and Navigation Pipeline

## Overview

The Sitemap and Navigation Pipeline is a unified system designed to generate website sitemaps and navigation structures efficiently and consistently. This pipeline consolidates the functionality previously handled by separate sitemap, navigation, and rendering scripts into a single, maintainable workflow.

## CLI Flags and Options

| Flag/Operator   | Purpose                          | Effect / Notes                                   | Example Usage          |
|-----------------|---------------------------------|-------------------------------------------------|-----------------------|
| `--index-only`  | Generate only sitemap index      | Skips detailed sitemap and navigation rendering | `sitemap_pipeline.py --index-only`  |
| `--metadata-only` | Process and extract metadata only | Does not render output files                     | `sitemap_pipeline.py --metadata-only` |
| `--write-only`  | Write outputs without processing | Uses cached data to write files                  | `sitemap_pipeline.py --write-only`  |
| `--dry-run`     | Simulate pipeline run            | No files are written; useful for testing         | `sitemap_pipeline.py --dry-run`     |
| `--verbose`     | Enable detailed logging          | Provides debug information during execution      | `sitemap_pipeline.py --verbose`     |

**Note:** Usage of triple-dash flags (e.g., `---flag`) is invalid and will result in errors.

## Purpose

- Generate sitemaps that represent the website's structure.
- Build navigation menus for multi-page websites.
- Render sitemaps and navigation data into various output formats.
- Support incremental rendering to minimize processing time.
- Ensure multi-site safety when handling multiple sites or configurations.
- Provide integration with Pandoc for flexible output options.

## Inputs

- Site content files (Markdown, HTML, etc.)
- Configuration files (`CONFIG`) specifying site parameters and pipeline options.
- Frontmatter metadata embedded in content files.
- Optional command-line flags for dry-run or debug modes.

## Outputs

- Sitemap files (e.g., XML, JSON).
- Navigation structures (e.g., HTML menus, JSON).
- Rendered navigation and sitemap outputs in user-specified formats.
- Logs and reports for debugging and verification.

### Example Metadata Output

```yaml
rotkeeper_nav:
  - label: "Home"
    url: "/"
    order: 1
  - label: "Docs"
    url: "/docs/"
    order: 2
    children:
      - label: "Getting Started"
        url: "/docs/getting-started/"
        order: 1
      - label: "API Reference"
        url: "/docs/api/"
        order: 2
  - label: "About"
    url: "/about/"
    order: 3
```

## Frontmatter Usage

Frontmatter metadata in content files can control pipeline behavior on a per-page basis. Common frontmatter keys include:

- `sitemap_include`: Boolean to include/exclude a page in the sitemap.
- `nav_order`: Integer to specify the order of items in navigation.
- `nav_label`: Custom label for navigation menus.
- `render_format`: Specify output format for the page (HTML, JSON, etc.)

## Incremental Rendering

To optimize build times, the pipeline supports incremental rendering by:

- Detecting changed or updated content files.
- Processing only those files that have changed since the last run.
- Caching intermediate results to avoid redundant computation.

## Multi-site Safety

When managing multiple sites or configurations, the pipeline ensures:

- Isolation of site-specific data and outputs.
- Correct handling of site-specific configuration parameters.
- Prevention of cross-site data contamination.

## Pandoc Output Options

The pipeline integrates with Pandoc to enable flexible output formats, including:

- HTML
- JSON
- LaTeX
- EPUB

Users can specify Pandoc options via configuration or frontmatter to customize rendering.

## Integration with CONFIG

The pipeline reads from the central `CONFIG` file to obtain:

- Site URLs and base paths.
- Output directories.
- Rendering options and flags.
- Dry-run and debug settings.

Ensure `CONFIG` is correctly set up before running the pipeline.

## Testing Instructions

To test the Sitemap and Navigation Pipeline:

1. Prepare a test site with sample content files and frontmatter.
2. Configure `CONFIG` with appropriate parameters.
3. Run the pipeline in dry-run mode to verify processing without writing outputs.
4. Enable debug mode to view detailed logs.
5. Check generated sitemap and navigation outputs for correctness.
6. Validate incremental rendering by modifying content and re-running.

---

# sitemap_pipeline.py

