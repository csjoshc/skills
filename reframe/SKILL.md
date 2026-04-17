---
name: reframe
description: >-
  Rewrites source material (docs, code, specs, existing decks) for a specific
  audience—exec, architect, or engineer—restructuring narrative, emphasis, and
  detail level. Optionally generates Mermaid diagrams and PPTX slide decks.
  Use when preparing presentations, briefings, or when the same content must
  serve multiple audiences with different concerns.
---

# reframe

Reframe source material for a specific audience. This is not summarization
(shortening) — it is narrative restructuring: different arc, different emphasis,
different language, different detail level.

## Invocation

```
/reframe <audience> [source-path] [--slides] [--diagrams]
```

**Parameters:**

| Param | Values | Default |
|-------|--------|---------|
| `audience` | `exec`, `architect`, `engineer`, `auto` | required |
| `source-path` | file, directory, or omit for conversation context | conversation |
| `--slides` | generate PPTX output | off |
| `--diagrams` | generate Mermaid diagrams | on for architect/engineer, off for exec |

**Examples:**
- `/reframe exec ./docs/architecture.md --slides`
- `/reframe architect` (uses conversation context)
- `/reframe auto ./specs/api-design.md --slides --diagrams`

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
   ├─ --slides requested → check python-pptx (see reference/pptx-generation.md)
   └─ --diagrams requested or default-on → will use mmdc
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

### Phase 3: Structure

Select the slide/section structure for the chosen audience.
Load [templates/slide-structures.md](templates/slide-structures.md) for concrete
ordered slide lists with content guidance per mode.

- **Exec**: 5-8 slides. Title → Punchline → Value → Risk → Timeline → Ask → Appendix
- **Architect**: 8-15 slides. Context → Options → Architecture → Boundaries → Integration → NFRs → Migration → Risks
- **Engineer**: 10-20 slides. What → How → Components → Interfaces → Data Flow → Failure Modes → Ops → Impl Notes

### Phase 4: Output

**Always produce:** Markdown document with section headers matching the slide structure.

**If diagrams enabled** (default for architect/engineer):
1. Generate `.mmd` files using patterns from [reference/diagram-patterns.md](reference/diagram-patterns.md).
2. Use `classDef` conventions from `~/.skills/confluence-diagrams/example-conventions.mmd`.
3. Render: `mmdc -i <file>.mmd -o <file>.svg -b transparent`

**If --slides requested:**
1. Follow [reference/pptx-generation.md](reference/pptx-generation.md) for setup and generation.
2. Embed rendered diagrams as PNG: `mmdc -i <file>.mmd -o <file>.png -b white -w 1200`
3. Fallback: if python-pptx unavailable, produce markdown with a note about manual conversion.

**File naming:** `<source-stem>-<audience>.md` / `.pptx` / `.svg`
Output to same directory as source, or CWD if source is conversation context.

## Output Contract

Every reframe output includes:

1. **Main document**: Markdown structured for the audience with clear section headers.
2. **Parking lot appendix**: Content from the source that was cut for this audience,
   listed with brief rationale. Prevents silent information loss.
3. **Diagrams** (conditional): `.mmd` source + rendered `.svg` or `.png`.
4. **Slide deck** (conditional): `.pptx` file.

## Hard Constraints

- **Never mix audience registers.** An exec deck with architecture diagrams is a failed exec deck.
  An engineer doc leading with ROI is a failed engineer doc.
- **Never fabricate data.** If the source has no metrics, write "METRICS NEEDED" rather than inventing numbers.
  If no timeline exists, write "TIMELINE TBD".
- **Never lose information silently.** Content cut for the audience goes in the parking lot appendix.
- **Diagram conventions.** Reuse `classDef` colors and edge styles from
  `~/.skills/confluence-diagrams/example-conventions.mmd`. Include a legend subgraph for
  diagrams with more than 5 nodes.
- **PPTX is best-effort.** If python-pptx cannot be installed, produce markdown + a note.
  Do not block the entire reframe on slide generation.

## Companion Files

| File | Load when |
|------|-----------|
| [reference/audience-profiles.md](reference/audience-profiles.md) | Reframing content (Phase 2) |
| [reference/diagram-patterns.md](reference/diagram-patterns.md) | Generating diagrams (Phase 4) |
| [reference/pptx-generation.md](reference/pptx-generation.md) | Generating PPTX (Phase 4) |
| [templates/slide-structures.md](templates/slide-structures.md) | Choosing deck structure (Phase 3) |
| [example/three-audience-transform.md](example/three-audience-transform.md) | Understanding the reframe transformation |

## Quality Checklist

Before delivering output:

- [ ] Narrative uses the correct audience register (no jargon leaks)
- [ ] Story arc matches the audience pattern (punchline / tradeoff / mechanism first)
- [ ] No fabricated metrics or claims not present in source material
- [ ] Omitted content noted in parking lot appendix
- [ ] Diagrams (if any) render without errors via `mmdc`
- [ ] PPTX (if any) opens without errors
- [ ] Output file paths reported to user
- [ ] Gaps in source material flagged explicitly (METRICS NEEDED, TIMELINE TBD)

## Validation

```bash
python3 "$HOME/.skills/skillsmith/scripts/skill_audit.py" "$HOME/.skills"
```

Confirm `reframe` passes frontmatter rules.
