# AI-specific architectural violations

Smells that agents introduce at rates much higher than human engineers.
Worth catalog-ing separately because they pattern-match to "adding
safety" or "being thorough" but compound as shadow abstractions, dead
defenses, and silent drift from project conventions.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (5)

### Parallel implementation

**Shape (language-agnostic):** A new helper, utility, or client is
introduced to do a job the codebase already has a canonical
implementation for. Occurs when the agent generated from training
priors instead of searching the repo first.

**Decidable at:** `diff`

**Why it compounds:** Now two implementations of the same concern must
be kept in sync. Fixes applied to one diverge from the other; new
engineers pick whichever they find first. The duplication entrenches.

**Category mapping:** `category: Redundancy` / severity `MEDIUM` / `rule_code: ARCH-AI-PARALLEL`

---

### Unjustified shim / adapter layer

**Shape (language-agnostic):** A thin wrapper is inserted between the
caller and the underlying library "in case the library changes" or
"for testability," with no current caller that benefits from the
indirection. The wrapper passes every argument through and adds no
invariants.

**Decidable at:** `diff`

**Why it compounds:** The wrapper becomes a fifth wheel that every
reader must trace through. It accrues one-off tweaks over time,
entrenching the indirection without ever delivering the substitutability
it was meant to enable.

**Category mapping:** `category: Modularity` / severity `LOW` / `rule_code: ARCH-AI-SHIM`

---

### Defensive code for scenarios that cannot happen

**Shape (language-agnostic):** Null checks on values the type system
guarantees non-null; try/catch around code paths that cannot throw;
fallback branches for enum variants the compiler already proves
exhaustive. The check is statically impossible to hit.

**Decidable at:** `diff`

**Why it compounds:** Readers assume checks exist because the scenario
is possible. They write new code matching the defensive style,
spreading the misconception. Coverage metrics drop because the dead
branch is unreachable. Over time the invariants become ambiguous.

**Category mapping:** `category: Modularity` / severity `LOW` / `rule_code: ARCH-AI-DEAD-DEFENSE`

---

### Re-introducing patterns the project rejected

**Shape (language-agnostic):** Code uses a construct the repository's
conventions, linter config, or AGENTS.md explicitly bans — a banned
type (`any`, untyped dict), a banned logger, a banned error class, a
banned dependency. The agent didn't read the conventions.

**Decidable at:** `both` — /antiplan's ARCHITECTURE-DECISIONS should
surface the bans; diff review catches specific violations.

**Why it compounds:** Each reintroduction dilutes the ban. Reviewers
see the pattern in the tree and assume it's allowed. Eventually the
convention is fully eroded.

**Category mapping:** `category: Architectural Drift` (when plan or
AGENTS.md named the ban) / severity `MEDIUM` / `rule_code: ARCH-AI-REJECTED-PATTERN`

---

### Backwards-compat cruft for code with no users

**Shape (language-agnostic):** Deprecation shims, compatibility
aliases, or version-guarded branches are added for a symbol or API
that was never released, has no external consumers, and has no history
of the shape being relied upon.

**Decidable at:** `diff`

**Why it compounds:** The shim cannot be removed without an audit of
"who is using it" — and since the answer is "no one," the audit never
gets scheduled. Every touch of the surrounding code must reason about
both the real and the legacy path.

**Category mapping:** `category: Modularity` / severity `LOW` / `rule_code: ARCH-AI-COMPAT-CRUFT`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| Parallel implementation | `rg -n "<new-helper-name>" src/` paired with `rg -n "<canonical-helper-name>" src/` showing both exist and do the same job; `jscpd --min-lines 15` flagging overlap. |
| Unjustified shim | `rg -n "def <wrapper>\|function <wrapper>" <file>` showing the wrapper body is a single passthrough line; `rg -l "<wrapper>"` showing one caller, which could import the library directly. |
| Dead defensive code | Type-checker output (e.g. `mypy --strict`, `tsc --noImplicitAny`) flagging unreachable branches; `ruff` rule for redundant-None; compiler exhaustiveness warnings. |
| Rejected pattern | `rg -n "<banned-pattern>" <new-file>` plus AGENTS.md / tsconfig / ruff config excerpt showing the ban; `git log -S"<banned-pattern>"` showing prior removals. |
| Compat cruft for unpublished code | `git log --follow <legacy-path>` showing the legacy form was never tagged in a release; `rg -n "<legacy-symbol>" src/` returning zero external callers. |

Prose alone never satisfies proof.

---

## Few-shot: good finding

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Redundancy
  lens: redundancy-watcher
  file: src/lib/time_utils.py
  line: 3
  rule_code: ARCH-AI-PARALLEL
  severity: MEDIUM
  source: lens-derived
  decidable_at: diff
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    New helper `format_iso_timestamp` in src/lib/time_utils.py duplicates
    `to_iso8601` in src/common/dates.py, which has been the canonical
    timestamp formatter in this repo for 14 months (26 call sites).
  proof: |
    $ rg -n "to_iso8601|format_iso_timestamp" src/
    src/common/dates.py:41:def to_iso8601(dt):
    src/lib/time_utils.py:3:def format_iso_timestamp(dt):
    [26 call sites of to_iso8601, 0 of format_iso_timestamp]
    $ jscpd --min-lines 5 src/common/dates.py src/lib/time_utils.py
    → 100% overlap on the formatter body.
  suggested_fix: |
    Delete src/lib/time_utils.py. If the name is preferable, rename
    `to_iso8601` in common/dates.py and update the 26 call sites in one
    pass.
```
````

---

## Few-shot: good dismissal

A reviewer sees a new wrapper `db_fetch_user(id)` around the ORM's
`User.objects.get(id=id)` and flags it as an unjustified shim. It is
**not** a smell if the wrapper adds a real invariant the ORM call
doesn't — e.g., translating the ORM's `DoesNotExist` exception into the
project's domain `UserNotFound` error, applying a tenant filter, or
centralizing a query-timing metric. The shape (one-line wrapper) looks
identical; the justification ("translates the boundary / enforces tenant
scoping") is the difference. Similarly, a null check that looks
redundant given the type signature may be load-bearing if the value
crosses a trust boundary (an external API response, a deserialized
payload) where the type is nominal, not enforced.

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| Parallel implementation | ❌ — requires repo knowledge | ✅ | ✅ |
| Unjustified shim | ❌ — emerges from diff shape | ✅ | ✅ |
| Dead defensive code | ❌ — visible only with types in hand | ✅ | ✅ |
| Rejected pattern | partial — should surface bans | ✅ | ✅ |
| Compat cruft for unpublished code | ❌ — requires release-history check | ✅ | ✅ |

**partial** means /antiplan should name the ban but cannot detect
instances. When `plan_present: true` and the plan or AGENTS.md named
the rejected pattern, emit as `category: Architectural Drift` with
`decidable_at: design`.
