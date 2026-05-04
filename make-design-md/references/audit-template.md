# Phase 1 Audit Template

Fill every row of every table. If a value is absent, write "none" — never leave blank. If the codebase is greenfield, write "N/A — greenfield" and skip to Phase 2.

## Table 1 — Stack

| Field | Value |
|---|---|
| CSS framework | Tailwind v4 / Tailwind v3 / CSS modules / styled-components / vanilla / other |
| Component library | shadcn / MUI / Chakra / Kendo / Radix / custom / none |
| Icon set | lucide / phosphor / heroicons / FA / custom / none |
| Animation library | framer-motion / motion / CSS-only / none |
| Dark-mode mechanism | `.dark` class / `prefers-color-scheme` / data attribute / none |

## Table 2 — Token Inventory

| Field | Value |
|---|---|
| Color tokens defined where? | `tailwind.config.js` / CSS custom properties / scattered hex / none |
| Number of distinct hex values in use | (grep count) |
| Has semantic naming (`bg-primary`)? | yes / no — partial |
| Has both light + dark values? | yes / no / dark only / light only |
| Has state variants (hover/pressed/disabled)? | yes / no — partial |

## Table 3 — Typography

| Field | Value |
|---|---|
| Font families loaded | (list with source: Google Fonts / local / system) |
| Number of distinct sizes used | (grep count of `text-` classes) |
| Hierarchy clear? | yes / no |
| Mono font for code? | yes / no |

## Table 4 — Components

| Field | Value |
|---|---|
| `ui/` or shared primitives directory? | path or "none" |
| Buttons: extracted component or copy-pasted classes? | extracted / copy-pasted / mixed |
| Cards: extracted? | extracted / copy-pasted / mixed |
| Inputs: extracted? | extracted / copy-pasted / mixed |
| Empty / loading / error states defined? | yes / partial / no |

## Table 5 — Layout & Responsive

| Field | Value |
|---|---|
| Layout primitive (sidebar / topnav / grid) | (describe) |
| Breakpoints declared | (list or "Tailwind defaults") |
| Mobile drawer / collapse strategy | (describe or "none") |
| Touch target rule enforced? | yes / no / unknown |

## Table 6 — Motion

| Field | Value |
|---|---|
| What animates today | (list: page transitions / hover / skeletons / none) |
| Duration tokens defined? | yes / no |
| `prefers-reduced-motion` honored? | yes / no |

## Table 7 — Consistency

| Field | Value |
|---|---|
| Color drift (raw `slate-*` / `gray-*` mixed in)? | yes / no — count files |
| Radius drift (mix of `rounded-lg` `rounded-md` `rounded-xl`)? | yes / no — count files |
| Hardcoded hex outside tokens? | yes / no — count occurrences |
| Existing DESIGN.md / STYLE_GUIDE / brand doc? | path or "none". If a DESIGN.md exists, note whether it has YAML front matter (Stitch-conforming) or is bespoke prose only — bespoke specs need front-matter migration on emit. |

## Table 8 — Brand Inputs (if any)

| Field | Value |
|---|---|
| Brand guide PDF / Figma / spec doc? | path or URL or "none" |
| Logo files? | path or "none" |
| Approved color palette from marketing? | yes / no |
| Approved fonts (licensed)? | yes / no |

---

## After filling tables

Summarize in one paragraph (3–4 sentences):
- Current visual identity in one sentence ("looks like generic shadcn", "C3-aligned", "drift-heavy custom")
- Strongest pattern to preserve
- Biggest gap to close
- Whether brand-ingest path applies (Table 8 has values)
