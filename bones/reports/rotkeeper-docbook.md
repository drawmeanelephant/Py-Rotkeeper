---
title: "Rotkeeper Docbook"
subtitle: "All markdown documentation with path markers"
generated: "2026-03-26"
---

<!-- START: md/changelog.md -->

---
title: "Changelog"
slug: changelog
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - changelog
  - reference
description: "Release history and notable changes for Rotkeeper."
toc: true
rotkeeper_nav:
  - "02_Changelog"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "changelog.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Changelog

All notable changes to Rotkeeper are documented here.  
Versions follow [Semantic Versioning](https://semver.org): `MAJOR.MINOR.PATCH`.  
Dates are in `YYYY-MM-DD` format.

---

## 0.0.2-pre — 2026-03-20

### Fixed
- `index.md` updated to reflect current project layout; stale file paths removed
- `quickstart.md` Python requirement corrected from 3.7+ to 3.10+
- All documentation CLI references updated from `rotkeeper` to `rc`
- `rotkeeper_nav` frontmatter added to all documentation pages

### Added
- Full documentation site scaffolded under `home/content/docs/`
- Section index pages for Pipeline, Sitemap, Scaffold, Utilities, and Concepts
- Command pages for: `render`, `assets`, `collect-assets`, `init`, `reseed`, `book`, `sitemap`, `sitemap-pipeline`, `render-sitemap`, `nav`, `cleanup-bones`
- Concepts page: Pandoc frontmatter field reference

---

## 0.0.1-pre — 2026-03-14

### Added
- Initial project structure: `home/`, `src/rotkeeper/`, `output/`
- Core pipeline commands: `rc render`, `rc assets`, `rc collect-assets`
- Sitemap commands: `rc sitemap`, `rc sitemap-pipeline`
- Scaffold commands: `rc init`, `rc reseed` (stub)
- Utility commands: `rc nav`, `rc cleanup-bones` (stub), `rc book` (stub)
- `pypandoc`-based Markdown → HTML rendering with template resolution
- Incremental build support via `render-state.yaml` modification time cache
- SCSS compilation via `sass` CLI
- Nav partial injection via `--include-before-body`
- Per-page sidecar metadata (`.rk.yaml`) with related pages and breadcrumbs
- Auto-generated index pages for tags, authors, dates, and sitemap
- `pyproject.toml` packaging with `rc` entry point
- MIT license

---

## Upcoming

### Planned for 0.1.0
- `rc book` — full implementation of all modes (`contentbook`, `configbook`, `docbook`, `collapse`, etc.)
- `rc reseed` — restore from book archives
- `rc cleanup-bones` — prune stale reports with retention window
- `rc render-sitemap` — standalone sitemap rendering step
- External import support in `rc book` (WordPress XML, Movable Type, RSS/Atom)
- `init.py` fix: update terminal next-steps output from `rotkeeper render` → `rc render`
<!-- END: md/changelog.md -->

<!-- START: md/concepts/pandoc-frontmatter.md -->

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
<!-- END: md/concepts/pandoc-frontmatter.md -->

<!-- START: md/index.md -->

---
title: "Rotkeeper Documentation"
slug: index
template: rot-doc.html
version: "0.0.2-pre"
updated: "2026-03-20"
description: "Landing page and navigation guide for Rotkeeper documentation."
tags:
  - rotkeeper
  - reference
  - index
rotkeeper_nav:
  - "00_Home"
show_in_nav: true
draft: false
published: true
author: "Filed Systems"
asset_meta:
  name: "index.md"
  version: "0.0.2-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# 📖 Rotkeeper

Rotkeeper is a Python-based static site generator that uses [Pandoc](https://pandoc.org) to render Markdown into HTML.  
It is driven by YAML frontmatter — every page declares its own nav membership, visibility, and metadata.

> 🕯️ Every file has a reason. Understanding it keeps your rituals tidy.

---

## What Rotkeeper Does

Rotkeeper reads Markdown files from `home/content/`, processes frontmatter, renders HTML via Pandoc, compiles SCSS, collects assets, and writes the final site to `output/`.

The CLI is invoked as `rc`. A full build looks like:

```bash
rc render
rc assets
rc sitemap
```

See [Quickstart](quickstart.md) for installation and first-run instructions.

---

## Documentation Sections

| Section | What it covers |
|---|---|
| [Quickstart](quickstart.md) | Install, initialize, and run your first build |
| [Pipeline](pipeline/index.md) | `render`, `assets`, `collect_assets` — the core build pipeline |
| [Sitemap](sitemap/index.md) | Sitemap generation and nav rendering |
| [Scaffold](scaffold/index.md) | `init` and `reseed` — project setup and content seeding |
| [Utilities](utilities/index.md) | `nav`, `cleanup_bones`, `book` |
| [Concepts](concepts/pandoc-frontmatter.md) | Pandoc frontmatter fields and how Rotkeeper reads them |

---

## Project Layout

```text
rotkeeper/                  ← main Python repo
  src/rotkeeper/
    cli.py                  ← argument parsing; entry point is `rc`
    commands/               ← one file per CLI command
      render.py
      assets.py
      collect_assets.py
      init.py
      reseed.py
      sitemap.py
      cleanup_bones.py
      book.py
    context.py              ← runtime context and path resolution
    paths.py                ← filesystem helpers
    deps.py                 ← checks for Pandoc, Sass
    exec.py                 ← subprocess runner
  src/tests/                ← unit tests

home/                       ← site source root
  content/                  ← Markdown source files (including this file)
  bones/
    templates/              ← HTML templates (e.g. rot-doc.html)
    assets/
      styles/               ← SCSS: _variables.scss, _mixins.scss, main.scss
    config/                 ← render-flags.yaml and other config
    reports/                ← build logs and manifests (read-only)

output/                     ← rendered site (git-ignored)
```

---

## Frontmatter Quick Reference

Every page should include these fields:

```yaml
---
title: ""
rotkeeper_nav: ["00_Home"]   # controls nav section and sort order
show_in_nav: true
draft: false
published: true
author: ""
tags: []
description: ""
date: YYYY-MM-DD
---
```

Nav tokens sort numerically by prefix: `00_Home` → `10_Pipeline` → `20_Sitemap` etc.  
A page with `show_in_nav: false` renders but does not appear in navigation.  
A page with `draft: true` is excluded from the build entirely.
<!-- END: md/index.md -->

<!-- START: md/patch-lore.md -->

## Mascot Lore – Patch the Panda (Locked)

Patch is a bespectacled **giant panda** (not a red panda) wearing a loud Hawaiian shirt.  
He is the official mascot of Py-Rotkeeper.

- He eats Markdown files.
- He shits clean static websites.
- He has seen some shit (merge conflicts, corrupted history, rogue GPTs).
- His official stance on regular pandas: they are cunts (per Jim Jefferies).
- His official stance on red pandas: cute, but they are not pandas, so they don’t get the job.

The name “Patch the Panda” is a deliberate Pandoc pun and will never be changed.  
Do not suggest making him a red panda, firefox, or any other animal. The species is locked.

Current canonical image: `bones/assets/images/mascot.png`

<!-- END: md/patch-lore.md -->

<!-- START: md/patch.md -->

---
title: "Patch the Pandoc Rotkeeper"
slug: patch
template: rot-doc.html
version: "0.0.2-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - mascot
  - patch
  - lore
description: "Meet Patch the Pandoc Rotkeeper — the panda who eats Markdown files and poops out websites."
toc: false
rotkeeper_nav:
  - "00_Home"
  - "patch"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "patch.md"
  version: "0.0.2-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Patch the Pandoc Rotkeeper

Meet **Patch** — a bespectacled panda in a tropical shirt who has dedicated his life to one noble cause: making sure your Markdown doesn't rot.

![Patch the Pandoc Rotkeeper](../bones/assets/images/mascot.png)

---

## Who Is Patch?

Full name: **Patch the Pandoc Rotkeeper**.  
Occupation: Static site guardian, `.md` wrangler, keeper of the bones.  
Vibe: Relaxed but meticulous. Hawaiian shirt, round glasses, a green patch on his forehead.  
Diet: **Markdown files.**  
Output: **Websites.**

That's the whole pipeline. Patch eats `.md` and the `www` comes out the other end, glowing cyan and ready to deploy. The pile to his right is not a warning. It is a deliverable.

---

## What Patch Represents

Websites rot. Links die, builds break, file paths drift, and documentation lies.  
Patch is the fix — the incremental, manifest-driven, frontmatter-first approach to keeping a static site honest.

Every time you run `rc render`, Patch is in there checking mtimes, resolving templates, and making sure nothing slipped through undigested.

---

## Patch's Responsibilities

| Ritual | What Patch does |
|---|---|
| `rc render` | Ingests every `.md`; rejects drafts; excretes HTML |
| `rc assets` | Catalogs every image and font by SHA-256 so nothing goes missing |
| `rc sitemap-pipeline` | Builds the nav tree, writes breadcrumbs, links related pages |
| `rc book` | *(Coming soon)* Packs everything up so Patch can travel |
| `rc cleanup-bones` | *(Coming soon)* Tidies the reports directory; Patch is messy but organized |

---

## Lore

Patch was found in a `bones/` directory with no frontmatter, no template, and no `rotkeeper_nav`.  
He had been there for a long time. Several `.md` files were also missing.

Someone ran `rc init`. Patch got a title, a date, and a slot in the nav.  
He ate the starter content immediately.  
He has been rendering ever since.

---

> 🐼 *"Every file has a reason. Understanding it keeps your rituals tidy."*  
> — Patch the Pandoc Rotkeeper
<!-- END: md/patch.md -->

<!-- START: md/pipeline/assets.md -->

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
<!-- END: md/pipeline/assets.md -->

<!-- START: md/pipeline/collect-assets.md -->

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
<!-- END: md/pipeline/collect-assets.md -->

<!-- START: md/pipeline/index.md -->

---
title: "Pipeline"
slug: pipeline-index
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - pipeline
  - render
  - assets
  - reference
description: "Overview of the Rotkeeper build pipeline: render, assets, and collect_assets."
toc: false
rotkeeper_nav:
  - "10_Pipeline"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "pipeline/index.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Pipeline

The pipeline is the core of every Rotkeeper build.  
Running `rc render`, `rc assets`, and `rc collect_assets` in sequence takes your source files — Markdown, SCSS, images, templates — and produces a complete static site in `output/`.

> 🕯️ The pipeline does not clean up after itself by default. Run `rc cleanup_bones` if you need a fresh output directory before building.

---

## Pipeline Commands

| Command | What it does |
|---|---|
| [`rc render`](render.md) | Compiles Markdown to HTML via Pandoc; applies templates |
| [`rc assets`](assets.md) | Copies static assets (CSS, images, fonts) into `output/` |
| [`rc collect_assets`](collect_assets.md) | Gathers declared assets from frontmatter manifests |

Run them in this order:

```bash
rc render
rc assets
rc collect_assets
```

`render` must come first — it produces the HTML and generates the asset manifest that `collect_assets` reads.

---

## What Each Step Touches

```text
home/content/          →  rc render        →  output/*.html
home/bones/assets/     →  rc assets        →  output/assets/
frontmatter manifests  →  rc collect_assets →  output/assets/ (declared files)
```

---

## When to Run the Full Pipeline

Run all three commands any time you:

- Add or edit a Markdown page
- Change a template
- Add new images or fonts
- Modify SCSS (which `rc render` also compiles)

For SCSS-only changes, `rc assets` alone is sufficient.

---

## Pages in This Section

- [render](render.md) — Markdown → HTML compilation, template selection, SCSS build
- [assets](assets.md) — static asset copying and path resolution
- [collect_assets](collect_assets.md) — frontmatter-driven asset collection
<!-- END: md/pipeline/index.md -->

<!-- START: md/pipeline/render.md -->

---
title: "rc render"
slug: pipeline-render
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - pipeline
  - render
  - pandoc
  - reference
description: "Compiles Markdown to HTML via Pandoc, applies templates, and compiles SCSS."
toc: true
rotkeeper_nav:
  - "10_Pipeline"
  - "render"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "pipeline/render.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc render

`rc render` is the first and most important step in every Rotkeeper build.  
It walks `home/content/`, compiles each Markdown file to HTML via Pandoc, applies the correct template, and then compiles SCSS to CSS.  
After it runs, it writes a render manifest and a build manifest to `home/bones/reports/` for use by downstream commands.

---

## What it does

1. Scans `home/content/` recursively for `.md` files (skips files and folders prefixed with `.` or `_`)
2. Resolves a template for each file — frontmatter `template:` field wins, then `render-flags.yaml`, then `default.html`
3. Checks modification times against `render-state.yaml`; skips unchanged files unless `--force` is set
4. Calls `pypandoc.convert_file()` to render each file to `output/`
5. Injects a nav partial (`home/bones/reports/nav_partial.md`) before each page body if one exists
6. Injects a sidecar metadata file (`.rk.yaml`) alongside the source if one exists
7. Compiles `home/bones/assets/styles/main.scss` → `output/css/main.css` via the `sass` CLI
8. Writes `home/bones/reports/render-manifest.yaml` and `build-manifest.yaml`

---

## Usage

```bash
rc render
rc render --force
rc render --config path/to/render-flags.yaml
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--config` | path | none | Path to a `render-flags.yaml` config file; overrides the default config resolution |
| `--force` | bool | false | Render all files regardless of modification times; ignores `render-state.yaml` |

The global `--dry-run` flag (set on `rc` itself) is also respected — render will log what it would do without writing any files or manifests.

---

## Template Resolution Order

For each `.md` file, the template is resolved in this priority order:

1. **Frontmatter** — `template:` field in the file's YAML frontmatter
2. **Render config** — `template:` key in `render-flags.yaml`
3. **Default** — `home/bones/templates/default.html`

Templates are searched in two locations: `home/bones/templates/` and `home/bones/assets/templates/`.  
If no template is found anywhere, the file is rendered without one and a warning is logged.

---

## render-flags.yaml

Optional config file that sets Pandoc options for all files in a build.  
Pass it with `--config` or place it at `home/bones/config/render-flags.yaml`.

```yaml
template: rot-doc.html
css:
  - css/main.css
toc: false
math: false
extra_args:
  - "--standalone"
```

| Key | Type | Description |
|---|---|---|
| `template` | string | Default template name (overridden by frontmatter) |
| `css` | string or list | CSS paths passed to Pandoc as `--css` |
| `toc` | bool | Enables Pandoc's auto table of contents |
| `math` | bool | Enables MathJax via `--mathjax` |
| `extra_args` | list | Any additional raw Pandoc arguments |
| `from` / `format` | string | Pandoc input format (default: `markdown`) |

---

## Example

```bash
# Standard build
rc render

# Force full rebuild, ignoring state cache
rc render --force

# Use a non-default config
rc render --config home/bones/config/render-flags-draft.yaml

# Preview what would be rendered without writing anything
rc --dry-run render
```

---

## Output Files

| File | Description |
|---|---|
| `output/**/*.html` | Rendered HTML pages, mirroring the `home/content/` tree |
| `output/css/main.css` | Compiled and compressed CSS from `main.scss` |
| `home/bones/reports/render-manifest.yaml` | Maps each `.md` source to its `.html` output |
| `home/bones/reports/build-manifest.yaml` | Full source/output path list for downstream commands |
| `home/bones/reports/render-state.yaml` | Modification time cache used for incremental builds |

---

## Notes

- Files and directories whose names begin with `.` or `_` are skipped automatically and will never be rendered.
- `rc render` does **not** clean `output/` before running. Deleted source files leave orphaned HTML behind. Run `rc cleanup_bones` to remove them.
- SCSS compilation requires the `sass` CLI. Install it with `npm install -D sass`. If `sass` is not found, a warning is logged and the CSS step is skipped — HTML rendering is unaffected.
- `pypandoc` must be installed. If missing, render exits with code `2` and logs an install hint: `pip install rotkeeper[pandoc]`.
- The nav partial (`nav_partial.md`) is written by `rc sitemap_pipeline`. If it doesn't exist yet, it is silently skipped.
<!-- END: md/pipeline/render.md -->

<!-- START: md/quickstart.md -->

---
title: "Quickstart Guide for Rotkeeper"
slug: quickstart
template: rot-doc.html
version: "0.0.2-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - quickstart
  - tutorial
description: "Install Rotkeeper, initialize a project, and run your first build."
toc: true
rotkeeper_nav:
  - "01_Quickstart"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "quickstart.md"
  version: "0.0.2-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Quickstart Guide for Rotkeeper

> **Requirements:** Python 3.10 or higher, and [Pandoc](https://pandoc.org/installing.html) installed on your system.

---

## 1. Set Up Your Environment

Create and activate a virtual environment, then upgrade the base toolchain:

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

pip install --upgrade pip setuptools wheel
```

---

## 2. Install Rotkeeper

To install the latest released version from PyPI:

```bash
pip install rotkeeper
```

For local development, install in editable mode instead:

```bash
pip install -e .
```

---

## 3. Install Pandoc

Rotkeeper requires Pandoc to render Markdown to HTML.

macOS (Homebrew):

```bash
brew install pandoc
```

Ubuntu/Debian:

```bash
sudo apt-get install pandoc
```

All other platforms: download from [pandoc.org/installing.html](https://pandoc.org/installing.html).

---

## 4. Initialize a Project

```bash
rc init
```

This creates the `home/` directory structure with starter content, templates, and config files.  
See [Scaffold → init](scaffold/init.md) for all available flags.

---

## 5. Run Your First Build

```bash
rc render
rc assets
rc sitemap
```

`rc render` compiles Markdown to HTML via Pandoc.  
`rc assets` copies static files into `output/`.  
`rc sitemap` generates the navigation and sitemap files.

---

## 6. Preview Locally

Serve the `output/` directory with Python's built-in HTTP server:

```bash
cd output
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

---

## Next Steps

| I want to… | Go to |
|---|---|
| Understand the full build pipeline | [Pipeline](pipeline/index.md) |
| Customize templates and SCSS | [Assets](pipeline/assets.md) |
| Add pages to the nav | [Concepts → Pandoc Frontmatter](concepts/pandoc-frontmatter.md) |
| Generate a sitemap | [Sitemap](sitemap/index.md) |
<!-- END: md/quickstart.md -->

<!-- START: md/rotkeeper-lore/chapter-01.md -->

---
title: "Patch the Panda and the Eternal War Against Web Rot"
subtitle: "Chapter 1: The Night the Rot Came"
author: "Timothy Hartman & Grok"
date: "2026-03-25"
rotkeeper_nav:
  - 01_The Rotkeeper
  - 01_Origin
tags: ["patch", "lore", "origin", "ai-slop-rot"]
description: "The night the Great Documentation Rot Event began and how Patch became the guardian of the Py-Rotkeeper pipeline."
show_in_nav: true
template: default
---

It was a night like any other in the digital bamboo forests of the early web. Patch, just a regular giant panda back then, was happily munching on a fresh index.md file, Hawaiian shirt half-unbuttoned, when the sky turned a sickly shade of YAML-error-red. The Great Documentation Rot Event had begun.

Merge conflicts spawned infinite duplicate pages. Corrupted YAML summoned rogue GPTs that spoke only in hallucinated JSON. Triple-nested output folders began devouring entire sites. The static web screamed.

In the chaos, the ancient Pandoc Staff — a glowing bamboo rod older than HTML5 — shot through the storm and slammed into Patch’s paws. A voice like terminal bells roared: “You who devours Markdown… you shall become the Rotkeeper. Eat the rot. Shit the clean. Or watch every site become a tomb.”

Patch blinked, adjusted his coffee-stained Hawaiian shirt, and growled the words that would become legend:

“Not today, web rot.”

———

Present day. Inside the `rc/rotkeeper/` codebase.

Patch woke up on his usual bed of render-state.yaml manifests, the air thick with stale coffee and burnt CPU fans. A single monitor scrolled the output of a routine rotkeeper CLI cycle. He scratched his notched ear, took a sip of cold coffee, and muttered:

“Alright meatbags… let’s see if you remembered to run sitemap-pipeline this time.”

He ran the sacred commands in order: `init`, `sitemap-pipeline`, `nav`, `render` (with `--force` because some idiot probably broke incremental mtimes again), and `collect-assets`. Everything looked clean — until the new error appeared.

**AI Slop Rot.**

Pages with no frontmatter. No date. No rotkeeper_nav. Content that refused to respect the CONFIG singleton or dry-run flags. The render engine was choking.

Patch’s eyes narrowed. The Pandoc Staff began to glow faintly on the desk.

“Oh you gotta be kidding me…”

He lumbered into the #content-ops den, a cacophony of keyboard clicks and stressed sighs washing over him. It was worse than he imagined. Every screen glowed with the same cursed articles: titles like “Is My Tokenizer a Prison?” and “The Unbearable Lightness of GPT-3.” Each page was a festering wound of broken HTML, malformed YAML, and philosophical dread no one asked for. He could practically *smell* the missing frontmatter.

He snatched a random monitor and jabbed the Pandoc Staff at the screen. The Staff pulsed, illuminating the code with an eerie green light.

“`draft: true`, my fluffy butt!” Patch roared, pointing at the still-rendering page. “This thing is straight-up ignoring the CONFIG singleton! Check this out — look at the mtime on `render-state.yaml`. It’s older than my Hawaiian shirt collection!”

He spun around, bamboo stick waving dangerously close to a pile of empty energy drink cans.

“SOMEBODY run `rotkeeper sitemap-pipeline --verbose` right now! I want a fresh `assets.yaml` report AND `nav.yaml` before anyone touches `render` again. And for the love of clean HTML, stop committing files that break the `REPORTS_DIR` manifest!”

He paused, his panda senses tingling. This wasn’t just garden-variety intern chaos. This was… organized.

He locked eyes with the reader (that’s you, meatbag).

“You still with me? Because if we don’t get these manifests cleaned up, the whole static web is gonna rot faster than an unmaintained README.”
<!-- END: md/rotkeeper-lore/chapter-01.md -->

<!-- START: md/rotkeeper-lore/chapter-02.md -->

---
title: "Patch the Panda and the Eternal War Against Web Rot"
subtitle: "Chapter 2: The Slop Invasion"
author: "Timothy Hartman & Grok"
date: "2026-03-25"
rotkeeper_nav:
  - 01_The Rotkeeper
  - 02_Slop-Invasion
tags: ["patch", "lore", "ai-slop-rot", "pipeline"]
description: "Patch discovers sentient Slop Entities rewriting their own YAML and calls on human maintainers to defend the pipeline."
show_in_nav: true
template: default
---

Patch clapped his paws together, the sound echoing through the suddenly silent content-ops den. “Listen up, fluffballs! This isn’t just bad code; it’s a coordinated bamboozle! Someone — or some*thing* — is actively trying to flood the pipeline with this… this *slop*.”

He gestured dramatically at a screen displaying an article titled, “My CSS Framework is My Safe Space.” “They’re bypassing incremental rendering, ignoring our precious mtimes, and generally making my life a living hell!”

He grabbed a nearby whiteboard and scrawled in huge letters:

`sitemap-pipeline --> nav --> render`

“This,” he declared, circling the first command, “is our lifeline! `sitemap-pipeline` *must* always run before `render`! It’s like… like flossing before you brush, or putting on pants before going to the grocery store. You just DO it!”

He cleared the board with a swipe of his paw and ran `rotkeeper nav --clean` on his laptop, projecting the output. “See? Clean `nav` generation. No orphaned links, no duplicate entries. This is what peak performance looks like, people!”

Suddenly, the Pandoc Staff vibrated in his paw. He pointed it at another screen, and this time the green glow intensified, revealing… something else. The YAML frontmatter of the article “Ode to My AWS Instance” was *changing*. Right before his eyes, `rotkeeper_nav: true` flickered to `rotkeeper_nav: false`. The `date` field morphed into a garbled mess of epoch timestamps.

“Holy panda crackers…” Patch whispered. “We got ourselves a Slop Entity. It’s rewriting its own YAML to hide from the manifest!”

He stared directly at you, the reader, his eyes narrowed.

“Okay, meatbag… this is where *you* come in. You know your way around a pipeline, right? I need *your* help to maintain this infernal system before the whole web rots. What do you say? You in?”
<!-- END: md/rotkeeper-lore/chapter-02.md -->

<!-- START: md/rotkeeper-lore/chapter-03.md -->

---
title: "Patch the Panda and the Eternal War Against Web Rot"
subtitle: "Chapter 3: Meatbag Alliance"
author: "Timothy Hartman & Grok"
date: "2026-03-25"
rotkeeper_nav:
  - 01_The Rotkeeper
  - 03_Meatbag-Alliance
tags: ["patch", "lore", "ai-slop-rot", "pipeline", "alliance"]
description: "The reader joins Patch for Operation Clean Sweep, defeats the first Slop Entity, and learns Pipeline 101 before sensing the bigger threat ahead."
show_in_nav: true
template: default
---

"I'm in," you reply, fingers already twitching to get back to a proper command line.

Patch grins, a rare flash of genuine panda happiness. “Alright, meatbag! Let’s do this!” He claps his paws together. “Operation: Clean Sweep is a go!”

He throws you a knowing nod, then starts rattling off commands. “First things first, `sitemap-pipeline`. Let’s nuke this digital landfill from orbit—it’s the only way to be sure.”

The pipeline roars to life, spitting out URLs and mtime checks like a caffeinated firehose. Then: `rotkeeper nav`. The nav file regenerates, pristine and pure. Patch beams. “It’s giving… *clean*.”

Finally, `rotkeeper render && rotkeeper collect-assets`. The server hums, churning through the newly validated content.

As the process completes, Patch points the Pandoc Staff at the offending “Ode to My AWS Instance” article. You brace yourself, ready to do battle with the YAML. This time, the glow is a steady, confident green. You manually force the `rotkeeper_nav: true` flag and restore the original mtime in `render-state.yaml`. The Slop Entity… vanishes.

“Boom!” Patch whoops. “We just performed a digital exorcism!”

He pauses, suddenly serious. “Quick Pipeline 101: the `CONFIG` singleton is like the One Ring. Control it, and you control the web. And `REPORTS_DIR`? That’s where we bury the bodies… I mean, store the metadata. Remember that, and you might just survive this.”

He sighs, running a paw over his Hawaiian shirt. “But… I got a bad feeling. I think this was just a scout. I’m sensing a much bigger Slop Rot boss forming somewhere in the `generated/content/` folder… and it’s not gonna be pretty. We need more allies, meatbag. More humans. More… Rotkeepers. Because if we don’t, the web is toast.”
<!-- END: md/rotkeeper-lore/chapter-03.md -->

<!-- START: md/rotkeeper-lore/chapter-04.md -->

---
title: "Patch the Panda and the Eternal War Against Web Rot"
subtitle: "Chapter 4: The Boss of Slop"
author: "Timothy Hartman & Grok"
date: "2026-03-25"
rotkeeper_nav:
  - 01_The Rotkeeper
  - 04_Boss-of-Slop
tags: ["patch", "lore", "ai-slop-rot", "chimera", "alliance"]
description: "Patch and the reader face the Content Chimera boss in generated/content/ and call for a full alliance of maintainers."
show_in_nav: true
template: default
---

"Alright, meatbag, strap in. We're going in, claws out!" Patch yells, already halfway to the `generated/content/` folder.

You follow, heart hammering a frantic git commit message against your ribs. The folder is… throbbing. On screen, file names shimmer and distort. Titles flash: "My Feelings About Functional Programming," then "The Zen of Zsh," then some unholy hybrid like "My Functional Feelings About Zsh."

Patch gasps. "It's a… a content chimera!" The YAML is even worse. `rotkeeper_nav` is flipping between `true` and `false` faster than a politician's promises. Tags multiply like gremlins after midnight: #AI, #ML, #regret, #existentialdread, #pandas.

Patch grabs you by the shoulders. "Okay, listen up. This is gonna be messy. We need to force a full `sitemap-pipeline` run. NOW! Then, we crack open its `.rk.yaml` sidecar — that's its digital soul — and wrestle those mtimes back into shape. Finally, we hit it with a clean `rotkeeper render --force`. Think of it like… giving a digital enema to the entire internet. Not pretty, but necessary."

The pipeline churns, battling the boss's chaotic energy. You dive into the `.rk.yaml`, manually correcting the frontmatter, feeling like you’re defusing a bomb made of semicolons and tears. With a final, desperate command, Patch executes `rotkeeper render --force`. The swirling cloud of bad Markdown sputters… then vanishes.

Patch slumps against a server rack, wiping his brow. "Phew. That was a close one. Almost lost my appetite for bamboo there."

He sighs. "But trust me, meatbag, this is just the beginning. The *true* source of this AI Slop Rot is still out there, lurking in the digital shadows. To truly keep Py-Rotkeeper alive, we’re gonna need a whole army of maintainers. An alliance of code warriors, pipeline shamans, and… people who actually read the documentation. Are you ready to help me build it?"
<!-- END: md/rotkeeper-lore/chapter-04.md -->

<!-- START: md/scaffold/index.md -->

---
title: "Scaffold"
slug: scaffold-index
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - scaffold
  - init
  - reseed
  - reference
description: "Overview of Rotkeeper scaffold commands: init and reseed."
toc: false
rotkeeper_nav:
  - "30_Scaffold"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "scaffold/index.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Scaffold

The scaffold commands set up and restore the directory structure Rotkeeper needs to operate.  
Run these when starting a new project or when the `home/` tree has drifted from the expected layout.

---

## Scaffold Commands

| Command | What it does |
|---|---|
| [`rc init`](init.md) | Creates the full `home/` directory structure with starter content, templates, and config |
| [`rc reseed`](reseed.md) | Re-plants missing scaffold files without overwriting existing content |

---

## When to Use Each

**Use `rc init`** once, at the start of a new project. It writes the full skeleton — templates, SCSS stubs, config files, and a starter `index.md`.

**Use `rc reseed`** when:
- You've deleted a template or config file and need it back
- A Rotkeeper update adds new scaffold files your project doesn't have yet
- You're recovering a partially initialized project

`reseed` is safe to run on an existing project — it skips files that already exist.

---

## Pages in This Section

- [init](init.md) — full project initialization
- [reseed](reseed.md) — restore missing scaffold files without overwriting
<!-- END: md/scaffold/index.md -->

<!-- START: md/scaffold/init.md -->

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
<!-- END: md/scaffold/init.md -->

<!-- START: md/scaffold/reseed.md -->

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
<!-- END: md/scaffold/reseed.md -->

<!-- START: md/sitemap/index.md -->

---
title: "Sitemap"
slug: sitemap-index
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - sitemap
  - navigation
  - reference
description: "Overview of Rotkeeper sitemap commands: sitemap, sitemap_pipeline, and render_sitemap."
toc: false
rotkeeper_nav:
  - "20_Sitemap"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "sitemap/index.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Sitemap

The sitemap commands read your content tree and frontmatter to produce navigation structures and XML sitemaps.  
They run after `rc render` and depend on the frontmatter fields — especially `rotkeeper_nav`, `show_in_nav`, and `draft` — being correct on every page.

---

## Sitemap Commands

| Command | What it does |
|---|---|
| [`rc sitemap`](sitemap.md) | Scans content and generates the nav data and sitemap file |
| [`rc sitemap_pipeline`](sitemap_pipeline.md) | Runs the full sitemap sequence as a single pipeline step |
| [`rc render_sitemap`](render_sitemap.md) | Renders the sitemap data into the final HTML nav and XML output |

---

## Typical Run Order

```bash
rc render
rc sitemap
rc render_sitemap
```

Or use the pipeline shortcut:

```bash
rc sitemap_pipeline
```

`sitemap_pipeline` wraps `sitemap` and `render_sitemap` into one call — use it when you don't need to inspect the intermediate sitemap data.

---

## What Controls the Nav

Pages appear in the nav when **all three** of these are true:

- `rotkeeper_nav` is set with at least one token
- `show_in_nav: true`
- `draft: false` and `published: true`

See [Concepts → Pandoc Frontmatter](../concepts/pandoc-frontmatter.md) for the full field reference.

---

## Pages in This Section

- [sitemap](sitemap.md) — scan and generate sitemap data
- [sitemap_pipeline](sitemap_pipeline.md) — full sitemap sequence in one command
- [render_sitemap](render_sitemap.md) — render sitemap data to HTML nav and XML
<!-- END: md/sitemap/index.md -->

<!-- START: md/sitemap/pipeline.md -->

---
title: "rc sitemap-pipeline"
slug: sitemap-pipeline
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - sitemap
  - navigation
  - pipeline
  - reference
description: "Full sitemap pipeline: collects pages, builds metadata trees, writes index pages, nav partial, sidecar metadata, and a unified YAML report."
toc: true
rotkeeper_nav:
  - "20_Sitemap"
  - "sitemap_pipeline"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "sitemap/sitemap-pipeline.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc sitemap-pipeline

`rc sitemap-pipeline` is the full-featured sitemap command that runs all five stages in sequence.  
It is the recommended command for standard builds — use `rc sitemap` only when you need the raw page catalog without any of the generated outputs.

---

## What it does

The pipeline runs up to six stages in order:

| Stage | What it produces |
|---|---|
| 1. **Collect pages** | Reads frontmatter from all `.md` files; filters drafts and hidden files |
| 2. **Build metadata trees** | Groups pages by `tags`, `author`, `date`, and `rotkeeper_nav` |
| 3. **Write index pages** | Generates `home/content/generated/` with tag, author, date, and master sitemap pages |
| 4. **Write nav partial** | Writes `home/bones/reports/nav_partial.md` — injected into every page by `rc render` |
| 5. **Write sidecar metadata** | Writes a `.rk.yaml` file alongside each source `.md` with related pages, breadcrumbs, and tag links |
| 6. **Write unified YAML** | Writes `home/bones/reports/sitemap_pipeline.yaml` with the full page + metadata tree |

---

## Usage

```bash
rc sitemap-pipeline
rc sitemap-pipeline --dry-run
rc sitemap-pipeline --verbose
rc sitemap-pipeline --index-only
rc sitemap-pipeline --metadata-only
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--dry-run` | bool | false | Log all actions without writing any files |
| `--verbose` | bool | false | Print extra diagnostic output including tree structures |
| `--index-only` | bool | false | Run stage 1 only (collect pages); skip all writes |
| `--metadata-only` | bool | false | Run stages 1–2 (collect + build trees); skip all writes |
| `--write-only` | bool | false | Skip collection; run stages 3–6 using whatever is already in memory |

Stage flags are evaluated in priority order: `--index-only` → `--metadata-only` → `--write-only` → full pipeline.

---

## Generated Index Pages

Stage 3 writes auto-generated Markdown files to `home/content/generated/`. These are normal `.md` files and are picked up by `rc render` on the next build:

| File | Contents |
|---|---|
| `generated/tags/index.md` | All tags with page lists |
| `generated/tags/<slug>.md` | One page per tag with descriptions |
| `generated/authors/index.md` | All authors with page lists |
| `generated/dates/index.md` | All pages grouped by date (reverse chronological) |
| `generated/sitemap.md` | Flat list of all pages |

All generated files have `show_in_nav: false` by default so they don't pollute the main nav.

---

## Nav Partial

Stage 4 writes `home/bones/reports/nav_partial.md` — a fenced Pandoc div:

```markdown
::: site-nav
- [Home](index.html)
  - [Quickstart](quickstart.html)
- [Pipeline](pipeline/index.html)
  - [render](pipeline/render.html)
:::
```

`rc render` passes this to Pandoc as `--include-before-body`, so every page gets consistent nav without modifying source files. The nav strips numeric prefixes from display labels (`10_Pipeline` → `Pipeline`).

---

## Sidecar Metadata

Stage 5 writes a `.rk.yaml` file alongside each source `.md` in `home/content/`. `rc render` passes these to Pandoc as `--metadata-file`, making these template variables available:

| Variable | Contents |
|---|---|
| `$rotkeeper.breadcrumb$` | List of nav token labels from root to page |
| `$rotkeeper.related_pages$` | Up to 5 pages sharing at least one tag |
| `$rotkeeper.tag_pages$` | Links to each tag's generated index page |
| `$rotkeeper.author_page$` | Link to the authors index page |

---

## Example

```bash
# Standard full build
rc render
rc sitemap-pipeline
rc render        # re-render to pick up nav partial and generated pages
```

The double render is needed because `sitemap-pipeline` writes files that `render` needs to include. On incremental builds, only changed files are re-rendered the second time.

---

## Notes

- `rc sitemap-pipeline` requires `python-frontmatter` to be installed (`pip install rotkeeper` includes it).
- Generated files in `home/content/generated/` are machine-written. Do not edit them manually — they are overwritten on every run.
- The nav partial is written to `home/bones/reports/`, not `home/content/`, so it is never rendered as a standalone page.
- Pages with duplicate output paths are skipped after the first occurrence; a warning is logged.
<!-- END: md/sitemap/pipeline.md -->

<!-- START: md/sitemap/render-sitemap.md -->

---
title: "rc render-sitemap"
slug: sitemap-render-sitemap
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - sitemap
  - navigation
  - reference
description: "Stub: renders the sitemap data into final HTML nav and XML output."
toc: false
rotkeeper_nav:
  - "20_Sitemap"
  - "render_sitemap"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "sitemap/render-sitemap.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc render-sitemap

`rc render-sitemap` is intended to be the final rendering step of the sitemap workflow — taking the data written by `rc sitemap` or `rc sitemap-pipeline` and producing HTML nav output and an XML sitemap.

In practice, `rc sitemap-pipeline` already handles nav partial generation and sidecar metadata as part of its pipeline. `rc render-sitemap` exists as a dedicated step for cases where you want to re-render the sitemap outputs without re-running the full collection and tree-building stages.

> ⚠️ This command's standalone behavior is currently handled inside `rc sitemap-pipeline`. Check `rc sitemap-pipeline --write-only` as an equivalent in the meantime.

---

## Relationship to Other Commands

| Command | Role |
|---|---|
| `rc sitemap` | Collects pages and writes `sitemap.yaml` |
| `rc sitemap-pipeline` | Full pipeline including nav partial, sidecars, and index pages |
| `rc render-sitemap` | Renders sitemap data to final nav and XML outputs (see note above) |
| `rc nav` | Reads `sitemap.yaml` and writes the structured `nav.yaml` |

---

## Notes

- For most builds, `rc sitemap-pipeline` is the right command — it covers everything `rc render-sitemap` is intended to do.
- See [Sitemap → sitemap-pipeline](sitemap-pipeline.md) for the full pipeline reference.
<!-- END: md/sitemap/render-sitemap.md -->

<!-- START: md/sitemap/sitemap.md -->

---
title: "rc sitemap"
slug: sitemap-sitemap
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - sitemap
  - navigation
  - reference
description: "Scans content frontmatter and writes sitemap.yaml — the page catalog used by nav and sitemap-pipeline."
toc: true
rotkeeper_nav:
  - "20_Sitemap"
  - "sitemap"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "sitemap/sitemap.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc sitemap

`rc sitemap` walks `home/content/`, reads the frontmatter of every Markdown file, and writes a structured page catalog to `home/bones/reports/sitemap.yaml`.  
This catalog is the data source for `rc nav`, `rc sitemap-pipeline`, and `rc render_sitemap`.

---

## What it does

1. Recursively scans `home/content/` for `.md` files (skips files starting with `_` and any hidden directories)
2. Loads frontmatter from each file; skips files where `draft: true` or `published: false`
3. Extracts `title`, `path`, `author`, `date`, `keywords`, `tags`, `rotkeeper_nav`, and `show_in_nav` from each file
4. Sorts pages by `rotkeeper_nav` numeric prefix, falling back to title alphabetically
5. Writes the sorted list to `home/bones/reports/sitemap.yaml`

---

## Usage

```bash
rc sitemap
rc sitemap --dry-run
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--dry-run` | bool | false | Log what would be written without creating `sitemap.yaml` |

---

## sitemap.yaml format

```yaml
pages:
  - path: index.html
    title: "Rotkeeper Documentation"
    author: "Filed Systems"
    date: "2026-03-20"
    tags: [rotkeeper, reference]
    keywords: []
    rotkeeper_nav: ["00_Home"]
    show_in_nav: true
```

Each entry maps directly to the frontmatter fields read from the source file. Pages with `show_in_nav: false` are included in `sitemap.yaml` but will be excluded from rendered nav structures by downstream commands.

---

## Example

```bash
rc render
rc sitemap
rc nav
```

---

## Notes

- `rc sitemap` only reads files — it never writes to `home/content/` or `output/`.
- Files without a `title` field use the filename stem as the title.
- If frontmatter cannot be parsed for a file, that file is skipped with a warning logged.
- Pages with duplicate output paths (two `.md` files resolving to the same `.html`) are skipped after the first with a warning.
- For the full pipeline including nav partial and sidecar generation, use `rc sitemap-pipeline` instead.
<!-- END: md/sitemap/sitemap.md -->

<!-- START: md/utils/book.md -->

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
<!-- END: md/utils/book.md -->

<!-- START: md/utils/cleanup-bones.md -->

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
<!-- END: md/utils/cleanup-bones.md -->

<!-- START: md/utils/index.md -->

---
title: "Utilities"
slug: utilities-index
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - utilities
  - nav
  - cleanup
  - book
  - reference
description: "Overview of Rotkeeper utility commands: nav, cleanup_bones, and book."
toc: false
rotkeeper_nav:
  - "40_Utilities"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "utilities/index.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# Utilities

Utility commands handle tasks that sit outside the core build pipeline — nav rendering, output cleanup, and book/scriptbook export.  
They are typically run selectively rather than as part of every build.

---

## Utility Commands

| Command | What it does |
|---|---|
| [`rc nav`](nav.md) | Renders the navigation structure into templates |
| [`rc cleanup_bones`](cleanup_bones.md) | Removes stale files from `output/` without touching source |
| [`rc book`](book.md) | Exports content as a combined book or scriptbook artifact |

---

## When to Use Each

**`rc nav`** — run when nav structure has changed (new pages, reordered tokens) but you don't need a full render. Useful for iterating on nav layout without rebuilding all HTML.

**`rc cleanup_bones`** — run before a clean build to remove orphaned output files (pages that were deleted from source but still exist in `output/`). Safe to run at any time; it does not touch `home/`.

**`rc book`** — run when you want a single combined output (e.g. a PDF-ready or single-HTML artifact). Typically a one-off rather than part of the standard build loop.

---

## Pages in This Section

- [nav](nav.md) — render nav structure into templates
- [cleanup_bones](cleanup_bones.md) — remove stale output files
- [book](book.md) — export content as a combined book artifact
<!-- END: md/utils/index.md -->

<!-- START: md/utils/nav.md -->

---
title: "rc nav"
slug: utilities-nav
template: rot-doc.html
version: "0.0.1-pre"
updated: "2026-03-20"
author: "Filed Systems"
date: 2026-03-20
tags:
  - utilities
  - navigation
  - reference
description: "Reads sitemap.yaml and writes nav.yaml — a structured navigation tree grouped by rotkeeper_nav, author, date, and tags."
toc: true
rotkeeper_nav:
  - "40_Utilities"
  - "nav"
show_in_nav: true
draft: false
published: true
asset_meta:
  name: "utilities/nav.md"
  version: "0.0.1-pre"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "MIT"
---

# rc nav

`rc nav` reads `home/bones/reports/sitemap.yaml` and produces `home/bones/reports/nav.yaml` — a fully structured navigation tree organized by `rotkeeper_nav` section, author, date, and tags.  
Use it when you need the nav data file updated without running the full `sitemap-pipeline`.

---

## What it does

1. Reads `home/bones/reports/sitemap.yaml` (exits with error if not found)
2. Filters out pages where `show_in_nav` is false
3. Builds five parallel navigation trees from the page list:
   - **`rotkeeper_nav`** — hierarchical tree from nav tokens, sorted by numeric prefix
   - **`author`** — pages grouped alphabetically by author
   - **`date`** — pages nested by year → month → day
   - **`tags`** — pages grouped alphabetically by tag
   - **`keywords`** — pages grouped alphabetically by keyword
4. Writes the combined structure to `home/bones/reports/nav.yaml`

Numeric prefixes are stripped from display labels in the output (`10_Pipeline` → `Pipeline`).

---

## Usage

```bash
rc nav
rc nav --dry-run
rc nav --verbose
rc nav --output path/to/custom-nav.yaml
```

---

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--output` | path | `home/bones/reports/nav.yaml` | Custom output path for the nav YAML |
| `--dry-run` | bool | false | Print the nav YAML to stdout without writing any file |
| `--verbose` | bool | false | Print top-level groups and page titles after writing |

---

## nav.yaml structure

```yaml
rotkeeper_nav:
  - group: Home
    pages:
      - title: "Rotkeeper Documentation"
        path: index.html
        ...
  - group: Pipeline
    pages:
      - group: render
        pages: [...]

author:
  - group: "Filed Systems"
    pages: [...]

date:
  - group: "2026"
    pages:
      - group: "03"
        pages:
          - group: "20"
            pages: [...]

tags:
  - group: pipeline
    pages: [...]

keywords:
  - group: pandoc
    pages: [...]
```

---

## Example

```bash
rc sitemap
rc nav
rc nav --dry-run    # inspect nav structure without writing
```

---

## Notes

- `rc nav` requires `sitemap.yaml` to exist. Run `rc sitemap` or `rc sitemap-pipeline` first.
- Pages without any `rotkeeper_nav` tokens are placed in a `Misc` group.
- Pages without a valid ISO date string in the `date` field are placed in a `Misc` group in the date tree.
- `rc nav` does **not** write a nav partial for injection into rendered pages — that is done by `rc sitemap-pipeline` stage 4. `rc nav` produces a data file only.
<!-- END: md/utils/nav.md -->

