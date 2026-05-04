# DESIGN.md Format — Canonical Stitch + Skill Extensions

Source of truth: [Google Stitch DESIGN.md specification](https://stitch.withgoogle.com/docs/design-md/specification/) and [overview](https://stitch.withgoogle.com/docs/design-md/overview/).

A DESIGN.md has two layers:

1. **YAML front matter** — machine-readable design tokens (the **normative** values agents enforce).
2. **Markdown body** — human-readable rationale organized into `##` sections.

This skill emits **canonical Stitch** at the core, plus opinionated **extensions** layered as additional front-matter keys and inline subsections. Stitch consumers preserve unknown sections and accept unknown token keys, so the extensions are safe — a Stitch CLI/agent reading our output gets a valid DESIGN.md; a skill-aware agent gets the full opinionated spec.

> **The spec is a foundation, not a prescription.** Sections are optional but, when present, must follow the canonical order.

---

## Front Matter (required)

The file MUST begin with a YAML front matter block delimited by `---` lines. Schema below.

### Canonical schema

```yaml
---
version: alpha
name: <project name>
description: <one-line tagline>          # optional

colors:                                  # map<token-name, Color>
  primary:    "#1A1C1E"
  secondary:  "#6C7278"
  accent:     "#2563EB"
  surface:    "#FFFFFF"
  on-surface: "#0A0A0A"
  on-accent:  "#FFFFFF"
  border:     "#E5E5E5"
  error:      "#DC2626"
  success:    "#16A34A"
  warning:    "#D97706"

typography:                              # map<token-name, Typography>
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.4
  code:
    fontFamily: "JetBrains Mono"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5

rounded:                                 # map<scale-level, Dimension>
  none: 0
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px

spacing:                                 # map<scale-level, Dimension|number>
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px

components:                              # map<component-name, map<prop, value|tokenref>>
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-accent}"
    rounded: "{rounded.md}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 12px
---
```

### Token types (Stitch)

| Type | Format | Example |
|---|---|---|
| Color | `#` + sRGB hex | `"#1A1C1E"` |
| Dimension | number + unit (`px`, `em`, `rem`) | `48px`, `-0.02em` |
| Token reference | `{path.to.token}` (curly-braced object path) | `{colors.primary}` |
| Typography | composite object — see properties below | (see schema) |

Typography composite properties: `fontFamily`, `fontSize`, `fontWeight`, `lineHeight` (Dimension or unitless number; unitless recommended), `letterSpacing`, `fontFeature` (optional), `fontVariation` (optional).

Component property tokens (canonical): `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Unknown properties are accepted with warning.

Component variants: emit as separate keyed entries with a related name — `button-primary` / `button-primary-hover`. **Do not** model variants as a single entry with state columns.

### Extension keys (skill-specific, beyond Stitch)

These keys are **not** part of the canonical Stitch schema. Stitch consumers accept unknown keys; skill-aware tools read them.

```yaml
colors-dark:                             # dark-mode parallel to `colors:` (extension)
  primary:    "#F5F5F5"
  secondary:  "#A3A3A3"
  accent:     "#3B82F6"
  surface:    "#0A0A0A"
  on-surface: "#F5F5F5"
  border:     "#262626"

motion:                                  # extension — not in Stitch canonical
  duration:
    fast: 100ms
    normal: 200ms
    slow: 350ms
  easing:
    standard: "cubic-bezier(0.4, 0, 0.2, 1)"
    out:      "cubic-bezier(0, 0, 0.2, 1)"
    in:       "cubic-bezier(0.4, 0, 1, 1)"

shadows:                                 # extension — referenced by §Elevation prose
  card:  "0 1px 2px rgba(0,0,0,0.04)"
  menu:  "0 4px 12px rgba(0,0,0,0.08)"
  modal: "0 16px 48px rgba(0,0,0,0.16)"

shadows-dark:                            # extension — dark-mode shadows
  card:  "0 1px 2px rgba(0,0,0,0.4)"
  menu:  "0 4px 12px rgba(0,0,0,0.5)"
  modal: "0 16px 48px rgba(0,0,0,0.6)"

breakpoints:                             # extension — Stitch §Layout prose-only
  sm: 640px
  md: 1024px
  lg: 1440px

icons:                                   # extension — Stitch has no canonical icon schema
  set: lucide-react
  sizes: [16, 20, 24]
  weight: regular
```

**Pairing rule (skill opinion):** every `colors:` token has exactly one `colors-dark:` counterpart. Do not derive dark from light by inversion — pick deliberately and source from the dark token file directly.

---

## Body sections

All sections use `##` headings. **Canonical order is fixed**; sections are optional but must appear in this sequence when present. Two extension sections (Iconography, Agent Prompt Guide) are appended after the canonical 8.

| # | Heading | Aliases | Required by skill |
|---|---|---|---|
| 1 | Overview | "Brand & Style" | yes (atmosphere prose lives here) |
| 2 | Colors | — | yes |
| 3 | Typography | — | yes |
| 4 | Layout | "Layout & Spacing" | yes |
| 5 | Elevation & Depth | "Elevation" | yes |
| 6 | Shapes | — | yes |
| 7 | Components | — | yes |
| 8 | Do's and Don'ts | — | yes |
| — | Iconography | (extension) | yes (skill mandates) |
| — | Agent Prompt Guide | (extension) | yes (skill mandates) |

An optional `# <Title>` heading may appear at the top of the body for document titling; it is not parsed as a section.

---

### §1 Overview

Holistic description of look and feel. Defines brand personality, target audience, and the emotional response the UI should evoke. Canonical Stitch uses this section to provide foundational context when a specific rule or token is undefined.

**Skill extension — Atmosphere prose:** include one paragraph (3–6 sentences) covering:

- **Mood** — adjectives ("industrial / calm / editorial / cinematic")
- **Density** — explicit choice: compact / balanced / airy
- **Philosophy** — what this UI prioritizes ("speed over decoration", "trust over delight")
- **Cultural references** — 1–2 anchor products ("Linear-tight with Vercel-monochrome restraint")

Example:

> Industrial calm. Density: compact. The interface prioritizes information throughput over delight — every pixel earns its place. Visual references: Linear's tight typography and Grafana's panel discipline. No gradients, no decorative illustration, no whimsy.

---

### §2 Colors

Defines color palettes. Canonical: at least the primary palette; common convention is `primary`, `secondary`, `tertiary`, `neutral`. Tokens live in front matter; this prose section names roles and explains usage.

```markdown
- **Primary** (#1A1C1E): Deep ink for headlines and core text.
- **Accent** (#2563EB): Single driver for primary actions.
- **Surface** (#FFFFFF): Page and card backgrounds.
- **Border** (#E5E5E5): Default dividers.
```

**Skill extension — light/dark dual-hex table.** When the project supports both modes (`colors-dark:` is present), emit a dual-mode reference table after the role list:

| Token | Role | Light | Dark | On-color |
|---|---|---|---|---|
| `primary` | Default body | `#1A1C1E` | `#F5F5F5` | — |
| `accent` | Primary action | `#2563EB` | `#3B82F6` | `on-accent` |
| `surface` | Page / card bg | `#FFFFFF` | `#0A0A0A` | `primary` |
| `border` | Default divider | `#E5E5E5` | `#262626` | — |
| `error` | Destructive | `#DC2626` | `#EF4444` | `#FFFFFF` |

State variants for interactive tokens (`-hover`, `-pressed`, `-disabled`, focus-ring) are encoded as additional entries (`accent-hover`, `accent-pressed`) in the front matter, not as separate columns.

---

### §3 Typography

Most design systems define 9–15 typography tokens, each with a semantic role (headline / body / label) and a size variant (sm / md / lg). Tokens live in front matter; this prose section explains hierarchy and use.

```markdown
- **Headlines:** Inter Semi-Bold for institutional voice.
- **Body:** Inter Regular at 14px for long-form readability.
- **Labels:** Inter Medium at 12px for metadata.
- **Code:** JetBrains Mono at 13px for inline and block code.
```

**Skill extension — hierarchy table.** Map tokens to UI use cases:

| Token | Use | Family | Size | Weight | Line-height | Tracking |
|---|---|---|---|---|---|---|
| `headline-lg` | Top of page | Inter | 24px | 600 | 1.2 | -0.01em |
| `body-md` | Default text | Inter | 14px | 400 | 1.5 | 0 |
| `label-sm` | Captions, metadata | Inter | 12px | 500 | 1.4 | 0 |
| `code` | Inline / block code | JetBrains Mono | 13px | 400 | 1.5 | 0 |

---

### §4 Layout

Layout and spacing strategy — grid model, spacing scale, containment. Spacing tokens live in front matter under `spacing:`.

```markdown
A 12-column grid at lg, 4-column at sm, with a 16px gutter (`spacing.md`).
Mobile uses a single column with drawer nav. Desktop max content width: 1280px, centered.
```

**Skill extension — breakpoints + touch targets.** Breakpoint values live in the front-matter `breakpoints:` extension; this subsection documents behavior:

| Breakpoint | Width | Behavior |
|---|---|---|
| sm | 0–640px | Single column, drawer nav, touch ≥44px |
| md | 640–1024px | 2-column grids, sidebar collapsible |
| lg | 1024–1440px | Full sidebar, 3-column grids |
| xl | 1440px+ | Max content 1280px, centered |

**Touch targets:** minimum 44×44px on touch devices; adjacent targets ≥8px apart.

---

### §5 Elevation & Depth

How visual hierarchy is conveyed. For shadow-based designs, defines the shadow scale (front-matter `shadows:` / `shadows-dark:`). For flat designs, document the alternative (borders, tonal layers, contrast).

```markdown
Depth via tonal layers and a 3-step shadow scale. Surface hierarchy back-to-front:
page → surface → card → menu → modal → toast.
```

**Skill extension — shadow scale table:**

| Token | Use | Light value | Dark value |
|---|---|---|---|
| `shadows.card` | Resting card | `0 1px 2px rgba(0,0,0,0.04)` | `0 1px 2px rgba(0,0,0,0.4)` |
| `shadows.menu` | Dropdown | `0 4px 12px rgba(0,0,0,0.08)` | `0 4px 12px rgba(0,0,0,0.5)` |
| `shadows.modal` | Dialog | `0 16px 48px rgba(0,0,0,0.16)` | `0 16px 48px rgba(0,0,0,0.6)` |

**Skill extension — motion grammar.** Tokens live in front-matter `motion:`. This subsection documents choreography:

| Duration | Token | Use |
|---|---|---|
| 100ms | `motion.duration.fast` | Hover/focus state changes |
| 200ms | `motion.duration.normal` | Component enter/exit |
| 350ms | `motion.duration.slow` | Page transitions |

| Easing | Token | Use |
|---|---|---|
| `cubic-bezier(0.4, 0, 0.2, 1)` | `motion.easing.standard` | Default |
| `cubic-bezier(0, 0, 0.2, 1)` | `motion.easing.out` | Enter |
| `cubic-bezier(0.4, 0, 1, 1)` | `motion.easing.in` | Exit |

Choreography rules:
- Lists stagger at 30ms intervals.
- Page transitions use `layoutId` (framer-motion) for shared elements.
- Honor `prefers-reduced-motion: reduce` — disable non-essential animation.

---

### §6 Shapes

Corner radii, edge treatment, and overall shape language. Tokens live in front-matter `rounded:`.

```markdown
Minimal 4–8px radii — modern enough to feel current, rigid enough to feel engineered.
No mixed sharp/rounded corners in a single view.
```

| Token | Value | Use |
|---|---|---|
| `rounded.none` | 0 | Buttons, inputs, cards in industrial themes |
| `rounded.sm` | 4px | Buttons, inputs |
| `rounded.md` | 8px | Cards, modals |
| `rounded.lg` | 12px | Hero cards |
| `rounded.full` | 9999px | Pills, avatars |

---

### §7 Components

Style guidance for component atoms. Stitch lists Buttons, Chips, Lists, Inputs, Checkboxes, Radio buttons, Tooltips as common types — design systems may add domain-specific components freely.

Tokens live in front-matter `components:`. This prose section explains usage.

```markdown
- **Buttons:** primary fills with `colors.accent`, secondary outlines with `colors.border`, danger fills with `colors.error`. All radius `rounded.sm`.
- **Inputs:** 1px `colors.border`, surface bg, padding `spacing.md`. Focus: `colors.accent` border + 2px ring.
- **Cards:** `colors.surface` + 1px `colors.border` + `rounded.md` + `shadows.card`.
- **Dropdowns:** custom listbox or Radix. **Never `<select>`** — OS popup ignores dark mode.
```

**Variants** are encoded as separate front-matter entries with related names: `button-primary`, `button-primary-hover`, `button-primary-disabled`. Do not collapse states into a single entry.

**Skill extension — state catalog (required).** Every component spec must cover:

| State | Treatment |
|---|---|
| Empty | Centered icon (40px) + headline (`headline-lg`) + helper + optional CTA |
| Loading | Skeleton blocks at content rhythm; pulse `animate-pulse 1.5s` |
| Error | `colors.error-weak` panel + danger icon + message + retry button |
| Success | Toast top-right, `colors.success` + check icon, auto-dismiss 4s |
| Skeleton | `colors.surface` rounded blocks at content rhythm |

---

### §8 Do's and Don'ts

Practical guardrails. Format as a table with rationale.

| Don't | Do | Why |
|---|---|---|
| `rounded-xl` on cards | `rounded.md` (`8px`) | Consumer/SaaS cliché |
| Generic gradient bg (purple→blue) | Solid `colors.surface` | Reads as AI-template |
| `<select>` for dropdowns | Custom listbox or Radix | OS popup ignores dark mode |
| Hardcoded hex in components | Token references only | Drift |
| `font-semibold` on buttons | Default weight | Visual noise |
| Slate-blue dark mode (`#0F172A`) | Neutral grays per `colors-dark:` | Reads as default Tailwind |

---

### Iconography (extension)

Stitch has no canonical icon schema; tokens live in front-matter `icons:`.

- **Set:** specify one — lucide-react / phosphor / heroicons / Font Awesome / custom.
- **Sizes:** 16 / 20 / 24 px. Use one per context (nav = 20, body = 16).
- **Weight:** match adjacent typography weight where possible.
- **Optical alignment:** icons sit on the same baseline as adjacent text; nudge ±1px if visually off.
- **Illustration style:** specify — none / line / flat / gradient / 3D.
- **Photography:** specify — full-bleed / framed / none. Aspect ratio convention.

---

### Agent Prompt Guide (extension)

Required by this skill. Without it, downstream agents drift.

#### Quick token reference

```
Surface: colors.surface (#FFFFFF / #0A0A0A)
Accent:  colors.accent  (#2563EB / #3B82F6)
Text:    colors.primary (#1A1C1E / #F5F5F5)
Border:  colors.border  (#E5E5E5 / #262626)
```

#### Copy-paste CSS bridge (light + dark)

```css
:root {
  --color-surface: #FFFFFF;
  --color-accent:  #2563EB;
  --color-primary: #1A1C1E;
  --color-border:  #E5E5E5;
  /* ... full token list ... */
}
.dark {
  --color-surface: #0A0A0A;
  --color-accent:  #3B82F6;
  --color-primary: #F5F5F5;
  --color-border:  #262626;
}
```

#### Ready-to-use prompts

> "Build a login screen following DESIGN.md. Use `button-primary` from `components:` with email/password inputs, centered on `colors.surface`. Card uses `rounded.md` and `shadows.card`."

> "Build a settings page following DESIGN.md. Use `headline-lg` from `typography:`, two-column grid at `lg` breakpoint, and the Empty state pattern from §7 when no settings exist."

> "Restyle this component to conform to DESIGN.md. Replace hardcoded colors with token references from `colors:`, remove `rounded-xl` per §8, and verify against `preview-ui/preview.html`."

---

## Stitch consumer-behavior rules

Memorize these — they explain why our extensions are safe.

| Scenario | Stitch behavior |
|---|---|
| Unknown section heading (e.g., `## Iconography`) | Preserve; do not error |
| Unknown color token name | Accept if value is a valid `Color` |
| Unknown typography token name | Accept |
| Unknown spacing value | Accept; store as string if not a valid `Dimension` |
| Unknown component property | Accept with warning |
| Duplicate `##` heading | **Error; reject the file** |

Implication: never emit two `## Colors` headings. All extensions must use unique heading names.
