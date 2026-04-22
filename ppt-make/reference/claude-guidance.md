# Claude Guidance for Generating YAML

## Contents

- Layout selection by content type
- Content density rules
- Color assignment conventions
- Structural patterns
- Shape density target
- YAML authoring tips

---

## Layout Selection by Content Type

| Source content                         | Layout       | Decision rule                              |
|----------------------------------------|--------------|---------------------------------------------|
| Sequential steps, request/response     | `flow`       | Process/relationship: direction matters   |
| Categorized lists (problem/solution)   | `panels`     | 2-4 related but non-comparable ideas      |
| System layers, component relationships | `diagram`    | Topology: how pieces fit together          |
| Processing stages with per-stage detail| `pipeline`   | Flow + detail: stages + associated info    |
| Feature matrix, status tracking        | `table`      | Comparison: rows vs. columns *are the point*|
| Before/after, option A vs B            | `comparison` | Comparison + annotation: needs callout    |
| Mixed narrative + data                 | `mixed`      | One slide, multiple types (use sparingly) |
| Simple key takeaways, agendas          | `bullets`    | List: simple, not comparative              |

**Key distinction:** Use `table` when the grid structure *is* the message (Config A vs. Config B, Feature 1 vs. Feature 2). Use `flow` when time/process *is* the message (Step 1 → 2 → 3, API request → response). Use `diagram` when spatial relationships *is* the message (Layer X connects to Module Y).

---

## Content Density Rules

- **One concept per slide.** If a source section covers auth flow AND
  token caching, split into two slides.
- **Max 6-8 bullets per panel**, 4-6 rows per table section, 5 boxes per
  flow row. Exceeding these limits degrades readability on dark backgrounds.
- **Use subtitles** to add context without consuming body space.
- **Speaker notes** (`notes:`) should carry detail that doesn't fit on the
  slide — audience questions, implementation specifics, caveats.

---

## Color Assignment Conventions

Assign colors by **role**, not aesthetics. Follow the palette:

| Role                    | Fill   | Text  | Border    |
|-------------------------|--------|-------|-----------|
| User / external input   | gray   | white | warm_gray |
| CDAO-owned component    | orange | white | none      |
| C3 platform component   | green  | white | none      |
| Guardrail / security    | blue   | white | none      |
| Decision / branch       | dark   | white | warm_gray |

Use the same color for the same component across slides to build
visual consistency throughout the deck.

---

## Structural Patterns

- **Open with a `title` slide**, close with a `closing` slide.
- **Use `panels` early** (slide 2-3) to frame the problem/constraints.
- **Use `flow` or `diagram`** for the core technical content (slides 4-8).
- **Use `table`** for reference data, failure modes, config matrices.
- **Use `mixed`** for summary slides that combine a box row + table + callout.

---

## Shape Density Target

Aim for **8-15 shapes per slide** (excluding title/subtitle). The canonical
reference deck averages 15.3 shapes/slide. Below 5 shapes usually means
the slide is an underutilized text blob.

---

## Prose Quality (Titles, Captions, Speaker Notes)

All text on slides and in speaker notes must follow **stop-slop** principles:

- **Cut filler.** No "here's what," "it should be noted that," "it's important to understand."
- **Use active voice.** Subject + verb. Not: "The decision emerges." But: "We chose X because..."
- **Be specific.** Not: "The implications are significant." But: "This removes the 3-minute auth delay."
- **Vary rhythm.** Mix short and long sentences. Avoid three consecutive sentences of the same length.
- **Trust readers.** State facts directly. No softening ("perhaps," "arguably," "in some cases") unless warranted by uncertainty.

**Speaker notes are not exempt.** They carry implementation detail, but should also be direct and jargon-light.

---

- Always use `|` (literal block scalar) for multi-line `content` fields.
- Use `\n` inside `text` fields for line breaks within boxes (e.g.,
  `"Browser\nGET /flights"`).
- Prefer named palette colors (`orange`, `green`, `blue`) over hex codes.
- Include a `legend` on flow and diagram slides when using 3+ colors.
- Add `links` for wiki/Confluence references so reviewers can trace sources.
