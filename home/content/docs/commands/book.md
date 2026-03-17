---
title: "Book Command"
author: "rotkeeper"
date: "2026-03-16"
lang: "en-US"
toc: true
numbersections: true
geometry: "margin=1in"
fontsize: "12pt"
keywords: [book, rotkeeper, cli]
tags: [commands, book]
rotkeeper_nav: ["01_Docs", "Commands", "Book"]
show_in_nav: true
template: "rot-doc.html"
---

# Book Command


## Concept

The `book` command manages book-style documents in Rotkeeper projects, such as compiling chapters, organizing sections, and preparing structured content for rendering. It helps maintain consistent formatting and ordering of multi-chapter documents.

## Usage

```bash
rotkeeper book [--dry-run] [--verbose] [--output <dir>]
```

- `--dry-run`: Show what would be done without making changes.
- `--verbose`: Display detailed logs during processing.
- `--output <dir>`: Specify the output directory for generated book files.

## Example

```bash
rotkeeper book --verbose --output ./output/book
```

Processes all book-style documents with detailed logging and outputs them to `./output/book`.

## Future Goals

- Support automatic chapter numbering and ordering from frontmatter.
- Enable multi-format outputs (PDF, HTML, ePub).
- Integrate with templates for styling and layout customization.
- Add validation for frontmatter metadata in chapters.