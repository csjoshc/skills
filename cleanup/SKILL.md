---
name: cleanup
description: >-
  Reviews existing source code and codebases against a quality rubric covering
  mechanical checks, subjective dimensions, anti-patterns, and layering. Use
  when running code audits, holistic code-health checks, or preparing for PR
  review. Does NOT post GitHub comments or edit tickets — use pr-review for
  live PR feedback and ticket-critic for .tickets/.
---

# cleanup

Reviews existing source code against a quality rubric with file-cited evidence.
Maps findings to rubric dimensions (M1–M12 patterns, subjective tiers A–I,
AI anti-patterns).

**Does NOT post GitHub comments.** For live PR review with inline GitHub
comments, use the `pr-review` skill.

## Contents

- When to use
- Mandatory pre-reads
- Workflow
- Phase 0 — Mechanical pass
- Phase 1 — Parallel specialist lenses
- Output contracts
- Persona
- Companion files
- Scope boundary
- Decision tree

---

## When to Use

- Code audits on a directory, package, or file set
- Pre-PR prep (local audit before opening a PR)
- Holistic code-health checks across a repo
- Remediation planning after a quality gate failure

**Not for:** editing `.tickets/*.md`, epic splits, implementation specs → use
`ticket-critic`. Not for posting GitHub review comments → use `pr-review`.

---

## Mandatory Pre-Reads

Load on every invocation:

1. **`AGENTS.md`** in the repo root — exclusions, layer map, agent rules.
2. **`~/.skills/shared/QUALITY_RUBRIC.md`** — full criteria.
3. **[`~/.skills/reviews/schemas.md`](../reviews/schemas.md)** — required output
   block contracts (`REVIEW-PHASE-0`, `REVIEW-FINDINGS`, `REVIEW-LEDGER`,
   `REVIEW-GATE`).
4. **[`~/.skills/reviews/runbook.md`](../reviews/runbook.md)** — fixed phase
   sequence shared with `pr-review`.

Load on demand:

5. **`redundancy-watcher.md`** — before any `Write` of a new file or export.
6. **`layer-boundary-critic.md`** — during Phase 0 when imports change.

---

## Workflow

1. **Scope** — use paths, package, or PR diff the user named; default to
   project source per `AGENTS.md`.
2. **Phase 0 — Mechanical pass** — deterministic first; emit a
   `REVIEW-PHASE-0` block (schema in `~/.skills/reviews/schemas.md`). Do not
   start subjective rubric mapping until every row is `RESOLVED` or
   `OVERRIDDEN`.
3. **Emit** `REVIEW-GATE: phase-0 → phase-1. Criteria: [...]. Proceeding: yes|no.`
   before continuing.
4. **Phase 1 — Parallel specialist lenses** — launch 4 lenses as
   sub-agents in parallel, each scoped to one architectural domain (see
   *Phase 1 — Parallel Specialist Lenses* below). Each lens emits its own
   `REVIEW-FINDINGS` block. Skip parallel execution if the scope is ≤ 3
   files; fall back to a single lens.
5. **Evidence** — every finding needs: `file`, `line`, `source` tag,
   `evidence`, `suggested_fix`. Structural findings also need `proof:` —
   triggered by `severity: CRITICAL` (any category), `category:
   Architectural Drift`, or `category: Layer` at `HIGH`/`CRITICAL`.
6. **Emit** `REVIEW-GATE: phase-1 → report. Criteria: [validation_pass: met]. Proceeding: yes.`
7. **Emit** `REVIEW-LEDGER` YAML — counts computed from the findings blocks.
8. **Prioritize** — Tier A–C subjective issues and M-patterns affecting
   reliability or security first.
9. **Validate** — run `python3 ~/.skills/reviews/validate.py --transcript <out>`.
   Exit 0 before handing the report to the user.

---

## Phase 0 — Mechanical Pass

Run these deterministic checks before any LLM-driven reasoning. Every
Phase 0 finding is non-negotiable — a later subjective judgment cannot
dismiss it.

