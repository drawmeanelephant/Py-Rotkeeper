---
title: "rc reseed"
slug: scaffold-reseed
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - scaffold
  - reseed
  - reference
description: "Restores missing scaffold files from a book archive without overwriting existing content."
toc: true
rotkeeper_nav:
  - "30_Scaffold"
  - "reseed"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "scaffold/reseed.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc reseed

`rc reseed` reconstructs missing scaffold files from a bound book archive.  
It is the complement to `rc book` — where `book` packs a project up, `reseed` unpacks it into a new or partial installation.  
Unlike `rc init --force`, reseed does not overwrite files that already exist unless explicitly told to.

> ⚠️ `rc reseed` is currently a stub. The flags and behavior described here reflect the intended design and will be implemented alongside `rc book`.

---

## What it does (intended)

1. Reads a book archive produced by `rc book` (via `--input`) or scans all known books (`--all`)
2. Extracts content, templates, config, and scaffold files
3. Writes extracted files into the current project tree
4. Skips any file that already exists at the destination unless `--force` is set

---

## Usage

```bash
rc reseed --input path/to/book.md
rc reseed --all
rc reseed --all --force
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--input` | path | none | Path to a specific book file to reseed from |
| `--all` | bool | false | Reseed from all known book archives |
| `--force` | bool | false | Allow overwriting files that already exist at the destination |

---

## Notes

- `rc reseed` is designed to work in tandem with `rc book`. A typical portability workflow is: `rc book --mode contentbook` on the source machine, then `rc reseed --input contentbook.md` on the destination.
- Without `--force`, reseed is safe to run on an active project — only truly missing files are written.
- See [Utilities → book](../utilities/book.md) for the full book mode reference.
