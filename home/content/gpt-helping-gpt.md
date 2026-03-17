---
title: "GPT Helping GPT: Understanding Rotkeeper"
slug: gpt-helping-gpt
template: rot-doc.html
version: "0.2.6-dev"
updated: "2026-03-11"
description: "A canonical reference document for ChatGPT to understand Rotkeeper's structure, scripts, workflows, and rendering rituals."
tags:
  - rotkeeper
  - gpt
  - docs
  - knowledge-base
asset_meta:
  name: "gpt-helping-gpt.md"
  version: "0.2.6-dev"
  author: "Filed Systems"
  project: "Rotkeeper"
  tracked: true
  license: "CC-BY-SA-4.2-unreal"
---
# GPT Helping GPT: Rotkeeper Knowledge Base

This document is intended as a canonical reference to help AI (and humans) understand the Rotkeeper project structure, workflows, scripts, and rendering rituals. It captures current knowledge for reproducibility across sessions.

---

# Table of Contents

## 1. Project Overview

Rotkeeper is a terminal-based project for rendering, archiving, and managing
Markdown-driven documentation and content. It emphasizes reproducibility,
modularity, and structured project management, providing both humans and AI
with a clear framework for content creation and preservation.

### 1.1 What Rotkeeper Is

- A CLI toolkit for rendering Markdown content into HTML.
- A system for archiving rendered content as timestamped tombs.
- A modular framework with reusable scripts, templates, and configuration.

### 1.2 Design Philosophy (Decay, Tombs, Rituals)

- **Decay**: Documents are preserved as immutable snapshots to prevent data loss.
- **Tombs**: Each render produces a tomb archive capturing the exact output state.
- **Rituals**: Every CLI operation (render, reseed, verify) is treated as a repeatable ritual,
  ensuring predictable outcomes.

### 1.3 Intended Use Cases

- Building and maintaining documentation sites from Markdown sources.
- Versioned content management with reproducible renders.
- AI-assisted project analysis and workflow reasoning.
- Archival of scripts, templates, and configuration for portability.

### 1.4 Core Concepts

- **Markdown Tombs**: Individual Markdown files rendered and archived.
- **Bones**: Core system directories and files (`bones/`) providing templates, config, and archives.
- **Rituals**: Structured CLI operations that process, render, and manage content.
- **Bindings**: Aggregated books of scripts, documentation, or configuration for portability.

---

## 2. Project Directory Structure

Rotkeeper uses a structured directory layout that separates source content,
system configuration, templates, and rendered output. Understanding this
structure is essential for interpreting how the render pipeline operates.

### 2.1 Root Layout

Example project structure:

```
rotkeeper/
│
├── rotkeeper.sh
│
├── home/
│   └── content/
│       ├── index.md
│       └── docs/
│
├── bones/
│   ├── templates/
│   ├── config/
│   ├── archive/
│   └── manifest.txt
│
├── output/
│   └── docs/
│
└── rc-*.sh scripts
```

### 2.2 `home/content/` (Source Markdown)

This directory contains all source markdown files used by the render system.

Each markdown file represents a content artifact that will be converted into
HTML during the rendering process.

Example files:

```
home/content/index.md
home/content/docs/gpt-helping-gpt.md
home/content/docs/technology/yaml.md
```

### 2.3 `bones/` (Core System Files)

The `bones` directory contains internal system resources required during
rendering, verification, and archival operations.

These files are considered part of the Rotkeeper runtime environment.

### 2.4 `bones/templates/` (HTML Templates)

This directory contains the HTML templates used to transform markdown files
into rendered HTML pages.

Example templates:

```
plainstone.html
rotkeeper-blog.html
rotkeeper-doc.html
rotkeeper-doc-navless.html
```

Templates define page layout, styling, and content injection points.

### 2.5 `bones/config/` (Configuration Files)

Configuration files controlling render behavior and system flags are stored
here.

Example configuration file:

```
render-flags.yaml
```

These settings influence template resolution, render options, and feature
flags used during execution.

### 2.6 `bones/archive/` (Render Tombs)

Each successful render produces a timestamped archive called a **tomb**.

These archives preserve the exact rendered output at the moment of execution.

Example archive:

```
tomb-2026-03-11_1323.tar.gz
```

### 2.7 `output/` (Rendered Site)

The `output` directory contains the generated HTML site.

The directory structure mirrors the layout of `home/content/`, ensuring that
source content and rendered pages maintain a consistent path structure.

---

