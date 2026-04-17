# Quality rubric — code & design review (tool-agnostic)

**Audience:** Reviewers auditing **existing codebases** (human or LLM). Companion to the **cleanup** skill.

**Not for ticket markdown:** Use the **ticket-critic** skill for `.tickets/*.md` hardening, blast-radius splits, and implementation-ready specs.

**Precedence:** Any **organization review packet** (dimensions, prompts, anchors in JSON) **overrides** this file. Then **Architecture Decisions (spec-writer skill)** / **`AGENTS.md`**. This rubric fills gaps with portable patterns.

**Why weights matter:** Many health programs blend a **holistic** pool (~three-quarters of the composite) with **mechanical** checks (~one-quarter). Prioritize **file-cited evidence** on **high-weight dimensions** when writing review notes.

---

## Part 1 — Review rules (all dimensions)

1. **Evidence over vibes** — cite paths, symbols, import edges, test gaps.
2. **Coupling over cleverness** — dependency direction, cycle risk, blast radius.
3. **Match the dimension** — do not score “tests” under “elegance” without labeling `test_strategy` (or your org’s equivalent).
4. **No threshold anchoring** — score from code evidence, not a target number.
5. **Structured findings** — when a tool requires JSON, supply `related_files`, `evidence`, `suggestion` per that schema.

---

## Part 2 — Canonical subjective keys & weight tiers

### 2.1 Keys and display labels (typical holistic sets)

| Canonical key | Typical display label |
|---------------|----------------------|
| `high_level_elegance` | High elegance |
| `mid_level_elegance` | Mid elegance |
| `low_level_elegance` | Low elegance |
| `contract_coherence` | Contracts |
| `type_safety` | Type safety |
| `design_coherence` | Design coherence |
| `abstraction_fitness` | Abstraction fit |
| `logic_clarity` | Logic clarity |
| `package_organization` | Structure nav |
| `test_strategy` | Test strategy |
| `error_consistency` | Error consistency |
| `naming_quality` | Naming quality |
| `ai_generated_debt` | AI generated debt |
| `cross_module_architecture` | Cross-module arch |
| `initialization_coupling` | Init coupling |
| `convention_outlier` | Convention drift |
| `dependency_health` | Dep health |
| `api_surface_coherence` | API coherence |
| `authorization_consistency` | Auth consistency |
| `incomplete_migration` | Stale migration |

### 2.2 Pool weights (typical policy table)

| Tier | Approx. weight | Display names | Typical keys |
|------|----------------|---------------|--------------|
| **A** | 22 | High elegance, Mid elegance | `high_level_elegance`, `mid_level_elegance` |
| **B** | 12 | Low elegance, Contracts, Type safety | `low_level_elegance`, `contract_coherence`, `type_safety` |
| **C** | 10 | Design coherence | `design_coherence` |
| **D** | 8 | Abstraction fit | `abstraction_fitness` |
| **E** | 6 | Logic clarity | `logic_clarity` |
| **F** | 5 | Structure nav | `package_organization` |
| **G** | 3 | Error consistency | `error_consistency` |
| **H** | 2 | Naming quality | `naming_quality` |
| **I** | 1 | AI generated debt | `ai_generated_debt` |

Keys like `test_strategy`, `cross_module_architecture`, `dependency_health`, … still deserve evidence; they may use **default weight 1.0** unless your org overrides. Spend most narrative on **Tiers A–C**.

---

## Part 3 — Subjective tiers (requirements, anti-patterns, examples)

### Tier A — High & mid elegance (weight 22 each)

**Intent:** System shape, seams, **orchestration vs I/O**, dependency direction.

**High score:** Thin CLI (`main` / `__main__`); core importable without side effects at import; adapters (HTTP, subprocess, FS, DB) behind narrow interfaces or injection; acyclic package imports; god modules split or tracked.

**Low score:** argparse + subprocess + rules in one file; utility dumps importing half the tree; wrong-direction layer imports.

**Example — poor:** `cli.py` calls `subprocess.run` directly inside `main()` with no extracted runner.

**Example — better:** `runner.run(job, executor)` in importable module; `SubprocessExecutor` in adapter; `main()` only builds job + exit code.

