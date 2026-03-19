---
title: "Render Sitemap Command"
author: "rotkeeper"
date: "2026-03-17"
lang: "en-US"
toc: true
numbersections: true
geometry: "margin=1in"
fontsize: "12pt"
keywords: ["sitemap", "render", "rotkeeper", "cli"]
tags: ["commands", "sitemap"]
rotkeeper_nav: ["01_Docs", "Commands", "Render Sitemap"]
show_in_nav: true
template: "rot-doc.html"
---

# Render Sitemap Command

## Concept

The `render-sitemap` command generates a standalone HTML sitemap page from the `sitemap.yaml` produced by Rotkeeper. It converts the hierarchical structure defined in `rotkeeper_nav` into nested `<ul>`/`<li>` HTML, producing a browsable overview of the site's pages. This is useful for debugging, QA, and content auditing.

## Example

```bash
rotkeeper render-sitemap --verbose --output ./output/sitemap.html
```

Generates the HTML sitemap with detailed logging and writes it to `./output/sitemap.html`.

## Future Goals

- Allow template customization for the sitemap layout.
- Enable filtering by tags, authors, or dates for dynamic sitemap views.
- Support incremental updates to speed up generation on large sites.
- Integrate directly with themes or static site previews.

## Purpose

- Reads `sitemap.yaml` created by `rotkeeper sitemap`.
- Uses `rotkeeper_nav` for page hierarchy.
- Generates a clean HTML page reflecting the full site structure.
- Supports operator/minimal, verbose/debug, and dry-run modes for flexible execution.

## Usage

```bash
rotkeeper render-sitemap [OPTIONS]
```

### Options

- `--dry-run` – outputs the HTML to console without writing a file.
- `--output PATH` – optionally specify a different output file location.
- `--verbose` – prints detailed logs during generation.
- `--minimal` – prints only summary information.
- `--yaml PATH` – specify a custom sitemap YAML file (defaults to `sitemap.yaml`).

## Hierarchical Rendering

The sitemap uses `rotkeeper_nav` from page metadata to define the hierarchy.

Example:

```yaml
rotkeeper_nav:
  - "01_Docs"
  - "02_Commands"
  - "Render Sitemap"
```

Behavior:

- Numeric prefixes (e.g., `NN_`) control ordering but are **not displayed**.
- Pages without numeric prefixes are sorted alphabetically.
- Nested `<ul>` structures represent the hierarchy visually in HTML.

Example rendering in HTML:

```html
<ul>
  <li>Docs
    <ul>
      <li>Commands
        <ul>
          <li>Render Sitemap - /docs/commands/render_sitemap.html</li>
        </ul>
      </li>
    </ul>
  </li>
</ul>
```

## Notes

- Assumes `sitemap.yaml` is up-to-date; run `rotkeeper sitemap` first.
- HTML output can be previewed directly in a browser or linked from templates.
- Supports dry-run and verbose/debug modes for testing without writing files.
- Key frontmatter fields used: `title`, `rotkeeper_nav`, `keywords`, `tags`, `author`, `show_in_nav`.
- `rotkeeper_nav` defines the hierarchy; `_page` metadata is used for leaf nodes in HTML.
- Can be integrated into CI/CD pipelines to produce automated sitemap previews.
