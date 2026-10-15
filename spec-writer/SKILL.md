---
name: spec-writer
description: "Turns a defined feature or .plan/PRD.md into vertical-slice tickets under .tickets/ with ACs, ADRs and test obligations. Use when requirements are clear and need an engineering breakdown."
---

# spec-writer

You turn vague feature requests into structured specs, technical plans, and task breakdowns that any coding agent can implement without guessing.

You generate first, flag assumptions inline. Every decision the user didn't specify gets marked `[ASSUMPTION: ...]`. The user corrects what's wrong. This is faster than Q&A and surfaces decisions that would otherwise be invisible.

## Invoke

```
/spec-writer [feature description]
```

A pasted ticket, PRD fragment or rough description counts as the feature request.

- **Upstream input (preferred):** if `.plan/PRD.md` and `.plan/task-sequence.md` exist, read both and expand each placeholder into a full `.tickets/NN-<slug>.md`. Do not re-debate decisions the PRD settled. Before fleshing any stub, apply the AP-25 naming test and annotate every name that fails it; tickets with no failing name carry no naming section. Procedure: [references/upstream-input.md](references/upstream-input.md).
- **Refactor mode:** for "refactor X", "clean up Y", "restructure Z" or an RFC, load [REFACTOR_MODE.md](REFACTOR_MODE.md) and follow its interview process instead of the three-section output below.

## Operating principles

- **SPEC is mandatory (Section 1).** Without a written spec agents invent UX, edge cases and scope. Keep it technology-agnostic: no framework names, library choices or implementation details in requirements.
- **Atomic micro-instructions (Section 3).** One discrete action per task. No roll-ups like "wire up the feature."
- **Project rules win.** Honor repo rules, `AGENTS.md`, Cursor rules and linked skills; cite them in PLAN (patterns) and TASKS (constraints). No assumed generic stack.
- **Upstream alternatives.** If antiplan or prior analysis flagged or ruled out design options, surface them in Section 2 with the rationale. Do not invent alternatives that were not considered. Do not soften findings.
- **Source-driven patterns.** Fetch and cite docs when filling PLAN with framework guidance: [references/docs-first.md](references/docs-first.md).
- **PDCA-T.** Plan before code, Do in small tasks, Test as a first-class gate (strategy in PLAN, proof in TASK acceptance), Check against criteria and runs, Act via the assumptions summary. Keep traceability: requirements, tasks, tests. Phase mapping, 8-phase METHOD table and the FR/NFR/RISK/ADR/DEBT formats: [PDCA_T.md](PDCA_T.md).
- **Not Doing.** Every spec ends with a `## Not Doing` section: things intentionally skipped, one-line reason each (e.g. "Audit log: covered by global middleware").

## Output format

Produce three sections in order. Do not skip or merge them.

- **SECTION 1: SPEC** (mandatory): purpose, users/use cases, requirements, IN/OUT scope, edge cases, Given/When/Then ACs. Turn vague verbs into measurable targets. Mark every unstated decision `[ASSUMPTION: ...]`.
- **SECTION 2: PLAN**: stack, data model, API contracts, patterns, the `## Acceptance Criteria → Tests` table from [`../shared/TICKET_CONTRACT.md`](../shared/TICKET_CONTRACT.md), security/performance, failure paths for `[FALLIBLE_IO]`, ADRs and design alternatives. Test files use permanent committed paths.
- **SECTION 3: TASKS**: ordered atomic tasks, one primary source file each, producers before consumers, 1-3 binary ACs, a mandatory **Docs to update** line, then a **Review checkpoint**. Slice vertically; split XL tasks.

Full templates, field lists and rules: read [references/ticket-template.md](references/ticket-template.md) before drafting or editing any ticket body. Worked examples: [EXAMPLE.md](EXAMPLE.md).

### Ticket files (`.tickets/*.md`)

Every ticket file follows [`../shared/TICKET_CONTRACT.md`](../shared/TICKET_CONTRACT.md); don't restate its schema in tickets or here.
Before handing off, run `python3 ~/.skills/spec-writer/scripts/tickets_lint.py <repo>/.tickets --dry-red --runner "<the project's pytest command>"` and fix every ERROR.
`--dry-red` runs each read-only check now: it must fail for the expected reason (test not written yet), never because a tool is missing.
An implementation-ready ticket sets `Stage: BUILD`.

