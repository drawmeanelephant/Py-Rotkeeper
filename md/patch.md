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
