---
name: reframe
description: >-
  Rewrites source material (docs, code, specs, existing decks) for a specific
  audience—exec, architect, or engineer—restructuring narrative, emphasis, and
  detail level. Produces structured markdown with YAML frontmatter that
  downstream skills (like c3ppt) can consume for presentation generation.
  Optionally generates Mermaid diagrams. Use when preparing briefings,
  structuring content for presentations, or when the same material must serve
  multiple audiences with different concerns.
---

# reframe

Reframe source material for a specific audience. This is not summarization
(shortening) — it is narrative restructuring: different arc, different emphasis,
different language, different detail level.

The output is structured markdown with YAML frontmatter — a portable contract
that downstream skills (such as c3ppt for PPTX generation) can parse directly.

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

For PPTX output, pipe reframe's markdown through the c3ppt skill:
```
/reframe exec ./docs/architecture.md
/c3ppt ./docs/architecture-exec.md
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
   └─ For PPTX output → pipe reframe's markdown through the c3ppt skill
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

#### Runtime-agnostic naming pass

When the source material covers multiple runtime modes or vendor
choices (e.g. process / Docker Compose / kind+helm; DMR / Ollama /
cloud OpenAI), apply this pass before structure selection:

1. **Identify the abstraction name** — the role-based noun the
   feature plays: "model runtime", "chat stack", "inference
   endpoint", "OpenAI-compatible provider". Use it in the
   primary narrative.
2. **Demote vendor / runtime tokens** — `Docker Model Runner`,
   `Ollama`, `host.docker.internal:11434` go in a feature table
   row labeled by mode, never in the prose backbone.
3. **Mermaid node labels follow the same rule.** A node labeled
   "Docker Model Runner" in an architecture diagram for a
   runtime-agnostic stack is a self-contradiction; relabel to the
   role ("LLM runtime — OpenAI-compatible endpoint") with the
   binding env var as the secondary label.
4. **Mode-specific subsections are explicit.** When you genuinely
   need runtime-specific content, put it under a subsection whose
   heading names the mode ("Mode: Docker Model Runner",
   "Runtime: Ollama"). The reader can scope-read; the abstract
   narrative stays clean.

The reframe output that ships with a vendor token in the title or a
runtime-specific Mermaid node in the primary diagram fails this skill.

#### Multi-mode comparison tables

If the source covers more than one run mode but does not include a
side-by-side comparison table, generate one during Phase 2. The
table rows are at minimum:

| Aspect | Mode A | Mode B | Mode C |
|---|---|---|---|
| Startup command | … | … | … |
| Base URL the consumer sees | … | … | … |
| Ports exposed on host | … | … | … |
| Key env vars | … | … | … |
| External-dep plumbing (LLM, MCP, DB) | … | … | … |
| Teardown / cleanup | … | … | … |

If a cell is unknown, mark it `[TO BE DOCUMENTED]` — surface the
gap rather than guessing. The comparison table is what makes
multi-mode docs scannable; without it, the reader has to
reconstruct the comparison from mode-specific subsections.

#### Doc fan-out audit

Before finalizing, check whether the source directory has more
than one standalone page covering the same feature (e.g.
`local-dev.md` *and* `docker-compose.md` *and* `runtime-modes.md`
all describing the same chat stack). If so, the reframe output
either:

- Picks the canonical hub and folds the rest into mode-specific
  subsections of that hub, or
- Explicitly labels the others as satellites with prominent
  links back to the hub.

A reframe that adds a fourth parallel page increases the doc-rot
surface; it doesn't help the audience.

### Phase 3: Structure

Select the content structure for the chosen audience.
Load [templates/slide-structures.md](templates/slide-structures.md) for concrete
ordered section lists with content guidance per mode.

- **Exec**: 5-8 sections. Title → Punchline → Value → Risk → Timeline → Ask → Appendix
- **Architect**: 8-15 sections. Context → Options → Architecture → Boundaries → Integration → NFRs → Migration → Risks
- **Engineer**: 10-20 sections. What → How → Components → Interfaces → Data Flow → Failure Modes → Ops → Impl Notes

Each section maps to a slide when consumed by a presentation skill like c3ppt.

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
contract that downstream skills (like c3ppt) parse to generate presentations.

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

### Complete Example

```markdown
---
title: "Platform Migration"
subtitle: "Q3 Recommendation"
audience: exec
author: "Jane Doe"
date: "April 2026"
sources:
  - label: "Architecture RFC"
    url: "./docs/rfc-042.md"
diagrams:
  - path: "./platform-migration-exec-timeline.mmd"
    slide: "Timeline"
---

## Slide: Recommendation

- Migrate to managed Kubernetes by Q4
- Projected 30% infrastructure cost reduction
- Risk: 2-week service disruption during cutover

## Slide: Business Value

- $1.2M annual savings from consolidated compute
- 40% faster deployment cycles
- Improved compliance posture (FedRAMP inheritance)

## Slide: Timeline

- **Q3**: Proof of concept + team training
- **Q4**: Production migration (3 phases)
- **Q1 next year**: Decommission legacy

## Slide: Parking Lot

- **Detailed migration runbook**: Cut because exec audience; available in engineer reframe
- **Kubernetes operator comparison**: Cut because implementation detail
```

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
| [example/three-audience-transform.md](example/three-audience-transform.md) | Understanding the reframe transformation |

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
- [ ] Prose output passes `/stop-slop` to remove AI writing patterns

## Validation

```bash
python3 "$HOME/.skills/skillsmith/scripts/skill_audit.py" "$HOME/.skills"
```

Confirm `reframe` passes frontmatter rules.
