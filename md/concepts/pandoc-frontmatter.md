---
title: "Pandoc Frontmatter in Rotkeeper"
slug: pandoc-frontmatter
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - concepts
  - frontmatter
  - pandoc
  - reference
description: "How Rotkeeper reads and uses YAML frontmatter fields, and how they map to Pandoc metadata."
toc: true
rotkeeper_nav:
  - "50_Concepts"
  - "pandoc-frontmatter"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "pandoc-frontmatter.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Pandoc Frontmatter in Rotkeeper

Every Rotkeeper page is a Markdown file with a YAML frontmatter block at the top.  
Pandoc reads this block as document metadata and makes it available to templates as variables.  
Rotkeeper adds its own fields on top — they control nav, build behavior, and pipeline logic.

---

## How It Works

Pandoc treats any valid YAML block delimited by `---` at the top of a file as a metadata block.  
String scalars are interpreted as Markdown, so you can use inline formatting (bold, links, etc.) in fields like `description`.  
Fields ending in an underscore are **ignored by Pandoc** and are reserved for external processors — Rotkeeper uses this convention for `asset_meta` sub-fields.

```yaml
---
title: "My Page"
description: "A short summary used in `<meta>` tags."
date: 2026-03-20
---
```

Pandoc passes all fields to your HTML template as variables, accessible as `$title$`, `$description$`, `$date$`, etc.

---

## Rotkeeper-Specific Fields

These fields are read by the Rotkeeper pipeline — they are not standard Pandoc variables but are available to templates that reference them.

| Field | Type | Required | Description |
|---|---|---|---|
| `rotkeeper_nav` | list of strings | Yes | Nav section tokens; controls placement and sort order |
| `show_in_nav` | bool | Yes | `true` = appears in rendered nav; `false` = built but hidden |
| `draft` | bool | Yes | `true` = excluded from build entirely |
| `published` | bool | Yes | `false` = treated same as `draft: true` |
| `slug` | string | Recommended | Output filename stem; defaults to source filename if absent |
| `template` | string | Recommended | HTML template to use (e.g. `rot-doc.html`) |

---

## Standard Pandoc Fields

These are native Pandoc metadata variables passed directly to templates.

| Field | Type | Description |
|---|---|---|
| `title` | string | Page title; maps to `$title$` in templates |
| `author` | string or list | Author name(s); maps to `$author$` |
| `date` | string | Publication date; maps to `$date$` |
| `description` | string | Page summary; used in `<meta name="description">` |
| `tags` | list of strings | Keyword tags; available as `$tags$` in templates |
| `toc` | bool | `true` enables Pandoc's auto table of contents |
| `lang` | string | Document language, e.g. `en` |

---

## `rotkeeper_nav` in Detail

The `rotkeeper_nav` field is a list of string tokens with a numeric prefix.  
The first token is always the **section** (`10_Pipeline`, `20_Sitemap`, etc.).  
An optional second token is the **page identifier** within that section.

```yaml
# Section overview page — one token
rotkeeper_nav:
  - "10_Pipeline"

# Command page — two tokens
rotkeeper_nav:
  - "10_Pipeline"
  - "render"
```

Sections sort by numeric prefix. Pages within a section sort by the order they appear in the section overview's nav list, or alphabetically if unspecified.

The full section hierarchy:

| Token | Section |
|---|---|
| `00_Home` | Landing / index |
| `01_Quickstart` | Getting started |
| `02_Changelog` | Release history |
| `10_Pipeline` | Core build pipeline |
| `20_Sitemap` | Sitemap and nav generation |
| `30_Scaffold` | Project init and reseed |
| `40_Utilities` | Nav, cleanup, book |
| `50_Concepts` | Reference concepts |

---

## YAML Gotchas

- **Field names cannot be bare numbers or booleans.** `yes`, `true`, `15` are invalid as field names.
- **Fields ending in `_` are ignored by Pandoc** but passed to external processors. Use this for internal bookkeeping (e.g. `asset_meta`).
- **Multiple metadata blocks are allowed**, but if two blocks set the same field, the second value wins.
- **Close with `---` or `...`** — both are valid YAML block terminators in Pandoc.
- **Do not leave a blank line** between the opening `---` and the first field; Pandoc will not parse it as a metadata block.

---

## Full Reference Block

Copy this into any new page and fill in the values:

```yaml
---
title: ""
slug: ""
template: rot-doc.html
version: "0.0.1-pre"
updated: "YYYY-MM-DD"
author: "Filed Systems"
date: YYYY-MM-DD
tags: []
description: ""
toc: false
rotkeeper_nav:
  - "10_Pipeline"     # replace with correct section token
  - "page-name"       # optional; omit for section overview pages
show_in_nav: true
draft: false
published: true
asset_meta:
  name: ""
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---
```
