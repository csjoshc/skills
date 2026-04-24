# quality-rubric

**Audience:** Reviewers auditing existing codebases. Companion to the `cleanup` skill.

**Not for ticket markdown.** Use `ticket-critic` for `.tickets/*.md`.

**Precedence:** Organization review packet overrides this file. Then
Architecture Decisions / `AGENTS.md`. This rubric fills gaps.

**Cross-reference.** M-codes and Part-5 AI anti-patterns are the
mechanical / subjective altitude of the pattern taxonomy. For the
design-time (AP-\*) and diff-time (ARCH-\*) counterparts of each
code, see
[`~/.skills/reviews/cross-reference.md`](../reviews/cross-reference.md).
When a mechanical tool surfaces an M-code, the cross-reference tells
you whether the finding escalates to a lens-level architectural
violation or stays mechanical.

## Contents

- Part 1 — Review rules
- Part 2 — Subjective keys and weight tiers
- Part 3 — Subjective tiers
- Part 4 — Mechanical patterns (M1–M12)
- Part 5 — AI anti-patterns
- Part 6 — Layer-specific notes
- Part 7 — Finding output (REVIEW-FINDINGS schema)
- Part 8 — Rubric → cleanup lens ownership

---

## Part 1 — Review Rules

1. **Evidence over vibes** — cite paths, symbols, import edges, test gaps.
2. **Coupling over cleverness** — dependency direction, cycle risk, blast radius.
3. **Match the dimension** — do not score "tests" under "elegance."
4. **No threshold anchoring** — score from code evidence, not a target number.
5. **Structured findings** — emit every finding into a `REVIEW-FINDINGS`
   block (see *Part 7* and
   [`~/.skills/reviews/schemas.md`](../reviews/schemas.md)).
6. **Source tag required** — every finding carries `source: tool-flagged |
   rubric-derived | user-confirmed`. `tool-flagged` only for Phase 0
   promotions; `rubric-derived` for M-pattern / Tier matches.
7. **Proof for structural findings** — any finding needs a `proof:` field
   (reproducible command, failing test, or log excerpt) when it meets
   any of: `severity: CRITICAL` (any category), `category: Architectural
   Drift`, or `category: Layer` at `HIGH`/`CRITICAL`.

---

## Part 2 — Subjective Keys and Weight Tiers

| Tier  | Approx. weight | Keys                                                      |
| ----- | -------------- | --------------------------------------------------------- |
| **A** | 22             | `high_level_elegance`, `mid_level_elegance`               |
| **B** | 12             | `low_level_elegance`, `contract_coherence`, `type_safety` |
| **C** | 10             | `design_coherence`                                        |
| **D** | 8              | `abstraction_fitness`                                     |
| **E** | 6              | `logic_clarity`                                           |
| **F** | 5              | `package_organization`                                    |
| **G** | 3              | `error_consistency`                                       |
| **H** | 2              | `naming_quality`                                          |
| **I** | 1              | `ai_generated_debt`                                       |

Additional keys (`test_strategy`, `cross_module_architecture`, `dependency_health`,
`api_surface_coherence`, `authorization_consistency`, `incomplete_migration`,
`initialization_coupling`, `convention_outlier`) use default weight 1.0 unless
org overrides. Spend most narrative on **Tiers A–C**.

> **Note on `ai_generated_debt`:** Weight 1 reflects composite scoring policy,
> not severity. AI-generated structural failures (god modules, semantic naming
> drift, doc drift) surface under **Tier A/B** — cite them there. Use
> `ai_generated_debt` for leftover boilerplate, lying docstrings, and TODO
> graveyards only.

---

## Part 3 — Subjective Tiers

### Tier A — High and Mid Elegance (22)

System shape, seams, orchestration vs I/O, dependency direction.

**High score:** Thin CLI entry; core importable without side effects; adapters
(HTTP, subprocess, FS, DB) behind narrow interfaces; acyclic package imports.

**Low score:** argparse + subprocess + rules in one file; utility dumps importing
half the tree; wrong-direction layer imports.

**Evidence template:** "`high_level_elegance`: `main.py` delegates to `runner.py`;
subprocess only under `executors/`."

### Tier B — Low Elegance, Contracts, Type Safety (12)

**Low elegance:** Functions ~80–100 LOC max; early returns; dead temp paths removed.

**Contracts:** Meaningful types at boundaries (TypedDict, Pydantic, domain types);
specific errors or result types; docs match behavior.

**Type safety:** Parse JSON/env/files once into models; minimal `Any` on public APIs.

### Tier C — Design Coherence (10)

