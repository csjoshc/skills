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

Search the project for these inputs. Ask for a missing asset only when it blocks a requested brand-faithful result.

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

### Step 3 — Fill gaps from project evidence

Use existing project patterns for unspecified values. For genuinely missing design decisions, choose a restrained default that fits the brand and note it in the spec:

- **Dark-mode pairs** — read the project's dark tokens if available. If none exist, add dark values only when the product supports dark mode; derive them deliberately and document the choice.
- **State colors** — follow the existing semantic palette or choose accessible status colors consistent with the brand.
- **Spacing scale** — reuse the existing scale or infer a small consistent scale from current layouts.
- **Motion grammar** — follow existing motion conventions and honor reduced-motion preferences.
- **State catalog** — include only states relevant to the product and components.

### Step 4 — Emit

Use the brand evidence directly and follow [design-spec.md](design-spec.md). Keep uncertain assignments explicit in the spec; pause only if the unresolved choice would materially misrepresent the brand.

## Anti-patterns

- Don't invent colors not in the brand. If the brand only has 3 colors, the spec uses 3 + neutrals.
- Don't override approved fonts with "better-looking" defaults.
- Don't skip dark-mode pairing because the brand is light-only — generate them and flag them as derived for the user to confirm.
