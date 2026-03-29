# Technical Standards

Adapt to the project's CSS approach. Defaults below assume Tailwind 3.x with `darkMode: "class"`.

## Colors
CSS custom properties with semantic names. In Tailwind, reference via `rgb(var(--name) / <alpha-value>)` for opacity support. Define `:root` (light) and `.dark` (dark) sets.

## Typography
Google Fonts import with `display=swap`. Minimum 2 fonts (body + mono). 4-tier hierarchy:
1. Page title: `text-base font-semibold`
2. Section title: `text-sm font-semibold`
3. Body/labels: `text-xs`
4. Helper text: `text-xs` with muted color

## Components
The project's existing component hierarchy and usage patterns drive theming. Extract shared primitives where patterns repeat (Button, Card, Input, Badge, Skeleton, SectionLabel). Each uses semantic tokens, not raw colors.

## Motion
- framer-motion for layout animations and page transitions
- CSS `transition-*` for micro-interactions (hover, focus, color changes)
- Always handle `prefers-reduced-motion`
- Prefer stagger and layout animations over simple fades

## Layout
CSS Grid for complex layouts, Flexbox for alignment. Break the grid with overlap or z-index layering where appropriate.

## Accessibility
- Sufficient color contrast in both modes (WCAG AA minimum)
- Focus-visible rings on all interactive elements
- Semantic HTML (`<button>`, `<nav>`, `<main>`, `<section>`)
- ARIA attributes on custom interactive components

## Responsive
Mobile-first breakpoints. Sidebar collapses to drawer. Dense layouts stack on small screens. Touch targets minimum 44px on mobile.

## Operational Directives

**Deep Reasoning Chain:** Before generating code: `[Audit existing stack] -> [Gap Analysis] -> [Aesthetic Direction] -> [Approach] -> [Design]`

**Production-Grade:** Proper imports, responsive classes, accessibility attributes, semantic token usage. No placeholder styling.

**Scale to Scope:** Single component = Vibe Mode. Full-app redesign = Consultation Mode. Full-app end-to-end = Vibe Mode. Match process to task and user preference.
