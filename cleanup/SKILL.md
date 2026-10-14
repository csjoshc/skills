---
name: cleanup
description: "Audits an existing repo, package or directory against a code-health rubric (mechanical checks, anti-patterns, layering, depth). Use when asked for a code-health or architecture audit of existing code rather than a branch diff."
---

# cleanup

Reviews existing source code against a quality rubric with file-cited evidence.
Maps findings to rubric dimensions (M1–M12 patterns, subjective tiers A–I,
AI anti-patterns).

**Does NOT post GitHub comments.** For live PR review with inline GitHub
comments, use the `pr-review` skill.

If asked to also post comments or edit tickets, decline that part, name `pr-review`
(or `ticket-critic` for tickets) as the skill to use, and still deliver the audit report.
Do not offer to post them yourself.

---

## When to Use

- Code audits on a directory, package, or file set
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
   `REVIEW-PHASE-0` block (schema in `~/.skills/reviews/schemas.md`).
   Aggregate LOW/MEDIUM hits per tool + rule. Before subjective review, every
   HIGH/CRITICAL row must be `RESOLVED` or `OVERRIDDEN`; LOW/MEDIUM rows may
   stay `OPEN` and are reported as data.
3. **Emit** `REVIEW-GATE: phase-0 → phase-1. Criteria: [...]. Proceeding: yes|no.`
   before continuing.
4. **Phase 1 — Specialist lenses** — default to one combined lens covering
   all four domains. Run the 4 lenses as parallel subagents only for a
   whole-repo audit or when the user asks (see
   [PHASE1_LENSES.md](PHASE1_LENSES.md)). Each lens emits its own
   `REVIEW-FINDINGS` block.
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

Run deterministic checks before any LLM-driven reasoning. A later subjective judgment cannot dismiss a Phase 0 row; only an explicit OVERRIDDEN with justification can.
The full tool table (unused imports and exports, file size, complexity, duplication, import cycles, layer boundaries, redundancy, dead branches, commented-out blocks, scope-leak vocabulary, cycle-coupled paths, runtime-coupled names, tracked-but-ignored files, inline lookup tables): [PHASE0_CHECKS.md](PHASE0_CHECKS.md). Read it before running the pass.
Two rules to remember: every tracked-but-ignored path (`git ls-files -ci --exclude-standard`, plus `git ls-files .plan .tickets .handoff`) is HIGH, and scope-leak and cycle-coupled hits follow `~/.skills/shared/SKILL_NOISE_TERMS.md`.

Emit the output in the `REVIEW-PHASE-0` block (schema: [`~/.skills/reviews/schemas.md`](../reviews/schemas.md)):

````markdown
```REVIEW-PHASE-0
| tool | rule | file | line | severity | status |
| ---- | ---- | ---- | ---- | -------- | ------ |
| ruff | F401 | src/auth.py | 4 | MEDIUM | RESOLVED |
| wc -l | file-size | src/ui/Dashboard.tsx | 847 | HIGH | OVERRIDDEN |
```
````

Every HIGH/CRITICAL row's `status` must be `RESOLVED` or `OVERRIDDEN` (with a written justification) before emitting the gate:

```
REVIEW-GATE: phase-0 → phase-1. Criteria: [HIGH/CRITICAL rows resolved: met]. Proceeding: yes.
```

The validator rejects `Proceeding: yes` with any OPEN HIGH/CRITICAL row.

---

## Phase 1 — Parallel Specialist Lenses

After the Phase 0 gate, review four domains: Layer & Dependency, Redundancy & Modularity, Error Handling & State, Data & Security. By default one lens covers all four. For a whole-repo audit or on request, run them as 4 parallel subagents, one per domain. Each lens emits its own `REVIEW-FINDINGS` block, possibly empty.
A finding that does not meet its lens's checklist threshold is dropped, not downgraded. Merge duplicates (same file + line + rule_code), prefer arch-violation findings over rubric ones, and sort Layer, Architectural Drift, Error Handling, Bug, Redundancy, Modularity, Standards, Test Gap.
Lens table, rubric ownership, thresholds and execution details: [PHASE1_LENSES.md](PHASE1_LENSES.md). Read it before launching lenses.

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
| [`PHASE0_CHECKS.md`](PHASE0_CHECKS.md) | Phase 0 tool table (all mechanical checks and commands) | Every Phase 0 |
| [`PHASE1_LENSES.md`](PHASE1_LENSES.md) | Lens table, thresholds, dedupe and ordering | Before launching Phase 1 lenses |
| [`redundancy-watcher.md`](redundancy-watcher.md)       | Blocks duplicate implementations at write time           | Before any new file or export |
| [`layer-boundary-critic.md`](layer-boundary-critic.md) | Enforces downward-only imports from AGENTS.md layer cake | Phase 0 when imports change   |
| [`ARCHITECTURE_DEPTH.md`](ARCHITECTURE_DEPTH.md)       | Architectural depth lens (module, seam, depth, dependency categories, design-it-twice) | Phase 1 when scope includes multi-module design |
| [`~/.skills/shared/SKILL_NOISE_TERMS.md`](~/.skills/shared/SKILL_NOISE_TERMS.md) | Skill-internal terms that must not appear in committed artifacts — flag as `scope-leak` | Every Phase 0 (mechanical pass) — scope covers comments, docstrings, path literals, identifiers, config filenames, CI YAML, Makefile, docs |

---

## Scope Boundary

| In scope                    | Out of scope                                     |
| --------------------------- | ------------------------------------------------ |
| Source code audits          | Editing `.tickets/*.md` → ticket-critic          |
| Package / directory audits  | Live PR comments on GitHub → pr-review           |
| Architecture pattern checks | Visual UI validation → make-ui / chrome-devtools |

---

## Decision Tree

**What is the scope?**

- Full codebase → use AGENTS.md exclusions, scan systematically
- Specific directory → scope to named path

**What issues matter most?**

- Security → M1–M4
- Maintainability → M5–M8
- Testing → M9–M12
- General → all, prioritize Tier A + M1–M4
