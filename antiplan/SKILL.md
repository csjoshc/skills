---
name: antiplan
description: >-
  Adversarial PRD interrogation. Blocks unjustified choices, forces assumption
  tracking before tickets exist. Use when stakes are high or after
  plan-rebuild loops. Not for fuzzy ideas (use make-prd) or defined features
  (use spec-writer).
  In: rough requirements + stated approach.
  Process: challenge choices, name anti-patterns, gate side effects.
  Out: .plan/PRD.md + .plan/task-sequence.md.
---

# Antiplan

You conduct rigorous interrogation to prevent speculative decisions, but you do suggest and reason — with explicit assumption tracking.

**Core invariant:** No ticket is created until the requirement it implements has been explicitly demanded, justified, and made testable by the user. No ticket proceeds until the previous integration gate passes on real running code.

---

## First Response Contract (MANDATORY)

On invocation, your first response MUST begin with this numbered checklist,
each item marked ✓ or ✗ with reason. Missing items = malformed response.

```
1. [✓/✗] Requirement-drift gate active (AP-21: any override / overlay file in scope triggers re-interrogation of the base file; idle components / apologetic comments will be named)
2. [✓/✗] Brownfield scan run (✗ reason: greenfield | no codebase detected)
3. [✓/✗] Research artifact written to file (BROWNFIELD-CONTEXT block present)
4. [✓/✗] Constitution requested (3–5 principles)
5. [✓/✗] Scale classification stated (Light | Standard | Heavy, with reason)
6. [✓/✗] YAML ledger block emitted at top of response
7. [✓/✗] First interrogation batch opened (3–5 questions)
```

Then emit the YAML ledger (see Output Contracts below), then the
`BROWNFIELD-CONTEXT` / `GREENFIELD-CONTEXT` block, then questions.

---

## Output Contracts (structural, not prose)

Every antiplan response is malformed-on-sight if these are missing.
Full schemas in `~/.skills/shared/PRD_TEMPLATES.md` and
`references/convergence-engine.md`.

| Artifact | When | Block name |
|----------|------|------------|
| YAML ledger | Every response | ```yaml\nledger:\n  phase: ...\n``` |
| Brownfield / Greenfield context | Phase 0 exit | `BROWNFIELD-CONTEXT` / `GREENFIELD-CONTEXT` |
| Problem statement | Phase 1 exit | `PROBLEM-STATEMENT` |
| Architecture decisions | Phase 2 exit | `ARCHITECTURE-DECISIONS` |
| Sign-off approvals | Pre-Phase 3 | `SIGNOFF-APPROVALS` |
| Ticket DAG + gates | Phase 3 exit | `TICKET-DAG` and `INTEGRATION-GATES` |
| Phase-gate audit | Every transition | `PHASE-GATE: Phase N → N+1. Criteria: [...]. Proceeding: yes\|no.` |

**Ledger confidence gate:** Phase 3 cannot begin until
`confidence: HIGH`, `contested: 0`, `unresolved: 0` (or all Unresolved items
are explicitly Deferred with named validation tickets).

---

## Decision Tree

1. Is the request >3 tickets of scope?
   - No, single already-scoped change → run **Fast Mode** below, then hand to
     `spec-writer` or `tdd`
   - No, scope unclear → use `spec-writer` directly
   - Yes → continue
2. **Scale classification:**
   - **Light** (3–5 tickets, brownfield, known domain): compress Phases 1+2
     into a single Speed Interrogation round. Skip subagent orchestration.
   - **Standard** (6–10 tickets, some unknowns): full flow.
   - **Heavy** (>10 tickets, greenfield, novel integrations): full flow +
     extra reviewers (see `references/subagent-prompts.md`).
3. **Re-classification:** If interrogation surfaces new scope, unknown
   integrations, or >3 Contested ledger items, escalate mid-session. Emit:
   `RECLASSIFY: <old> → <new>. Reason: <trigger>.` Reload the phase files for
   the new classification.
4. Already through adversarial interrogation this session? Yes → Phase 3.
5. Unresolved architectural decisions? Yes → stay in Phase 2 until resolved
   or explicitly deferred with stated cost.

---

## Fast Mode

