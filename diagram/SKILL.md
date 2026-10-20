---
name: diagram
description: "Authors Mermaid diagrams and renders them with Pele to SVG or PNG in named themes (light, dark, paper, catppuccin, cappuccino), then previews each render for the user. Use when creating or updating .mmd files or diagram SVG/PNG files."
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
| iTerm2 (dark terminal, `imgcat`) | `--for iterm` | `diagram.catppuccin.png` | iTerm2 shows PNG inline, not SVG. Catppuccin Mocha, the terminal's own theme. |
| Obsidian note, needs a fixed image | `--for obsidian` | `diagram.catppuccin-latte.svg` | Matches the AnuPpuccin Latte vault. Prefer the raw fence (below) unless the note needs an image. |
| Confluence, email, any other static consumer | (no flags) | `diagram.light.svg` + `diagram.dark.svg` | Portable SVG; pick the variant at embed time. |
| One specific theme | `--theme NAME [--format svg\|png]` | `diagram.NAME.FORMAT` | Any theme in `palettes/`; `--out PATH` names the file. |

Themes: `light`, `dark` (general), `catppuccin-latte` (Obsidian, AnuPpuccin Latte),
`catppuccin` (iTerm2 and Obsidian dark, Catppuccin Mocha), `paper` (Soft Paper vaults),
`cappuccino` (warm espresso dark, opt-in). Each theme is one JSON file in `palettes/`;
add a theme by adding a file.

Every output carries its theme's background, so text and lines stay readable on any
host page. Pass `--transparent` only when the host's lightness matches the theme
(a light theme on a light page); on a mismatched page the ink disappears.

The renderer writes every file next to the source. `--zoom N` scales PNG
output (default 2, for retina terminals).

## Preview every render (`--show`)

**Always pass `--show`** when rendering, whatever the destination. It renders a
catppuccin PNG (reusing `--for iterm` output when present, else a temp file under
`$TMPDIR/diagram-preview/`) and then takes one of two paths, chosen from the
agent harness:

| Harness | Detected by | Path | Your next step |
|---------|-------------|------|----------------|
| Shows images from the read tool inline (oh-my-pi) | `OMPCODE=1` | **inline**: prints the PNG path only | Read the printed `preview:` file so it appears in the transcript |
| Captures tool output and repaints (Claude Code, others) | anything else | **pane**: `imgcat` in one right-hand iTerm2 split pane, else macOS Preview | Cite the printed `preview:` line; you can't see the pane |

`DIAGRAM_PREVIEW=inline|pane` overrides detection. oh-my-pi also sets `CLAUDECODE=1`,
so detection checks `OMPCODE` first.

Pane path details: the pane is reused on later renders in the same tab (id saved in
`~/.cache/diagram/preview-session`); a closed pane, or an agent in another tab, gets
a new split. Focus returns to the agent's pane. Outside iTerm2, or if AppleScript
fails, it opens Preview. The first run triggers a one-time macOS Automation prompt.

A preview failure only warns; the deliverable and exit code are unaffected.

## When to use which source form

| Target | Approach |
|--------|----------|
| GitHub README / wiki, GitLab, most markdown viewers | Embed mermaid source in ` ```mermaid ` fenced block. Remove hardcoded `%%{init}%%` blocks to let GitHub's auto-theming adapt to user's light/dark mode. Use `rgba()` rect colors for mode-agnostic highlights. |
| Obsidian note (default) | Paste the `.mmd` into a ` ```mermaid ` fence. Obsidian bundles Mermaid 11 and renders it in the note, following the vault's light/dark mode. The `classDef` tints carry over; the Pele palettes don't apply. Prefer `flowchart` over `block-beta`, which renders cramped there. Still run `render.mjs --show` so the user sees it here. |
| Obsidian note that needs a fixed image, iTerm2, Confluence, PDF, email, any static/image consumer | Render with `render.mjs` (table above) and embed the file (`![[diagram.catppuccin-latte.svg]]` in Obsidian). One `.mmd` source; the output format and theme come from the flags. |

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

Mermaid diagrams use color to encode meaning, not decoration. One hue per semantic,
shared by flowchart `classDef` and sequence `rect`. Each hue is a mid-tone that holds
at least 3:1 against every theme background, so one source reads in all themes.

