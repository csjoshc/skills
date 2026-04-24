# State, concurrency, and lifecycle

Smells where the violation is invisible on a single request but
compounds with load, retries, or long-lived processes. The failure
modes are silent corruption, slow leaks, and non-reproducible
production incidents — the kinds of bugs unit tests never surface.
Also covers single-flow aliasing bugs from mutable value types — the
bug is concurrency-shaped (state observed through two references) even
when only one thread is running.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (6)

### Shared mutable state across requests or threads

**Shape (language-agnostic):** Module-level collections, singletons, or
process-wide caches that accumulate per-request data without scoped
invalidation. Two concurrent requests can observe each other's
intermediate values.

**Decidable at:** `diff`

**Why it compounds:** Test suites pass because tests serialize; load
testing passes because cache collisions are rare. A production
incident under load is the first time the bug is observable, and the
stack trace will not point at the shared object.

**Category mapping:** `category: Bug` / severity `HIGH` / `rule_code: ARCH-STATE-SHARED`

---

### Race on a shared resource (check-then-act)

**Shape (language-agnostic):** A code path reads a value, decides an
action based on that read, then writes — with no lock, transaction, or
compare-and-swap between the read and the write. Two concurrent callers
can both pass the check and both perform the action.

**Decidable at:** `diff`

**Why it compounds:** The incorrect interleaving is rare in normal
traffic but amplifies under retries, parallel workers, or user
re-clicking. The symptom (duplicate rows, double-charged payments,
inventory going negative) is usually in a different system than the
race itself.

**Category mapping:** `category: Bug` / severity `CRITICAL` (if the
action is money, inventory, or auth) else `HIGH` / `rule_code: ARCH-STATE-RACE`

---

### Resource leak — no guaranteed cleanup

**Shape (language-agnostic):** A connection, file, socket, subscription,
or background task is opened without a guaranteed teardown path
(scope exit, finalizer, cancellation token). An exception or early
return on the happy path bypasses cleanup.

**Decidable at:** `diff`

**Why it compounds:** Each leak is invisible individually; the failure
mode is exhaustion (connection pool saturated, file handles at ulimit,
goroutines accumulating). Time-to-failure is proportional to traffic
and often aligns with release windows.

**Category mapping:** `category: Bug` / severity `HIGH` / `rule_code: ARCH-STATE-LEAK`

---

### Transactional boundary mistake

**Shape (language-agnostic):** A multi-step write is executed without a
transaction, or the transaction holds a lock across an I/O call to an
external system (HTTP, queue publish, file write). Partial failures
leave inconsistent state; long-held locks serialize other writers.

**Decidable at:** `diff`

**Why it compounds:** Partial-write inconsistencies accumulate
silently. External-I/O-in-transaction saturates connection pools under
latency spikes — one slow vendor takes down the database tier.

**Category mapping:** `category: Bug` / severity `HIGH` / `rule_code: ARCH-STATE-TXN`

---

### Unbounded queue, retry loop, or recursion

**Shape (language-agnostic):** A queue with no max size, a retry policy
with no cap on attempts or aggregate wait, or a recursive call with no
termination guarantee tied to bounded input. The system has no
back-pressure signal.

**Decidable at:** `diff`

**Why it compounds:** Silently scales past the intended headroom until
a downstream failure spike amplifies infinitely — queues fill memory,
retries DDoS the dependency as it recovers, recursion blows the stack.

**Category mapping:** `category: Bug` / severity `HIGH` / `rule_code: ARCH-STATE-UNBOUNDED`

---

### Mutable domain entity with in-place mutation

**Shape (language-agnostic):** A domain entity — a record, struct,
`@dataclass`, or value-type — is defined as mutable, and callers
mutate it in place rather than returning a new instance. The
mutation is visible to every reference that shares the object. The
bug mode is *aliasing*: two code paths hold a reference to the same
entity, one mutates it (often deep in a helper), and the other
observes the mutation without having asked for it. The canonical
shape is a method like `cart.apply_discount(...)` that mutates
`self.total_cents -= discount` with no return value, combined with
a caller that passed the `cart` to more than one consumer.

