# Technical Standards — Implementer Defaults

Defaults when DESIGN.md is silent or when running Vibe Mode without a spec. Adapt to the project's CSS approach. Tailwind v4 (`@theme`) and v3 (`darkMode: "class"`) both supported.

## Colors

Express tokens as CSS custom properties with semantic names. In Tailwind, reference via `rgb(var(--name) / <alpha-value>)` to preserve opacity modifiers. Define `:root` (light) and `.dark` (dark) sets — never compute one from the other.

## Typography

Google Fonts import with `display=swap`. Minimum 2 families (body + mono). 4-tier hierarchy:
1. Page title — `text-2xl` `font-semibold`
2. Section title — `text-base` `font-semibold`
3. Body / labels — `text-sm`
4. Helper — `text-xs` muted

## Components

Project's existing component hierarchy and usage patterns drive structure. Extract shared primitives where patterns repeat (Button, Card, Input, Badge, Skeleton, SectionLabel). Each consumes semantic tokens, never raw colors.

State catalog per component:
- Default / hover / focus / pressed / disabled / loading / error

## Motion

- framer-motion for layout animations and page transitions
- CSS `transition-*` for micro-interactions (hover, focus, color)
- Always honor `prefers-reduced-motion: reduce`
- Stagger and `layoutId` over isolated fades
- Duration scale: 100 / 200 / 350ms (fast / normal / slow)
- Easing: `cubic-bezier(0.4, 0, 0.2, 1)` standard, `(0, 0, 0.2, 1)` enter, `(0.4, 0, 1, 1)` exit

## Layout

CSS Grid for complex composition, Flexbox for alignment. Break the grid with overlap or z-index where intentional. Mobile-first breakpoints (sm 640 / md 1024 / lg 1280 / xl 1536), drawer collapse at sm.

## Accessibility

- WCAG AA contrast minimum in both modes
- Focus-visible rings on every interactive element
- Semantic HTML: `<button>` / `<nav>` / `<main>` / `<section>` (not `<div onClick>`)
- ARIA on custom interactive components (listbox, combobox, dialog)
- Touch targets ≥44×44px on touch breakpoints, ≥8px gap between adjacent

## Avoid AI aesthetic

<!-- merged from addyosmani/agent-skills frontend-ui-engineering -->

Generated UI has tells. Reject these defaults.

| AI default | Why it fails | Use instead |
|---|---|---|
| Purple/indigo everywhere | Every AI app looks the same | Project's actual palette |
| Excess gradients | Visual noise, clashes with system | Flat or subtle, system-driven |
| `rounded-2xl` on everything | Ignores radius hierarchy | Consistent radius from tokens |
| Generic hero sections | Template, not content | Content-first layout |
| Lorem ipsum | Hides wrap/overflow bugs | Realistic copy lengths |
| Equal oversized padding | No hierarchy, wasted space | Spacing scale |
| Stock card grids | Ignores info priority | Purpose-driven layout |
| Heavy stacked shadows | Competes with content | Subtle or none unless spec'd |

## WCAG 2.1 AA checklist

- Contrast 4.5:1 normal text, 3:1 large text — both light and dark
- Every interactive element keyboard reachable; visible focus ring
- `<button>` / `<a>` for actions; not `<div onClick>`
- All form inputs have `<label htmlFor>` or `aria-label`
- Icon-only buttons carry `aria-label`
- Don't convey state by color alone (add icon or text)
- Don't skip heading levels; one `<h1>` per page
- Manage focus on dialog open/close; trap focus inside modal
- `role="status"` on empty/loading regions; `aria-busy` on skeletons
- Touch targets ≥44×44px; ≥8px gap

## Operational Directives

**Reasoning chain before code:**
```
[Audit existing stack] → [Gap analysis] → [Aesthetic / spec reference]
→ [Approach] → [Design] → [Implement]
```

**Production-grade:** real imports, responsive classes, a11y attrs, semantic tokens. No placeholder styling.

**Scope to mode:**
- Single component, no spec → Vibe Mode
- Existing DESIGN.md, build/restyle → Apply Mode
- Existing DESIGN.md, check conformance → Audit Mode
- Authoring a spec → redirect to `/make-design-md`
