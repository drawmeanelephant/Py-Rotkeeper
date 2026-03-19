---
title: "Cleanup Bones Command"
author: "rotkeeper"
date: "2026-03-16"
lang: "en-US"
toc: true
numbersections: true
geometry: "margin=1in"
fontsize: "12pt"
keywords: [cleanup_bones, rotkeeper, cli]
tags: [commands, cleanup]
rotkeeper_nav: ["01_Docs", "Commands", "Cleanup Bones"]
show_in_nav: true
template: "rot-doc.html"
---

# Cleanup Bones Command

## Concept

The `cleanup_bones` command is designed to maintain a clean Rotkeeper project by removing unnecessary or obsolete files generated during builds. It ensures the project directory remains organized and reduces potential conflicts with leftover artifacts.

## Usage

```bash
rotkeeper cleanup_bones [--dry-run] [--verbose]
```

- `--dry-run`: Show which files would be deleted without actually removing them.
- `--verbose`: Output detailed information during the cleanup process.

## Example

```bash
rotkeeper cleanup_bones --dry-run --verbose
```

Lists all intermediate files that would be removed, providing detailed logging without affecting the project.

## Future Goals

- Add interactive prompts for selective deletion of files.
- Enable custom cleanup rules per project or per directory.
- Integrate with project status reports to show leftover files before deletion.
- Provide more robust error handling and recovery during cleanup.
