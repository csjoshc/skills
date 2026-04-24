# Boundary and contract violations

Smells at the layer boundary — how the system greets inbound data, how
it talks to outside systems, and what it exposes to its own callers. The
compounding damage here is usually invisible until a framework, vendor,
or consumer changes, at which point the blast radius is everything
downstream of the leak.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (6)

### Business logic coupled to transport

**Shape (language-agnostic):** Validation, authorization, or
domain-rule evaluation lives inside a transport handler (HTTP endpoint,
GraphQL resolver, message consumer) rather than in a layer the transport
delegates to. The same rule cannot be reached from another transport or
a batch job without re-entering the HTTP/queue machinery.

**Decidable at:** `both` — /antiplan Phase 2 sets the topology ("domain
rules belong in domain/"); pr-review/cleanup catches drift.

**Why it compounds:** Each new transport (a CLI, a scheduled task, a
second API version) duplicates the rule. Tests require standing up the
framework. When the rule changes, the divergences quietly grow.

**Category mapping:** `category: Architectural Drift` (if plan named
the layer) else `Standards` / severity `HIGH` / `rule_code: ARCH-BND-TRANSPORT`

---

### Validation at the wrong boundary

**Shape (language-agnostic):** Either the system edge accepts
externally-sourced data without validation and trusts every internal
caller downstream, or every internal function re-validates data that an
edge already proved safe. One extreme produces injection and corruption;
the other produces noise that hides real checks.

**Decidable at:** `both` — policy ("validate at the edge, trust within")
at design; specific gaps at diff.

**Why it compounds:** Missing edge validation lets malformed data
propagate through caches, queues, and storage before anyone notices.
Over-defensive internal validation hides the real invariant and trains
reviewers to ignore validation code.

**Category mapping:** `category: Standards` / severity `HIGH` / `rule_code: ARCH-BND-VALIDATION`

---

### Missing anti-corruption layer around an external system

**Shape (language-agnostic):** Types, field names, or error shapes from
a third-party API, vendor SDK, or legacy system flow unchanged through
the codebase. Internal callers import the vendor's types and react to
the vendor's error codes directly.

**Decidable at:** `both` — /antiplan should require an adapter when an
external system is introduced.

**Why it compounds:** A vendor rename, field removal, or error-code
change touches every consumer. The public surface of the application
becomes a de facto re-export of the vendor's contract, and swapping the
vendor requires a full-codebase migration.

**Category mapping:** `category: Architectural Drift` (if plan specified
an adapter) else `Standards` / severity `HIGH` / `rule_code: ARCH-BND-ACL`

---

### Public API surface that exposes internals

**Shape (language-agnostic):** A publicly exported function, endpoint,
or response type surfaces storage shape, ORM rows, internal enums, or
implementation-coupled optional parameters that only make sense to
someone who has read the implementation.

**Decidable at:** `both` — policy at design ("boundary types are owned
by the current layer"); specific leaks at diff.

**Why it compounds:** Every consumer grows a dependency on the internal
shape. Refactoring the internals requires coordinating breaking changes
across all consumers, and the "public" API is really the union of every
internal detail anyone has ever used.

**Category mapping:** `category: Architectural Drift` / severity `MEDIUM` /
`rule_code: ARCH-BND-LEAK`

---

### Law of Demeter violation (reaching through collaborators)

**Shape (language-agnostic):** Production code reaches through a chain
of attribute or method accesses across two or more collaborator
boundaries — `order.user.address.zip`, `a.getB().getC().doThing()` —
requiring the caller to know the object graph of its collaborators'
collaborators. The test shape is the fingerprint: verifying this code
requires nested mock structures like
`mock_order.user.address.get_zip.return_value = "90210"`, which is a
picture of the coupling, not an incidental testing detail. The
caller is coupled to every link in the chain.

**Decidable at:** `diff` — shape visible only in code; /antiplan
cannot predict which chain depths will appear.

**Why it compounds:** Every link in the chain is a collaborator the
function knows about. A rename or refactor anywhere in the graph
ripples to every caller that reaches through it. Tests ossify the
coupling — each `mock.x.y.z` assignment entrenches knowledge of the
shape, and adding `create_autospec` to make the mock stricter locks
in the violation more rigorously. Refactoring the chain requires
changing the call site *and* all its tests *and* every other caller
that reached through the same path.

Distinct from `ARCH-BND-LEAK`: LEAK is about *exposing* internal
types outward across a boundary; DEMETER is about *reaching through*
collaborators inward from a caller. LEAK lives on APIs; DEMETER
lives in use-cases and handlers.

**Category mapping:** `category: Standards` (or `category: Layer` if
the chain crosses a declared layer boundary) / severity `MEDIUM` /
`rule_code: ARCH-BND-DEMETER`

---

### Eager construction of infrastructure at init or import time

**Shape (language-agnostic):** A class, module, or service
instantiates expensive, failure-prone, or environment-coupled
collaborators (DB clients, HTTP clients, message brokers, file
handles, network sockets, background threads) directly inside its
`__init__`, at module import, or via a default argument that
evaluates at definition time. No dependency injection, no lazy
initialization, no configurable seam. The canonical shape is
`def __init__(self, db=None): self.db = db or PostgresClient()` —
the fallback *looks* injectable but defaults to a concrete client
that the module now depends on unconditionally for its own import.

**Decidable at:** `both` — /antiplan should set "external
collaborators are injected through a port, never constructed at
init or module-load" as a policy. pr-review/cleanup catches the
direct-construction pattern on the diff.

**Why it compounds:** Every test of the class now requires either a
working collaborator or an elaborate mock of the constructor. The
class cannot be reused in a different context (different DB, test
harness, migration script) without the same collaborator graph. If
construction can fail — network unreachable, config missing — that
failure propagates to every caller trying to instantiate the class,
often at import time where it crashes the whole process before any
error-handling layer gets a chance. Module import gains side effects
(opens connections, reads config, starts threads), making import
order load-bearing.

Distinct from `ARCH-BND-ACL`: ACL is about *translating* vendor
types at the boundary so callers don't import vendor SDKs. EAGER-INIT
is about *owning* the construction of collaborators instead of
receiving them. A module can have a clean ACL and still violate
EAGER-INIT by constructing its own adapter.

**Category mapping:** `category: Layer` / severity `HIGH` / `rule_code: ARCH-BND-EAGER-INIT`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| Logic in transport | `rg -n "validate\|authorize\|policy" <transport-dir>/` showing rule bodies inline, plus absence of the same call in the domain layer via `rg -L`. |
| Validation at wrong boundary | Edge handler unit test that passes malformed input and reaches internal code; OR `rg "validate" <internal-dir>/` showing N+1 redundant validations of the same field. |
| Missing anti-corruption layer | `rg -n "from <vendor-sdk>" --type <lang>` showing vendor types imported outside a single adapter directory; OR graph query of callers of the vendor package crossing >1 layer. |
| Public surface leaks internals | Schema diff / OpenAPI diff showing ORM column names in response bodies; OR `rg -n "class .*Row\|def .*_model" <public-api-dir>/` showing storage types on the boundary. |
| Demeter violation | `rg -nE "\.\w+\.\w+\.\w+" <caller-dir>/` surfacing three-deep access chains; OR a test file that builds nested mock chains (`rg -n "\.return_value\." <test-dir>/`) — each nested `.return_value.` is a collaborator the code under test knows about. |
| Eager construction | `rg -nE "def __init__.*=\s*None.*\n.*or \w+\(\)" <dir>/ -U` for the `x = x or Client()` anti-pattern; OR `rg -n "= \w+Client\(\)\|= \w+\(\)" <module-top>/` for module-level construction; OR a test that imports the module with no network available and observes import failure. |

Prose alone never satisfies proof. A reviewer should re-run the command
and see the same evidence.

---

## Few-shot: good finding

### Logic in transport — the canonical exemplar

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Architectural Drift
  lens: layer-boundary-critic
  file: src/http/orders.py
  line: 58
  rule_code: ARCH-BND-TRANSPORT
  severity: HIGH
  source: lens-derived
  decidable_at: both
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    POST /orders handler inlines the discount-eligibility rule
    (lines 58-91) and calls the DB directly. The same rule is not
    reachable from the nightly reconciliation job, which duplicates
    the logic in src/jobs/reconcile.py:212.
  proof: |
    Plan ARCHITECTURE-DECISIONS block (.plans/orders-v2.md §3):
    "All order eligibility rules live in domain/orders/policy.py;
    transports delegate." The http handler bypasses the policy module.
    Reproduce: `rg -n "eligible_for_discount" src/` → two definitions,
    one in http/, one in jobs/, none in domain/orders/policy.py.
  suggested_fix: |
    Move the rule to domain/orders/policy.py as `is_eligible_for_discount`.
    Have both the HTTP handler and the reconcile job call it. Delete the
    duplicate in jobs/.
```
````

### Law of Demeter — ARCH-BND-DEMETER

````markdown
```REVIEW-FINDINGS
- id: F-002
  category: Standards
  lens: layer-boundary-critic
  file: src/use_cases/shipping_cost.py
  line: 23
  rule_code: ARCH-BND-DEMETER
  severity: MEDIUM
  source: lens-derived
  decidable_at: diff
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    src/use_cases/shipping_cost.py:23:
        rate = order.user.address.country.tax_rate
    Four-deep attribute chain across three collaborator boundaries
    (order → user → address → country). The matching test fixture at
    tests/use_cases/test_shipping_cost.py:41 mirrors the chain:
        mock_order.user.address.country.tax_rate = 0.08
    The nested mock is a picture of the coupling, not an incidental
    test detail.
  proof: |
    $ rg -nE "\.\w+\.\w+\.\w+\.\w+" src/use_cases/shipping_cost.py
    23:    rate = order.user.address.country.tax_rate
    $ rg -nE "\.\w+\.\w+\.\w+\s*=" tests/use_cases/test_shipping_cost.py
    41:    mock_order.user.address.country.tax_rate = 0.08
    Chain depth matches between production and test, confirming the
    coupling shape rather than a one-off.
  suggested_fix: |
    Add a `tax_rate_for(order)` method to the order aggregate (or an
    `OrderTaxPort`) and have the use-case call that. Tests mock the
    port, not the attribute chain. Fix must delete the
    `order.user.address.country` dereference — replacing the leaf name
    (`.tax_rate` → `.tax_rate_value`) or wrapping the chain behind a
    helper that still reads through the same attributes preserves the
    violation.
```
````

### Eager construction at init — ARCH-BND-EAGER-INIT

````markdown
```REVIEW-FINDINGS
- id: F-003
  category: Layer
  lens: layer-boundary-critic
  file: src/services/order_service.py
  line: 18
  rule_code: ARCH-BND-EAGER-INIT
  severity: HIGH
  source: lens-derived
  decidable_at: both
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    src/services/order_service.py:18:
        def __init__(self, db=None, stripe=None):
            self.db = db or PostgresClient()
            self.stripe = stripe or StripeClient(api_key=os.environ["STRIPE_KEY"])
    Every production caller invokes `OrderService()` with no arguments.
    The `or Client()` fallback opens a TCP connection and reads env
    vars at construction time. Test suite monkey-patches the module
    attributes to avoid real clients.
  proof: |
    $ rg -n "OrderService\(" src/ | grep -v order_service.py
    src/bootstrap/app.py:34:    service = OrderService()
    src/jobs/reconcile.py:12:    svc = OrderService()
    No call site injects the dependencies.
    $ rg -n "monkeypatch\.setattr.*order_service\.(Postgres|Stripe)Client" tests/
    tests/services/test_order_service.py:8
    tests/services/test_order_service.py:19
    tests/services/test_order_service.py:31
    Three tests patch module-level attributes — the X-ray of coupling.
  suggested_fix: |
    Make `db` and `stripe` required parameters (no default). Assemble
    `OrderService` once in `src/bootstrap/app.py`, passing real clients.
    Tests construct with in-memory fakes. Fix must delete the `None`
    defaults *and* the `or Client()` fallback — changing the default to
    `db: DbPort = NullDb()` when `NullDb()` itself does real work at
    module import preserves the eager-init shape.
```
````

---

## Few-shot: good dismissal

A reviewer sees an HTTP handler reading a request header and rejecting
the request with 400 if it's malformed, and suspects "validation at the
wrong boundary." It is **not** a violation: rejecting malformed inbound
transport envelopes (headers, content-type, auth token shape) is
transport-layer responsibility and the correct place for it. The
validation smell is about *domain rules* (e.g., "the order total must
match the line items") leaking into the handler, not about parsing the
envelope. Another common false-positive: a lightweight DTO-to-domain
translation in the handler. If the handler takes the parsed request and
hands a plain domain object to the service layer, that is the
anti-corruption boundary doing its job — not a leak.

For **ARCH-BND-DEMETER** specifically: a fluent builder whose methods
each return a new instance (`Query().select(...).where(...)`) has the
same visual chain depth but is *not* Demeter — each step returns the
builder itself, not a collaborator's collaborator. The fingerprint is
whether the chain crosses object-identity boundaries. If the test of
such code uses `mock_builder.select.return_value.where.return_value`,
reconsider — that shape indicates the builder isn't truly fluent and
has collaborators masquerading as method returns.

For **ARCH-BND-EAGER-INIT** specifically: `def __init__(self,
logger=None): self.logger = logger or logging.getLogger(__name__)` is
*not* the anti-pattern. `logging.getLogger` is idempotent, touches no
I/O, and the stdlib's logger registry is designed for exactly this
access pattern. The violation is when the default path opens a
connection, reads a file, or sends a request. Null-object defaults
(`db or NullDb()` where `NullDb` has an empty constructor and no I/O)
are fine provided the test suite can swap them. The discriminator is:
does `Service()` with no arguments cause *any* effectful work?

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| Logic in transport | partial — sets layer policy | ✅ | ✅ |
| Validation at wrong boundary | partial — sets edge-validation policy | ✅ | ✅ |
| Missing anti-corruption layer | partial — should mandate adapter | ✅ | ✅ |
| Public surface leaks internals | partial — sets boundary-type policy | ✅ | ✅ |
| Demeter violation | ❌ — emerges in code | ✅ | ✅ |
| Eager construction | partial — sets DI / no-construction-at-init policy | ✅ | ✅ |

**partial** means /antiplan sets the policy but cannot see the code;
pr-review/cleanup should emit `category: Architectural Drift` with
`decidable_at: design` whenever `plan_present: true` and the plan's
ARCHITECTURE-DECISIONS block addresses this smell.