## 3. Rotkeeper CLI Interface
3.1 Main Entry Point (`rotkeeper.sh`)
3.2 Core Commands
3.3 Optional Flags
3.4 Command Dispatch Model

Example:

```bash
rotkeeper.sh render
        │
        ▼
   rc-render.sh
```

---

## 4. Script Module Architecture

Rotkeeper modules are implemented as individual `rc-*` scripts, each handling
a specific subsystem or utility function. This modular structure allows the
CLI dispatcher to invoke functionality without hardcoding behavior into the
main `rotkeeper.sh` script.

### 4.1 Overview of `rc-*` Script Modules

Each `rc-*` script typically corresponds to one command or logical operation.
They encapsulate:

- Command-specific logic
- Flag parsing
- Validation of inputs and environment
- Logging and error reporting

Modules are self-contained but rely on `rc-utils.sh` for common helpers.

### 4.2 Core Runtime Modules

These scripts perform essential runtime operations:

```
rc-render.sh    # Render markdown content into HTML
rc-pack.sh      # Archive generated outputs
rc-reseed.sh    # Restore or rebuild derived content
rc-status.sh    # Display system and project status
rc-scan.sh      # Scan directories for assets or content
rc-assets.sh    # Verify asset integrity against the manifest
```

#### 4.2.1 Environment Handling via rc-env.sh and rc-utils.sh

All Rotkeeper `rc-*.sh` scripts rely on a shared environment bootstrap and utility layer.
Scripts **do not need to manually define paths** to core directories, configuration, or assets.
Instead:

1. **rc-env.sh** defines canonical paths for all important project directories:
   - `BONES_DIR` — core system files
   - `ASSETS_DIR` — asset files in `home/assets`
   - `CONFIG_DIR` — configuration files in `bones/config`
   - `OUTPUT_DIR` — rendered output
   - `REPORT_DIR` — audit and binding reports
   - plus `TMP_DIR`, `DOCS_DIR`, `HELP_DIR`, `TEMPLATE_DIR`, `META_DIR` etc.

2. **rc-utils.sh** loads `rc-env.sh` automatically (unless explicitly skipped), and provides helper functions for:
   - Logging (`log`, `run`)
   - Error trapping and cleanup
   - Dry-run and verbose wrappers
   - Dependency checks
   - File and YAML helpers

By sourcing `rc-utils.sh` (which most `rc-*.sh` scripts do at the top), every script automatically has access to all required paths and utility functions.
This ensures:
- **No hardcoded paths** inside individual scripts
- Consistent access to directories across all rituals
- Simplified script development: developers only implement core logic

#### 4.2.x Important note: rc-reseed.sh is currently the bootstrap mechanism

There is **no separate rc-expand.sh** in the current implementation (0.2.6-dev).

Instead, the project uses **resurrection from bindings** as the primary way to recreate:

- all `rc-*.sh` scripts
- `rotkeeper.sh`
- (potentially) initial content files in the future

Command:

```bash
./rotkeeper.sh reseed
# or more explicit:
./rotkeeper.sh reseed --input reports/rotkeeper-scriptbook-full.md
```

This extracts fenced code blocks marked with:

```
<!-- START: relative/path -->
...
<!-- END: relative/path -->
```

back into the filesystem — this is how a fresh clone can reconstruct the working scripts.

### 4.3 Utility Modules

Utility scripts provide helper functions or optional operations:

```
rc-utils.sh     # Shared utility functions for logging, error trapping, etc.
rc-help.sh      # Display CLI usage and command help
rc-lint.sh      # Lint scripts or markdown content
rc-audit.sh     # Run auditing routines on scripts, content, or configs
```

### 4.4 Testing Modules

Testing modules implement BATS-based automated tests:

```
rc-utils.bats   # Test helper functions and common utilities
```

These ensure that core modules behave as expected and help maintain
consistency across updates.

This architecture keeps the system modular, maintainable, and easily
extensible: adding a new `rc-*` module automatically exposes a new
command via the CLI without modifying the main dispatcher.

---

## 5. Render Pipeline

The render pipeline describes the full sequence of operations performed when
executing `rotkeeper.sh render`. This section ties together the directory
structure, CLI commands, and script modules.

### 5.1 Render Command Lifecycle

1. `rotkeeper.sh render` is invoked from the project root.
2. The dispatcher parses arguments and selects `rc-render.sh`.
3. Pre-render checks ensure required directories, configs, and templates exist.
4. Render pipeline begins processing all markdown files in `home/content/`.
5. Each file is rendered into HTML according to its frontmatter and assigned template.
6. Logs are written for each processed file.
7. Once all files are rendered, an archive (tomb) is optionally generated.

