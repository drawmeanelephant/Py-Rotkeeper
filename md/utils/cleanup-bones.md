---
title: "rc cleanup-bones"
slug: utilities-cleanup-bones
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - utilities
  - cleanup
  - reference
description: "Backup and prune stale files from bones/ based on a configurable retention window."
toc: true
rotkeeper_nav:
  - "40_Utilities"
  - "cleanup_bones"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "utilities/cleanup-bones.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc cleanup-bones

`rc cleanup-bones` prunes stale files from `home/bones/` — primarily old reports, manifests, and render logs — based on a configurable age threshold.

> ⚠️ `rc cleanup-bones` is currently a stub. The flags and behavior described here reflect the intended design and will be implemented in a future release.

---

## What it does (intended)

1. Scans `home/bones/reports/` for files older than `--days` days
2. Optionally backs up matched files before deletion
3. Removes stale files, leaving current reports and manifests intact
4. Prompts for confirmation unless `--yes` is set

---

## Usage

```bash
rc cleanup-bones
rc cleanup-bones --days 14
rc cleanup-bones --days 7 --yes
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--days` | int | 30 | Retention window in days; files older than this are candidates for removal |
| `--yes` | bool | false | Skip confirmation prompt and delete immediately |

---

## Notes

- `rc cleanup-bones` targets `home/bones/reports/` — it does not touch `home/content/`, `home/bones/templates/`, or `output/`.
- This command is safe to skip entirely on small projects where report accumulation is not a concern.
- For removing orphaned HTML from `output/` (pages deleted from source), the intended tool is a separate `output` pruning mode — `cleanup-bones` focuses on the `bones/` tree only.
