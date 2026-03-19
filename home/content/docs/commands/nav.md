---
title: "Navigation Command"
author: "rotkeeper"
date: "2026-03-16"
lang: "en-US"
toc: true
numbersections: true
geometry: "margin=1in"
fontsize: "12pt"
keywords: ["nav", "navigation", "rotkeeper", "cli"]
tags: ["commands", "navigation"]
rotkeeper_nav: ["01_Docs", "Commands", "Navigation"]
show_in_nav: true
template: "rot-doc.html"
---

# Navigation Command

## Concept

The `nav` command manages the navigation structure of a Rotkeeper project. It reads the sitemap and generates a hierarchical navigation file that can be used by templates to produce menus, sidebars, and breadcrumbs, ensuring consistent navigation across the site.

## Example

```bash
rotkeeper nav --verbose --output ./build/nav.yaml
```

Generates the navigation file with detailed logging and writes it to `./build/nav.yaml`.

## Future Goals

- Provide interactive editing of navigation structure.
- Support multiple layouts for menus and sidebars.
- Integrate with theme and template customization options.
- Enable incremental updates for large sites to improve efficiency.

## Purpose

- Reads the existing `sitemap.yaml` produced by `rotkeeper sitemap`.
- Filters pages based on `show_in_nav` flags and sections.
- Builds a hierarchical structure suitable for navigation templates.

## Usage

```bash
rotkeeper nav [OPTIONS]
```

### Options

- `--dry-run` – outputs the structure without writing to disk.
- `--output PATH` – optionally specify a different output file for the navigation YAML/JSON.
- `--verbose` – prints detailed logs during generation.

## Navigation Ordering

Navigation paths defined in `rotkeeper_nav` may include a numeric prefix to control ordering.

Example:

```yaml
rotkeeper_nav:
  - "01_Docs"
  - "02_Commands"
  - "Navigation"
```

Behavior:

- A prefix in the form `NN_` (number + underscore) is used only for sorting.
- The numeric prefix is **not displayed** in navigation menus or breadcrumbs.
- Items without a numeric prefix fall back to alphabetical ordering.

Example rendering:

Docs > Commands > Navigation

This allows authors to override default alphabetical sorting while keeping clean display labels in templates.

## Notes

- The command assumes the sitemap is up-to-date; run `rotkeeper sitemap` first.
- Navigation metadata comes from page frontmatter collected by `rotkeeper sitemap`.
- Key fields used for navigation include: `title`, `rotkeeper_nav`, `keywords`, `tags`, `author`, and `show_in_nav`.
- `rotkeeper_nav` defines the hierarchical path used to build menus, sidebars, and breadcrumbs.
- Pages can also be grouped dynamically (for example by `author` or `tags`) depending on how templates consume the generated navigation data.
- The output is typically consumed by templates to build menus or sidebars.