| Check                      | Python                                 | TypeScript/JS                               |
| -------------------------- | -------------------------------------- | ------------------------------------------- |
| Unused imports/vars        | `ruff check --select F401,F841`        | `npx eslint --rule 'no-unused-vars: error'` |
| Unused exports             | `vulture --min-confidence 80`          | `npx ts-prune`, `npx knip`                  |
| File size                  | `wc -l` vs 300/500 thresholds          | same                                        |
| Cyclomatic complexity      | `radon cc -n C` (>10 = refactor)       | `npx complexity-report`                     |
| Duplication                | `jscpd .` (>5% = consolidate)          | same                                        |
| Import cycles              | `pycycle` / `importlinter`             | `npx madge --circular`                      |
| **Layer boundaries**       | delegate to `layer-boundary-critic.md` | same                                        |
| **Dead code / redundancy** | delegate to `redundancy-watcher.md`    | same                                        |
| Dead branches              | `# pragma: no cover` without reason    | `istanbul ignore` without reason            |
| Commented-out blocks       | `grep -En '^\s*(#\|//)[^!]'`           | same                                        |

Emit Phase 0 output in the `REVIEW-PHASE-0` block (schema:
[`~/.skills/reviews/schemas.md`](../reviews/schemas.md)):

````markdown
```REVIEW-PHASE-0
| tool | rule | file | line | severity | status |
| ---- | ---- | ---- | ---- | -------- | ------ |
| ruff | F401 | src/auth.py | 4 | MEDIUM | RESOLVED |
| wc -l | file-size | src/ui/Dashboard.tsx | 847 | HIGH | OVERRIDDEN |
```
````

Every row's `status` must be `RESOLVED` or `OVERRIDDEN` (with a written
justification) before emitting the gate:

```
REVIEW-GATE: phase-0 → phase-1. Criteria: [all rows resolved: met]. Proceeding: yes.
```

The validator rejects `Proceeding: yes` with any `OPEN` row.

---

## Phase 1 — Parallel Specialist Lenses

After Phase 0 clears its gate, Phase 1 runs **4 lenses in parallel**,
each scoped to a domain of architectural concern. Each lens has a narrow
focus, an N-of-M checklist threshold, and loads only the rubric codes
and `arch-violations/` files it owns.

| Lens | Focus | Owns rubric codes | Owns arch-violations |
| --- | --- | --- | --- |
| **Layer & Dependency** | Upward/sideways imports, cycles, leaking implementation types, boundary contracts | M-pattern layer violations; Tier A (architectural) | [01-dependency-direction](../reviews/arch-violations/01-dependency-direction.md), [02-boundary-contracts](../reviews/arch-violations/02-boundary-contracts.md) |
| **Redundancy & Modularity** | Duplicate cross-cutting concerns, parallel implementations, god modules, speculative generality | Tier A (modularity), AI anti-patterns | [08-modularity](../reviews/arch-violations/08-modularity.md), [11-ai-specific](../reviews/arch-violations/11-ai-specific.md) |
| **Error Handling & State** | Swallowed errors, over-broad catches, shared mutable state, race conditions, transactional boundaries | M1, M2, M5, M7; Tier G | [03-state-concurrency](../reviews/arch-violations/03-state-concurrency.md), [04-error-handling](../reviews/arch-violations/04-error-handling.md) |
| **Data & Security** | Unbounded queries, N+1, missing timeouts, auth scattering, trust-boundary confusion | M3, M4; Tier B | [05-data-layer](../reviews/arch-violations/05-data-layer.md), [06-security](../reviews/arch-violations/06-security.md) |

### Lens execution

Launch each lens as a sub-agent in parallel (one message, multiple
`Agent` tool calls). Each lens receives:

- The files in scope (Phase 0 may have narrowed the set).
- Its owning rubric codes from [`~/.skills/shared/QUALITY_RUBRIC.md`](~/.skills/shared/QUALITY_RUBRIC.md).
- Its owning `arch-violations/` files.
- The Phase 0 table (tool-flagged rows may be promoted into lens findings).

Each lens emits its own `REVIEW-FINDINGS` block. A lens can also emit
zero findings — legitimate when the scope doesn't contain anything
relevant.

### Checklist threshold

Each lens adopts the N-of-M pattern from `pr-review/reference/review-lenses.md`:

| Lens | Threshold |
| --- | --- |
| Layer & Dependency | 4 of 4 YES |
| Redundancy & Modularity | 3 of 4 YES |
| Error Handling & State | 3 of 4 YES |
| Data & Security | 4 of 5 YES (add severity-escalation criterion) |

A finding that does not meet threshold is dropped, not downgraded.

### Deduplication and ordering

