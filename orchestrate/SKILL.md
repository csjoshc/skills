---
name: orchestrate
description: >-
  Guide for agents and operators working outside the Orchestra repo itself.
  Explains how to prepare ticket files and project structure so Orchestra can
  ingest them correctly via the runtime CLI such as `orch run`.
---

# Orchestra Runtime Intake Guide

Use this skill when you are **outside the Orchestra repo** and need to prepare a
target project for ingestion by Orchestra's runtime CLI.

This skill is **not** the authoritative internal state machine for Orchestra's
own prompt artifacts. It is an operator guide for people and agents creating or
editing `.tickets/*.md` files that Orchestra will later consume.

## What This Skill Is For

- Preparing a target project so `orch` or `python main.py --project ...` can run
- Creating implementation-ready tickets in a target repo's `.tickets/` folder
- Verifying the minimum filesystem layout before handing the project to Orchestra
- Explaining which stage a newly created ticket should use for runtime ingestion

## What This Skill Is Not For

- Defining Orchestra's internal prompt-stage semantics
- Replacing the in-repo prompt artifacts under
  `orchestra/prompts/artifacts/skills/`
- Writing handoff files manually unless the workflow explicitly requires it

## Minimum Project Layout

Orchestra expects a **target project** with this structure:

```text
<project-root>/
  .tickets/
  .orchestra/
  AGENTS.md           # recommended
  STANDARDS.md        # recommended
```

Notes:

- `.tickets/` is where Orchestra discovers work items
- `.orchestra/` stores internal runtime state, handoff files, logs, worktrees,
  and the database after Orchestra starts running
- `AGENTS.md` and `STANDARDS.md` are strongly recommended because Orchestra
  agents use them for constraints and conventions

## Ticket Intake Rules

Every ticket file must:

1. Live under `<project-root>/.tickets/`
2. Start with YAML frontmatter
3. Include a canonical `Stage:` field
4. Be executable as a single work item with clear acceptance criteria

Minimal example:

```yaml
---
Stage: BUILD
Priority: P1
Depends-On: []
---

# Add Example Feature

## Goal

Describe the user-visible outcome.

## Acceptance Criteria

- Given ...
- When ...
- Then ...
```

## Which Stage To Use For New Tickets

For **implementation tickets being created for Orchestra ingestion**, default to:

- `Stage: BUILD`

Use `BUILD` when:

- The ticket is ready for implementation work
- The ticket already contains enough scope, requirements, and acceptance
  criteria for the runtime to act on it
- You want Orchestra to pick it up as executable work

Use `SPEC` or `SPEC_SPLIT` only when:

- The ticket is intentionally a planning/specification artifact
- The runtime should not treat it as ready-to-build implementation work yet

Practical rule:

- `.tickets/*.md` created for `orch run` should usually start at `Stage: BUILD`
- planning docs and PRD-like artifacts should stay in `SPEC` / `SPEC_SPLIT`

## Handoff Guidance

Do **not** assume you must manually create handoff files before Orchestra can
run.

For normal runtime ingestion:

- Humans/agents prepare the ticket in `.tickets/`
- Orchestra ingests the ticket
- Orchestra writes runtime artifacts under `.orchestra/`, including handoff
  context as the workflow progresses

Only write a handoff file manually if the current repo's workflow explicitly
calls for that. Otherwise, treat handoff content as an Orchestra-managed
artifact, not an intake prerequisite.

## Pre-Run Checklist

Before calling `orch run` or the equivalent project command, verify:

- The target project root is correct
- `.tickets/` exists
- At least one ticket is present with `Stage: BUILD`
- Ticket frontmatter is valid YAML
- `Depends-On` references only tickets that already exist
- The ticket body includes concrete acceptance criteria
- `AGENTS.md` and `STANDARDS.md` are present if the project relies on them

## Common Intake Mistakes

Avoid these:

- Creating implementation tickets with `Stage: SPEC` by default
- Treating handoff files as mandatory pre-ingestion inputs
- Putting tickets outside `.tickets/`
- Writing vague tickets with no observable acceptance criteria
- Referencing dependencies that do not exist yet

## Operator Commands

Common patterns:

```bash
orch run /path/to/project
```

or, inside the Orchestra repo:

```bash
python main.py --project /path/to/project
```

If supported by the current wrapper or local shell setup, dry-run and
single-ticket invocations can also be used to verify discovery before full
execution.

## Rule Of Thumb

If you are preparing tickets **for Orchestra to execute**, think like an intake
operator:

- put the ticket in `.tickets/`
- make it concrete
- default it to `Stage: BUILD`
- let Orchestra generate runtime artifacts after ingestion
