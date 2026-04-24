# Dependency direction and coupling

Compounding violations at the import-graph level. These distort the whole
system's shape, not just the module that contains the bad line. The
layer-boundary-critic tool catches most of them mechanically; this
catalog file captures the *reasoning* a reviewer should apply when the
tool flags something or when the tool doesn't exist in the project.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (5)

### Upward import

**Shape (language-agnostic):** A module in a lower layer of the documented
layer cake (data, domain, infrastructure) imports a symbol defined in a
higher layer (transport, presentation, application). The direction is
inverted relative to the project's declared topology.

**Decidable at:** `both` — /antiplan Phase 2 sets the topology; pr-review
and cleanup catch drift from it.

**Why it compounds:** The lower layer is no longer reusable in isolation.
Every downstream project that wants the lower layer now transitively
pulls the higher layer, its dependencies, and its configuration. Testing
the lower layer requires bootstrapping the higher one.

**Category mapping:** `category: Layer` / severity `HIGH` / `rule_code: ARCH-DEP-UP`

---

### Sideways import without shared sublayer

**Shape (language-agnostic):** Two peer modules at the same layer depth
import directly from each other instead of both depending on a shared
sublayer. Creates an implicit bidirectional edge that is easy to turn
into a cycle on the next change.

**Decidable at:** `diff` — only visible after both modules exist.

**Why it compounds:** Every new call path between the two modules
tightens the coupling; one eventually grows a cycle, at which point the
pair must deploy, test, and evolve together.

**Category mapping:** `category: Layer` / severity `MEDIUM` / `rule_code: ARCH-DEP-SIDE`

---

### Import cycle at the module or package level

**Shape (language-agnostic):** The transitive import graph contains a
cycle A → B → A (direct) or A → B → C → A (indirect) at the module,
file, or package boundary.

**Decidable at:** `diff`

**Why it compounds:** All modules in the cycle must be loaded, tested,
and deployed as a unit. Refactoring one forces re-testing all. Incremental
compilation and hot-reload degrade. Eventually one circular member
depends on an implementation detail of another, freezing the cycle in
place permanently.

**Category mapping:** `category: Layer` / severity `HIGH` / `rule_code: ARCH-DEP-CYCLE`

---

### Leaking implementation type across a public boundary

**Shape (language-agnostic):** A public function, endpoint, or exported
type surfaces a concrete implementation type — an ORM row, a framework
request object, a vendor SDK type — instead of a domain type owned by
the current layer.

**Decidable at:** `both` — /antiplan should set the policy at Phase 2
("domain types at the boundary, never implementation types"); diff
review catches specific leaks.

**Why it compounds:** Every caller is now coupled to the implementation
choice. Swapping the ORM, framework, or vendor requires updating every
consumer. The public API becomes a de facto re-export of the vendor's
API surface.

**Category mapping:** `category: Architectural Drift` (if plan specified
domain types) or `category: Layer` / severity `HIGH` / `rule_code: ARCH-DEP-LEAK`

---

### I/O primitive used inside a pure or domain module

**Shape (language-agnostic):** A module that the project's layer cake
designates as pure (domain, use-case, business-logic) invokes an I/O
primitive directly — `open()` on the filesystem, a socket or HTTP call,
`subprocess`, stdin/stdout, a clock, a random source without injection.
The module may have no imports from a higher layer at all; the
violation is the *use* of an environmental primitive, not the import
edge. Imports like `import requests` or `from pathlib import Path`
inside `domain/` are structurally enough to trigger this smell even
when no upward layer import exists.

**Decidable at:** `both` — /antiplan Phase 2 should set "no I/O in
domain; environmental dependencies go through ports" as a policy.
pr-review/cleanup catches the primitives on the diff. Distinct from
`ARCH-DEP-UP` because no upward import is required — reaching for
`open()` or `requests.get()` inside a pure module is the violation.

**Why it compounds:** Every test of the pure layer now requires a
working filesystem, network, clock, or subprocess runner. Unit tests
either go slow and flaky or grow elaborate mock structures of the I/O
primitive (which — per the mock-as-X-ray heuristic — indict the
coupling). The pure layer loses its portability property: it cannot
run in a different environment (different storage backend, async
runtime, WASM target) without re-creating its I/O assumptions.
Domain logic becomes structurally inseparable from its I/O choices.

**Category mapping:** `category: Layer` / severity `HIGH` / `rule_code: ARCH-DEP-IO-IN-PURE`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| Upward import | `madge --circular` or `importlinter` config showing the forbidden edge, OR a `rg` on the offending import line + AGENTS.md layer map excerpt |
| Sideways without sublayer | `madge --image deps.svg` showing bidirectional edge, OR a grep for both sides importing each other |
| Import cycle | `madge --circular .` / `npx madge --circular` / `pycycle` output listing the cycle members |
| Leaking implementation type | Public signature line + a grep of callers showing them importing the leaked type, OR the linked plan's ARCHITECTURE-DECISIONS block stating domain-type requirement |
| I/O primitive in pure module | `rg -nE "\bopen\(\|requests\.\|httpx\.\|socket\.\|subprocess\.\|time\.time\(\)\|datetime\.now\(\)\|random\." <pure-dir>/` — every hit in the pure-layer directory is a candidate. Cross-reference with the project's declared layer map. |

