---
title: "Render Command"
keywords: [render, rotkeeper, cli]
show_in_nav: true
---

# Render Command

## Concept

The `render` command compiles and processes all source files in a Rotkeeper project into their final output formats. It applies templates, converts Markdown to HTML or PDF, compiles SCSS to CSS, and ensures that manifests and navigation are properly linked.

## Usage

```bash
rotkeeper render [--dry-run] [--verbose] [--output <dir>]
```

- `--dry-run`: Show what would be rendered without creating any output files.  
- `--verbose`: Display detailed logs of each rendering step.  
- `--output <dir>`: Specify a custom output directory for the rendered files. Defaults to the standard build directory.

## Example

```bash
rotkeeper render --verbose --output ./output
```

Renders all project files into the `./output` directory with detailed logging.

## Future Goals

- Support incremental rendering for faster builds.  
- Add preview mode to view pages before final output.  
- Integrate with alternative rendering engines or export formats.  
- Validate templates and frontmatter metadata before rendering to prevent errors.