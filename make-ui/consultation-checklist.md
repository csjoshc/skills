# Consultation Mode — Full Checklist & Reference

## Contents

- Step-by-Step Process


Companion to `SKILL.md`. Read this when running Consultation Mode.

## Step-by-Step Process

### Step 1: Audit Current State

Explore the codebase for:
- CSS framework (Tailwind, CSS modules, styled-components, etc.)
- Component library (Shadcn, MUI, Chakra, custom, none)
- Component hierarchy — how components are organized, which are shared, which are page-specific
- Usage patterns — are buttons/cards/inputs copy-pasted or extracted? Is there a `ui/` directory?
- Fonts — what's loaded, what's declared, is it from Google Fonts or local?
- Color palette — custom tokens or raw Tailwind defaults? Consistent or drifting?
- Layout patterns — sidebar, grid, flex, responsive approach
- Animation — what library, how much, what quality?
- Design consistency — do all pages share the same visual language?

**Key question:** Does a design system already exist? If yes, the default approach is to extend/refine it. A full replacement requires explicit user approval at Step 6.

### Step 2: Offer Visual Companion

Offer to use Chrome DevTools for live style inspection, side-by-side comparison, and rapid prototyping during the consultation.

> "I can use Chrome DevTools to inspect the current UI, prototype style changes live, and compare before/after as we go. Want to try it?"

This must be its own message. If declined, proceed text-only.

### Step 3: Assess Against Quality Bar

Compare the current UI to these principles (from Anthropic's frontend-design skill):

| Principle | What to check |
|-----------|--------------|
| **Typography** | Distinctive font choices? Weight/size hierarchy? Or everything the same size? |
| **Color identity** | Intentional palette with semantic tokens? Or scattered raw Tailwind defaults? |
| **Motion** | Orchestrated animations? Or just `animate-pulse` on skeletons? |
| **Visual depth** | Gradients, shadows, layered transparencies? Or flat solid backgrounds? |
| **Spatial composition** | Intentional layout with rhythm? Or uniform grid with no variation? |
| **Design system** | Extracted shared components? Or copy-pasted class strings? |

Present the gaps as a structured assessment, not a wall of text.

### Step 4: Anchor With Product References

Every direction you propose MUST include 2-3 real products the user can look at.

| Direction | Example Products | Why They Work |
|-----------|-----------------|---------------|
| Refined dark tool | Linear, Raycast, Vercel Dashboard | Subtle gradients on dark surfaces, precise spacing, smooth transitions |
| Editorial / studio | Readymag, Framer, Stripe Docs | Strong type hierarchy, serif/sans pairings, generous whitespace |
| Industrial / DAW | Ableton Live, Blender, Bitwig | Extreme density, monospace, hard edges, status lights |
| Grafana-level polish | Grafana, n8n, Retool | Data-dense dark panels, good visual hierarchy, consistent tokens |
| Minimal polish | shadcn/ui, Radix Themes | Same stack, just consistent tokens and extracted components |

**Anchoring technique:** When the user doesn't know what direction to take, name the closest existing product to their current UI. "Your app currently looks most like Home Assistant / Grafana / etc." This gives them a reference point to move from.

### Step 5: Narrow Aesthetic Direction

Present options as multiple choice. Always include "keep current, just polish" as a valid choice. Include the product references from Step 4 in the option labels.

### Step 6: Scope the Pass

Options to present:

| Scope | What's included |
|-------|----------------|
| **Foundational only** | Design tokens, font loading, shared component extraction, color consistency |
| **Foundational + motion** | Above + page transitions, skeleton improvements, entrance animations |
| **Full visual pass** | Above + richer backgrounds, visual hierarchy, empty states, status polish |
| **Full migration** | Replace existing design system entirely. Requires explicit approval. |

### Step 7: Propose 2-3 Approaches

Each approach should cover:
- What changes (tech stack, dependencies, scope)
- Trade-offs (bundle size, migration effort, learning curve)
- Your recommendation and why

### Step 8: Present Design Section by Section

Get approval after each section before continuing.

**Token section** must include:
- CSS custom property definitions (light + dark values)
- Tailwind config extension code (or equivalent for the project's CSS approach)
- Semantic naming rationale
- Opacity modifier compatibility (if Tailwind)

**Typography section** must include:
- Font choices with Google Fonts URL
- Scale hierarchy (4 tiers minimum: page title, section title, body, helper)
- Monospace pairing for code/technical values
- How existing component hierarchy maps to the type scale

**Shared primitives section** must include:
- Which components to extract (based on audit of repeated patterns)
- Variant/size API for each
- How they map to the token system

**Depth & texture section** must include:
- Background treatment (gradient, texture, solid)
- Card/panel elevation tiers
- Section divider approach
- Shadow definitions

**Motion section** must include:
- What library (framer-motion, CSS-only, or hybrid)
- What to animate (page transitions, card stagger, loading states, status changes)
- What NOT to animate
- Reduced motion handling (`prefers-reduced-motion`)

**Cleanup scope section** must include:
- Files to migrate (count and list)
- Dead code to remove
- Consistency fixes (color drift, radius drift, etc.)

### Step 9: Final Design Summary

Recap every decision in one block. Get explicit "approved" before proceeding.

### Step 10: Output

Two options based on user preference:
- **Structured specs:** Generate spec-writer-format task files with SPEC/PLAN/TASKS sections, plus a PROGRESS.md tracker
- **Implementation plan:** Transition to writing-plans skill for a plan file
