# Evolution and reversibility

Smells where today's change forecloses tomorrow's option. The
compounding damage is in the incident you cannot roll back, the
breaking change clients cannot absorb, the flag you cannot turn off.
These are architectural because the reversibility property is a
cross-cutting design decision, not a per-line concern.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (4)

### Irreversible migration without a rollback plan

**Shape (language-agnostic):** A schema or data change is merged
whose only path back is data loss or manual reconstruction — dropping
a column before readers stop referencing it, renaming in place rather
than add-then-remove, or a simultaneous deploy across services with
no staggered compatibility window.

**Decidable at:** `design` — /antiplan should require an explicit
rollback path for any schema or contract change.

**Why it compounds:** When the change breaks in production, the only
recovery is a forward fix under pressure. Future migrations inherit
the "we don't need a rollback" pattern until one blows up badly enough
to retrofit discipline.

**Category mapping:** `category: Architectural Drift` / severity `HIGH` /
`rule_code: ARCH-EVO-IRREVERSIBLE`

---

### Backwards-incompatible API change with no deprecation path

**Shape (language-agnostic):** A published endpoint, message shape, or
exported type is changed such that older clients break the moment the
change ships — no version, no dual-write period, no overlap window
during which both shapes are accepted.

**Decidable at:** `design` — /antiplan should require a deprecation
window for any public surface change.

**Why it compounds:** Any deploy becomes a coordination problem with
clients. A future release schedule must accommodate the slowest
consumer. Internal teams develop deploy-anxiety and batch changes,
which makes each batch riskier.

**Category mapping:** `category: Architectural Drift` / severity `HIGH` /
`rule_code: ARCH-EVO-BREAK`

---

### Feature flag without a kill-switch path through dependent layers

**Shape (language-agnostic):** A flag gates a visible feature in one
layer (UI, handler) but the dependent layers (backend workers, data
emission, background jobs) continue executing as if the feature were
on. Disabling the flag hides the feature from users but doesn't stop
the work.

**Decidable at:** `both` — /antiplan should require that kill
switches propagate through every dependent layer.

**Why it compounds:** A flag that doesn't fully disable the behavior
is not a safety control — it's a UI toggle. Incidents triggered by
the feature cannot be mitigated by flipping the flag; the system
still writes data, still emits events, still pages oncall.

**Category mapping:** `category: Architectural Drift` / severity `MEDIUM` /
`rule_code: ARCH-EVO-FLAG-PARTIAL`

---

### "Temporary" solution without owner or sunset date

**Shape (language-agnostic):** A shim, workaround, or stopgap is added
with language like "temporary," "TODO: remove after X," or "until we
fix Y," without a named owner, a concrete removal criterion, or a
tracked ticket. The solution outlives the team that wrote it.

**Decidable at:** `both` — /antiplan should require owner + sunset
criteria for anything labeled temporary.

**Why it compounds:** Temporary solutions accumulate as permanent
fixtures. Each is a small tax on comprehension; together they form a
substrate of "why is this here?" that new contributors spend
disproportionate time puzzling out.

**Category mapping:** `category: Architectural Drift` / severity `MEDIUM` /
`rule_code: ARCH-EVO-ORPHAN-TEMP`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| Irreversible migration | Migration file with DROP/RENAME that has no add-first companion; OR absence of a linked rollback script / down migration; OR plan-doc check for a rollback section. |
| Backwards-incompatible API change | API schema diff (`openapi-diff`, GraphQL schema diff) showing breaking changes without version bump; OR `rg -n "/api/v1/\|/api/v2/" <routes>/` showing the old surface was deleted in the same PR it was superseded. |
| Flag without kill-switch through layers | `rg -n "<flag-name>" <dir>/` showing the flag referenced only in the UI / handler layer, not in the worker / emitter / job layers; OR a test that disables the flag and asserts downstream work stops. |
| Orphan "temporary" solution | `rg -n "TODO\|FIXME\|HACK\|TEMP\|temporary" <dir>/` counting occurrences without adjacent ticket references; `git blame` showing > 6-month age on lines marked temporary. |

Prose alone never satisfies proof.

---

## Few-shot: good finding

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Architectural Drift
  lens: evolution-reversibility
  file: migrations/20260420_drop_legacy_user_name.sql
  line: 1
  rule_code: ARCH-EVO-IRREVERSIBLE
  severity: HIGH
  source: lens-derived
  decidable_at: design
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    Migration drops the `users.legacy_name` column in a single step.
    The column is still referenced by src/reports/export_v1.py:88
    (grep shows 14 call sites). No add-new-column + backfill + dual-read
    + drop sequence. No down migration.
  proof: |
    Plan ARCHITECTURE-DECISIONS block (.plans/user-name-cleanup.md §4)
    requires "expand-contract migrations: add new, backfill, dual-read
    for one release, then drop." The current migration compresses that
    into a single destructive step.
    Reproduce:
    $ rg -n "legacy_name" src/   # → 14 live references
    $ ls migrations/*drop_legacy*down*  # → no down migration present
  suggested_fix: |
    Split into: (1) add `name` column, (2) backfill, (3) ship readers
    reading the new column while still writing both, (4) ship writers
    writing only the new column, (5) drop `legacy_name`. Include a
    down migration for each step.
```
````

---

## Few-shot: good dismissal

A reviewer sees a migration that `DROP TABLE`s and flags it as
irreversible. It is **not** an evolution violation when the table is a
materialized cache or idempotently-derivable view — rebuilding it is
cheap, and no authoritative data lives there. The question is not
"does the migration drop something?" but "can the system recover its
state after the drop without intervention?" Similarly, a missing
deprecation window is not a violation when the API is internal,
consumed only by code in the same deploy unit, and the PR updates
every consumer in the same atomic change. Backwards-compat rules
apply to published surfaces, not to refactors within a deploy boundary.

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| Irreversible migration | ✅ — must require rollback plan | ✅ | ✅ |
| Backwards-incompatible API | ✅ — must require deprecation window | ✅ | ✅ |
| Flag without kill-switch | partial — must mandate flag propagation | ✅ | ✅ |
| Orphan temporary solution | partial — must require owner + sunset | ✅ | ✅ |

**partial** means /antiplan sets the policy but cannot see the code.
When `plan_present: true` and the plan specified rollback, deprecation,
or flag propagation requirements, emit as `category: Architectural Drift`
with `decidable_at: design`.