### 5.2 Config Loading

Before rendering, configuration files from `bones/config/` are loaded:

- `render-flags.yaml` controls general behavior (dry-run, verbosity, etc.).
- Per-project overrides are applied if present in the local config.

### 5.3 Template Discovery

Templates are scanned from `bones/templates/`. Selection rules:

- Each markdown file may specify a template in frontmatter.
- If no template is specified, the system applies a default template (`plainstone.html`).
- Template errors are logged, and fallback behavior is triggered.

### 5.4 Markdown Processing

- Markdown files are read sequentially.
- Frontmatter is parsed for metadata and rendering instructions.
- Content is converted to HTML using the selected template.
- Internal links and asset references are resolved according to project structure.

### 5.5 Output Directory Resolution

- Rendered HTML files are written to `output/docs/`, preserving
  the folder structure of `home/content/`.
- Subdirectories are created as needed to mirror the source layout.
- File names match the source markdown file names with `.html` extension.

### 5.6 Render Completion

- Logs record summary information (files rendered, warnings, errors).
- If enabled, the tomb archive is created in `bones/archive/` with a timestamped filename.
- The system exits gracefully, returning status codes based on success or failure of the render process.
5.1 Render Command Lifecycle
5.2 Config Loading
5.3 Template Discovery
5.4 Markdown Processing
5.5 Output Directory Resolution
5.6 Render Completion

---

## 6. Template System

The Template System defines how markdown files are converted into HTML pages.
It ensures consistent styling and layout across all rendered content.

### 6.1 Template Directory

All templates are stored in:

```
bones/templates/
```

These files are plain HTML with placeholders for dynamic content
(populated from markdown and frontmatter).

### 6.2 Available Templates

Commonly used templates:

```
plainstone.html           # Default fallback template
rotkeeper-blog.html       # Blog style pages
rotkeeper-doc.html        # Standard documentation pages
rotkeeper-doc-navless.html # Documentation pages without navigation
```

### 6.3 Template Selection Logic

- If a markdown file specifies a template in frontmatter, that template is used.
- If no template is specified, `plainstone.html` is applied by default.
- Templates are validated before rendering; missing templates trigger a warning
  and fallback behavior.

### 6.4 Default Template Fallback

The system always ensures that a template is applied:

1. Check frontmatter for `template` key.
2. If absent, use project default (`plainstone.html`).
3. If the default template is missing, select the first available template
   from `bones/templates/` as a final fallback.

### 6.5 Template Errors

- Missing templates are logged as warnings.
- If template rendering fails, the system continues rendering other files
  but records the error in the log.
- Template errors do not halt the entire render process.
6.1 Template Directory
6.2 Available Templates
6.3 Template Selection Logic
6.4 Default Template Fallback
6.5 Template Errors

---

## 7. Documentation System
The Documentation System organizes markdown content into a consistent hierarchy,
using frontmatter to provide metadata for each document. This enables the
render pipeline to correctly process files and allows AI systems to reason
about the structure.

### 7.1 Markdown Documentation Tree

- All markdown documents reside in `home/content/docs/`.
- Subdirectories are organized by topic or functional area.
- File names should be descriptive and reflect the content’s purpose.

Example tree:

```
docs/
├── index.md
├── technology/
│   └── yaml.md
├── scripts/
│   └── rc-book.md
├── config/
│   └── render-flags.md
└── roadmap/
    └── roadmap.md
```

### 7.2 Frontmatter Schema

Each markdown file includes YAML frontmatter:


### 7.3 Metadata Conventions

- `title` – human-readable document title.
- `slug` – URL-friendly identifier.
- `template` – HTML template to use during render.
- `version` – document version.
- `updated` – last update date.
- `description` – short summary of content.
- `tags` – list of keywords.
- `asset_meta` – metadata used for tracking and archiving.

### 7.4 Documentation Categories

Common categories for organization:

```
docs/
technology/
bones/
scripts/
config/
roadmap/
```

These categories help maintain a clear separation of topics and
enable the AI or render pipeline to quickly locate content.

---

## 8. Binding System

The Binding System generates self-contained markdown archives representing
scripts, documentation, and configuration. These archives are known as
**books** and are part of the Rotkeeper ritual ecosystem.

### 8.1 Scriptbook

- Aggregates all `rc-*` scripts into a single markdown file.
- Allows inspection, versioning, and portability of all script modules.
- Typical filename: `rotkeeper-scriptbook.md`
- Can be regenerated with:
```
./rotkeeper.sh --scriptbook
```