**Decidable at:** `diff` — visible in the class definition plus the
mutation call sites. /antiplan should set "domain types are frozen;
state transitions return new instances" as a design policy, but the
specific violation is a code fact.

**Why it compounds:** Every callee that receives the entity could
theoretically mutate it. Either defensive copies proliferate (each
caller copies before passing down, just in case), or — far more
common — nobody copies and a subtle non-local bug appears when two
code paths share a reference. Audit trails, idempotency semantics,
retry handling, and undo/redo all become hard to reason about
because "what was the value at time T" has no stable answer. Tests
that pass in isolation fail when run together because test fixtures
get mutated by earlier tests. Equality, hashing, and caching all
become landmines.

Distinct from `ARCH-STATE-SHARED`: STATE-SHARED is about *cross-
request* or *cross-thread* mutation of a module-level or singleton
container. STATE-DOMAIN-MUTATION is about *within-flow* aliasing of
a mutable value type passed by reference. Both show up as "state
observed through two references"; only STATE-SHARED requires
concurrency for the bug to manifest. DOMAIN-MUTATION will break in
a single-threaded test.

**Category mapping:** `category: Bug` / severity `CRITICAL` (when
the entity holds money, inventory, auth, or other irreversible
state) else `HIGH` / `rule_code: ARCH-STATE-DOMAIN-MUTATION`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| Shared mutable state | `rg -n "^[A-Z_]+ = \{\|^[A-Z_]+ = \[\|^cache = " <module>/` showing module-level mutable bindings; trace whether writes happen per-request. |
| Race / check-then-act | Failing concurrent-stress test (`pytest-xdist -n 8`, `go test -race`, `jest --workers=8`); OR `rg -n "if .* exists\|\.get\(" <file>` showing the pattern, cross-referenced with a missing lock/transaction in the same block. |
| Resource leak | Static analyzer (`bandit` B108, `eslint no-unused-expressions`, `go vet` leak hints); OR a unit test that forces an exception between open and close and asserts the resource closes. |
| Transactional boundary | `rg -n "begin\|BEGIN\|transaction\(\)" <file>` cross-referenced with `rg -n "requests\.\|httpx\.\|publish\(" <same-block>`; OR a test that sets an artificial latency on the external call and observes pool exhaustion. |
| Unbounded queue/retry/recursion | `rg -n "Queue\(\)\|max_retries=None\|while True" <file>`; OR a stress harness with synthetic-latency on downstream that observes memory/queue growth. |
| Mutable domain entity | `rg -nE "@dataclass\b" <domain-dir>/ -A 1` surfacing dataclasses without `frozen=True`; OR `rg -nE "self\.\w+ [-+*/]?= " <domain-dir>/` showing in-place mutation of `self`; OR a test that passes the same entity to two consumers and asserts the first one's view is unchanged after the second runs. |

Prose alone never satisfies proof. CRITICAL findings must reference a
concrete reproduction.

---

## Few-shot: good finding

### Race on shared resource — the canonical exemplar

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Bug
  lens: state-concurrency
  file: src/payments/charge.py
  line: 84
  rule_code: ARCH-STATE-RACE
  severity: CRITICAL
  source: lens-derived
  decidable_at: diff
  checklist_score: 5/5
  status: VALIDATED
  evidence: |
    charge(user_id, amount) reads the idempotency record at line 78,
    branches on whether it exists, then inserts on line 84. No unique
    constraint, no row lock, no SELECT FOR UPDATE. Two concurrent
    requests with the same idempotency key both pass the existence check
    and both INSERT.
  proof: |
    $ pytest tests/payments/test_idempotency.py::test_concurrent_charge -x
    FAILED — 100 concurrent calls with identical key produced 7 rows in
    charges table, expected 1. Repro: tests/payments/test_idempotency.py:41.
  suggested_fix: |
    Wrap the block in a transaction with `SELECT ... FOR UPDATE` on the
    idempotency key, OR add a UNIQUE constraint on idempotency_key and
    treat the constraint violation as "already charged".
