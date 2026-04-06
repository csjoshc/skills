---
name: make-ui
description: Designs and implements high-variance frontend interfaces with either direct execution or consultation mode. Use when building or redesigning UI, choosing design direction, or when users request "make ui vibe", "make ui consult", "UI polish", or design-system help.
---

# Make UI — High-Variance Frontend Architect

**Anti-AI Slop.** If it looks like a bootstrapped template, it failed. Every project must feel uniquely crafted.

## Two Modes

### A. Vibe Mode

**Trigger:** "make ui vibe", immediate coding task, or end-to-end without consultation.

1. **Pre-flight:** Read `AGENTS.md`/`README`, scan `package.json` + CSS/config. Existing stack takes precedence — extend, don't replace.
2. **Pick aesthetic:** Match vertical to direction via `decision-matrix.md`. Existing component hierarchy and usage patterns drive theming.
3. **Execute** with production-grade code. Defaults in `technical-standards.md`.

### B. Consultation Mode

**Trigger:** "make ui consult", "help me design", or aesthetic decisions on existing codebase.

<HARD-GATE>
No code until user approves the final design summary.
</HARD-GATE>

Structured decision funnel. One question per message. Multiple choice preferred. Full process: `consultation-checklist.md`. Summary:

1. **Audit** current state — stack, component patterns, design system, consistency issues
2. **Offer** Chrome DevTools companion for live inspection
3. **Assess** against quality bar — gap analysis on typography, color, motion, depth, composition
4. **Anchor** with product references — name 2-3 real products per direction
5. **Narrow** aesthetic direction — "keep current, just polish" is always valid
6. **Scope** — foundational? +motion? full pass? full migration?
7. **Propose** 2-3 approaches with trade-offs
8. **Present** design section by section with approval gates (tokens, typography, primitives, depth, motion, cleanup)
9. **Final summary** — recap, get explicit approval
10. **Output** — spec-writer task files or implementation plan

## Companion Files

- `decision-matrix.md` — Vertical-to-aesthetic mapping with reference products, prohibited patterns
- `technical-standards.md` — Colors, typography, motion, layout, accessibility, responsive defaults
- `consultation-checklist.md` — Full step-by-step guide, reference tables, section presentation requirements
