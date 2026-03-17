

---
title: "Pandoc YAML Frontmatter Guide"
author: "Mister Toastyboy"
date: "2026-03-16"
lang: "en-US"
toc: true
numbersections: true
geometry: "margin=1in"
fontsize: 12pt
keywords: ["pandoc", "markdown", "yaml", "documentation"]

# Custom metadata
project: "Rotkeeper"
version: "0.1.0"
tags: ["docs", "reference"]
custom_note: "This document illustrates standard and custom YAML frontmatter usage in Pandoc."
---

# Overview

Pandoc YAML frontmatter is metadata at the top of your Markdown file, enclosed between `---` lines. It configures document output, templates, and can hold custom variables.

## Standard Fields

- `title`, `author`, `date` — basic document info.
- `lang` — language for accessibility and template processing.
- `toc` — generate table of contents.
- `numbersections` — number chapters/sections.
- `geometry`, `fontsize` — for PDF formatting.
- `keywords` — HTML or EPUB metadata.

## Custom Fields

You can define any custom variable. Examples:

```yaml
project: "Rotkeeper"
version: "0.1.0"
tags: ["docs", "reference"]
custom_note: "This doc is auto-generated."
```

These variables can be accessed in templates or filters using `{{variable}}`.

## Best Practices

1. Use snake_case or kebab-case for custom variables.
2. Keep standard and custom fields organized.
3. Prefer arrays over comma-separated strings for multi-values.
4. Be consistent with data types (string vs list).
5. Provide defaults in templates for optional custom variables.

## Usage

Pandoc reads this frontmatter into metadata, which can be used by:

- Templates (`{{variable}}`)
- Filters (Python, Lua)
- Output formats (HTML, PDF, EPUB, DOCX)

This allows you to treat frontmatter as a lightweight per-document configuration file.