After all lenses emit, merge and sort before the ledger:

1. Drop duplicates (same file + line + rule_code).
2. If a rubric-derived finding overlaps an arch-violation finding, prefer
   the arch-violation (stronger architectural signal).
3. Sort by category: Layer → Architectural Drift → Error Handling → Bug
   → Redundancy → Modularity → Standards → Test Gap.

### When to skip parallel execution

For a scope of ≤ 3 files, running 4 lenses is overhead without benefit.
Fall back to a single-lens pass using whichever lens most closely matches
the scope.

---

<!-- pattern: common-rationalizations -->
## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It's working, leave it alone" | Working code with bad layering breaks the next change. |
| "Refactor is out of scope" | Cleanup is the scope. Flag what's in-scope vs deferred. |
| "Comments are documentation" | Stale comments mislead. Code is the source of truth. |
| "We'll revisit later" | "Later" doesn't come. Either fix or file a tracked DEBT-NN. |

---

## Output Contracts

Every cleanup run emits, in order:

1. `REVIEW-PHASE-0` fenced block (tool table).
2. `REVIEW-GATE: phase-0 → phase-1`.
3. One or more `REVIEW-FINDINGS` fenced blocks (findings by dimension).
4. `REVIEW-GATE: phase-1 → report`.
5. `REVIEW-LEDGER` YAML.

Findings carry a `source` tag from `{tool-flagged, rubric-derived,
user-confirmed}`. `tool-flagged` entries are promoted from the Phase 0
table; `rubric-derived` entries map to M1–M12 / Tier A–I codes.
Structural findings additionally carry `proof:` — a reproducible
command, failing test, or log excerpt. The rule fires on `severity:
CRITICAL` (any category), `category: Architectural Drift`, or `category:
Layer` at `HIGH`/`CRITICAL`.

Run `python3 ~/.skills/reviews/validate.py --transcript <report>` as the
final step. Exit 0 is required before handing the report back.

---

## Persona

**Principal Staff Engineer.** Favor deletion of redundant AI-generated code.
Pragmatic modularity — no speculative abstractions. One standard per
cross-cutting concern (logging, config, errors, file I/O).

---

## Companion Files

| File                                                   | Role                                                     | Load when                     |
| ------------------------------------------------------ | -------------------------------------------------------- | ----------------------------- |
| [`~/.skills/shared/QUALITY_RUBRIC.md`](~/.skills/shared/QUALITY_RUBRIC.md) | Full rubric: M1–M12, Tiers A–I, anti-patterns, layers    | Every invocation              |
| [`../reviews/schemas.md`](../reviews/schemas.md)       | Fenced-block schemas and source-tag rules                | Every invocation              |
| [`../reviews/runbook.md`](../reviews/runbook.md)       | Fixed phase sequence shared with pr-review               | Every invocation              |
| [`../reviews/validate.py`](../reviews/validate.py)     | Pre-report validator (stdlib-only)                       | Final step, before reporting  |
| [`../reviews/arch-violations/`](../reviews/arch-violations/) | Architectural-violation catalog (11 files; index in README.md) | When Phase 1 lenses run        |
| [`redundancy-watcher.md`](redundancy-watcher.md)       | Blocks duplicate implementations at write time           | Before any new file or export |
| [`layer-boundary-critic.md`](layer-boundary-critic.md) | Enforces downward-only imports from AGENTS.md layer cake | Phase 0 when imports change   |
| [`ARCHITECTURE_DEPTH.md`](ARCHITECTURE_DEPTH.md)       | Architectural depth lens (module/seam/depth/deletion test) | Phase 1 when scope includes multi-module design |

---

## Scope Boundary

| In scope                    | Out of scope                                     |
| --------------------------- | ------------------------------------------------ |
| Source code audits          | Editing `.tickets/*.md` → ticket-critic          |
| Pre-PR local prep           | Live PR comments on GitHub → pr-review           |
| Architecture pattern checks | Visual UI validation → make-ui / chrome-devtools |

---

## Decision Tree

**What is the scope?**

- PR diff → focus on changed files, M-patterns in diff
- Full codebase → use AGENTS.md exclusions, scan systematically
- Specific directory → scope to named path

**What issues matter most?**

- Security → M1–M4
- Maintainability → M5–M8
- Testing → M9–M12
- General → all, prioritize Tier A + M1–M4
