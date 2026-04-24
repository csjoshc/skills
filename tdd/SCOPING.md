# Phase 0: Scoping — Test Obligation Queue (TOQ)

Runs **before** user-approval Planning. Turns "which tests?" into a deterministic
ranking problem. Model ranks and shapes candidates; it does **not** invent scope
from prose.

Output: `.tickets/tdd/toq-<ticket-id>.yaml` — the ranked, bounded queue the RED
loop will execute.

---

## Inputs contract

| Input | Source | Required |
|---|---|---|
| `diff_base` | orchestrate envelope, else `git merge-base HEAD main` | yes |
| `ticket_path` | orchestrate envelope (`.tickets/NNN-slug.md`) | yes |
| `risk_registry` | repo root `.risk-registry.yaml` | optional |
| `prd_path` | `.tickets/prep/prd.md` (for Risk Surface fallback) | optional |
| `flake_log` | `.tickets/tdd/flake-log.jsonl` | optional |

Missing optionals degrade to defaults — never error.

---

## Signal collectors (deterministic, no LLM)

Run all collectors in parallel where possible. Each writes structured facts into
the TOQ assembly buffer.

1. **Touched files**
   `git diff --name-only <diff_base>...HEAD`
   Also capture touched symbols with `git diff -U0 <diff_base>...HEAD` → parse
   hunk headers for function/class names.

2. **Blast radius (grep layer)**
   For each touched file `F`: `rg -l "from .*F|import .*F|require\\(.*F\\)"` and
   reverse references of touched symbols by name. Language-agnostic heuristics:

   - Python: `from X import`, `import X`
   - JS/TS: `import … from 'X'`, `require('X')`
   - Go: `"module/pkg"` import blocks
   - Rust: `use crate::X`, `use X::`
   - Java/Kotlin: `import pkg.X`

3. **Dependency graph (MCP layer, preferred)**
   Call `mcp__codebase-memory-mcp__trace_path` from each touched symbol to
   find transitive callers/callees. Use `query_graph` for 1-hop neighbourhood
   when `trace_path` is overkill. Fall back to the grep layer if MCP is
   unavailable or the project is not indexed.

4. **Churn**
   `git log --since=90.days --name-only --pretty=format: <touched_files>` →
   count per file. Capped at 10 for scoring.

5. **Failure history**
   If `.tickets/tdd/flake-log.jsonl` exists, count prior failures per file.
   Schema: `{"ts": iso, "test": str, "target": str, "outcome": "fail|flake"}`.

6. **Existing tests**
   For each touched file, locate tests by convention:

   - `tests/…/test_<name>.py`, `<name>_test.py`, `<name>.spec.ts`, `<name>.test.tsx`
   - Or, if coverage data is available (`.coverage`, `coverage/lcov.info`),
     reverse-map touched lines → tests.

7. **Risk tier**
   For each touched path:

   1. Match against `.risk-registry.yaml` glob tiers → T1/T2/T3.
   2. If unmatched, look up `Test Obligation Profile` in ticket body; map
      requirement → tier.
   3. If still unmatched, look up `## Risk Surface` in `prd.md`.
   4. Default T2.

---

## Scoring formula

Additive, bounded 0–100. Applied per candidate obligation:

```
priority = business_impact      (T1=40, T2=20, T3=5)
         + change_proximity     (touched=15, adjacent=8, transitive=3)
         + dependency_reach     (round(log2(callers+1)*5), capped 15)
         + churn_signal         (commits_90d, capped 10)
         + failure_history      (prior_fails * 2, capped 10)
         + novelty              (new_file=8, new_public_api=10, else 0)
         - test_cost            (e2e=10, integration=4, unit=1, characterization=2, contract=2)
```

Weights table (override per repo via `.risk-registry.yaml: weights_override`):

| Term | Default weights |
|---|---|
| `business_impact` | T1=40, T2=20, T3=5 |
| `change_proximity` | touched=15, adjacent=8, transitive=3 |
| `dependency_reach` | `round(log2(callers+1)*5)`, cap 15 |
| `churn_signal` | cap 10 |
| `failure_history` | cap 10 |
| `novelty` | new_file=8, new_public_api=10 |
| `test_cost` | unit=1, characterization=2, contract=2, integration=4, e2e=10 |

`mutation_candidate: true` is set when `tier == T1 AND score > 60`.

---

## Candidate pattern catalog

Each pattern has a **trigger predicate** over signals. If the predicate fires,
emit one candidate obligation with the pattern's default shape.