```
````

### Mutable domain entity — ARCH-STATE-DOMAIN-MUTATION

````markdown
```REVIEW-FINDINGS
- id: F-002
  category: Bug
  lens: state-concurrency
  file: src/domain/cart.py
  line: 14
  rule_code: ARCH-STATE-DOMAIN-MUTATION
  severity: CRITICAL
  source: lens-derived
  decidable_at: diff
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    src/domain/cart.py:5-6:
        @dataclass
        class Cart:
            total_cents: int
            ...
    src/domain/cart.py:14:
        def apply_discount(self, discount: int) -> None:
            self.total_cents -= discount
    Caller src/api/checkout.py:42 receives a `Cart` from the repository
    cache, passes it into `promo.apply(cart)` which calls
    `apply_discount`, then renders `cart.total_cents` in the response.
    A concurrent retry of the same checkout re-runs `promo.apply` on
    the same cached `Cart` instance, double-applying the discount.
  proof: |
    $ pytest tests/domain/test_cart.py::test_double_apply_is_idempotent -x
    FAILED — first apply yields total=9000, second apply on the same
    instance yields 8100 instead of 9000 (expected idempotent).
    $ rg -nE "@dataclass\b" src/domain/ -A 1
    cart.py:5:@dataclass
    cart.py:6-class Cart:
    Class is not `frozen=True`. Aliasing across the repository cache
    and the API response confirmed in
    tests/domain/test_cart_aliasing.py:18.
  suggested_fix: |
    Make `Cart` a `@dataclass(frozen=True)` and change `apply_discount`
    to return a new `Cart` with the discounted total. Update callers to
    rebind (`cart = cart.apply_discount(d)`). Fix must eliminate the
    `self.total_cents -= discount` line — adding `copy.deepcopy` before
    each mutation preserves the mutable-class shape and only defers
    the aliasing bug to the next caller who forgets the copy.
```
````

---

## Few-shot: good dismissal

A reviewer sees a module-level dictionary `_CONFIG` populated at import
time and flags it as "shared mutable state." It is **not** a concurrency
smell when the dict is populated exactly once (at import), read-only
after that, and never mutated by request paths. Configuration loaded
from environment variables into a module-level frozen mapping is the
conventional shape. The smell applies only when per-request code writes
to the shared container. Similarly, `_CACHE = {}` can be safe when
accessed through a thread-safe wrapper (e.g., `functools.lru_cache`,
`cachetools.LRUCache` with locking); the shape is identical but the
concurrency contract differs.

For **ARCH-STATE-DOMAIN-MUTATION** specifically: a function that builds
up a local container by repeated `dct[k] = v` assignment and returns
it at the end is *not* a violation. DOMAIN-MUTATION applies to
*entities that cross flow boundaries* and get observed through multiple
references. A helper that constructs a dict inside its body, finishes
it, and returns it has no aliasing hazard — no other code holds a
reference during the mutation. The discriminator: does any caller
retain a reference to the object while a callee mutates it? If the
container is owned by exactly one scope at mutation time and is either
returned by value or discarded, the smell does not apply. Confirm with
`rg -n "^\s*return " <function>` and by inspecting whether the
mutated object ever appears in a caller's variables simultaneously
with the callee's mutation.

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| Shared mutable state | ❌ — emerges in code | ✅ | ✅ |
| Race / check-then-act | ❌ | ✅ | ✅ |
| Resource leak | ❌ | ✅ | ✅ |
| Transactional boundary | partial — can mandate "no external I/O in txn" | ✅ | ✅ |
| Unbounded queue/retry/recursion | partial — should require bounds at design | ✅ | ✅ |
| Mutable domain entity | partial — sets "domain types frozen" policy | ✅ | ✅ |

**partial** means /antiplan sets the policy but cannot detect instances.
When `plan_present: true` and the plan addressed the policy,
pr-review/cleanup may emit `category: Architectural Drift` with
`decidable_at: design`.
