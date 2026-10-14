---
name: reframe
description: "Rewrites source material for an exec, architect or engineer audience as structured markdown that ppt-make and others consume. Use when the same material must serve a different audience."
---

# reframe

Reframe source material for a specific audience. This is not summarization
(shortening) — it is narrative restructuring: different arc, different emphasis,
different language, different detail level.

The output is structured markdown with YAML frontmatter — a portable contract
that downstream skills (such as ppt-make for PPTX generation) can parse directly.

## Invocation

```
/reframe <audience> [source-path] [--diagrams]
```

**Parameters:**

| Param | Values | Default |
|-------|--------|---------|
| `audience` | `exec`, `architect`, `engineer`, `auto` | required |
| `source-path` | file, directory, or omit for conversation context | conversation |
| `--diagrams` | generate Mermaid diagrams | on for architect/engineer, off for exec |

**Examples:**
- `/reframe exec ./docs/architecture.md`
- `/reframe architect` (uses conversation context)
- `/reframe auto ./specs/api-design.md --diagrams`

For PPTX output, pipe reframe's markdown through a PPTX skill such as ppt-make:
```
/reframe exec ./docs/architecture.md
/ppt-make ./docs/architecture-exec.md
```

## Decision Tree

```
1. Audience specified?
   ├─ Yes → use it
   └─ No / "auto" → classify:
       ├─ Recipient is C-suite, VP, budget owner, non-technical → exec
       ├─ Recipient is staff+ eng, solution architect, platform lead → architect
       ├─ Recipient is IC engineer, SRE, implementer → engineer
       └─ Ambiguous → ask user (one question, three choices)

2. Source material?
   ├─ File path → read and ingest
   ├─ Directory → scan for .md, .py, .ts, .pptx, .pdf; summarize
   ├─ Conversation context → extract key content from session
   └─ Nothing useful → ask user for source

3. Output format?
   ├─ Always → structured markdown with YAML frontmatter (the output contract)
   ├─ --diagrams requested or default-on → generate .mmd files, reference in frontmatter
   └─ For PPTX output → pipe reframe's markdown through a PPTX skill such as ppt-make
```

## Workflow

### Phase 1: Ingest

1. Read all source material.
2. Extract a **fact inventory** — tag each item by type:
   - **Claim**: assertion about value, impact, or capability
   - **Metric**: quantified data point (cost, latency, throughput, timeline)
   - **Decision**: choice made or pending, with rationale
   - **Architecture**: system boundaries, patterns, components, integration points
   - **Implementation**: code paths, APIs, data structures, configs
   - **Risk**: what could go wrong, mitigation status
   - **Timeline**: milestones, dates, phases
3. Note gaps: if the source lacks metrics, timelines, or decisions, flag them — do not fabricate.

### Phase 2: Reframe

Select the narrative strategy for the chosen audience:

| Aspect | Exec | Architect | Engineer |
|--------|------|-----------|----------|
| Story arc | Punchline-first: conclusion → evidence | Tradeoff-first: options → recommendation | Mechanism-first: how it works → why |
| Opening | "We recommend X because Y" | "The core tension is X vs Y" | "The system does X via Y" |
| Detail | Minimal (metrics, timelines, ask) | Patterns and boundaries (no code) | Deep (code, configs, execution paths) |
| Language | Business only | Architecture vocabulary | Full technical vocabulary |
| Emphasis | Value, impact, risk, timeline, ask | Patterns, boundaries, tradeoffs, NFRs | Components, data flow, interfaces, failure modes |
| Cut | Impl details, code, internal debates | Code-level details, operational runbooks | Business justification, ROI calculations |

Load [reference/audience-profiles.md](reference/audience-profiles.md) for full profiles
including persona details, anti-patterns, and slide count targets.

Restructure the fact inventory into the chosen narrative. Change emphasis,
wording, and structure — not just length.

#### Phase 2 audits

Before finalizing, run the audits in [reference/phase-2-audits.md](reference/phase-2-audits.md) that apply:

- **Runtime-agnostic naming:** the source covers several runtimes or vendors. A vendor token in the title or a runtime-specific node in the primary diagram fails the skill.
- **Multi-mode comparison table:** the source covers more than one run mode with no side-by-side table. Generate one; mark unknown cells `[TO BE DOCUMENTED]`.
- **Doc fan-out:** several pages cover one feature. Fold into a canonical hub or label satellites; never add a parallel page.
- **Hub-shedding:** one page carries the work of its children. Push blocks into existing children and leave a gist plus link.
- **Confluence comment anchors:** read the storage format and keep anchored phrases verbatim or re-anchor them before editing a page with inline comments.

### Phase 3: Structure

Select the content structure for the chosen audience.
Load [templates/slide-structures.md](templates/slide-structures.md) for concrete
ordered section lists with content guidance per mode.

Section counts: exec 5-8, architect 8-15, engineer 10-20.

Each section maps to a slide when consumed by a presentation skill like ppt-make.

### Phase 4: Output

Produce a structured markdown document following the **Output Contract** below.