**Evidence template:** “`high_level_elegance`: `main.py` delegates to `runner.py`; subprocess only under `executors/`.”

### Tier B — Low elegance + contracts + type safety (12 each)

**Low elegance** (local structure; overlaps **Part 4 §M9** for size/complexity): functions ~80–100 LOC unless one algorithm; early returns; dead “temp” paths removed.

**Contracts:** Meaningful types at boundaries (`TypedDict`, Pydantic, domain types); specific errors or result types; docs match behavior.

**Type safety:** Parse JSON/env/files once into models; minimal `Any` on public APIs.

**Examples:** Replace `state: dict` key-churn with `OrchestratorState`; avoid `except Exception: return ""` for `read_text` when callers need distinct failures.

### Tier C — Design coherence (10)

One **logging** story (module logger, structured context)—not `print` + `logging` + raw traceback dumps mixed without reason. One **config** path (env → settings → consumers). One **durable write** strategy (e.g. atomic temp + rename). Centralize duplicate timeout/argv policy or document exceptions.

### Tier D — Abstraction fit (8)

One role per type; no pass-through wrappers without invariants; names match level (`run_batch` vs `do_stuff`). Use `Protocol` when policy injection is real.

### Tier E — Logic clarity (6)

Readable booleans; named constants; side effects visible in names (`load_`, `write_`); comments for **why**, not what.

### Tier F — Structure nav (5)

Feature directories; intentional `__init__` exports; tests mirror source or documented layout.

### Tier G — Error consistency (3)

User-facing vs log diagnostics distinct; same failure → same message pattern across entrypoints; `raise … from e` with context.

### Tier H — Naming quality (2)

Domain vocabulary; consistent verbs per layer; no `get_*` that mutates.

### Tier I — AI generated debt (1)

Remove placeholder fluff; no lying docstrings; TODOs only with owner/backlog.

### Test strategy (`test_strategy`)

**Intent:** Documented test command and what “green” means; pyramid (unit + mocked integration); **direct** tests for high-blast-radius modules; shared fixtures.

**Evidence template:** “`test_strategy`: `test_graph.py` exists; CLI entry still lacks direct tests.”

### Additional keys (default weight unless org overrides)

| Key | High-score signals |
|-----|-------------------|
| `cross_module_architecture` | Clear module graph; bounded contexts; low fan-in to god modules |
| `initialization_coupling` | Fast import; no network/env work in imported module init |
| `convention_outlier` | Formatter/linter/layout consistent |
| `dependency_health` | Pins/locks; no known bad deps; optional deps isolated |
| `api_surface_coherence` | Small public API; experimental areas marked |
| `authorization_consistency` | Auth at one layer; no duplicate/conflicting checks |
| `incomplete_migration` | No v1/v2 drift without bridge docs |

### Pre re-review self-audit (authors)

- [ ] CLI thin; core importable; I/O at edges  
- [ ] Boundary types; logging/config/file IO consistent  
- [ ] Tests/docs say how to run and what they prove  
- [ ] Evidence list: **files + coupling + tests** per weak dimension  

---

## Part 4 — Mechanical patterns (lint/security/test alignment)

Use when mapping code to **checkable** fixes. **Principles:** behavior-preserving refactors first; **suppressions** (`# nosec`, ignores) need **one-line threat-model note** (who controls input, local vs remote).

### M1 — Logging / exceptions / silent except

**Signals:** raw `traceback.print_exc()`, bare `except`, empty `except: pass`; often security linters flag try/except/pass (e.g. B110).

**Intent:** Observable failures via `logging.getLogger(__name__)`; `logger.exception` or `logger.error(..., exc_info=True)`; narrow `except` + log context.

**Before / after:** See Part 3 Tier C; classic fix: replace `except Exception: pass` with typed handlers + log + re-raise where fatal.

**Verify:** Linters clean on touched lines; or documented waiver.

### M2 — Subprocess without timeout

**Intent:** No hangs; configurable SLA.

**After:** `subprocess.run(..., timeout=…)` or `communicate(timeout=…)`; map timeouts to typed errors.

**Verify:** Every subprocess on touched paths has explicit timeout; behavior tested or documented.

### M3 — Subprocess / URL audit

