---
title: "Bootstrap Kitchen Sink"
description: "Everything Bootstrap can do via Markdown."
author: "Filed Systems"
date: "2026-03-01"
tags:
  - docs
  - bootstrap
  - demo
keywords:
  - bootstrap
  - components
  - markdown
  - demo
template: rot-doc.html
show_in_nav: false
highlighted: "This page demonstrates Bootstrap components rendered from plain Markdown. No raw HTML required."
---

# Bootstrap Kitchen Sink 🍳

Everything on this page is generated from plain Markdown.
Pandoc handles the conversion — Bootstrap handles the style.

---

## Typography

Regular paragraph text. **Bold.** *Italic.* ~~Strikethrough.~~
`inline code`. [A link](#).

> This is a blockquote. It renders cleanly and can be styled
> further with a few lines of SCSS targeting `blockquote`.

---

## Code Blocks

```python
def hello(name: str) -> str:
    return f"Hello, {name}"

print(hello("Rotkeeper"))
```

```bash
rotkeeper sitemap-pipeline
rotkeeper render --force
```

```yaml
title: "My Page"
tags:
  - example
  - demo
template: rot-doc.html
```

---

## Tables

| Command | Description | Required |
|---|---|---|
| `sitemap-pipeline` | Build nav and metadata trees | Yes |
| `render` | Render Markdown to HTML | Yes |
| `assets` | Catalog static assets | No |
| `nav` | Generate nav YAML | No |

---

## Lists

Unordered:

- Apples
- Oranges
- Bananas with a longer description that wraps

Ordered:

1. Run `sitemap-pipeline`
2. Run `render`
3. Open `home/output/index.html` in a browser

---

## Nested Lists

- Render pipeline
    - `sitemap-pipeline`
    - `render`
- Asset pipeline
    - `assets`
    - `assets-pipeline` (coming soon)

---

## Headings All The Way Down

### H3 Section

Some content under H3. The TOC sidebar in `rot-doc.html` will
pick all of these up automatically when you pass `--toc` to Pandoc.

#### H4 Subsection

More content. Getting deeper.

##### H5 Deep Dive

You probably only need this for very long reference docs.

###### H6

You almost certainly don't need this.

---

## Images

![Rotkeeper Mascot](../../images/mascot.png)

---

## Horizontal Rules

Three dashes in Markdown become a styled `<hr>`:

---

That's a rule above and below this line.

---

## Footnotes

Pandoc supports footnotes out of the box.[^1]

[^1]: This is the footnote content. It renders at the bottom of the page.
