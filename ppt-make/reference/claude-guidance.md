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

| Source content                         | Best layout    |
|----------------------------------------|----------------|
| Sequential steps, request/response     | `flow`         |
| Categorized lists (problem/solution)   | `panels`       |
| System layers, component relationships | `diagram`      |
| Processing stages with per-stage detail| `pipeline`     |
| Feature matrix, status tracking        | `table`        |
| Before/after, option A vs B            | `comparison`   |
| Mixed narrative + data                 | `mixed`        |
| Simple key takeaways, agendas          | `bullets`      |

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

## YAML Authoring Tips

- Always use `|` (literal block scalar) for multi-line `content` fields.
- Use `\n` inside `text` fields for line breaks within boxes (e.g.,
  `"Browser\nGET /flights"`).
- Prefer named palette colors (`orange`, `green`, `blue`) over hex codes.
- Include a `legend` on flow and diagram slides when using 3+ colors.
- Add `links` for wiki/Confluence references so reviewers can trace sources.
