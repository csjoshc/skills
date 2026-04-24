# Data layer and integration

Smells where correctness looks fine at development volume and the
failure mode emerges only at production scale, under retry storms, or
when a downstream dependency slows down. Hardest category to catch in
review because the "bad" code often looks unexceptional.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (5)

### Unbounded query

**Shape (language-agnostic):** A query that fetches a whole table or
relation with no explicit limit, pagination token, or cursor — relying
on "there won't be that many rows." Works on seed data; catastrophic
at scale.

**Decidable at:** `both` — /antiplan should set "all list endpoints
paginate" as a policy; diff review finds violations.

**Why it compounds:** Fine until the table grows. First incident is a
memory pressure event in an upstream service, with no obvious cause
other than "more data than before."

**Category mapping:** `category: Bug` / severity `HIGH` / `rule_code: ARCH-DATA-UNBOUNDED`

---

### N+1 query pattern

**Shape (language-agnostic):** A loop issues one query per element of
a collection fetched by a prior query. The round-trip count scales with
the outer collection size.

**Decidable at:** `diff`

**Why it compounds:** Looks O(1) per row in code; is O(n) in
round-trips at runtime. Latency grows linearly with data volume; an
endpoint that returns 10ms in dev returns 4s in prod after the table
triples.

**Category mapping:** `category: Bug` / severity `MEDIUM` / `rule_code: ARCH-DATA-N-PLUS-ONE`

---

### Implicit ordering assumption

**Shape (language-agnostic):** Code consumes query results in a
specific order (first row is latest, pagination depends on insert
order) without an explicit `ORDER BY` or equivalent deterministic sort.

**Decidable at:** `diff`

**Why it compounds:** Engine upgrades, index additions, or plan changes
flip row order without warning. Pagination returns duplicates or skips
rows; "most recent" shows an arbitrary row.

**Category mapping:** `category: Bug` / severity `MEDIUM` / `rule_code: ARCH-DATA-ORDER`

---

### No idempotency on a retriable write path

**Shape (language-agnostic):** A write endpoint (webhook handler,
message consumer, payment flow) can be invoked multiple times for the
same logical event and produce multiple side effects — no idempotency
key, no dedupe store, no compare-and-swap.

**Decidable at:** `both` — /antiplan should mandate idempotency for any
retried-by-design path.

**Why it compounds:** Retries are not "if," they're "when." A single
vendor hiccup plus a naive retry loop creates duplicate charges,
double-shipments, or double-notifications. Hard to detect until a
customer reports it.

**Category mapping:** `category: Bug` / severity `CRITICAL` when the
write is money/inventory/auth; else `HIGH` / `rule_code: ARCH-DATA-NON-IDEMPOTENT`

---

### Missing timeout on outbound call

**Shape (language-agnostic):** A network, subprocess, or blocking disk
call is issued without a bounded deadline. Default behavior on
upstream slowness is to wait forever.

**Decidable at:** `both` — /antiplan should mandate timeouts at every
outbound-call site.

**Why it compounds:** One slow dependency cascades: worker threads
block, connection pools saturate, upstream timeouts fire on the caller,
a minor vendor blip takes down the service. The finding in one place
applies to the entire outbound-call surface.

**Category mapping:** `category: Standards` / severity `HIGH` / `rule_code: ARCH-DATA-TIMEOUT`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| Unbounded query | `rg -n "\.all\(\)\|SELECT \* FROM\|find\(\{\}\)" <dir>/` cross-referenced with absence of `limit\|LIMIT\|cursor\|paginate`; OR endpoint response containing full table in test with seeded scale. |
| N+1 | `rg -n "for .* in .*\.all\(\):" -A 5 <dir>/` showing a query inside the loop; OR query-log capture from a test showing per-row queries; ORM-specific linters (e.g., `nplusone` middleware, `ActiveRecord::Bullet`). |
| Implicit ordering | `rg -n "\.first\(\)\|\[0\]" <dir>/` in a query-result context, plus grep of the same file/query for absence of `ORDER BY\|order_by`. |
| Non-idempotent write | `rg -n "@webhook\|consumer\|POST.*charge\|POST.*order" <dir>/` cross-referenced with absence of `idempotency_key\|dedupe_store\|ON CONFLICT`. |
| Missing timeout | `rg -n "requests\.\|httpx\.\|fetch\(\|urlopen\(" <dir>/` cross-referenced with absence of `timeout=\|AbortSignal\|Deadline`; OR `bandit B113` / language-specific lint output. |

Prose alone never satisfies proof. CRITICAL findings must cite a
concrete reproduction path.

---

## Few-shot: good finding

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Bug
  lens: data-integration
  file: src/integrations/stripe_webhook.py
  line: 47
  rule_code: ARCH-DATA-NON-IDEMPOTENT
  severity: CRITICAL
  source: lens-derived
  decidable_at: both
  checklist_score: 5/5
  status: VALIDATED
  evidence: |
    handle_charge_succeeded reads the event body and inserts a row into
    payments_received without checking whether event.id has been seen.
    Stripe's delivery contract is at-least-once; duplicate deliveries
    produce duplicate payment credits.
  proof: |
    $ pytest tests/integrations/test_stripe_webhook.py::test_duplicate_event_is_idempotent -x
    FAILED — posting the same Stripe event twice produced two rows in
    payments_received, total credited = 2× amount. Reproduces at
    tests/integrations/test_stripe_webhook.py:33.
  suggested_fix: |
    Add UNIQUE(event_id) constraint to payments_received. Wrap the insert
    in an ON CONFLICT DO NOTHING clause and treat the conflict as success.
    Document the idempotency contract in AGENTS.md so the next webhook
    handler inherits the pattern.
```
````

---

## Few-shot: good dismissal

A reviewer sees `Users.all()` in code and flags it as an unbounded
query. It is **not** a smell when the query targets a small, bounded
configuration table (e.g., `Roles.all()` where roles are a 5-row
enum-like table populated at deploy time), or when the caller
immediately chains a filter that is provably selective (`all().where(...)`).
The "unbounded" smell is about call-sites that can load arbitrarily many
rows into memory, not about the existence of a no-arg query method.
Similarly, a loop-with-query is not N+1 if the outer collection is
bounded to a small constant (e.g., the 3 payment gateways enabled in
config) — the query count doesn't scale with user data.

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| Unbounded query | partial — should mandate pagination | ✅ | ✅ |
| N+1 | ❌ — emerges in code | ✅ | ✅ |
| Implicit ordering | ❌ | ✅ | ✅ |
| Non-idempotent write | partial — should mandate idempotency policy | ✅ | ✅ |
| Missing timeout | partial — should mandate timeouts everywhere | ✅ | ✅ |

**partial** means /antiplan sets the policy but cannot see the code.
When `plan_present: true` and the plan addressed pagination, idempotency,
or timeouts, pr-review/cleanup may emit `category: Architectural Drift`
with `decidable_at: design`.
