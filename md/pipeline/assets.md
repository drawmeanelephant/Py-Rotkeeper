---
title: "rc assets"
slug: pipeline-assets
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - pipeline
  - assets
  - reference
description: "Catalogs static assets from bones/assets/ and page-local files, writing assets.yaml for use by collect_assets."
toc: true
rotkeeper_nav:
  - "10_Pipeline"
  - "assets"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "pipeline/assets.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc assets

`rc assets` scans your asset directories, computes a SHA-256 hash for every file it finds, and writes a catalog to `home/bones/reports/assets.yaml`.  
It does **not** copy files — that is `rc collect_assets`'s job.  
Think of `rc assets` as the inventory step and `rc collect_assets` as the fulfillment step.

---

## What it does

1. Scans `home/bones/assets/` recursively for all files (skips dotfiles and `.scss` files)
2. For each file found, computes a SHA-256 hash and records it as a **global** asset
3. Scans `home/content/` for non-Markdown, non-SCSS files sitting alongside `.md` files and records them as **page-local** assets
4. Writes the full catalog to `home/bones/reports/assets.yaml`

Page-local assets are only cataloged if they are not already present in the global asset list.

---

## Usage

```bash
rc assets
rc assets --dry-run
rc assets --verbose
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--dry-run` | bool | false | Log what would be cataloged without writing `assets.yaml` |
| `--verbose` | bool | false | Enable detailed per-file logging |

---

## assets.yaml Format

Each entry in the report has three fields:

```yaml
- path: fonts/inter.woff2
  sha256: a1b2c3d4...
  origin: global

- path: posts/hello/banner.jpg
  sha256: e5f6a7b8...
  origin: page-local
```

| Field | Description |
|---|---|
| `path` | Path relative to the asset's source root (`bones/assets/` for global, `home/content/` for page-local) |
| `sha256` | SHA-256 hex digest of the file contents |
| `origin` | `global` (from `bones/assets/`) or `page-local` (found next to a `.md` file) |

---

## Example

```bash
# Catalog all assets
rc assets

# Preview what would be cataloged
rc assets --dry-run

# Catalog with per-file output
rc assets --verbose
```

---

## Notes

- `.scss` files are always skipped — they are compiled by `rc render`, not copied as assets.
- Dotfiles (names starting with `.`) are skipped in both global and page-local scans.
- `rc assets` must run **before** `rc collect_assets`. `collect_assets` reads `assets.yaml` and will exit with an error if it doesn't exist.
- Running `rc assets` is safe at any time — it only reads files and writes the report; it never modifies `output/`.
- The SHA-256 hash recorded here is used by `rc collect_assets` to skip files that are already up-to-date in `output/`.