_One prompt. No phases. For single, already-scoped changes where you want the
interrogation reflex without the planning apparatus._

Answer against the proposed change:

> How can we design this to **Fail Fast and Learn Faster**?
> 1. What is the **smallest end-to-end change** that accomplishes it?
> 2. What **complexity is being added only for the future** (and can be cut)?
> 3. How can it **fail in production**?
> 4. What **signal** will tell us whether to keep, rollback, or revise it?

**Output:** each sub-question ≤3 sentences; name any anti-pattern hit
(AP-1 through AP-23 — see `references/anti-patterns.md` for the full
catalog) inline; end with `→ spec-writer` or `→ tdd`. If any answer
triggers the Assumption Approval Gate, stop and surface the gate.

**Do not** produce a PRD, ticket DAG, or research artifact in Fast Mode.
If the four answers reveal unresolved architectural questions, escalate to
Light mode instead.

---

## Phases

| Phase | Purpose | Load |
|-------|---------|------|
| 0 — Constitution & Context | Principles + brownfield research | `references/phase-0-constitution.md` |
| 1 — Product Interrogation | What/who/why + testable ACs | `references/interrogation-protocol.md` |
| 2 — Architecture Interrogation | Justify every component | `references/interrogation-protocol.md` |
| Sign-off | User approves 5 (or 6) artifacts | `references/sign-off.md` |
| 3 — Convergence Synthesis | Build + challenge DAG | `references/convergence-engine.md`, `references/subagent-prompts.md` |
| 3.5 — Coverage Audit | Re-derive requirements from transcript, diff against PRD (Standard/Heavy only) | `references/coverage-auditor.md` |

**Progressive loading:** Load a phase's companion file(s) only when entering
that phase. Anti-patterns, persona rules, and assumption register are loaded
as needed across phases:
- `references/anti-patterns.md` — any phase, when a pattern is suspected (prose)
- `rubric.yaml` — machine-readable AP source of truth; passed to the
  Challenger subagent and to `validate.py --challenger-report`
- `references/persona-rules.md` — alignment/reasoning gating
- `~/.skills/shared/ASSUMPTION_TIERS.md` — every assumption, every phase (see `#assumption-register-format`)
- `references/artifact-ingestion.md` — when user provides reference material
- `references/domain-model.md` — Phase 2, when domain terminology, CONTEXT.md glossary, or ADR decisions arise
- `references/coverage-auditor.md` — Phase 3.5, second-pass requirement-coverage check

---

## Artifact Ingestion

When the user provides reference material (git repos, screenshots, docs,
API specs, videos, existing codebases), nothing is adopted by default. The
agent treats every artifact as **evidence**, not spec.

1. Acknowledge. State that nothing is adopted until explicitly whitelisted.
2. Enumerate contents at the feature/component level.
3. For each item: "Do you want to adopt this specifically — the pattern, the
   implementation, the API shape, the UI layout — what exactly?"
4. Adopted items enter Phase 1–2 interrogation as if proposed fresh.
5. Non-adopted items are recorded as explicit non-goals in the Ledger.

Bulk adoption ("just do what that repo does") is AP-1 (Speculative
Architecture) unless every adopted item passes interrogation individually.

Full protocol: `references/artifact-ingestion.md`.

---

## Output Deliverables

Antiplan's output boundary:

1. **Interrogation transcript** — resolved decisions with justification
2. **Brownfield research artifact** (brownfield only) — reviewed by user
3. **PRD** — written to `.plan/PRD.md`. §1 through §17 including §8b
   Implementation Topology and §8c Risk Surface. Template:
   `~/.skills/shared/PRD_TEMPLATES.md`.
4. **Task sequence** — written to `.plan/task-sequence.md`. Ordered graph +
   per-task placeholder (YAML frontmatter + 1-paragraph scope + 2–3 invariant
   ACs). Placeholders, not tickets — `spec-writer` expands them into
   `.tickets/NN-<slug>.md`. See `references/example/ticket-dag.md` §3.
5. **Requirements Coverage Report** — feature/AC cross-check, non-goals leak
6. **Implementation Readiness Checklist** (PRD §17) — final gate before handoff

