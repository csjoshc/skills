# Audit Mode — Diff Codebase Against DESIGN.md

Output: `ui-audit.md` at repo root. Per-section findings with file:line citations. Categories ✅ conforms / ⚠️ drift / ❌ violation.

## Pre-flight

1. Confirm `<repo-root>/DESIGN.md` exists. If not → no spec to audit against; suggest `/make-design-md`.
2. Identify UI source roots (read `tsconfig.json`, `package.json`, look for `src/`, `apps/*/`, `packages/*/`).
3. Skip `node_modules/`, `dist/`, `build/`, `.next/`, `.cache/`.

## Deterministic checks (run first, no LLM)

| Check | Command | Expected |
|---|---|---|
| Hardcoded hex outside tokens | `grep -rE '#[0-9a-fA-F]{3,8}' src/ \| grep -v tokens.css` | low count or zero |
| Native `<select>` | `grep -rn '<select' src/` | zero (per common §8 rule) |
| `rounded-xl` on buttons/cards | `grep -rn 'rounded-xl' src/` | check against §4/§8 |
| Anti-pattern token names from §8 | `grep -rn '<anti-pattern>' src/` | zero |
| `prefers-reduced-motion` honored | `grep -rn 'prefers-reduced-motion' src/` | ≥1 if §6 has motion |

Capture counts with file:line for the report.

## Specialist lenses (per DESIGN.md section)

For each section, walk the codebase with that section as the rubric. Use one lens at a time.

### §2 lens — Color & Roles
- Are all colors expressed as semantic tokens? File:line for any raw hex outside `tokens.css` / `globals.css`.
- Does light↔dark coverage match? Find any token that's defined for one mode only.
- Are state variants (hover/pressed/disabled/focus) used or are components rolling their own?

### §3 lens — Typography
- Font families loaded match §3?
- Are size / weight / line-height combinations from the §3 hierarchy table, or ad-hoc?
- Any `font-semibold` on buttons if §3 specifies default weight?

### §4 lens — Components
- For each component variant in §4, find an instance in code. Does it match the recipe?
- State catalog: are Empty / Loading / Error / Success / Skeleton implemented per §4?
- Dropdowns: any native `<select>`? (anti-pattern in most specs)

### §5 lens — Layout
- Spacing values used match the §5 scale? Any `p-7` / `gap-5` outside the scale?
- Breakpoints declared match §5 table?
- Touch targets ≥44×44px on mobile breakpoints?

### §6 lens — Depth & Motion
- Shadow tokens match §6 scale? Any inline `box-shadow` with custom values?
- Animation durations from §6 duration tokens, or ad-hoc?
- `prefers-reduced-motion` paths exist?

### §7 lens — Iconography
- Icon set matches §7?
- Sizes from §7 (16/20/24)?
- Mixed sets (e.g. lucide + FA in same component)?

### §8 lens — Anti-patterns
- For each Don't in §8, grep for it. Report all hits.

## Report format

```markdown
# UI Audit — <project> vs DESIGN.md

Audit date: YYYY-MM-DD
Spec version: <git rev or hash of DESIGN.md>

## Summary

| Section | ✅ Conforms | ⚠️ Drift | ❌ Violations |
|---|---:|---:|---:|
| §2 Color | 12 | 3 | 1 |
| §3 Typography | 5 | 2 | 0 |
| ... | | | |

## §2 Color & Roles

### ✅ Conforms
- src/components/Button.tsx:14 — uses `bg-accent` semantic token

### ⚠️ Drift
- src/components/Card.tsx:8 — uses `bg-gray-100`; should be `bg-surface` per §2
  - Fix: replace `bg-gray-100` with `bg-surface`. 12 other files affected (run grep).

### ❌ Violations
- src/pages/Settings.tsx:42 — hardcoded `#0F172A`; spec forbids slate-blue dark in §8
  - Fix: replace with `var(--bg-page)` and verify dark mode pair.

## §3 Typography
... (same shape) ...

## Drift hotspots

Top 5 files with most drift, ranked.
```

## Hard rules

- Every finding must have file:line citation.
- Every ⚠️ / ❌ must include a suggested fix referencing the DESIGN.md section.
- Do not propose changes to DESIGN.md inside Audit Mode. If the spec seems wrong, flag it and recommend the user re-run `/make-design-md`.
- Do not edit code in Audit Mode. Audit emits a report; Apply Mode acts on it.