| Pattern | Trigger | Default level | Default `done_when` |
|---|---|---|---|
| `characterization` | refactor tag OR churn>5 on touched file with no existing test | characterization | Snapshot locks current output on N fixtures |
| `contract` | touched file is an interface/adapter/schema/public API boundary | contract | Request/response shape + error semantics verified |
| `invariant` | touched symbol is pure transform / domain rule / validator | unit | Valid, boundary, and malformed inputs exercised |
| `state_transition` | touched file matches UI flow / reducer / workflow / async orchestration | integration | Legal + forbidden transitions + recovery covered |
| `impacted_regression` | existing test maps to touched code | (level of existing test) | Existing assertion still holds |
| `high_risk_path` | tier=T1 AND no existing test covers the touched symbol | integration | Happy + failure + partial-failure path covered |
| `history_based` | prior_fails > 0 on touched file | unit | Regression test pinning last known failure |

Multiple patterns may fire on one file; deduplicate by `target`, keep highest score.

---

## Bounding rules

After scoring, sort descending and apply hard caps:

- Top **5 unit** (includes invariant, history_based)
- Top **3 integration** (includes state_transition, high_risk_path)
- Top **1 e2e**
- Characterization and contract tests are **not capped** — they run first when
  the ticket is a refactor or boundary change.

Anything above the cap is emitted with `deferred: true` and a `defer_reason`.
Deferred entries stay in the YAML so future runs can reconsider them.

**Refactor prepend**: if the ticket body has `type: refactor` in frontmatter OR
any touched file has churn>5, sort characterization candidates to the top of
the queue ahead of any `level: unit|integration|e2e` entry.

---

## Output schema

`.tickets/tdd/toq-<ticket-id>.yaml`:

```yaml
ticket: .tickets/042-bulk-archive.md
diff_base: origin/main
generated_at: 2026-04-23T14:05:00Z
change_summary: >
  Bulk archive adds multi-select state to cart reducer and new POST
  /items/archive endpoint.
touched_files:
  - src/cart/reducer.ts
  - src/api/items/archive.ts
impacted_modules:
  - src/cart/**
  - src/api/items/**
existing_tests:
  - tests/cart/reducer.test.ts
critical_flows:
  - checkout
risk_tags: [T1, writes, state-transition]
candidate_test_tasks:
  - title: Bulk archive reducer rejects locked items
    level: unit
    pattern: invariant
    target: src/cart/reducer.ts:archiveMany
    rationale: T1 state transition, no existing coverage for locked-item branch
    score: 73
    mutation_candidate: true
    done_when: archiving a selection containing a locked item leaves all items unchanged
    blockers: []
  - title: POST /items/archive persists atomically with partial-failure semantics
    level: integration
    pattern: high_risk_path
    target: src/api/items/archive.ts:handler
    rationale: T1 write, new public API, touches DB
    score: 68
    mutation_candidate: true
    done_when: partial failure returns 207 and commits only successful items
    blockers: []
  - title: Existing single-item archive regression
    level: unit
    pattern: impacted_regression
    target: src/cart/reducer.ts:archiveOne
    rationale: shared code path with archiveMany
    score: 41
    mutation_candidate: false
    done_when: existing assertion holds after reducer changes
    blockers: []
  - title: Full bulk-archive happy path e2e
    level: e2e
    pattern: state_transition
    target: cypress/cart.spec.ts
    rationale: user-visible core flow, one smoke check
    score: 32
    mutation_candidate: false
    done_when: user selects 3 items, clicks archive, sees success toast
    blockers: []
deferred:
  - title: Archive button disabled-state pixel regression
    level: e2e
    score: 12
    defer_reason: cosmetic, below e2e cap
```

---

## Phase 0 algorithm

```
1. Load inputs (env + repo). Degrade missing optionals.
2. Run signal collectors in parallel.
3. For each touched file/symbol, evaluate every pattern trigger.
   Emit candidate with default shape.
4. Score each candidate.
5. Deduplicate by target; keep highest score.
6. Sort descending.
7. Apply bounding rules; mark overflow as deferred.
8. Apply refactor prepend if applicable.
9. Set mutation_candidate flags.
10. Write .tickets/tdd/toq-<ticket-id>.yaml.
11. Hand to Planning: present TOQ for user confirm / reprioritize / reject.
```

The RED loop in Phase 2+ pulls from the top of the non-deferred queue. Tests
executed per cycle are restricted to `target` paths + their `existing_tests`
mapping — this is what stops unrelated suites from firing.
