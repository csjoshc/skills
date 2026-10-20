---
name: diagram
description: "Authors Mermaid diagrams and renders them with Pele to SVG or PNG in named themes (light, dark, paper, cappuccino). Use when creating or updating .mmd files or diagram SVG/PNG files."
---

# diagram — Mermaid Authoring + Rendering

Produces `.mmd` sources and renders them with Pele (MIT, no runtime dependencies,
no headless browser) into SVG or PNG. Decouples "how the diagram looks" (this skill)
from "where it ends up" (consumer skills: `confluence`, README embedding, etc.).

## Prerequisites

```bash
cd ~/.skills/diagram && npm install     # pins pele 1.7.0 in node_modules/
brew install librsvg                    # rsvg-convert, needed only for PNG
```

Run the renderer with Node 18+:

```bash
node ~/.skills/diagram/scripts/render.mjs diagram.mmd --for obsidian
```

## Choosing the output

| Destination | Flags | Output | Why |
|-------------|-------|--------|-----|
| iTerm2 (dark terminal, `imgcat`) | `--for iterm` | `diagram.cappuccino.png` | iTerm2 shows PNG inline, not SVG. Dark espresso theme. |
| Obsidian note (light vault) | `--for obsidian` | `diagram.paper.svg` | Obsidian embeds SVG as an image. Warm paper theme. |
| Confluence, email, any other static consumer | (no flags) | `diagram.light.svg` + `diagram.dark.svg` | Portable SVG; pick the variant at embed time. |
| One specific theme | `--theme NAME [--format svg\|png]` | `diagram.NAME.FORMAT` | Any theme in `palettes/`; `--out PATH` names the file. |

Themes: `light`, `dark` (general), `paper` (Obsidian light), `cappuccino` (iTerm2 dark).
Each theme is one JSON file in `palettes/`; add a theme by adding a file.

The renderer writes every file next to the source. `--zoom N` scales PNG
output (default 2, for retina terminals).

## When to use which source form

| Target | Approach |
|--------|----------|
| GitHub README / wiki, GitLab, most markdown viewers | Embed mermaid source in ` ```mermaid ` fenced block. Remove hardcoded `%%{init}%%` blocks to let GitHub's auto-theming adapt to user's light/dark mode. Use `rgba()` rect colors for mode-agnostic highlights. |
| Obsidian, iTerm2, Confluence, PDF, email, any static/image consumer | Render with `render.mjs` (table above). One `.mmd` source; the output format and theme come from the flags. |

## GitHub inline mermaid (markdown viewers)

For any diagram embedded in markdown (GitHub wikis, README files, etc.):

**DO:**
- Remove `%%{init}%%` blocks entirely; let GitHub's renderer auto-theme to the user's preference
- Use `rgba(R, G, B, 0.25)` for rect highlights and other fills; these blend with the host background
- Omit actor/text color overrides; GitHub handles contrast automatically

**DON'T:**
- Include `%%{init}%%` with hardcoded colors; it locks the diagram to light mode even in dark mode
- Use solid `rgb()` colors; they don't adapt to theme changes
- Embed `%%{init}%%` with hardcoded actor/text colors in diagrams meant for GitHub markdown

Pele ignores `%%{init}%%` theme variables, so the render theme always wins. Remove
them from sources anyway; they only matter for GitHub and mmdc-era files.

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

Pele renders `rect` fills literally, so an opaque `rect rgb(...)` pastel stays pastel in
every theme and its text becomes unreadable on dark themes. Always write
`rect rgba(...)` at 0.25 alpha.

## Rendering

### Default (GitHub wiki / README inline mermaid)

No render step needed — commit the `.mmd` source inside a ` ```mermaid `
fenced block. GitHub renders it with the user's theme (light/dark).

### Rendering with the script

```bash
node ~/.skills/diagram/scripts/render.mjs diagram.mmd                 # light + dark SVG
node ~/.skills/diagram/scripts/render.mjs diagram.mmd --for iterm      # cappuccino PNG
node ~/.skills/diagram/scripts/render.mjs diagram.mmd --for obsidian   # paper SVG
node ~/.skills/diagram/scripts/render.mjs diagram.mmd --theme dark --format png --zoom 3
```

Consumers pick the variant: for a Confluence light-theme page use `diagram.light.svg`;
for a dark-themed consumer use `diagram.dark.svg`; for ambient/auto use a
`<picture>` wrapper:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="diagram.dark.svg">
  <img src="diagram.light.svg" alt="...">
</picture>
```

### How the render works

Pele emits SVG that reads colors from CSS variables (`--pele-*`). The renderer
replaces every variable with the palette's literal value. Two reasons:
- SVG opened as an image (Obsidian embed, Confluence, `<img>`) can't see the page's CSS variables.
- librsvg, used for PNG, ignores `var()` in attributes and would draw solid black.

## Files in this skill

| File | Purpose |
|------|---------|
| [AUTHORING.md](AUTHORING.md) | Read when writing a diagram: GitHub inline example, sequence `rect rgba()`, flowchart `classDef`, edge styles |
| [LAYOUT_RULES.md](LAYOUT_RULES.md) | Read for complex flowcharts headed to a Confluence whiteboard or any dynamic connector router |
| [palettes/light.json](palettes/light.json) | Theme: light, general use |
| [palettes/dark.json](palettes/dark.json) | Theme: dark, general use |
| [palettes/paper.json](palettes/paper.json) | Theme: warm light, Obsidian (`--for obsidian`) |
| [palettes/cappuccino.json](palettes/cappuccino.json) | Theme: espresso dark, iTerm2 (`--for iterm`) |
| [scripts/render.mjs](scripts/render.mjs) | Render a `.mmd` to SVG or PNG with a theme |
| [package.json](package.json) | Pins `pele` 1.7.0 |
| [example-conventions.mmd](example-conventions.mmd) | Flowchart showing the full palette and legend |
| [example-sequence.mmd](example-sequence.mmd) | Sequence diagram using `rect rgba()` |

## Relation to other skills

- **`confluence`** — consumer. Use this skill to render `.mmd` →
  `.svg`; then use `confluence` to upload + embed in Confluence.
- **`reframe`** — producer. When reframe generates diagrams, it writes
  `.mmd` that follow this skill's conventions.
- **`docs`** — producer. Diagrams in docs should follow these
  conventions for consistency.

## Verification

Before committing diagrams:

- [ ] Each semantic color matches the palette table (Semantic colors).
- [ ] Sequence rects use `rgba(...)` not solid `rgb(...)` — Pele draws them literally, so they fight the dark themes.
- [ ] No hardcoded `%%{init}%%` in files destined for GitHub markdown.
- [ ] Flowcharts with >5 node classes include a Legend subgraph.
- [ ] Render for the destination and look at it: `node scripts/render.mjs diagram.mmd --for iterm` for PNG, or `--for obsidian` for SVG.
