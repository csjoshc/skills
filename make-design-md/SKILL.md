---
name: make-design-md
description: Authors a Stitch-format DESIGN.md plus preview-ui/ HTML swatches for any frontend project. Runs a three-phase workflow (audit → decide → emit) with an explicit approval gate before the spec is written. Use when starting a new project, defining a brand for an existing UI, or producing a portable design spec other agents can read.
---

# Make Design.md — Author a Portable Design Spec

Produces three artifacts at the target repo root:

```
<repo>/
├── DESIGN.md              # Stitch 9-section format
└── preview-ui/
    ├── preview.html       # light-mode swatch + component catalog
    ├── preview-dark.html  # dark-mode mirror
    └── README.md          # how to view / regenerate
```

DESIGN.md is what downstream agents read. `preview-ui/` is the human (and visual-AI) verification layer.

## Triggers

- "make design md", "/make-design-md", "author design spec", "create DESIGN.md"
- "design system spec for this project"
- User has a brand guide and wants it captured as a spec

## Out of Scope

- Building UI code from a DESIGN.md → use `/make-ui` Apply Mode
- Auditing existing code against a DESIGN.md → use `/make-ui` Audit Mode
- C3 brand specifically → already captured in `/c3-ui`'s `c3-design-system.md`

## Three-Phase Workflow

### Phase 1 — Audit (deterministic)

Use the fixed table in [audit-template.md](references/audit-template.md). Fill every row. No freestyle audit prose. Offer Chrome DevTools companion as its own message:

> "I can use Chrome DevTools to inspect the running UI and prototype changes live. Want to try it?"

If the codebase has no UI yet (greenfield), mark the audit table cells "N/A — greenfield" and proceed to Phase 2.

### Phase 2 — Decide (gated)

<HARD-GATE>
No DESIGN.md is written until the user explicitly approves the final summary.
</HARD-GATE>

Walk these steps in order. One question per message. Multiple choice preferred.

1. **Assess against quality bar** — typography distinctiveness, color identity, motion, depth, spatial composition, design system extraction. Present as table, not prose.
2. **Anchor with reference products** — name 2–3 real products per direction. If two references are named, briefly inspect them (fetch landing page, sample tokens) before proposing.
3. **Narrow direction** — present options including "keep current, just polish" and **hybrid combinations** (see [decision-matrix.md](references/decision-matrix.md)).
4. **Choose density axis** — compact / balanced / airy. Explicit.
5. **Scope** — foundational only / + motion / full visual / full migration.
6. **Propose 2–3 approaches** — trade-offs and recommendation.
7. **Present spec section by section** — get approval after each. Canonical Stitch order, with skill extensions inlined:
   - **§1 Overview** — atmosphere prose (mood / density / philosophy / references)
   - **§2 Colors** — front-matter `colors:` + `colors-dark:` extension, role table
   - **§3 Typography** — front-matter `typography:` (composite tokens), hierarchy table
   - **§4 Layout** — front-matter `spacing:` + `breakpoints:` extension, touch targets
   - **§5 Elevation & Depth** — front-matter `shadows:` + `motion:` extensions, choreography
   - **§6 Shapes** — front-matter `rounded:`, edge treatment
   - **§7 Components** — front-matter `components:` with `<name>-<state>` variants, state catalog
   - **§8 Do's and Don'ts** — table with rationale
   - **Iconography** (extension section) — front-matter `icons:` + alignment rules
   - **Agent Prompt Guide** (extension section) — quick token ref, CSS bridge, prompts
8. **Final summary** — recap every decision in one block. Get explicit "approved".

**Brand-ingest path:** if the user has a brand guide (color spec, logo lockup, font specimen), skip steps 2–4 (direction selection) and extract directly. See [brand-ingest.md](references/brand-ingest.md).

### Phase 3 — Emit

After approval:

1. Write `DESIGN.md` at repo root using the [stitch-format.md](references/stitch-format.md) template. Output MUST begin with a YAML front matter block (`---` … `---`) carrying canonical Stitch tokens (`version`, `name`, `colors`, `typography`, `rounded`, `spacing`, `components`) plus skill extensions (`colors-dark`, `motion`, `shadows`, `shadows-dark`, `breakpoints`, `icons`). Body uses canonical 8 sections in fixed order, plus `## Iconography` and `## Agent Prompt Guide` extension sections appended after `## Do's and Don'ts`.
2. Generate `preview-ui/preview.html` and `preview-ui/preview-dark.html` from [preview-template.html](references/preview-template.html), substituting tokens.
3. Write `preview-ui/README.md` with verification instructions.
4. Run `/stop-slop` on the prose sections of DESIGN.md (Overview, Do's/Don'ts rationale).

**Token sourcing rule:** when a project already has separate light/dark token files (e.g. `tokens.light.css` + `tokens.dark.css`, or C3's `c3SemanticTokensLight.css` + `c3SemanticTokensDark.css`), read **both** before emitting front matter. Never derive dark values from light values — read each side directly. The light-file values populate canonical `colors:`; the dark-file values populate the `colors-dark:` extension key. After emit, cross-check every key in `colors-dark:` has a counterpart in `colors:` and vice versa.

## Companion Files

- [stitch-format.md](references/stitch-format.md) — 9-section template + per-section authoring rules
- [audit-template.md](references/audit-template.md) — fixed Phase 1 audit table
- [decision-matrix.md](references/decision-matrix.md) — vertical→aesthetic + hybrid combinations + density axis
- [preview-template.html](references/preview-template.html) — preview-ui boilerplate
- [brand-ingest.md](references/brand-ingest.md) — alternate path when a brand guide exists
- [examples/c3-as-design-md.md](examples/c3-as-design-md.md) — worked example mapping `c3-design-system.md` to Stitch 9

## Hard Constraints

- DESIGN.md goes at repo root (matches [Stitch convention](https://stitch.withgoogle.com/docs/design-md/specification/) and `AGENTS.md` placement).
- DESIGN.md MUST begin with a YAML front matter block (`---` … `---`) carrying canonical Stitch token groups. Stitch's CLI validator rejects files without it.
- Body sections follow canonical Stitch order: Overview → Colors → Typography → Layout → Elevation & Depth → Shapes → Components → Do's and Don'ts. Never duplicate a `##` heading (Stitch errors on duplicates).
- Skill extensions (Iconography, Agent Prompt Guide) are appended as additional `##` sections **after** Do's and Don'ts. Both are required by this skill.
- Preview HTML files go in `preview-ui/` — never `preview/` (collides with framework dev servers).
- **Skill opinion (not Stitch):** every `colors:` token has a `colors-dark:` counterpart in front matter. Source from the dark token file directly; never derive by inversion.
- Component variants use Stitch's `<name>-<state>` keyed-entry model in front matter (e.g., `button-primary` / `button-primary-hover`). Do not collapse states into a single entry.
- Do not write DESIGN.md before the user approves the final Phase 2 summary.
