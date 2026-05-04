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