Prose alone never satisfies proof. A reviewer should be able to re-run
the command and see the same result.

---

## Few-shot: good finding

### Upward import — the canonical exemplar

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Layer
  lens: layer-dependency
  file: src/data/user_repo.py
  line: 12
  rule_code: ARCH-DEP-UP
  severity: HIGH
  source: tool-flagged
  decidable_at: both
  checklist_score: 4/4
  status: VALIDATED
  evidence: |
    src/data/user_repo.py:12 imports `AuthContext` from src/http/middleware.py.
    AGENTS.md declares data < domain < http; the data layer must not import
    from http.
  proof: |
    $ madge --circular --extensions py src/
    → data/user_repo.py -> http/middleware.py -> domain/auth.py -> data/user_repo.py
    Cycle formed by this edge.
  suggested_fix: |
    Move the auth-context type to domain/ (or a shared sublayer) and import
    from there. The http middleware can still reference the domain type.
```
````

### I/O primitive in pure module — ARCH-DEP-IO-IN-PURE

````markdown
```REVIEW-FINDINGS
- id: F-002
  category: Layer
  lens: layer-dependency
  file: src/domain/stats/aggregator.py
  line: 34
  rule_code: ARCH-DEP-IO-IN-PURE
  severity: HIGH
  source: lens-derived
  decidable_at: both
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    src/domain/stats/aggregator.py:34 calls `requests.get(url)` directly
    inside `compute_daily_rollup()`. Top of the module imports `requests`
    and `datetime`. AGENTS.md designates src/domain/ as the pure layer:
    "no I/O, no transport, no time — depend on injected ports". No
    `MetricsPort` / `Clock` argument is threaded through; the function
    takes only a `date_range` value.
  proof: |
    $ rg -n "requests\.|httpx\.|open\(|datetime\.now\(\)|time\.time\(" src/domain/
    src/domain/stats/aggregator.py:34:    response = requests.get(url)
    src/domain/stats/aggregator.py:48:    stamp = datetime.now()
    Both calls cross the pure-layer boundary. AP-15 at plan time would
    have required a port; its absence is the design-altitude evidence.
  suggested_fix: |
    Introduce `MetricsPort` and `Clock` protocols in src/domain/ports.py;
    `compute_daily_rollup` takes them as required parameters. Move the
    `requests.get` call into src/infrastructure/http_metrics.py implementing
    `MetricsPort`. Fix must delete `import requests` and `from datetime
    import datetime` from aggregator.py — renaming the function or
    wrapping the call behind a retry decorator preserves the violation.
```
````

---

## Few-shot: good dismissal

A reviewer sees `from src.data.models import User` imported inside
`src/http/handlers.py` and suspects a layer violation. It is **not** a
violation: `http` is a higher layer than `data`, so `http → data` is the
expected downward direction. The violation would be the reverse (data
importing from http).

Another common false-positive shape: type-only imports across layers in
languages where types don't affect runtime coupling (TypeScript `import
type`, Python `TYPE_CHECKING` blocks). These usually should not be
flagged — they carry no runtime dependency and exist to preserve
type-checking without creating an import cycle. Flag only if the
project's AGENTS.md explicitly bans type-only upward references.

For **ARCH-DEP-IO-IN-PURE** specifically: `from pathlib import Path`
imported inside `src/domain/orders/policy.py` is *not* a violation if
`Path` is used only for value manipulation (`Path("/").parts`,
`p.suffix`, string-equivalent operations) and never for `.read_text()`,
`.exists()`, or `.open()`. The `Path` type in isolation is a value-like
primitive; only its effectful methods cross the boundary. Confirm with
`rg -n "\.read_|\.write_|\.exists\(|\.open\(" <file>` — zero hits means
the import is benign. Similarly, `from datetime import timedelta` is
pure arithmetic; `datetime.now()` is the violation.

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| Upward import | partial — sets the topology but cannot see code | ✅ | ✅ |
| Sideways without sublayer | ❌ — emerges from code structure | ✅ | ✅ |
| Import cycle | ❌ | ✅ | ✅ |
| Leaking implementation type | partial — sets domain-type policy | ✅ | ✅ |
| I/O primitive in pure module | partial — sets "no I/O in domain" policy | ✅ | ✅ |

**partial** means /antiplan should set the policy but cannot detect
instances. pr-review/cleanup should emit `category: Architectural Drift`
with `decidable_at: design` whenever `plan_present: true` and the linked
plan explicitly addressed the policy.