**If diagrams enabled** (default for architect/engineer):
1. Generate `.mmd` files using patterns from [reference/diagram-patterns.md](reference/diagram-patterns.md).
2. Use `classDef` conventions from `~/.skills/confluence-diagrams/example-conventions.mmd`.
3. Render: `mmdc -i <file>.mmd -o <file>.svg -b transparent`
4. Reference each diagram in the YAML frontmatter `diagrams` array.

**File naming:** `<source-stem>-<audience>.md` / `.mmd` / `.svg`
Output to same directory as source, or CWD if source is conversation context.

## Output Contract

Every reframe output is a single markdown file with YAML frontmatter. This is the
contract that downstream skills (like ppt-make) parse to generate presentations.

### YAML Frontmatter

```yaml
---
title: "Deck Title"
subtitle: "Optional subtitle"
audience: exec|architect|engineer
author: "Name"
date: "Month Year"
sources:
  - label: "Source Name"
    url: "https://..."
diagrams:
  - path: "./diagram-name.mmd"
    slide: "Slide Title"
---
```

| Field | Required | Description |
|-------|----------|-------------|
| `title` | yes | Primary title for the content / deck |
| `subtitle` | no | Optional subtitle or tagline |
| `audience` | yes | One of `exec`, `architect`, `engineer` |
| `author` | no | Author name (defaults to user if known) |
| `date` | no | Date string, typically "Month Year" |
| `sources` | no | List of source materials used, each with `label` and optional `url` |
| `diagrams` | no | List of Mermaid diagram files, each with `path` and `slide` (the section title where it belongs) |

### Slide Sections

After the frontmatter, each slide/section is a level-2 heading with the `Slide:` prefix:

```markdown
## Slide: Section Title

- Bullet point one
- Bullet point two with **emphasis**

| Column A | Column B |
|----------|----------|
| data     | data     |
```

Content within each section can include:
- Bullet lists (primary content vehicle)
- Tables (for comparisons, metrics, timelines)
- Inline text paragraphs (sparingly — bullets preferred)
- `> blockquote` for speaker notes or callouts
- `METRICS NEEDED` / `TIMELINE TBD` placeholders for gaps

### Parking Lot Appendix

The final section is always:

```markdown
## Slide: Parking Lot

Content cut from the source for this audience, with brief rationale:

- **[Item]**: Cut because [reason]
```

This prevents silent information loss. Every fact from the source that was
excluded for the target audience appears here.

A complete worked output: [example/output-contract-example.md](example/output-contract-example.md).

## Hard Constraints

- **Never mix audience registers.** An exec document with architecture diagrams is a failed exec document.
  An engineer doc leading with ROI is a failed engineer doc.
- **Never fabricate data.** If the source has no metrics, write "METRICS NEEDED" rather than inventing numbers.
  If no timeline exists, write "TIMELINE TBD".
- **Never lose information silently.** Content cut for the audience goes in the parking lot appendix.
- **Diagram conventions.** Reuse `classDef` colors and edge styles from
  `~/.skills/confluence-diagrams/example-conventions.mmd`. Include a legend subgraph for
  diagrams with more than 5 nodes.
- **Output contract is strict.** Every output must use the YAML frontmatter + `## Slide:` section
  format so downstream consumers can parse it reliably.

## Companion Files

| File | Load when |
|------|-----------|
| [reference/audience-profiles.md](reference/audience-profiles.md) | Reframing content (Phase 2) |
| [reference/diagram-patterns.md](reference/diagram-patterns.md) | Generating diagrams (Phase 4) |
| [templates/slide-structures.md](templates/slide-structures.md) | Choosing content structure (Phase 3) |
| [reference/phase-2-audits.md](reference/phase-2-audits.md) | Source covers several runtimes, modes or pages, a hub is overloaded, or a Confluence page has inline comments |
| [example/three-audience-transform.md](example/three-audience-transform.md) | Understanding the reframe transformation |
| [example/output-contract-example.md](example/output-contract-example.md) | Checking the exact output shape |

## Quality Checklist

Before delivering output:

- [ ] Narrative uses the correct audience register (no jargon leaks)
- [ ] Story arc matches the audience pattern (punchline / tradeoff / mechanism first)
- [ ] No fabricated metrics or claims not present in source material
- [ ] Omitted content noted in parking lot appendix
- [ ] Output markdown follows the YAML frontmatter + slide section contract
- [ ] Diagrams (if any) render without errors via `mmdc`
- [ ] Diagrams (if any) referenced in frontmatter `diagrams` array
- [ ] Output file paths reported to user
- [ ] Gaps in source material flagged explicitly (METRICS NEEDED, TIMELINE TBD)
- [ ] Over-heavy hub: dominant blocks pushed into existing children with a gist + link left behind (hub-shedding audit)
- [ ] Confluence inline-comment anchors checked in storage format and preserved or re-anchored before editing
- [ ] Prose output passes `/stop-slop` to remove AI writing patterns

## Validation

```bash
python3 "$HOME/.skills/skillsmith/scripts/skill_audit.py" "$HOME/.skills"
```

Confirm `reframe` passes frontmatter rules.
