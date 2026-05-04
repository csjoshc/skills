---
name: orchestrate
description: >-
  Guide for agents and operators working outside the Orchestra repo itself.
  Explains how to prepare ticket files and project structure so Orchestra can
  ingest them correctly via the runtime CLI such as `orch run`. Use when
  preparing tickets for `orch run`, structuring a project for Orchestra
  ingestion, or troubleshooting Orchestra ticket-format errors.
---

# Orchestra Runtime Intake Guide

Use this skill when you are **outside the Orchestra repo** and need to prepare a
target project for ingestion by Orchestra's runtime CLI. It is an operator guide
for creating or editing `.tickets/*.md` files that Orchestra will consume — not
an internal spec of Orchestra's state machine or gate mechanics.

For runtime internals (stages, `unified_gate`, merge queue, branch-points,
commit hygiene, SPEC_SPLIT), see the Orchestra repo's own docs:

- `docs/ARCHITECTURE.md` — stages, routing, SPEC_SPLIT
- `docs/developer-guide.md` — assertion IDs, branch-points, commit hygiene, worktree lifecycle
- `docs/MERGE_QUEUE.md` — merge queue and end-of-run promotion

## Minimum Project Layout

```text
<project-root>/
  .tickets/
  .orchestra/         # created by Orchestra at first run
  AGENTS.md           # recommended
  STANDARDS.md        # recommended
```

`.tickets/` is where Orchestra discovers work items. `AGENTS.md` and
`STANDARDS.md` supply constraints and conventions for Orchestra's agents.

## Ticket File Format

Every ticket lives under `<project-root>/.tickets/` and starts with YAML
frontmatter. Minimal example:

```yaml
---
Stage: BUILD
Priority: P1
Depends-On: []
Ralph: true
Ralph-Reason: "Additive observability feature, 8 independent ACs, each grep/pytest-checkable"
---

# Add Example Feature

## Goal

Describe the user-visible outcome.

## Acceptance Criteria

- Given ...
- When ...
- Then ...
```

Frontmatter fields:

- `Stage:` — see below. Default to `BUILD` for implementation tickets.
- `Priority:` — `P0`/`P1`/`P2`.
- `Depends-On:` — list of slugs of tickets that must complete first. Must reference tickets that already exist.
- `Ralph:` / `Ralph-Reason:` — optional. When `true`, BUILD uses a fresh-subprocess loop per AC instead of one-shot. See [`shared/RALPH_DECISION_RULE.md`](../shared/RALPH_DECISION_RULE.md).
- `Requires-Assertions:` — optional list of assertion IDs (e.g., `[A1]`) that must be `validated` before this ticket runs. See `docs/developer-guide.md`.

## Stage To Use When Creating Tickets

For **implementation tickets**, default to `Stage: BUILD`. Orchestra will route
through spec/review as the mode requires.

Use `SPEC` or `SPEC_SPLIT` only for planning/specification artifacts that are
not yet ready to build.

## Pre-Run Checklist

Before calling `orch run`, verify:

- Target project root is correct
- `.tickets/` exists with at least one `Stage: BUILD` ticket
- Ticket frontmatter is valid YAML
- Every `Depends-On:` entry refers to an existing ticket slug
- Body includes concrete, observable acceptance criteria
- `AGENTS.md` and `STANDARDS.md` are present if the project relies on them

## Common Intake Mistakes

- Creating implementation tickets with `Stage: SPEC` by default
- Writing vague tickets with no observable acceptance criteria
- Referencing dependencies that do not exist yet
- Putting tickets outside `.tickets/`
- Manually writing handoff files — Orchestra manages `.orchestra/` artifacts itself

## CLI Invocation

```bash
orch run /path/to/project
```

Or, inside the Orchestra repo:

```bash
python main.py --project /path/to/project
```

## Pairs With

- **spec-writer** — produces the ticket body (goal, ACs, technical plan).
- **ticket-critic** — audits the ticket for readiness before BUILD.
- **antiplan** — upstream, for multi-ticket planning and PRD.
- **tdd** — runs inside each BUILD session for red-green-refactor.

## TDD Envelope (passed to /tdd at BUILD start)

When a BUILD session starts, pass these fields to /tdd so its Phase 0
([tdd/SCOPING.md](../tdd/SCOPING.md)) has deterministic inputs and does
not re-derive scope from prose:

| Field | Value | Source |
|---|---|---|
| `ticket_path` | `.tickets/NNN-slug.md` | current BUILD ticket |
| `diff_base` | merge-base of HEAD with main, or the previous ticket's completion SHA | git |
| `risk_registry` | `.risk-registry.yaml` at repo root, if present | repo convention |
| `prd_path` | `.tickets/prep/prd.md` | antiplan output |
| `toq_path` | `.tickets/tdd/toq-<ticket-id>.yaml` (/tdd writes here) | /tdd Phase 0 |

If a TOQ already exists and is fresher than the ticket (and `diff_base`
hasn't advanced), /tdd reuses it and skips Phase 0. Otherwise it
regenerates. This is the signal `/todo` checks when deciding whether to
recommend a re-scope.
