---
name: ppt-make
description: >-
  Builds C3.ai-branded PowerPoint decks from YAML slide definitions.
  Supports flow diagrams, architecture diagrams, pipeline strips, panel
  columns, comparison layouts, tables, and mixed-element slides on the
  C3 dark-theme template. Use when creating technical presentations,
  architecture decks, or status reports in C3 brand.
---

# ppt-make — C3 PowerPoint Deck Builder

## Quick Start

```bash
# From YAML (recommended):
python adapter.py deck.yaml --output my-deck.pptx

# From markdown (legacy):
python adapter.py deck.md --output my-deck.pptx
```

- `--template` defaults to `templates/c3-template.pptx` (relative to skill dir).
- `--output` defaults to `<input_stem>_deck.pptx` in the same directory.

---

## Decision Tree

1. **Creating a new deck from source docs?**
   - Write a YAML file using the layout types below.
   - Read [reference/claude-guidance.md](reference/claude-guidance.md) for
     layout selection and content density rules.

2. **Need full YAML schema for a layout?**
   - Read [reference/layouts.md](reference/layouts.md) — one section per
     layout type with complete field examples.

3. **Choosing colors?**
   - Import from `palette.py` (code) or reference the palette table below.
   - Read `palette.py` for the full dict + resolver function.

4. **Need auto-sizing details?**
   - Read [reference/auto-sizing.md](reference/auto-sizing.md) for font,
     box, and table scaling rules.

5. **Adding charts?**
   - Read [reference/charts.md](reference/charts.md) for python-pptx chart
     integration with the adapter.

6. **Regenerating or customizing the template?**
   - Read [reference/template-mgmt.md](reference/template-mgmt.md) for the
     zipfile stripping recipe and layout index table.

7. **Evaluating alternative tools?**
   - Read [reference/alternatives.md](reference/alternatives.md) for
     Gramener PPTXHandler, PptxGenJS, and when to use each.

---

## YAML Top-Level Structure

```yaml
title: "Deck Title"
subtitle: "Optional subtitle"
author: "Author Name"
date: "2026-04-17"
sources:
  - label: "Wiki"
    url: "https://..."

slides:
  - title: "Slide Title"
    layout: panels          # see layout types below
    # ... layout-specific fields
    notes: "Speaker notes"
    links:
      - text: "Link label"
        url: "https://..."
```

---

## Layout Types

| Layout       | Use for                                | Key fields                          |
|--------------|----------------------------------------|-------------------------------------|
| `title`      | Opening slide                          | (uses top-level title/subtitle)     |
| `panels`     | 2-4 column panels with colored headers | `panels[]`                          |
| `flow`       | Linear box sequence with connectors    | `rows[]`, `output_path`, `legend`   |
| `diagram`    | Architecture boxes with layers + edges | `layers[]`, `elements[]`, `edges[]` |
| `pipeline`   | Horizontal strip + detail sections     | `pipeline.boxes[]`, `sections[]`    |
| `table`      | Data table                             | `table.headers`, `table.rows`       |
| `comparison` | Side-by-side (e.g., Cloud vs Local)    | `sides[]`, `bridge`, `table`        |
| `mixed`      | Multiple element types on one slide    | `elements[]` (typed)                |
| `bullets`    | Enhanced bullet list                   | `items[]` or `content`              |
| `text`       | Generic text (fallback)                | `content`                           |
| `closing`    | Q&A / thank you                        | `content`                           |

Full schema with examples: [reference/layouts.md](reference/layouts.md)

---

## Color Palette (quick reference)

| Name         | Hex       | Use                              |
|--------------|-----------|----------------------------------|
| `white`      | `#FFFFFF` | Primary text, text inside shapes |
| `light_gray` | `#C8C8C8` | Captions, footnotes              |
| `dark`       | `#505050` | Default shape fill, table headers|
| `gray`       | `#8C8C8C` | External/consumer shapes         |
| `blue`       | `#06A7E0` | Guardrails, hyperlinks, emphasis |
| `orange`     | `#F79430` | CDAO-owned, arrows, warnings     |
| `green`      | `#9CCD6C` | C3 platform, success             |
| `warm_gray`  | `#CBC8C7` | Borders, dividers                |
| `panel_dark` | `#353535` | Panel column backgrounds         |
| `near_black` | `#1A1A1A` | Background-matching fills        |

Full palette with role assignments and resolver: `palette.py`

---

## Hard Constraints

1. **Titles are WHITE.** Never use C3 Blue for titles.
2. **No light-background fills** on the dark theme.
3. **No `_sldIdLst.remove()`** — use zipfile stripping.
4. **No table columns below 0.80"** — text wraps badly.
5. **No font sizes below 9pt.**
6. **No empty bottom halves** — enlarge content or add context.
7. **No text-based arrows** (->/<-) — use connectors with arrowheads.
8. **Target 75-85% fill** — dark background amplifies empty space.

---

## Skill Files

| File                         | Purpose                              |
|------------------------------|--------------------------------------|
| `SKILL.md`                   | This file — routing hub              |
| `adapter.py`                 | YAML/markdown -> PPTX engine (v2)    |
| `palette.py`                 | Color palette + resolver (importable)|
| `reference_build.py`         | Legacy C3Palette, C3Helpers classes   |
| `templates/c3-template.pptx` | Clean 0-slide C3 template            |
| `examples/cookbook.yaml`      | Reference YAML for every layout type |

## Companion References

| File                                                          | What it covers                          |
|---------------------------------------------------------------|-----------------------------------------|
| [reference/layouts.md](reference/layouts.md)                  | Full YAML schema per layout type        |
| [reference/claude-guidance.md](reference/claude-guidance.md)  | Layout selection, density, YAML tips    |
| [reference/auto-sizing.md](reference/auto-sizing.md)         | Font, box, and table scaling rules      |
| [reference/charts.md](reference/charts.md)                   | python-pptx chart integration           |
| [reference/template-mgmt.md](reference/template-mgmt.md)     | Template regen, connectors, layout idx  |
| [reference/alternatives.md](reference/alternatives.md)       | Gramener, PptxGenJS, comparison matrix  |