One **logging** story — not `print` + `logging` + raw tracebacks mixed. One
**config** path (env → settings → consumers). One **durable write** strategy.
Centralize duplicate timeout/argv policy or document exceptions.

### Tier D — Abstraction Fit (8)

One role per type; no pass-through wrappers without invariants; names match level.
Use `Protocol` when policy injection is real.

### Tier E — Logic Clarity (6)

Readable booleans; named constants; side effects visible in names (`load_`,
`write_`); comments for **why**, not what.

### Tier F — Structure Nav (5)

Feature directories; intentional `__init__` exports; tests mirror source.

### Tier G — Error Consistency (3)

User-facing vs log diagnostics distinct; same failure → same message pattern;
`raise … from e` with context.

### Tier H — Naming Quality (2)

Domain vocabulary; consistent verbs per layer; no `get_*` that mutates.

### Tier I — AI Generated Debt (1)

Remove placeholder fluff; no lying docstrings; TODOs only with owner/backlog ref.

### Test Strategy

Documented test command and what "green" means; pyramid (unit + mocked
integration); direct tests for high-blast-radius modules; shared fixtures.

**Evidence template:** "`test_strategy`: `test_graph.py` exists; CLI entry lacks
direct tests."

### Pre Re-Review Self-Audit (Authors)

- [ ] CLI thin; core importable; I/O at edges
- [ ] Boundary types; logging/config/file I/O consistent
- [ ] Tests/docs say how to run and what they prove
- [ ] Evidence list: files + coupling + tests per weak dimension

---

## Part 4 — Mechanical Patterns (M1–M12)

### M1 — Logging / Exceptions / Silent Except

Raw `traceback.print_exc()`, bare `except`, empty `except: pass`. Fix: narrow
`except` + `logger.exception` or `logger.error(..., exc_info=True)`.

### M2 — Subprocess Without Timeout

Fix: `subprocess.run(..., timeout=…)`; map timeouts to typed errors.

### M3 — Subprocess / URL Audit

No `shell=True` with user strings; argv lists; `shutil.which` or full paths;
`http/https` only unless documented. Verify: `bandit -r` clean.

### M4 — `sys.exit` Outside CLI Boundary

Library code raises or returns; only `__main__` / thin façade exits.

### M5 — Non-Atomic File Writes

Same-dir temp + `os.replace`; preserve encoding/newlines.

### M6 — Dict Dead Writes / Overwritten Keys

No placeholder keys immediately overwritten. Prefer `TypedDict`, dataclass, Pydantic.

### M7 — Swallowed Errors (Log-Only Catch)

Fatal errors propagate or become domain errors; non-fatal paths documented.

### M8 — Optional Parameter Sprawl

Config dataclass / `TypedDict` / builder. Public APIs have reasonable arity.

### M9 — Monster Function / Cyclomatic Complexity

Extract pure helpers and phase functions; early returns. Threshold: >10 or team
waiver + follow-up.

### M10 — Loose Annotations

Specific public types; shared `types` / `schemas` modules.

### M11 — Weak Hash

`usedforsecurity=False` with comment for fingerprints, or SHA-256 when
collisions affect correctness.

### M12 — Coverage Gaps / Orphaned Entry

Direct tests for critical modules; entry importable; README documents run command.

---

## Part 5 — AI Anti-Patterns

| #   | Category              | Remove                                                             | Write instead                                             |
| --- | --------------------- | ------------------------------------------------------------------ | --------------------------------------------------------- |
| 1   | God component         | UI+state+API+logic in one file                                     | Layering: UI renders; services own state; clients own I/O |
| 2   | Blind swallow         | `except: pass` / log-only                                          | Typed errors; boundary handling                           |
| 3   | Type illusion         | `any`, unchecked casts                                             | Validate at boundary (Pydantic, Zod)                      |
| 4   | Happy-path only       | Null/empty/timeout crashes                                         | Validate early; timeouts; empty states                    |
| 5   | Premature abstraction | Deep hierarchies for trivia                                        | Flat functions; two call sites before abstracting         |
| 6   | Dead graveyards       | Commented blocks, unused code                                      | Delete; use VCS                                           |
| 7   | Primitive obsession   | Magic numbers, string statuses                                     | Enums/constants; env for deploy config                    |
| 8   | Reinventing wheel     | Custom tiny parsers                                                | Stdlib / shared utils first                               |
| 9   | State entanglement    | Effect chains, deep prop drill                                     | Colocated logic; justified state boundaries               |
| 10  | Redundant comments    | Line-by-line narration                                             | Names + **why** comments only                             |
| 11  | Semantic naming drift | Names look valid but obscure intent (`processData`, `handleStuff`) | Domain vocabulary review; rename to match actual behavior |
| 12  | Documentation drift   | Code changed without updating related docs or docstrings           | Grep doc references in diff; flag stale param/return docs |
| 13  | Eager construction at init | Constructor / module-import builds real infrastructure (`def __init__(self, db=None): self.db = db or PostgresClient()`, module-level DB client, "DI-supported" with a defaulted real-client fallback) | Required constructor params for all infrastructure; composition root assembles and injects; module import has no side effects |
| 14  | Mutable domain entity | Mutable `@dataclass` / record; method mutates `self` (e.g., `apply_discount`, `add_item`) without returning; caller aliases the same instance across steps | `frozen=True` + method returns a new instance; or explicit copy before mutation; name mutations so the call site can audit them |

