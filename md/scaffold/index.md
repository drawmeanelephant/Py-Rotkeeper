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
