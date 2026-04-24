# Review output schemas

Fenced-block contracts shared by `pr-review` and `cleanup`. A review transcript
that omits any required block, or emits malformed content inside one, fails
`reviews/validate.py`.

## Contents

- REVIEW-PHASE-0
- REVIEW-FINDINGS
- REVIEW-LEDGER
- REVIEW-GATE
- Source tags
- Severity levels
- Required block order

---

## REVIEW-PHASE-0

Used by `cleanup` only. Emitted before any subjective critique. Every row comes
from a deterministic tool, not LLM judgment.

````markdown
```REVIEW-PHASE-0
| tool | rule | file | line | severity | status |
| ---- | ---- | ---- | ---- | -------- | ------ |
| ruff | F401 | src/auth.py | 4 | MEDIUM | OPEN |
| wc -l | file-size | src/ui/Dashboard.tsx | 847 | HIGH | OPEN |
```
````

Columns:

- `tool` — exact command or linter name (e.g., `ruff`, `eslint`, `ts-prune`).
- `rule` — rule code or short identifier the tool emits.
- `file`, `line` — location.
- `severity` — LOW | MEDIUM | HIGH | CRITICAL.
- `status` — OPEN | RESOLVED | OVERRIDDEN (with justification in the text below the block).

---

## REVIEW-FINDINGS

Used by both skills for rubric- or lens-derived findings. One row per finding;
the block may be split into multiple blocks by category.

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Bug
  lens: bug-hunter
  file: src/api/user.py
  line: 142
  rule_code: N/A
  severity: CRITICAL
  source: lens-derived
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    response.json()["user"] dereferenced without checking status_code
  proof: |
    curl -X GET /users/0 returns 404; code path hits line 142 unconditionally
  suggested_fix: |
    guard with `if response.ok:` before `.json()`
```
````

Required fields:

- `id` — stable per run (`F-001`, `F-002`, ...).
- `category` — Bug | Error Handling | Standards | Test Gap | Scope | Layer | Redundancy | Modularity | **Architectural Drift**.
- `lens` or `rubric_code` — the specialist or rubric dimension that produced the finding.
- `file`, `line` — concrete location in changed code (pr-review) or codebase (cleanup).
- `rule_code` — for Standards lens, the quoted rule code; `N/A` otherwise.
- `severity` — LOW | MEDIUM | HIGH | CRITICAL.
- `source` — tool-flagged | lens-derived | rubric-derived | user-confirmed. See *Source tags*.
- `checklist_score` — `N/M` matching the lens threshold (pr-review); `N/A` for cleanup rubric findings.
- `status` — VALIDATED | DISMISSED | DEFERRED.
- `evidence` — literal code or behavior quote.
- `proof` — required when `severity: CRITICAL`, `category: Architectural Drift`, **or** (`category: Layer` **and** `severity: HIGH` or `CRITICAL`). See *proof requirement* below.
- `suggested_fix` — concrete remediation. For `category: Architectural Drift` and `category: Layer`, `suggested_fix` must eliminate the quoted evidence pattern — not rename it, relocate it, or wrap it behind a new parameter. A fix that preserves the violation's shape is the five-example failure mode the validator's `structural_findings_have_proof` check does not catch; reviewers must self-enforce.

Optional fields:

- `decidable_at` — `design` | `diff` | `both`. Signals whether the
  violation should have been caught at /antiplan Phase 2 (`design`), is
  only visible post-code (`diff`), or both (policy at `design`,
  enforcement at `diff`). Required when `category: Architectural Drift`.

### Proof requirement (structural findings)

A finding must carry a `proof:` field when any of:

- `severity: CRITICAL` (any category)
- `category: Architectural Drift` (any severity)
- `category: Layer` with `severity: HIGH` or `CRITICAL`

Proof is one of:

- a reproducible command (`curl ...`, `pytest path::test`, `npm run ...`, `madge --circular`, `importlinter --config .importlinter`),
- a failing test name with file path,
- a log/transcript snippet with a timestamp and file/line,
- a linked CI job URL,
- for `category: Layer`: a concrete import edge, cycle, or layer-map excerpt that makes the violation reproducible — e.g. `madge --circular src/` output showing the forbidden edge.

Narrative prose alone is not proof. The validator blocks posting
without it. The Layer-HIGH extension covers ARCH-DEP-UP,
ARCH-DEP-CYCLE, ARCH-DEP-LEAK, ARCH-DEP-IO-IN-PURE, and
ARCH-BND-EAGER-INIT — the architectural claims that benefit most
from reproducible evidence.

---

## REVIEW-LEDGER

YAML block, emitted once at the end of every review response.

````markdown
```REVIEW-LEDGER
ledger:
  phase: phase-0 | phase-1 | report
  findings_total: 12
  validated: 9
  dismissed: 2
  deferred: 1
  critical: 1
  confidence: LOW | MEDIUM | HIGH
  plan_present: true | false
```
````

Rules:

- `findings_total == validated + dismissed + deferred`.
- `confidence: HIGH` only if `phase == report`, validator exits 0, **and**
  `plan_present: true`. Without a linked plan, confidence ceiling is MEDIUM
  because architectural-drift findings cannot be fully assessed.
- `critical` counts CRITICAL-severity validated findings; all must carry
  `proof:`.
- `plan_present: true` means the PR body, linked tickets, or branch
  contained a plan/PRD artifact that the lenses could compare against.
  `plan_present: false` is legitimate but blocks HIGH confidence.

---

## REVIEW-GATE

Single-line audit trail at every phase transition.

```
REVIEW-GATE: <from> → <to>. Criteria: [<c1>: met|not met — why]; [<c2>: ...]. Proceeding: yes|no.
```

Required transitions:

- `phase-0 → phase-1` (cleanup only; pr-review's pre-flight is a direct gate to lens phase).
- `phase-1 → report` (both skills).
- `report → post` (pr-review only; Criteria must include `validator exit 0`).

`Proceeding: yes` with any unresolved Phase 0 row = malformed, blocks the
validator.

---

## Source tags

Every finding carries exactly one source tag:

| Source | Origin | Dismissal rule |
| --- | --- | --- |
| `tool-flagged` | Deterministic tool (ruff, eslint, madge, etc.) | Dismiss only with `status: DISMISSED` + written override |
| `lens-derived` | pr-review specialist lens | Dismiss only if checklist_score below threshold |
| `rubric-derived` | cleanup rubric dimension (M1–M12, Tier A–I) | Dismiss only with evidence the rubric does not apply |
| `user-confirmed` | User flagged/confirmed in session | Not dismissible without user retraction |

---

## Severity levels

| Level | Meaning | Extra requirement |
| --- | --- | --- |
| LOW | Nit, style, minor | — |
| MEDIUM | Real issue, non-urgent | — |
| HIGH | Likely-broken or standards violation with impact | `proof:` field required for `category: Layer` or `category: Architectural Drift` |
| CRITICAL | Security, data loss, production outage risk | `proof:` field required (any category) |

---

## Required block order

Every review transcript ends with, in order:

1. `REVIEW-PHASE-0` (cleanup only).
2. `REVIEW-GATE: phase-0 → phase-1` (cleanup only).
3. One or more `REVIEW-FINDINGS` blocks.
4. `REVIEW-GATE: phase-1 → report`.
5. `REVIEW-LEDGER`.
6. `REVIEW-GATE: report → post` (pr-review only, immediately before `gh api`).

Any deviation trips `reviews/validate.py`.