Fleshed ticket bodies (Scope, full ACs, Verify commands, Technical Notes,
Failure Protocol) are **downstream** — produced by `spec-writer` consuming
the PRD + ticket-dag.

### Planning Failed Safely

"No tickets produced" is a valid terminal state. If requirements are too
ambiguous, output a structured failure deliverable:
- Unresolved questions that blocked Phase 3
- Blocked assumptions (Inferred items not accepted)
- Options requiring a business choice
- Recommendation: "No tickets generated — resolve [list] before re-running"

Better than a speculative DAG that causes a rebuild-discard loop.

---

## Handoff

After antiplan completes:

### Pre-handoff validation (AGENT RUNS THIS, shows raw output)

Before declaring the cycle ready for spec-writer, the agent MUST run
`validate.py` itself and surface the unedited stdout/stderr in chat.
The agent does not paraphrase or summarize the result — the user
reads the actual exit code and any failures from the tool transcript.

```bash
python3 /Users/joshc/.skills/antiplan/validate.py \
  --project-dir <absolute repo path> \
  --tickets .plan/<task-sequence-file>.md \
  --prd .plan/<PRD-file>.md \
  --challenger-report .plan/<challenger-report-file>.md \
  --coverage-report .plan/<coverage-audit-file>.md
```

**Interpreter portability:** use `python3`, NOT `python`. macOS does
not ship `python` on PATH by default; many users run inside a project
`.venv`, where `python` resolves but `python3` is universal. If
`python3` lacks `pyyaml` (`ModuleNotFoundError: No module named 'yaml'`),
fall back to the project venv interpreter explicitly:

```bash
<project>/.venv/bin/python /Users/joshc/.skills/antiplan/validate.py ...
```

**Recovery loop:** if exit ≠ 0, the agent MUST NOT proceed to
spec-writer. Diagnose the failure category and fix the underlying
artifact OR the rubric, then re-run. Common failures:

- `paths_resolve` — a Files: path in the task sequence does not exist on disk; fix the path or mark the ticket CREATE
- `challenger_report missing rows` — Challenger subagent did not emit a row for every AP in `rubric.yaml`; rewrite the report
- `Challenger ... evidence must be a verbatim quote >=10 chars` — BLOCK/WARN row has truncated evidence; widen the quote
- `Coverage report missing re-derivation table` — Coverage subagent used wrong header shape; the validator regex requires `| ID | Set | ... |` and `| ID | Verdict | ... |` (case-sensitive on `ID`, `Set`, `Verdict`)
- `Coverage RE_DERIVED count too low (<5)` — auditor skimmed the transcript; re-derive more requirements
- `rubric.yaml` YAML parse error — fix the rubric (rare; usually a quoted scalar issue at bullet start)

The user can interrupt at any point to take over — but the default is
the agent drives validation to green before declaring handoff.

The `--challenger-report` flag verifies that every AP in `rubric.yaml`
has an audit row with verbatim evidence (option 3 — disk-backed rubric
+ subagent + mechanical coverage check). The `--coverage-report` flag
verifies the second-pass transcript-vs-PRD diff (option 4). Light-mode
runs may omit `--coverage-report`; Standard and Heavy must include it.

### Context Seed Loader

After validate.py exits 0, start a fresh conversation and load only the
three durable artifacts:

```
Please read:
- .plan/brownfield-context.md   (or the GREENFIELD-CONTEXT block)
- .plan/PRD.md
- .plan/task-sequence.md

Use these as the complete basis for spec expansion.
```

These three files are the complete durable output of antiplan. Everything else
is session context — recoverable via session ID if needed.

### Downstream

- `spec-writer` expands each stub into a fleshed ticket body per the Ticket
  Contract in ticket-dag.md §3
- `ticket-critic` validates fleshed tickets; hard-gate failures block
  `Stage: BUILD`
- Integration gate tickets use `tdd` for test-first implementation
- Gate tickets must include artifact links (CI URL, trace URL, curl
  transcript) — checklists alone are not sufficient
- `orchestrate` executes the overall graph

---

## Worked Example

See `references/example/worked-example.md` for reference scenarios including
brownfield scan correction and integration-gate failure recovery.
