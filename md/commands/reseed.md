---
title: "Reseed Command"
keywords: [reseed, rotkeeper, cli]
show_in_nav: true
---

# Reseed Command

## Concept

The `reseed` command resets or refreshes the seed data in a Rotkeeper project. It ensures that sample content, default templates, and initial configuration files are returned to a known state, useful for testing, development, or restarting a project from scratch.

## Usage

```bash
rotkeeper reseed [--verbose] [--dry-run]
```

- `--verbose`: Show detailed information about what is being reseeded.  
- `--dry-run`: Display the actions that would be taken without making any changes.

## Example

```bash
rotkeeper reseed --verbose
```

Refreshes all seed data and prints detailed logs of the process without altering the existing project structure if `--dry-run` is not used.

## Future Goals

- Allow selective reseeding of specific data sets or sections of the project.  
- Integrate checks to prevent accidental overwriting of user-modified files.  
- Enable automated versioning and rollback of seed data.  
- Support custom templates or content for different project types.