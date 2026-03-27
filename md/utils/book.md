---
title: "rc book"
slug: utilities-book
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - utilities
  - book
  - export
  - archive
  - reference
description: "Packages Rotkeeper content, config, and scripts into portable archive files for migration, backup, or import to another installation."
toc: true
rotkeeper_nav:
  - "40_Utilities"
  - "book"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "utilities/book.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc book

`rc book` packages your Rotkeeper project into portable archive files called **books**.  
A book captures a specific slice of your project — content, config, scripts, or all of the above — into a self-contained file that can be moved to a new Rotkeeper installation and restored with `rc reseed`.

> ⚠️ `rc book` is currently a stub. The modes and behavior described here reflect the intended design and are actively being implemented.

---

## What it does (intended)

Each `--mode` produces a different archive:

| Mode | What it captures |
|---|---|
| `contentbook` | All Markdown files from `home/content/` |
| `configbook` | All config files from `home/bones/config/` |
| `docbook` | Templates, SCSS, and asset sources from `home/bones/` |
| `docbook-clean` | Same as `docbook` but strips build artifacts and reports |
| `scriptbook-full` | All Python source files from `src/rotkeeper/` |
| `contentmeta` | Frontmatter metadata only (no body content) — useful for nav/sitemap migration |
| `collapse` | Full project collapse: content + config + scripts in one archive |
| `all` | Runs all applicable modes and writes one archive per mode |

---

## Usage

```bash
rc book
rc book --mode contentbook
rc book --mode collapse
rc book --dry-run
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--mode` | choice | `all` | Which book to generate — see mode table above |
| `--dry-run` | bool | false | Show what would be archived without writing any files |

---

## Portability Workflow

To move a Rotkeeper project to a new installation:

```bash
# On the source machine
rc book --mode collapse

# Copy the resulting archive to the new machine, then:
rc init
rc reseed --input collapse-book.md
rc render
```

For content-only migration (e.g. moving posts from one site to another):

```bash
rc book --mode contentbook
# Transfer contentbook archive
rc reseed --input contentbook.md
```

---

## Future: Importing from External Systems

`rc book` is designed to eventually support import modes that pull content from external publishing platforms into the Rotkeeper content format, including:

- **WordPress** — via XML export → Markdown conversion with frontmatter mapping
- **Movable Type** — via MT export format parsing
- **Generic RSS/Atom** — for pulling posts from any feed-based system

Imported content would land in `home/content/` with a best-effort frontmatter mapping (`title`, `date`, `tags`, `author`) and would be ready to render with `rc render`.

---

## Notes

- Book archives are written to `home/bones/reports/` by default.
- `rc reseed` is the counterpart command that reads book archives and restores files. See [Scaffold → reseed](../scaffold/reseed.md).
- `contentmeta` mode is useful for rebuilding a sitemap or nav on a new installation without transferring full page bodies.
- `docbook-clean` is the recommended mode when sharing a project template with another user — it omits logs, manifests, and render state.