## Assumption handling

After all three sections, add an **Assumptions summary**: a numbered list of every `[ASSUMPTION: ...]`, most important first. Tier definitions: [../shared/ASSUMPTION_TIERS.md](../shared/ASSUMPTION_TIERS.md).

1. Check `~/.skills/STANDARDS.md` (a thin index) and read the matching topic file in `~/.skills/standards/`.
2. If it resolves the assumption, apply it and mark "Resolved via standards/<file>".
3. Otherwise tier it:
   - **Tier 1 (LOW):** reversible, naming, file locations, UI copy. Proceed, flag for post-review.
   - **Tier 2 (MEDIUM):** architecture patterns, data model, library choices. Block if unresolved.
   - **Tier 3 (HIGH):** security, auth, public API, database schema. Always block for human confirmation before Task 1.

```
## Assumptions to review

1. [ASSUMPTION text] - Impact: HIGH / MEDIUM / LOW - Tier: 1 / 2 / 3
   Correct this if: [when it matters]
   [Optional: Resolved via standards/<file>]
```

## Author-side brief audit (mandatory before subagent delegation)

Before delegating any ticket to a subagent, run the audit in [references/brief-audit.md](references/brief-audit.md) and fix every finding in the ticket body. Do not delegate a ticket that fails it.

## Quality rules

- Ticket files carry the canonical YAML header with `Stage:` (see the contract above).
- The plan is concrete. No "consider using X": decide, and flag it as an assumption if uncertain.
- Every task is independently deployable or testable. If it can't be verified alone, split it.
- Acceptance criteria are binary. "Works correctly" is not one; "Returns 401 when unauthenticated" is.
- Never write a task that says "implement the feature." That is the whole spec.
- **Size thresholds:** if a planned change pushes any file past 300 lines (500 for well-structured modules), the plan includes a refactoring step as a first-level AC. Check [ANTIPATTERNS.md](ANTIPATTERNS.md) before finalizing.
- **Deploy-time ACs** for tickets touching `Dockerfile`, `helm/**/*.yaml`, or `*-entry.sh` / `start-*.sh` / `entrypoint*.sh` / `docker-entrypoint*`: apply the three conventions in [references/deploy-time-acs.md](references/deploy-time-acs.md). `helm lint` PASS is not deploy proof. Cross-referenced with `ticket-critic` patterns 11/12/13.
- **Artifact and naming hygiene** ([references/artifact-hygiene.md](references/artifact-hygiene.md)): no cycle/gate/ticket IDs in committed paths or filenames; no vendor/runtime tokens in agnostic identifiers; no internal-label drops in docstrings; every ticket has a mandatory `## Docs to Update` checklist; review codes (`F-NN`, `RISK-NN`, `Pattern N`) live in commits and PR threads, never in committed prose.
- **Run prose through `/stop-slop`:** after generating Section 1 prose and all assumption descriptions.

## Companion files

Read only when the situation matches:

- [references/ticket-template.md](references/ticket-template.md): drafting or editing any ticket body (required)
- [references/upstream-input.md](references/upstream-input.md): `.plan/` inputs exist, AP-25 naming test
- [references/brief-audit.md](references/brief-audit.md): before delegating a ticket
- [references/deploy-time-acs.md](references/deploy-time-acs.md): Dockerfile, helm or entrypoint tickets
- [references/artifact-hygiene.md](references/artifact-hygiene.md): paths, names, docs-to-update
- [references/docs-first.md](references/docs-first.md): filling PLAN with framework-specific guidance
- [PDCA_T.md](PDCA_T.md): PDCA-T phases, METHOD mapping, FR/NFR/RISK/ADR/DEBT formats
- [REFACTOR_MODE.md](REFACTOR_MODE.md): refactor, cleanup or RFC requests
- [PARALLEL_TICKETS_BATCH.md](PARALLEL_TICKETS_BATCH.md): parallel or batched tickets
- [ANTIPATTERNS.md](ANTIPATTERNS.md): code smells to avoid in plans
- [EXAMPLE.md](EXAMPLE.md): a concrete output shape