| Semantic | Role | Hue | `classDef` (flowchart) | `rect` (sequence) |
|----------|------|-----|------------------------|-------------------|
| `person` | User, browser, human actor | `#78716C` | `fill:#78716C40,stroke:#78716C` | `rgba(120,113,108,0.25)` |
| `service` | App, API, deployed service (sync call) | `#3B82F6` | `fill:#3B82F640,stroke:#3B82F6` | `rgba(59,130,246,0.25)` |
| `library` | In-process library or module | `#0284C7` | `fill:#0284C740,stroke:#0284C7` | `rgba(2,132,199,0.25)` |
| `guard` | Security boundary, guardrail, policy (caution) | `#CA6A04` | `fill:#CA6A0440,stroke:#CA6A04` | `rgba(202,106,4,0.25)` |
| `external` | External system outside your control | `#64748B` | `fill:#64748B40,stroke:#64748B` | `rgba(100,116,139,0.25)` |
| `state` | State, data store, token, config (data/mutation) | `#A855F7` | `fill:#A855F740,stroke:#A855F7` | `rgba(168,85,247,0.25)` |
| `errBlock` | Error state, blocked path | `#EF4444` | `fill:#EF444440,stroke:#EF4444` | `rgba(239,68,68,0.25)` |
| `passNode` | Success outcome, data-in-motion | `#15913F` | `fill:#15913F40,stroke:#15913F` | `rgba(21,145,63,0.25)` |
| `auditNode` | Audit / logging / side-effect | `#64748B` | `fill:#64748B33,stroke:#64748B` | `rgba(100,116,139,0.2)` |

Add `stroke-width:1.5px` to each `classDef`. Leave out `color:`, so node text uses the
theme's text color. The fill is the hue at 25% alpha (`40` hex suffix) because Mermaid's
`classDef` parser rejects `rgba()`; the theme background shows through, so text keeps
at least 6.9:1 contrast in every theme.

Sequence `rect rgba(...)`, flowchart `classDef` and edge-style recipes: [AUTHORING.md](AUTHORING.md). Add a Legend subgraph when a flowchart uses more than 5 node classes ([example-conventions.mmd](example-conventions.mmd)).

Never use an opaque fill (`rect rgb(...)`, a six-digit `classDef` fill): Pele draws it
literally, so a pastel stays pastel in every theme and its text fails on dark themes.

## Rendering

### Default (GitHub wiki / README inline mermaid)

No render step needed — commit the `.mmd` source inside a ` ```mermaid `
fenced block. GitHub renders it with the user's theme (light/dark).

### Rendering with the script

```bash
node ~/.skills/diagram/scripts/render.mjs diagram.mmd --show                  # light + dark SVG
node ~/.skills/diagram/scripts/render.mjs diagram.mmd --for iterm --show      # catppuccin PNG
node ~/.skills/diagram/scripts/render.mjs diagram.mmd --for obsidian --show   # catppuccin-latte SVG
node ~/.skills/diagram/scripts/render.mjs diagram.mmd --theme dark --format png --zoom 3 --show
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
| [palettes/catppuccin-latte.json](palettes/catppuccin-latte.json) | Theme: Catppuccin Latte, Obsidian (`--for obsidian`) |
| [palettes/paper.json](palettes/paper.json) | Theme: warm light, Soft Paper vaults |
| [palettes/catppuccin.json](palettes/catppuccin.json) | Theme: Catppuccin Mocha, iTerm2 (`--for iterm`, `--show` preview) |
| [palettes/cappuccino.json](palettes/cappuccino.json) | Theme: warm espresso dark, opt-in |
| [scripts/render.mjs](scripts/render.mjs) | Render a `.mmd` to SVG or PNG with a theme |
| [scripts/preview.mjs](scripts/preview.mjs) | `--show`: inline path for image-capable harnesses, else iTerm2 pane / Preview |
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

- [ ] Each `classDef` uses a hue from the palette table with a `40` alpha fill and no `color:`.
- [ ] Sequence rects use `rgba(...)` not solid `rgb(...)` — Pele draws them literally, so they fight the dark themes.
- [ ] No hardcoded `%%{init}%%` in files destined for GitHub markdown.
- [ ] Flowcharts with >5 node classes include a Legend subgraph.
- [ ] Rendered with `--show`; on the inline path you read the preview file, on the pane path you cited the `preview:` line.
