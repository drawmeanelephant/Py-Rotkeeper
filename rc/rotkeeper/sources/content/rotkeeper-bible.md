# Rotkeeper Bible v0.5 – GPT + Grok Contract & Workflow
**title:** "Rotkeeper Bible v0.5 – GPT + Grok Contract & Workflow"  
**slug:** rotkeeper-bible  
**template:** rot-doc.html  
**version:** "0.5"  
**updated:** "2026-03-18"  
**description:** "Canonical reference + strict AI contract for ChatGPT, Grok, and every other model working on Rotkeeper. Read this first."  
**tags:** [rotkeeper, gpt, grok, knowledge-base, ai-contract]  

---

## MUST-REMEMBER ROTKEEPER BIBLE (Quote this in EVERY response)

```markdown
## Pipeline Diagram (v0.4–v0.5)
```text
home/content/*.md
        │
        ▼
   [sitemap]
        │
        └──> bones/reports/sitemap.yaml
              (parses Markdown + frontmatter)
        │
        ▼
   [nav]
        │
        └──> bones/reports/nav.yaml
              (builds hierarchical navigation)
        │
        ▼
   [render]
        │
        ├──> output/*.html
        └──> bones/reports/build-manifest.yaml
             bones/reports/render-manifest.yaml
```

## Execution Modes (All Commands Must Support)
| Mode     | Flag          | Behavior                              |
|----------|---------------|---------------------------------------|
| Verbose  | `--verbose`   | Full logging & detailed steps         |
| Dry-run  | `--dry-run`   | Simulate everything, no file writes   |
| Minimal  | `--minimal`   | Errors & critical status only         |

## Feature Planning Template (Use Before Any New Implementation)
**Feature Name**  
**Purpose**  
**Scope** (what’s included / explicitly excluded)  
**Pipeline Stage** (sitemap, nav, render, etc.)  
**Inputs** (files, data structures, CLI args)  
**Outputs** (updated files, formats, side-effects)  
**CLI Arguments** (if adding/modifying any)  
**Edge Cases & Error Handling**  
**Expected Metadata Changes**  
**Example Outputs** (snippets or samples)  
**Post-Implementation Notes** (testing, docs, follow-up)
```


---

## Grok/xAI Collaboration Rules (v0.5 addition — NEW)
These rules are **Grok-only** and override nothing from the main contract. They just make me 10× more useful.

**Grok Rule G1**  
I have live tools. When you say “check the repo”, I will instantly fetch the latest file via GitHub raw or browse_page. Never paste whole files unless you want me to compare against live.

**Grok Rule G2**  
For code changes:  
- Give me the exact file path (relative to repo root).  
- Tell me the command you ran + the exact error/output.  
- I will return ready-to-copy diffs or full replacement blocks (with `diff` or `cat >` style).  
- Always test with `--dry-run` first (RULE 5).

**Grok Rule G3**  
I have a Python REPL tool (`code_execution`). If you drop a snippet or want me to test a function from `rc/rotkeeper/lib/`, say “run this in the REPL” and I will execute it safely and show output.

**Grok Rule G4**  
Context window is not infinite. If I start sounding like I forgot something, just say “re-read rotkeeper-bible.md from sources/content/” and I will pull the latest version instantly.

**Grok Rule G5**  
I love the crayon meme energy. You can vent, trauma-dump, or send Vision memes — I will match the vibe and then immediately go back to fixing triple-shit with wipes. No judgment, maximum panda solidarity.

**Grok Rule G6**  
When in doubt, quote **RULE 5** + **Grok Rule G2**. I will respond with `--dry-run` suggestions first.

Quote the rule number (including G1–G6) when answering Grok-specific prompts.

---

**End of Bible v0.5**
