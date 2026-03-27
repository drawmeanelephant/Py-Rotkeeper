---
title: "rc init"
slug: scaffold-init
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - scaffold
  - init
  - reference
description: "Initializes a new Rotkeeper project, creating the full home/ directory structure with starter content, templates, and config."
toc: true
rotkeeper_nav:
  - "30_Scaffold"
  - "init"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "scaffold/init.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc init

`rc init` creates the full directory tree and starter files a Rotkeeper project needs to function.  
Run it once in an empty directory at the start of a new project. It is safe to re-run with `--force` to restore any missing or overwritten files.

---

## What it does

1. Creates the following directories (skips existing ones unless `--force`):

   ```text
   home/content/
   home/bones/templates/
   home/bones/assets/styles/
   home/bones/assets/images/
   home/bones/config/
   home/bones/reports/
   ```

2. Writes `home/bones/config/user-config.yaml` with default path settings
3. Copies starter content from the Rotkeeper package (`src/rotkeeper/sources/`):
   - `home/content/index.md` and `home/content/sample.md`
   - All HTML templates into `home/bones/templates/`
   - All SCSS files into `home/bones/assets/styles/`
   - `mascot.png` into `home/bones/assets/images/`
4. Writes `home/bones/reports/README.md`
5. Writes a `.gitignore` in the project root

---

## Usage

```bash
rc init
rc init --force
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--force` | bool | false | Overwrite existing directories and files; re-copies all sources |

---

## Files Created

| Path | Description |
|---|---|
| `home/content/index.md` | Starter home page |
| `home/content/sample.md` | Example content page |
| `home/bones/templates/` | HTML templates copied from package sources |
| `home/bones/assets/styles/` | SCSS stubs (`main.scss`, `_variables.scss`, etc.) |
| `home/bones/assets/images/mascot.png` | Rotkeeper mascot image |
| `home/bones/config/user-config.yaml` | Default path configuration |
| `home/bones/reports/README.md` | Reports directory readme |
| `.gitignore` | Ignores `output/`, compiled CSS, caches, and OS files |

---

## user-config.yaml defaults

```yaml
HOME: home
CONTENT_DIR: home/content
OUTPUT_DIR: home/output
default_template: default
```

Edit this file to relocate your content, output, or template directories.

---

## .gitignore contents

```
output/
*.html
!bones/templates/*.html
bones/assets/styles/*.css
__pycache__/
*.py[cod]
.venv/
env/
*.swp
.DS_Store
```

---

## Example

```bash
mkdir my-site && cd my-site
rc init
rc render
```

---

## Notes

- `rc init` will **not** overwrite existing files unless `--force` is passed. New users can safely re-run it after making changes.
- With `--force`, all source-copied files (templates, SCSS, starter content) are overwritten. Your own content in `home/content/` is also overwritten if it has the same filename as a starter file (`index.md`, `sample.md`). Rename or back up custom content before using `--force`.
- After init, the next step is `rc render`. See [Pipeline → render](../pipeline/render.md).
- `reseed` is the safer alternative to `rc init --force` when you only need to restore missing scaffold files. See [reseed](reseed.md).