> **#11 and #12** are AI-specific failure modes — LLMs tend to preserve
> existing names and docs even when the behavior changes. Cite these under
> Tier A or Tier H as appropriate.
>
> **#13 and #14** are the mechanical / subjective shadow of
> `ARCH-BND-EAGER-INIT` and `ARCH-STATE-DOMAIN-MUTATION` respectively.
> Cite the ARCH code when the finding is a topology fact (lens-owned);
> cite P5-13 / P5-14 when the finding is a single-site readability or
> testability cost (rubric-owned). See
> [`~/.skills/reviews/cross-reference.md`](../reviews/cross-reference.md).

---

## Part 6 — Layer-Specific Notes

**Frontend:** Decouple data-fetch from presentation; explicit props; loading/error
UI; use `make-ui` if the project uses it.

**Middleware / services:** Validation at boundary; standardized error objects;
business logic not coupled to HTTP transport.

**Data access:** Avoid N+1; indexes; repository-style modules; timeouts; handle
empty results without masking real errors.

---

## Part 7 — Finding Output (REVIEW-FINDINGS Schema)

Every finding this rubric produces is serialized into the shared
`REVIEW-FINDINGS` fenced block (full schema:
[`~/.skills/reviews/schemas.md`](../reviews/schemas.md)).

Required mapping from rubric to schema:

| Schema field | How to fill for a rubric finding |
| --- | --- |
| `category` | `Modularity`, `Layer`, `Redundancy`, `Standards`, `Test Gap`, `Error Handling`, `Bug` |
| `lens` *(optional)* | Omit — lenses are for pr-review |
| `rule_code` | The M-code (`M1`…`M12`), tier (`A`…`I`), or anti-pattern label |
| `source` | `rubric-derived` for subjective/M-pattern matches; `tool-flagged` only if promoted from Phase 0; `user-confirmed` only if the user explicitly flagged it |
| `severity` | LOW: style/nit · MEDIUM: maintainability · HIGH: reliability · CRITICAL: security/data loss |
| `proof` | **Required for structural findings.** Fires on `severity: CRITICAL` (any category), `category: Architectural Drift`, or `category: Layer` at `HIGH`/`CRITICAL`. Reproducible command, failing test, or log excerpt — never prose alone |
| `evidence` | Quoted code or concrete import edge |
| `suggested_fix` | Concrete remediation (or "needs Architecture Decisions" if policy gap) |

Findings that cannot fill `source` or `evidence` must not be emitted.
The shared validator rejects malformed rows, so emit structured YAML — do
not free-form prose outside the block.

---

## Part 8 — Rubric → Cleanup Lens Ownership

Each of the 4 parallel cleanup lenses owns a distinct subset of rubric
codes and arch-violation files. A finding is the responsibility of
exactly one lens; if two lenses could claim it, the one lower in the
table wins (more specialized scope).

| Lens | Rubric codes owned | arch-violations owned |
| --- | --- | --- |
| Layer & Dependency | M-pattern layer violations; Tier A (architectural) | 01, 02 |
| Redundancy & Modularity | Tier A (modularity, cohesion); AI anti-patterns (Part 5) | 08, 11 |
| Error Handling & State | M1 (logging/exceptions), M2 (subprocess timeout), M5 (non-atomic writes), M7 (swallowed errors); Tier G (error consistency) | 03, 04 |
| Data & Security | M3 (subprocess/URL audit), M4 (sys.exit boundary); Tier B (contracts/type safety) | 05, 06 |

Rubric codes not listed above (M6, M8–M12; Tiers C–F, H, I) default to
the Redundancy & Modularity lens. When a finding's rubric code is
ambiguous, pick the lens that owns the closer arch-violation file.
