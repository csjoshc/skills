# Worked Example — C3 as a canonical Stitch DESIGN.md

`/c3-ui/c3-design-system.md` is now itself a canonical-Stitch DESIGN.md (YAML front matter + canonical 8 body sections + Iconography + Agent Prompt Guide + Applicator Extras). This file shows the *shape* of the emit; for the actual document, read `~/.skills/c3-ui/c3-design-system.md`.

The example demonstrates three things:

1. **Canonical core is portable.** The front-matter `colors:`, `typography:`, `rounded:`, `spacing:`, `components:` keys are exactly Stitch's schema — readable by Stitch, the Stitch CLI, and any other Stitch-aware consumer.
2. **Skill extensions layer additively.** `colors-dark:`, `colors-css-vars:`, `motion:`, `shadows:`, `breakpoints:`, `icons:`, `z-index:` live in the same front matter as custom keys. Stitch consumers preserve unknown keys; skill-aware tools read them.
3. **Pre-existing C3 detail is preserved.** Tailwind class tables, Kendo overrides, dropdown rules, find-and-replace map, and the full anti-patterns table are kept in-section (under canonical Colors/Layout/Components/Do's-and-Don'ts) or in an "Applicator Extras" extension section after the Agent Prompt Guide.

## Skeleton (compare with the live file)

```yaml
---
version: alpha
name: C3 AI Design System

colors:                   # canonical (light) — only documented hex inlined
  surface: "#FFFFFF"
  page:    "#F7F8FA"

colors-dark:              # extension
  surface: "#1C1D1F"
  page:    "#111112"

colors-css-vars:          # extension — full Tailwind→CSS-var map
  bg-primary: "--color-primary-bg"
  ...

typography:               # canonical
  body-base:  { fontFamily: Inter, fontSize: "var(--font-size-03)", ... }
  ...

rounded:                  # canonical — C3 default is square
  none: 0
  sm: "var(--radius-sm)"
  ...

spacing:                  # canonical (14-step C3 scale)
  "00": "var(--c3-style-space-00)"
  ...

components:               # canonical — Stitch <name>-<state> variant model
  card: { backgroundColor: "{colors-css-vars.bg-primary}", rounded: "{rounded.sm}", ... }
  button-primary: { ... }
  button-primary-hover: { backgroundColor: "{colors-css-vars.bg-accent-hover}" }
  ...

motion:                   # extension
shadows:                  # extension
breakpoints:              # extension
icons:                    # extension
z-index:                  # extension
---

## Overview                  ← canonical §1 (atmosphere prose)
## Colors                    ← canonical §2 (role list + Tailwind class tables + light/dark hex table)
## Typography                ← canonical §3 (token map + family/size/weight tables)
## Layout                    ← canonical §4 (spacing scale + app shell + responsive table)
## Elevation & Depth         ← canonical §5 (shadow scale + motion grammar)
## Shapes                    ← canonical §6 (radii table)
## Components                ← canonical §7 (Card, Buttons, Inputs, TopNav, SideNav, Logo, Dropdowns, State catalog)
## Do's and Don'ts           ← canonical §8 (anti-patterns table with rationale)
## Iconography               ← extension
## Agent Prompt Guide        ← extension
## Applicator Extras         ← extension (Stack, CSS files, Dark Mode mechanism, Kendo overrides, color scales, z-index, opacity)
```

## Why this matters

- **Round-trippable.** `python3 -c "import yaml; print(yaml.safe_load(open('c3-design-system.md').read().split('---')[1]))"` parses without error.
- **Stitch CLI compatible.** Canonical sections are present in canonical order; extensions use unknown keys/headings (which Stitch preserves rather than rejecting).
- **Nothing lost in the rewrite.** Every table from the bespoke pre-rewrite version (Tailwind class tables, Kendo overrides, dropdown popup tokens, find-and-replace map, anti-patterns, color scales, z-index, opacity, brightness) appears in the canonical structure or in Applicator Extras.
- **`/c3-ui` still works.** The applicator skill consumes the same file by reading the body prose tables, which remain intact.

## Reading order for new contributors

1. Read the front matter for canonical token shape.
2. Read `## Overview` through `## Do's and Don'ts` for design intent.
3. Read `## Iconography` and `## Agent Prompt Guide` for skill-mandated extensions.
4. Read `## Applicator Extras` only when implementing the C3 stack (Tailwind v4 + Kendo + token CSS files).
