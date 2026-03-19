---
title: "Sitemap Command"
author: "rotkeeper"
date: "2026-03-16"
lang: "en-US"
toc: true
numbersections: true
geometry: "margin=1in"
fontsize: "12pt"
keywords: [sitemap, rotkeeper, cli]
tags: [commands, sitemap]
rotkeeper_nav: ["01_Docs", "Commands", "Sitemap"]
show_in_nav: true
template: "rot-doc.html"
---

# Sitemap Command


## Concept

The `sitemap` command scans all Markdown content in a Rotkeeper project and collects page metadata from YAML frontmatter. The command produces a canonical `sitemap.yaml` file that describes every document in the project.

This sitemap acts as the central metadata source for other Rotkeeper commands. In particular, the `nav` command consumes the sitemap to build hierarchical navigation, breadcrumbs, and other navigation structures used by templates.

Rather than relying on filesystem layout, Rotkeeper uses frontmatter fields to describe document structure and metadata. This allows pages to move freely in the repository while navigation remains deterministic.

## Usage

```bash
rotkeeper sitemap [--output <file>] [--verbose]
```

- `--output <file>`: Specify the file path for the generated sitemap. Defaults to `sitemap.yaml`.  
- `--verbose`: Display detailed information about which files are included and processed.

## Example

```bash
rotkeeper sitemap --verbose --output ./bones/reports/sitemap.yaml
```

Generates the sitemap with detailed logging and writes it to `./bones/reports/sitemap.yaml`.

## Future Goals

- Support multiple output formats (YAML, JSON, XML).
- Include complete frontmatter metadata such as `title`, `author`, `date`, `keywords`, `tags`, and `rotkeeper_nav`.
- Provide structured metadata for downstream commands like `nav` and `render`.
- Enable generation of derived pages such as tag indexes or author listings based on sitemap metadata.