**Intent:** No `shell=True` with user strings; argv lists; `shutil.which` or full paths; **http/https** only for URL opens unless documented.

**Verify:** `bandit -r` (or equivalent): no unexplained high/medium without fix or justified suppression.

### M4 — `sys.exit` outside CLI boundary

**Intent:** Library code raises or returns; only `__main__` / thin façade exits.

**Verify:** Importable modules testable without process exit.

### M5 — Non-atomic file writes

**Intent:** Same-dir temp + `os.replace` (or project helper); preserve encoding/newlines.

**Verify:** Durable write paths use atomic pattern.

### M6 — Dict dead writes / overwritten keys

**Intent:** No placeholder keys immediately overwritten; prefer incremental build, `TypedDict`, dataclass, Pydantic.

**Verify:** Static analysis or review shows no spurious overwrite pattern; regression tests if behavior changed.

### M7 — Swallowed errors (log-only catch)

**Intent:** Fatal errors propagate or become domain errors; non-fatal paths documented.

**Verify:** No log-only catch for state-corrupting failures.

### M8 — Optional parameter sprawl

**Intent:** Config dataclass / `TypedDict` / builder; CLI → env → file layering.

**Verify:** Public APIs have reasonable arity.

### M9 — Monster function / cyclomatic complexity

**Intent:** Extract pure helpers and phase functions; early returns (**subjective read** in Tier B low elegance).

**Verify:** Complexity within team threshold or waiver + follow-up; full test suite green.

### M10 — Loose annotations

**Intent:** Specific public types; shared `types` / `schemas` modules (**aligns Tier B type safety**).

**Verify:** Typecheck pass if project uses mypy/pyright.

### M11 — Weak hash (e.g. B324)

**Intent:** `usedforsecurity=False` with comment for fingerprints, or SHA-256 when collisions matter for correctness.

**Verify:** Security scanner clean or reviewed.

### M12 — Coverage gaps / orphaned entry

**Intent:** Direct tests for critical modules; entry importable (`__main__.py`, packaging, or test import); README documents run command.

**Verify:** Coverage tool + pytest; entry no longer “invisible” to static import graph where applicable.

---

## Part 5 — Ten AI anti-patterns → standard

| # | Category | Remove | Write instead |
|---|----------|--------|----------------|
| 1 | God component/module | UI+state+API+logic in one huge file | Layering: UI renders; services/hooks own state; clients own I/O |
| 2 | Blind swallow | `except: pass` / log-only | Typed errors; boundary handling |
| 3 | Type illusion | `any`, unchecked casts | Validate at boundary (Pydantic, Zod, …) |
| 4 | Happy-path only | Null/empty/timeout crashes | Validate early; timeouts; empty states |
| 5 | Premature abstraction | Deep hierarchies for trivia | Flat functions; two call sites before abstracting |
| 6 | Dead graveyards | Commented blocks, unused code | Delete; use VCS |
| 7 | Primitive obsession | Magic numbers, string statuses | Enums/constants; env for deploy config |
| 8 | Reinventing wheel | Custom tiny parsers | Stdlib / shared utils first |
| 9 | State entanglement | Effect chains, deep prop drill | Colocated logic; justified state boundaries |
| 10 | Redundant comments | Line-by-line narration | Names + **why** comments only |

---

## Part 6 — Layer-specific notes

**Frontend:** Decouple data-fetch from presentation; explicit props; loading/error UI; **make-ui** if project uses it.

**Middleware / services:** Validation at boundary; standardized error objects; business logic not coupled to HTTP transport.

**Data access:** Avoid N+1; indexes; repository-style modules; timeouts and empty results without over-abstracting.

---

## Part 7 — Verification commands (examples)

```bash
cd <repo>
pytest tests/ -q
ruff check .   # or project linter
bandit -r <paths>
mypy .         # if used
npx playwright test   # if frontend exists
```

Optional: if your org keeps **local tooling state** (open findings, queues), use it to **prioritize files**—not required for this rubric.

---

## Part 8 — Repo policy files (merge with review)

| Path | Role |
|------|------|
| `AGENTS.md` | Agent rules, exclusions |
| Architecture Decisions (spec-writer skill) | Blockers, architecture decisions |
| `README.md` | How to run tests and the product |
