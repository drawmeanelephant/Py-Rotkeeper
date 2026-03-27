---
title: "rc collect-assets"
slug: pipeline-collect-assets
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - pipeline
  - assets
  - reference
description: "Copies cataloged assets from source into output/, using SHA-256 hashes to skip unchanged files."
toc: true
rotkeeper_nav:
  - "10_Pipeline"
  - "collect_assets"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "pipeline/collect-assets.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc collect-assets

`rc collect-assets` reads the `assets.yaml` catalog produced by `rc assets` and copies each file into the correct location under `output/`.  
It uses SHA-256 hashes to skip files that are already up-to-date, so repeated runs are safe and fast.

---

## What it does

1. Reads `home/bones/reports/assets.yaml` (exits with error code `1` if missing)
2. For each entry, resolves the source file path based on its `origin` field
3. Checks whether the destination file in `output/` already exists with a matching SHA-256 hash — skips if so
4. Copies the file to `output/`, creating parent directories as needed
5. Verifies the hash of the copied file and logs an error if it doesn't match

Global assets land in `output/assets/`. Page-local assets land next to their corresponding HTML file in `output/`.

---

## Usage

```bash
rc collect-assets
rc collect-assets --dry-run
rc collect-assets --verbose
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--dry-run` | bool | false | Log what would be copied without writing anything |
| `--verbose` | bool | false | Enable detailed per-file logging including hash comparisons |

---

## Destination Logic

Where a file lands in `output/` depends on its `origin` value in `assets.yaml`:

| Origin | Source root | Destination |
|---|---|---|
| `global` | `home/bones/assets/` | `output/assets/<path>` |
| `page-local` | `home/content/<page-dir>/` | `output/<page-dir>/<filename>` |
| *(unknown)* | Falls back to `home/assets/` then `home/content/` | `output/assets/<path>` |

---

## Example

```bash
# Full standard run
rc assets
rc collect-assets

# Preview without writing
rc collect-assets --dry-run

# Verbose copy with hash logging
rc collect-assets --verbose
```

---

## Notes

- `rc collect-assets` **requires** `assets.yaml` to exist. Always run `rc assets` first.
- Hidden files (dotfiles) and `.scss` files present in `assets.yaml` are silently skipped.
- Hash verification runs after every copy. If the copied file's hash doesn't match the catalog, an error is logged but the run continues — no files are deleted.
- If a source file listed in `assets.yaml` cannot be found on disk, a warning is logged and that entry is skipped; other assets are still processed.
- `output/` must exist before running `collect-assets`. It is created by `rc render`. If `output/` is missing, the command exits cleanly with code `0` and logs a notice.