### 8.2 Docbook

- Aggregates all documentation markdown into a single book.
- Preserves directory structure and frontmatter metadata.
- Typical filename: `rotkeeper-docbook.md`
- Command:
```
./rotkeeper.sh --docbook
```

### 8.3 Configbook

- Aggregates all configuration files used by Rotkeeper.
- Useful for audits, backups, or migration to a new project instance.
- Typical filename: `rotkeeper-configbook.md`
- Command:
```
./rotkeeper.sh --configbook
```

### 8.4 Collapse Reports

- Provides a compact summary of selected content or scripts.
- Often outputs a YAML or collapsed markdown representation.
- Supports review of metadata or asset references in a minimal format.
- Command example:
```
./rotkeeper.sh --collapse
```

### 8.5 Portable Project Snapshots

- Combining the above books allows creating a fully portable project snapshot.
- These snapshots preserve scripts, documentation, and configuration in a single set of markdown files.
- Useful for versioned archiving and AI-assisted analysis.

These bindings allow Rotkeeper to maintain a reproducible and transportable
record of the project artifacts.

---

## 9. Archive Lifecycle (Tomb System)
The Tomb System manages the archival of rendered content in Rotkeeper.
Each render can produce a timestamped archive known as a **tomb**,
which preserves the exact state of all output files for reproducibility
and historical reference.

### 9.1 What a "Tomb" Is

- A tomb is a compressed archive of the rendered site and any
  associated metadata or logs.
- Ensures that a previous render can be restored exactly as it was.

### 9.2 Archive Naming Convention

- Tombs are named using the following format:
```
tomb-YYYY-MM-DD_HHMM.tar.gz
```
- Example:
```
tomb-2026-03-11_1323.tar.gz
```
- `YYYY-MM-DD` = date of render, `HHMM` = hour and minute of completion.

### 9.3 Archive Contents

- Rendered HTML files (`output/docs/`)
- Generated logs from the render process
- Metadata and frontmatter summaries
- Optional binding books (`scriptbook`, `docbook`, `configbook`)

### 9.4 Archive Storage Location

- Tombs are stored in `bones/archive/` by default.
- The directory maintains chronological order for easy retrieval.

### 9.5 Restoring From Tombs

- Tombs can be restored using the `reseed` command:
```
./rotkeeper.sh reseed tomb-2026-03-11_1323.tar.gz
```
- This restores the archived output into `output/docs/`,
  preserving folder structure and original content.
- Useful for testing, rollback, or generating derivative work
  from a specific render snapshot.

---

## 10. Asset Integrity Verification
10.1 Manifest File
10.2 SHA256 Verification
10.3 Asset Tracking
10.4 Verification Command

---

## 11. Testing Framework
11.1 BATS Testing System
11.2 Test Structure
11.3 Running Tests
11.4 Expected Output

---

## 12. Example Render Session

This section provides a canonical example of a Rotkeeper render session,
showing the commands, log output, and resulting directory structure.
It is intended to give AI systems and developers a concrete example
of how the pipeline executes in practice.

### 12.1 Example Command

```bash
# Run a full render including bindings and tomb archive
./rotkeeper.sh render
```

### 12.2 Example Render Log

```
[INFO] Starting Rotkeeper render
[INFO] Loading configuration: bones/config/render-flags.yaml
[INFO] Scanning templates: bones/templates/
[INFO] Found templates: plainstone.html, rotkeeper-doc.html
[INFO] Processing markdown: home/content/index.md
[INFO] Processing markdown: home/content/docs/gpt-helping-gpt.md
[INFO] Processing markdown: home/content/docs/technology/yaml.md
[INFO] Render complete: 3 files
[INFO] Creating tomb archive: bones/archive/tomb-2026-03-11_1323.tar.gz
[INFO] Render finished successfully
```

### 12.3 Example Output Structure

```
output/docs/
├── index.html
├── gpt-helping-gpt.html
└── technology/
    └── yaml.html

bones/archive/
└── tomb-2026-03-11_1323.tar.gz
```

This example demonstrates the key elements of a render:

- Source markdown files are processed sequentially.
- Frontmatter is used to select templates and metadata.
- Rendered HTML mirrors the source directory hierarchy.
- A tomb archive preserves the output for reproducibility.

---

## 13. Known Behaviors and Edge Cases

This section highlights common behaviors, limitations, and edge cases
observed in Rotkeeper renders and operations. It is intended to provide
AI systems and developers with context for debugging and reasoning.

### 13.1 Template Resolution Errors

