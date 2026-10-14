---
name: make-mmd
description: "Authors Mermaid diagrams and renders them to SVG that reads in light and dark mode. Use when creating or updating .mmd files or diagram SVGs."
---

# make-mmd — Mermaid Authoring + Rendering

Produces `.mmd` sources and renders them to `.svg` with the shared color
convention. Decouples "how the diagram looks" (this skill) from "where it ends
up" (consumer skills: `confluence-diagrams`, README embedding, etc.).

## Prerequisites

`@mermaid-js/mermaid-cli` installed globally:

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc --version   # 10+ required
```

## When to use which rendering path

| Target | Approach |
|--------|----------|
| GitHub README / wiki, GitLab, most markdown viewers | Embed mermaid source in ` ```mermaid ` fenced block. Remove hardcoded `%%{init}%%` blocks to let GitHub's auto-theming adapt to user's light/dark mode. Use `rgba()` rect colors for mode-agnostic highlights. |
| Confluence, PDF, email, any static/image consumer | Render to SVG via `mmdc`. Produce a light + dark variant; pick at embed time. |

These two paths share one `.mmd` source. The difference is at render time.

## GitHub inline mermaid (markdown viewers)

For any diagram embedded in markdown (GitHub wikis, README files, etc.):

**DO:**
- Remove `%%{init}%%` blocks entirely; let GitHub's renderer auto-theme to the user's preference
- Use `rgba(R, G, B, 0.25)` for rect highlights and other fills; these blend with the host background
- Omit actor/text color overrides; GitHub handles contrast automatically

**DON'T:**
- Include `%%{init}%%` with hardcoded colors; it locks the diagram to light mode even in dark mode
- Use solid `rgb()` colors; they don't adapt to theme changes
- Embed `%%{init}%%` with hardcoded actor/text colors in diagrams meant for GitHub markdown. Set a theme only when rendering to static SVG with a known target.

Example and recipes: [AUTHORING.md](AUTHORING.md).

## Authoring Rules

### Parser safety

- **No `{}`** or HTML entities in labels — mermaid's parser trips on them.
- **Use `<br/>`** for line breaks in labels (not `\n`).
- **Avoid `classDef`** in `sequenceDiagram` and `stateDiagram-v2` — it only
  works in flowcharts.
- **Edge `linkStyle N`** is index-based and breaks when you reorder edges.
  Prefer solid-vs-dashed arrows and descriptive labels.

### Semantic colors (the palette)

Mermaid diagrams use color to encode meaning, not decoration. Same palette
across flowchart `classDef` and sequence `rect`.

| Semantic | Role | Light hex | Dark hex | Mode-agnostic rgba() |
|----------|------|-----------|----------|-----------------------|
| `person` | User, browser, human actor | `#E8EAED` | `#374151` | `rgba(156,163,175,0.25)` |
| `service` | App, API, deployed service (sync call) | `#4285F4` | `#3B82F6` | `rgba(59,130,246,0.25)` |
| `library` | In-process library or module | `#4FC3F7` | `#38BDF8` | `rgba(56,189,248,0.25)` |
| `guard` | Security boundary, guardrail, policy (caution) | `#F9AB00` | `#F59E0B` | `rgba(245,158,11,0.25)` |
| `external` | External system outside your control | `#9AA0A6` | `#6B7280` | `rgba(107,114,128,0.25)` |
| `state` | State, data store, token, config (data/mutation) | `#A142F4` | `#A855F7` | `rgba(168,85,247,0.25)` |
| `errBlock` | Error state, blocked path | `#EA4335` | `#EF4444` | `rgba(239,68,68,0.25)` |
| `passNode` | Success outcome, data-in-motion | `#34A853` | `#22C55E` | `rgba(34,197,94,0.25)` |
| `auditNode` | Audit / logging / side-effect | `#9AA0A6` | `#6B7280` | `rgba(107,114,128,0.2)` |

Sequence `rect rgba(...)`, flowchart `classDef` and edge-style recipes: [AUTHORING.md](AUTHORING.md). Add a Legend subgraph when a flowchart uses more than 5 node classes ([example-conventions.mmd](example-conventions.mmd)).

## Rendering

### Default (GitHub wiki / README inline mermaid)

No render step needed — commit the `.mmd` source inside a ` ```mermaid `
fenced block. GitHub renders it with the user's theme (light/dark).

### Rendering to SVG (static consumers)

Render both modes from one source:

```bash
~/.skills/make-mmd/scripts/render.sh diagram.mmd
# produces: diagram.light.svg + diagram.dark.svg
```

The script wraps `mmdc` with the palette config files and emits both variants.
Consumers pick: for a Confluence light-theme page use `diagram.light.svg`;
for a dark-themed consumer use `diagram.dark.svg`; for ambient/auto use a
`<picture>` wrapper:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="diagram.dark.svg">
  <img src="diagram.light.svg" alt="...">
</picture>
```

### Manual render (single mode)

```bash
mmdc -i diagram.mmd -o diagram.svg \
  -c ~/.skills/make-mmd/palettes/light.json \
  -b transparent
```

Swap `light.json` → `dark.json` for the dark variant. `-b transparent` keeps
the SVG background neutral so it picks up the host's page background.

## Files in this skill

| File | Purpose |
|------|---------|
| [AUTHORING.md](AUTHORING.md) | Read when writing a diagram: GitHub inline example, sequence `rect rgba()`, flowchart `classDef`, edge styles |
| [LAYOUT_RULES.md](LAYOUT_RULES.md) | Read for complex flowcharts headed to a Confluence whiteboard or any dynamic connector router |
| [palettes/light.json](palettes/light.json) | `mmdc -c` config, light-mode theme variables |
| [palettes/dark.json](palettes/dark.json) | `mmdc -c` config, dark-mode theme variables |
| [scripts/render.sh](scripts/render.sh) | Render a `.mmd` to both light and dark SVGs |
| [example-conventions.mmd](example-conventions.mmd) | Flowchart showing the full palette and legend |
| [example-sequence.mmd](example-sequence.mmd) | Sequence diagram using `rect rgba()` |

## Relation to other skills

- **`confluence-diagrams`** — consumer. Use this skill to render `.mmd` →
  `.svg`; then use `confluence-diagrams` to upload + embed in Confluence.
- **`reframe`** — producer. When reframe generates diagrams, it writes
  `.mmd` that follow this skill's conventions.
- **`brief-docs`** — producer. Diagrams in brief docs should follow these
  conventions for consistency.

## Verification

Before committing diagrams:

- [ ] Each semantic color matches the palette table (Semantic colors).
- [ ] Sequence rects use `rgba(...)` not solid `rgb(...)` — otherwise dark
      mode viewers see the same fill as light mode.
- [ ] No hardcoded `%%{init}%%` in files destined for GitHub markdown.
- [ ] Flowcharts with >5 node classes include a Legend subgraph.
- [ ] Render both modes and eyeball: `./scripts/render.sh diagram.mmd &&
      open diagram.{light,dark}.svg`.
