# Brand-Ingest Path

Use when the user has existing brand assets (color spec, logo, fonts, marketing guide) instead of picking from the decision matrix.

## When to use

Phase 1 audit Table 8 has any of:
- Brand guide (PDF, Figma file, internal wiki)
- Approved color palette
- Licensed/approved font families
- Logo files

## Process

### Step 1 — Inventory the brand inputs

Ask the user to provide or point at:
- Color spec (hex values + names + usage rules if available)
- Font files or Google Fonts names
- Logo files (light + dark variants ideally)
- Tone/voice doc (if relevant for §1 atmosphere)

### Step 2 — Map brand → DESIGN.md targets

Brand inputs populate front-matter token groups first, then prose sections:

| Brand input | Front-matter target | Body section |
|---|---|---|
| Color palette | `colors:` (+ `colors-dark:` extension if dark variant supplied) | §2 Colors (role table) |
| Fonts | `typography:` (composite tokens per tier) | §3 Typography (hierarchy) |
| Logo | `icons:` (extension; logo lockup as component entry) | Iconography (extension section) |
| Tone doc | — | §1 Overview (atmosphere prose) |
| Spacing / grid (rare) | `spacing:` | §4 Layout |
| Corner radii / shape language | `rounded:` | §6 Shapes |

### Step 3 — Fill gaps from defaults

Brand guides usually under-specify. Things to fill from defaults:

- **Dark-mode pairs** — most brand guides are light-only. Generate dark counterparts (rule of thumb: invert lightness, preserve hue, slightly desaturate).
- **State colors** — if no success/warning/danger in the brand, use semantic neutrals (`#16A34A` / `#D97706` / `#DC2626`) and tune toward brand hue if needed.
- **Spacing scale** — almost never in brand guides. Use the standard 8-step scale (0/4/8/12/16/24/32/48/64).
- **Motion grammar** — almost never specified. Use defaults from `stitch-format.md` §5 (Elevation & Depth).
- **State catalog** — empty/loading/error/success patterns. Use defaults.

### Step 4 — Confirm assigned roles

Before emitting DESIGN.md, present the role assignments back to the user:

> "Your brand has 5 colors. I'm assigning #2563EB → bg-accent (primary actions), #DC2626 → bg-danger, #16A34A → bg-success, #F59E0B → bg-warning, #525252 → text-secondary. Sound right?"

Approval gate — if user disagrees, reassign before emitting.

### Step 5 — Skip Phase 2 steps 2–4

Brand-ingest replaces aesthetic direction selection. Still run:
- Phase 2 §1 atmosphere prose (extracted from brand voice doc if any)
- Phase 2 §5 scope decision (foundational / + motion / full)
- Phase 2 §7 section-by-section presentation with approval gates

Then proceed to Phase 3 emit.

## Anti-patterns

- Don't invent colors not in the brand. If the brand only has 3 colors, the spec uses 3 + neutrals.
- Don't override approved fonts with "better-looking" defaults.
- Don't skip dark-mode pairing because the brand is light-only — generate them and flag them as derived for the user to confirm.
