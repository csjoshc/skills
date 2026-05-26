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

## Gitignored Orch Directories

These directories are orch-internal and must **never** appear as added files in upstream PRs.
Ensure `.gitignore` covers all of them:

```
tests/tickets/   # DEPRECATED staging area — write tests to permanent paths directly
evidence/        # docker logs, gate artifacts
proof/           # screenshots, replay transcripts
.plan/           # PRD + task-sequence from make-prd/antiplan
.tickets*        # ticket markdown files
.orchestra*      # orch internal state
```

**Test authoring rule — write directly to the permanent path:**  
Never use `tests/tickets/` as a staging area. The ticket's AC→Test Traceability table names
the destination before BUILD starts; write the file there from the first keystroke.

| Test type | Permanent committed path |
|---|---|
| Dockerfile / Helm / nginx / CI workflow regression | `tests/infra/test_<artifact>.py` |
| Documentation consistency | `tests/docs/test_<topic>.py` |
| Package unit/integration | `packages/<pkg>/tests/test_<module>.py` |
| E2E | `tests/template_agent_e2e/` |

The per-file `test_coverage_anchor` + `import agent_guardrails` function handles the orch
coverage gate for YAML/Dockerfile-only diffs — no `conftest.py` shim needed.

PRs that include `tests/tickets/`, `evidence/`, or `proof/` as **added** files must be blocked at review.

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

## Docs to Update

- [ ] `path/to/doc.md` — what to change there
- [ ] `path/to/diagram.mmd` — what to update
<!-- Or "- [ ] None — internal change" when truly nothing user-visible -->
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
- Body includes a `## Docs to Update` section (or an explicit "None — internal change")
- `AGENTS.md` and `STANDARDS.md` are present if the project relies on them

### Source-prose hygiene scan (before BUILD)

Before any BUILD ticket starts, scan the working tree for skill-internal
scaffolding vocabulary that would leak into committed code if the ticket
mandates touching those files. This is the same patterns set as
[`~/.skills/shared/SKILL_NOISE_TERMS.md`](../shared/SKILL_NOISE_TERMS.md):

```bash
# Run from the project root. Excludes planning artifacts (.tickets, .plan, .handoff, .orchestra)
# and historical proof/.
git grep -nE '(ADR-[A-Z0-9-]+|T-[0-9]{3,}|FR-[0-9]+|NFR-[0-9]+|RISK-[0-9]+|IG-[0-9]+G[0-9]*|[0-9]+G[0-9]+|Slice [0-9]+|Constitution P[0-9]+|AP-[0-9]+)' \
  -- '*.py' '*.ts' '*.tsx' '*.js' '*.mjs' '*.sh' '*.md' '*.mmd' '*.yaml' '*.yml' \
  ':!.tickets' ':!.plan' ':!.handoff' ':!.orchestra' ':!docs/ADR-*' ':!proof/' \
  | head -40
```

Pre-existing hits are not a hard block, but the ticket author should
record them in the ticket's `## Notes` so the BUILD phase doesn't
inadvertently propagate the pattern to new files.

## Common Intake Mistakes

- Creating implementation tickets with `Stage: SPEC` by default
- Writing vague tickets with no observable acceptance criteria
- Referencing dependencies that do not exist yet
- Putting tickets outside `.tickets/`
- Naming proof / verify / fixture files after the ticket itself (`scripts/verify-T-732.sh`, `proof/4G-ui-cycle/`) — these names rot once the ticket closes; use feature- or test-scoped names and make per-cycle directories env-overridable
- Pasting review-time finding codes (`F-001`, `RISK-NN`, `AP-NN`, `Pattern 12`) into source code or doc bodies that the ticket mandates — those labels belong in commit messages and PR threads
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
