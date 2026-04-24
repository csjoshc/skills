# Error handling as architecture

Smells where the error-handling structure itself is the bug — not a
missing null check, but a handler strategy that guarantees silent
corruption or confused failure modes as the system evolves. These are
architectural because the shape spreads: every new call site inherits
the surrounding pattern.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (5)

### Swallowed error

**Shape (language-agnostic):** A caught exception is logged (or
ignored) at a layer that cannot meaningfully recover, and the calling
code proceeds as if the operation succeeded. Downstream callers observe
empty or default values where failure was the truth.

**Decidable at:** `diff`

**Why it compounds:** Data corruption and silent skips accumulate in
the backing store. The incident signal — a failing dependency — is
hidden from monitoring because the caller returned "success."

**Category mapping:** `category: Error Handling` / severity `HIGH` /
`rule_code: ARCH-ERR-SWALLOW`

---

### Catching too broadly

**Shape (language-agnostic):** A catch clause grabs the base exception
type (or all-throwables) and continues execution as if the condition
were expected. Programming bugs (null dereference, type error) are
treated identically to domain failures (not-found, unauthorized).

**Decidable at:** `diff`

**Why it compounds:** Bugs that should crash are silently absorbed.
Each new kind of failure added downstream is auto-handled by the
existing over-broad catch, deepening the masking over time.

**Category mapping:** `category: Error Handling` / severity `MEDIUM` /
`rule_code: ARCH-ERR-BROAD`

---

### Fallback that masks the root cause

**Shape (language-agnostic):** On failure, the code returns an empty
collection, a stale cached value, or a default — without signaling
staleness or degradation to the caller. Callers cannot distinguish
"no data" from "fetch failed."

**Decidable at:** `diff`

**Why it compounds:** UIs render emptiness that looks like "no
results"; downstream consumers treat stale data as fresh; error
budgets show green because no error propagated. The real outage is
invisible until a customer reports missing data.

**Category mapping:** `category: Error Handling` / severity `HIGH` /
`rule_code: ARCH-ERR-MASKING-FALLBACK`

---

### Errors crossing a boundary without translation

**Shape (language-agnostic):** Exceptions or error shapes from a lower
layer (database driver, vendor SDK) reach a higher layer (HTTP,
user-facing UI) unchanged. Storage or vendor implementation details
leak into error responses, logs, and client retry logic.

**Decidable at:** `both` — /antiplan should set the error-translation
policy; diff catches specific leaks.

**Why it compounds:** Clients couple their retry behavior to the
vendor's error codes. Swapping storage or vendor requires updating
every client. Stack traces in user-facing errors become a security
and UX problem.

**Category mapping:** `category: Error Handling` / severity `MEDIUM` /
`rule_code: ARCH-ERR-UNTRANSLATED`

---

### Expected and unexpected failures conflated

**Shape (language-agnostic):** A single catch clause handles both
domain-expected outcomes (not-found, duplicate, rate-limited) and
unexpected programming bugs (type error, null dereference, assertion
failure) with the same response. There is no distinction in logs,
metrics, or alerting.

**Decidable at:** `both` — /antiplan should define the error taxonomy.

**Why it compounds:** Monitoring cannot distinguish "user tried an
invalid thing" from "code is broken." Alert fatigue sets in; real
regressions get buried in expected-error noise.

**Category mapping:** `category: Error Handling` / severity `MEDIUM` /
`rule_code: ARCH-ERR-CONFLATE`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| Swallowed error | `rg -n "except.*:\s*$\|except.*:\s*pass\|\.catch\(\(\) => \)" <dir>/`; OR a failing test that injects an error at a dependency and asserts the caller propagates it. |
| Catching too broadly | `rg -n "except Exception\|except BaseException\|catch \(Throwable\|catch \(Error\)" <dir>/` (note: exclude documented top-level boundaries). |
| Masking fallback | `rg -n "except.*: return \[\]\|except.*: return None\|\.catch\(\(\) => \[\]\)" <dir>/`; OR response-schema audit showing no "degraded" flag. |
| Untranslated boundary errors | `rg -n "except <VendorError>\|except <DbError>" <outer-layer>/` where the outer layer has no adapter; OR an API response containing storage-specific error codes. |
| Expected/unexpected conflation | Metrics audit: one counter for "errors"; OR `rg -n "except Exception as e: log.*error\(e\)" <dir>/` showing domain and programming errors sharing a sink. |

Prose alone never satisfies proof.

---

## Few-shot: good finding

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Error Handling
  lens: error-handling
  file: src/services/inventory_sync.py
  line: 132
  rule_code: ARCH-ERR-SWALLOW
  severity: HIGH
  source: lens-derived
  decidable_at: diff
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    sync_batch() wraps each row update in `try/except: log.warning(...)`
    and continues the loop. On a failed update the row is counted toward
    `rows_synced` and the caller receives a success response. Next
    sync treats the stale row as current.
  proof: |
    $ pytest tests/services/test_inventory_sync.py::test_partial_failure_is_reported -x
    FAILED — injected DB failure on row 5 of 10; sync_batch returned
    rows_synced=10, status="ok". Expected rows_synced=9 and a partial
    error shape. Repro at tests/services/test_inventory_sync.py:58.
  suggested_fix: |
    Distinguish recoverable per-row errors from caller contract: collect
    failed row IDs into `failures`, return `{rows_synced, failures}`, and
    emit a metric per failure. Do not count failed rows as synced.
```
````

---

## Few-shot: good dismissal

A reviewer sees `except Exception: log.exception(e); raise` at the top
of a request handler and flags it as "catching too broadly." It is
**not** an over-broad-catch smell when the catch exists solely to
capture-and-rethrow at a telemetry boundary, and the exception is
re-raised unmodified. The purpose is to ensure the error is logged
with request context before it crosses the HTTP layer. The smell is
about silently continuing; re-raising preserves the failure signal.
Similarly, a `try/except ValueError: return None` in a parser is fine
when the caller's contract is "returns the parsed value or None if
unparseable" and the caller branches on None — the error is part of
the function's declared contract, not a swallowed signal.

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| Swallowed error | ❌ — emerges in code | ✅ | ✅ |
| Catching too broadly | ❌ | ✅ | ✅ |
| Masking fallback | partial — should define degraded-vs-ok contract | ✅ | ✅ |
| Untranslated boundary errors | partial — should mandate translation layer | ✅ | ✅ |
| Expected/unexpected conflation | partial — should define error taxonomy | ✅ | ✅ |

**partial** means /antiplan should set the policy but cannot see code.
When `plan_present: true` and the plan specified the taxonomy or
translation layer, pr-review/cleanup may emit
`category: Architectural Drift` with `decidable_at: design`.
