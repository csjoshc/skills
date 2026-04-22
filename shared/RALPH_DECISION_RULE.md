# Ralph Decision Rule — Canonical

**Context:** Orchestra orchestrates LangGraph-driven agent work. Ralph is a subprocess-per-task loop pattern from the Ralph Wiggum technique: fresh process boundary, fixed prompt, markdown checklist on disk, tests as the only arbiter. Ralph is faster for large tickets with independent ACs; it's overhead for small tickets or bootstrap-heavy work.

**Decision:** Set `Ralph: true | false` in ticket front-matter during authoring. This flag gates whether BUILD uses the Ralph sub-loop (fresh subprocess per AC) or one-shot BUILD.

## Eligibility Rule

A ticket is **Ralph-eligible** if **ALL** of these hold. **Ralph-ineligible** if **ANY** disqualifier fires.

### Eligibility (all required)

1. **AC count ≥ 6**, and each AC row has an independent verification command (grep, pytest -k, ruff check) in the AC→Tests table. Below 6, one-shot BUILD is cheaper.
2. **Additive scope.** Each AC creates a new artifact (new file, new function, new test, new log entry). Partial completion leaves the codebase in a valid state. No refactoring mid-ticket.
3. **ACs are independently checkable** — each can be verified without depending on a later AC to have run. Order the AC table accordingly (dependencies first).
4. **No "bootstrap" or "after BUILD" ACs** that depend on the new code running against the live repo. Examples: ticket that runs its own migration, or that commits its own safety check during BUILD. These MUST use `Ralph: false`.
5. **Failure Protocol does NOT mandate "revert all on failure"** — that language signals the work is atomic; half-done state is worse than not-done.

### Disqualifiers (any one sets `Ralph: false`)

- **Refactor / global rename / schema migration** — cross-cutting change where per-box commits leave callers broken.
- **Self-mutating or bootstrap tickets** — ticket invokes its own new code against the live repo during BUILD execution.
- **Destructive/irreversible operations** (force-push, branch delete, data migration without rollback).
- **Holistic ACs** like "coverage ≥ 90%" or "e2e flow passes" that cannot be attributed to one sub-task.
- **Single logical change** — bug fix or one-file feature with trivially small diff. Ralph overhead exceeds benefit.

## Front-Matter Shape

```yaml
---
Stage: NEW
Type: feature
Ralph: true
Ralph-Reason: "12 additive ACs, each with independent grep/pytest, no bootstrap"
---
```

Or ineligible:

```yaml
Ralph: false
Ralph-Reason: "Bootstrap: ticket runs its preflight safety check against live repo"
```

**`Ralph-Reason` is mandatory** — forces the author to apply the rule instead of defaulting blindly.

## Authoring Workflow

1. **antiplan / make-prd:** When decomposing the PRD into tickets, **prefer Ralph-shaped decomposition** — i.e., tickets with 6-12 independent additive ACs over 1 monolithic ticket. This is upstream shaping, not just labeling.

2. **spec-writer:** During ticket authoring, **apply the rule above** to set `Ralph: true | false` in the YAML header. If unsure, default to `false` (one-shot is safer).

3. **ticket-critic:** **Audit the flag.** Block tickets where:
   - The flag contradicts the scope (e.g., `Ralph: true` but scope is a refactor).
   - AC table has non-grep-checkable rows (e.g., "verify manually that the UI looks good"). Under Ralph, ACs become load-bearing; they must be machine-checkable.
   - `Ralph-Reason` is absent or vague.

4. **orchestrate:** **Read the flag only.** During ticket execution, BUILD routes to Ralph loop vs one-shot based on it. No inference at run time.

## Implementation in BUILD Node

If `Ralph: true`:
- First iteration: agent reads AC→Tests table, writes `.tickets/NNN-slug/plan.md` with a checkbox list (one per AC).
- Loop: invoke opencode with fixed `ralph_build.md` prompt (phases 0-4 + 999-guardrails). Agent reads plan, picks first unchecked box, implements, runs the AC's verification command. If green, check the box, commit per-box. If red, append a "sign" and stop.
- Exit conditions: all boxes checked (return to unified_gate) OR K consecutive iterations without progress (escalate to existing `retry_node` / `blocked`).

If `Ralph: false`:
- Existing one-shot BUILD flow unchanged.
