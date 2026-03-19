---
title: "Init Command"
author: "rotkeeper"
date: "2026-03-16"
lang: "en-US"
toc: true
numbersections: true
geometry: "margin=1in"
fontsize: "12pt"
keywords: [init, rotkeeper, cli]
tags: [commands, init]
rotkeeper_nav: ["01_Docs", "Commands", "Init"]
show_in_nav: true
template: "rot-doc.html"
---

# Init Command


## Concept

The `init` command sets up a new Rotkeeper project by creating the required directory structure, configuration files, and initial assets. It provides a standardized starting point for all projects, ensuring consistency and proper organization.

## Usage

```bash
rotkeeper init [--verbose]
```

- `--verbose`: Display detailed information about the initialization steps.

## Example

```bash
rotkeeper init --verbose
```

Initializes a new project and prints step-by-step information about the directories and files created.

## Future Goals

- Provide interactive prompts for selecting project templates or configurations.
- Automatically install dependencies and required system binaries.
- Support multiple project types or presets for different workflows.
- Validate the project environment and suggest best practices for setup.