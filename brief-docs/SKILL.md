---
name: brief-docs
description: Author and refactor internal technical documentation with brevity—summary-first, progressive disclosure, hub-and-spoke navigation, minimal diagrams. Use when writing or tightening wiki pages, repo docs under docs/, onboarding overviews, or short internal "overview" pages (scannable summary, optional follow-up detail, canonical facts in one place). Not for diagram render/embed workflows (use confluence-diagrams); not for full PRDs or ticket specs (use spec-writer).
---

# brief-docs

Apply this skill when producing or editing **short, scannable** technical docs—**one screen of value up front**, detail on demand.

## Before writing

1. Decide **hub vs satellite**: one index page linking out, or a single standalone page.
2. Identify **canonical homes** for facts that change (ports, env names, API fields). Other pages **link** there; do not duplicate tables.
3. Open [references/pattern-anatomy.md](references/pattern-anatomy.md) for section labels and diagram rules.

## Greenfield (new doc set)

1. Draft the **hub** using [references/templates.md](references/templates.md) (hub stub).
2. Add **satellites** only where a topic needs more than ~2 short paragraphs; each satellite uses the satellite stub.
3. Add a **lookup** page (env/secrets, URLs) if the stack has more than a handful of names—use the lookup stub.
4. Run the checks in [references/accuracy-and-drift.md](references/accuracy-and-drift.md) against source code or OpenAPI before shipping.

## Editing existing docs

1. **Promote** the main insight into a **Summary** line or paragraph at the top; move former intro detail into **Follow-up:**.
2. **Delete** duplicated port/env/API tables; replace with one link to the canonical doc.
3. **Collapse** multiple Mermaid diagrams to **one per page**; split pages if two diagrams serve different audiences.
4. Remove **stale behavior** (deprecated flags, removed services) using the drift checklist.
5. **Retire stale satellite pages.** When a spoke becomes obsolete (API changed, feature collapsed, package deleted), delete it and grep the hub for dangling cross-references. Hub-and-spoke only works if spokes stay current or are pruned — a parallel page that contradicts the hub is worse than no satellite.

## Structural rules

These are blocking — apply before shipping any new or edited doc.

### No inline script / Makefile bodies

Scripts, `make` targets, multi-line `docker`/`kubectl` invocations, and CI-step bodies belong in the canonical file (Makefile, `scripts/*.sh`, workflow YAML). Docs **reference** them via `make <target>` or a single-line shell example, never by pasting the body. Inline bodies rot the moment the underlying command changes; the canonical target is the single source of truth.

If the canonical target doesn't exist yet, create the target first, then reference it.

### Comparison table when the feature has more than one run mode

When a feature ships in more than one run mode (process / Docker Compose / kind+Helm / cloud), the doc includes a side-by-side comparison table whose rows are at minimum: startup command, base URL, ports exposed on host, key env vars, LLM / external-dep URL plumbing, teardown.

Without the table, every reader has to grep across mode-specific subsections to reconstruct the comparison. Mode-specific *details* still live in their own subsections; the table is the navigation hub.

### Internal labels are doc-filename identifiers, not source-comment identifiers

`docs/ADR-XXX.md` is a fine filename. Copying `ADR-XXX` (or `T-NNN`, `Constitution P\d+`, `Slice \d+`, `IG-\d+G\d+`, `RISK-NN`, `Pattern \d+`, `AP-\d+`) into source-code docstrings, code comments, or other doc-page bodies is not. The label tells the reader nothing they didn't already know from filename or context; the *why* of the decision is what they actually need.

When a runtime docstring or a doc body needs to reference an ADR, pair the rationale prose with the stable path:

Bad: `"""ADR-CHAT-1: single SSE endpoint."""`

Good:

```
Single SSE chat endpoint. POST /v1/chat emits the locked event-name
set {text, tool_start, tool_end, done}. The prior JSON + stream pair
was collapsed here so the SPA has a single stable target.
Background: docs/ADR-CHAT-1.md.
```

Bare label drops fail this skill's quality bar.

### Name the abstraction, not today's vendor

If the doc claims to describe a runtime-agnostic or vendor-agnostic feature, the prose, table headers, and Mermaid node labels must reflect the abstraction (`Model runtime`, `OpenAI-compatible endpoint`) — not a current default (`Docker Model Runner`, `Ollama`). Runtime-specific notes go in a side table or per-runtime subsection.

A doc title "Local dev with DMR" for a runtime-agnostic stack is the canonical version of this failure — the title picks a winner the architecture deliberately doesn't pick.

## Companion references

| File | Use when |
|------|----------|
| [references/pattern-anatomy.md](references/pattern-anatomy.md) | Defining sections, tone, tables vs prose, Mermaid limits |
| [references/templates.md](references/templates.md) | Copy-paste Markdown stubs |
| [references/accuracy-and-drift.md](references/accuracy-and-drift.md) | Verifying names and behavior against code |
| [references/example-hub-page.md](references/example-hub-page.md) | Fictional hub + satellite shape (example) |

## Quality bar

- A reader skimming **only bold Summary** still learns what the system is and where to go next.
- No secret **values**; env and key **names** only.
- Internal links use **stable paths** relative to the doc tree or repo root as per project convention.
- Prose output passes `/stop-slop` to remove AI writing patterns and filler.

## ADR template

<!-- merged from addyosmani/agent-skills documentation-and-adrs -->

Use for decisions costly to reverse (framework, schema, auth, API style, infra). Store in `docs/decisions/NNN-slug.md`. Don't delete superseded ADRs — write a new one that supersedes.

```markdown
# ADR-NNN: <decision title>

## Status
Proposed | Accepted | Superseded by ADR-XXX | Deprecated

## Date
YYYY-MM-DD

## Context
Constraints, requirements, forces in tension.

## Decision
The choice, stated plainly.

## Alternatives Considered
- **Option A** — pros / cons / why rejected
- **Option B** — pros / cons / why rejected

## Consequences
Positive, negative, and follow-on work the decision creates.
```

## Changelog maintenance

Keep `CHANGELOG.md` at the repo root, newest first. Group entries under `Added` / `Changed` / `Fixed` / `Removed` / `Deprecated` / `Security`. Reference issue or PR numbers.

```markdown
## [1.2.0] - 2025-01-20
### Added
- Task sharing across teams (#123)

### Fixed
- Duplicate task on rapid create clicks (#125)

### Changed
- List page size 20 -> 50 (#126)
```

## Validation

After edits, run the skillsmith audit on the skills directory (if installed):

`python3 "$HOME/.skills/skillsmith/scripts/skill_audit.py" "$HOME/.skills"`

Confirm this skill folder passes frontmatter rules (`name` matches directory `brief-docs`, `description` present).