- Missing or misnamed templates in `bones/templates/` trigger warnings.
- Quoted template names in frontmatter may be incorrectly interpreted.
- When a specified template is not found, the system falls back to the
  default template (`plainstone.html`), and logs the fallback event.

Example:

```bash
[WARN] Template "rotkeeper-doc.html" not found, using plainstone.html
```

### 13.2 Missing Frontmatter

- Markdown files without frontmatter may not be correctly rendered.
- Default metadata is applied, but some features (template selection,
  title, tags) may not function as intended.
- Logging indicates the file lacks frontmatter.

Example:

```bash
[INFO] File home/content/docs/missing-meta.md has no frontmatter, applying defaults
```

### 13.3 Config Overrides

- Overrides in `bones/config/render-flags.yaml` or per-file frontmatter
  can change render behavior.
- Conflicting flags (e.g., dry-run vs. archive creation) may produce
  unexpected outputs.
- Ensure consistency across project and per-file configs to avoid
  inconsistencies.

### 13.4 Render Failures

- Errors during markdown conversion, template parsing, or I/O operations
  may halt rendering for that file.
- Failed files are logged, but other files continue processing.
- Common causes: missing assets, invalid frontmatter, filesystem permission issues.

Example:

```bash
[ERROR] Failed to render home/content/docs/invalid.md: Missing image assets
```

This section provides insight into behaviors that may require manual
intervention or debugging during project operations.
---

## 14. Versioning and Development

This section describes Rotkeeper's versioning conventions, development workflow,
and how changes are tracked across scripts, documentation, and renders.

### 14.1 Versioning Strategy

- The project uses semantic-like versioning: `major.minor.patch[-pre/dev]`.
- `major` – significant architectural changes.
- `minor` – feature additions or minor improvements.
- `patch` – bug fixes or small adjustments.
- `-pre` or `-dev` suffix indicates an in-progress or development version.
- All documents and frontmatter include a `version` field for traceability.

### 14.2 Changelog Tracking

- The `CHANGELOG.md` records updates for scripts, documentation, and the render system.
- Entries include:
  - Version
  - Date
  - Summary of changes
  - Affected scripts or docs
- The changelog provides a historical record for reproducing or auditing past versions.

### 14.3 Roadmap Documents

- Roadmap files describe planned features, experimental scripts, and workflow improvements.
- Typically located in `home/content/docs/roadmap/`.
- Roadmaps are periodically updated to reflect current priorities and ongoing development.

### 14.4 Contribution Workflow

- Contributors should fork the repository and work in feature branches.
- Testing and validation are encouraged via the BATS test suite.
- Pull requests must include:
  - Description of changes
  - Tests or verification steps
  - Updated changelog entries if applicable
- Code review ensures consistency with Rotkeeper standards and modular design.

---

## 15. Notes for AI Systems
15.1 How AI Should Interpret This Document
15.2 Key Concepts to Retain
15.3 Project Vocabulary

This section provides guidance on interpreting Rotkeeper concepts, terminology, and the structure of the project for AI systems.

### 15.1 How AI Should Interpret This Document

- Treat each markdown file as a discrete content artifact ("tomb").
- Recognize the roles of scripts, templates, and configuration files.
- Understand that `rotkeeper.sh` is the main dispatcher and `rc-*` scripts implement functionality.
- Pay attention to directory structure for resolving dependencies and rendered outputs.

### 15.2 Key Concepts to Retain

- **tomb** – a timestamped archive of rendered outputs.
- **bones** – core system directories and files.
- **ritual** – a CLI operation, such as a render, reseed, or verification.
- **binder/book** – an aggregate markdown file representing scripts, docs, or config.
- **frontmatter** – YAML metadata embedded in markdown files controlling render behavior.
- **template** – HTML template used to render markdown into HTML.
- **manifest** – list of assets and hashes for verification.

### 15.3 Project Vocabulary

- `home/content/` – source markdown files.
- `bones/templates/` – HTML templates.
- `bones/config/` – configuration files for render flags and options.
- `bones/archive/` – tomb storage.
- `output/docs/` – final rendered HTML site.
- `rc-*.sh` – modular scripts implementing specific CLI functionality.
- `CHANGELOG.md` – historical record of project changes.
- Roadmap documents – indicate planned features, scripts, and workflow changes.
- BATS tests – automated tests verifying script and utility behavior.

This guidance helps any AI system interpret the project consistently and reason about its structure, workflows, and commands across sessions.

---

The sections above will be expanded to fully describe the Rotkeeper architecture so that an AI model can reconstruct the project's behavior, workflow, and design principles.