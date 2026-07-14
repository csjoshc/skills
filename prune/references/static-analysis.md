# Static Analysis for File-Level Pruning

Rigorous, incremental, one-target-at-a-time removal — for whole packages **and**
individual dead files/modules inside packages you KEEP. The guiding principle: a
fast static analyzer (compiler / typechecker / dead-code tool) surfaces and
**proves** safety at each step, **failing fast before the test suite runs**.
`grep` (gate G1) is a coarse first pass; the tools here are the rigorous one.

## Contents

- Why grep is not enough
- Per-ecosystem tool tables (Python / TS-JS / Rust)
- Reachability-from-entrypoints (the rigorous definition of dead code)
- The delete-and-prove loop (per file or package)
- Iterate-to-fixpoint (cascading orphans)
- Confidence tiers (what evidence each requires)
- Coverage as corroborating evidence
- The CI ratchet (so dead code does not regrow)

## Why grep is not enough

`grep` finds the **substring**, not the **edge**. It cannot tell an import from a
comment, a live call from a dead re-export, or compute what is reachable from the
app's real entrypoints. It produces both false positives (a name in a docstring)
and false negatives (a `from .x import *` barrel that pulls a symbol you searched
for under a different alias). A typechecker / dead-code tool builds the actual
import graph and either proves a target unreachable or names the dangling
reference the instant you delete it. Use grep to *nominate* candidates; use these
tools to *prove* the verdict.

## Per-ecosystem tool tables

Columns: **tool → what it proves → command shape → confidence** of a positive
("this is dead") result. Run the *fast* tools (typecheck / lint) as the G1.5
static gate; run the *graph* and *dead-code* tools to nominate and to iterate to
fixpoint.

### Python

| Tool | What it proves | Command shape | Confidence |
|---|---|---|---|
| `ruff` / `pyflakes` | unused imports, undefined names (instant dangling-ref after a delete) | `ruff check . --select F` | High (dangling ref is definitive) |
| `vulture` | unused funcs/classes/vars/modules (dead code) | `vulture src/ --min-confidence 80` | Medium-High (flags dynamic-use false positives) |
| `grimp` | import graph + reachability from entrypoints | python API: `build_graph(...)`, `find_downstream/upstream` | High (graph is exact for static imports) |
| `pydeps` / `importlab` | import graph (viz / typed) | `pydeps pkg --max-bacon=0 --show-deps` | Medium-High |
| `deptry` | unused + missing + transitive deps | `deptry .` | High for unused deps |
| `unimport` | unused imports (auto-fix) | `unimport --check --diff` | High |
| `coverage.py` | runtime reachability **evidence** (not proof of dead) | `coverage run -m pytest && coverage report --show-missing` | Corroborating only |

Fast static gate (seconds, run first): `ruff check . --select F` plus, if a
typed project, `mypy` / `pyright` — both report undefined names and unresolved
imports the moment a referenced module is deleted.

### TypeScript / JavaScript

| Tool | What it proves | Command shape | Confidence |
|---|---|---|---|
| `knip` | unused files, exports, deps (the primary tool) | `knip` / `knip --production` | High (purpose-built, entrypoint-aware) |
| `ts-prune` | unused exports | `ts-prune` | Medium-High |
| `depcheck` | unused + missing deps | `depcheck` | High for unused deps |
| `madge` | orphan modules + circular deps | `madge --orphans src/` · `madge --circular src/` | High for orphans |
| `tsc` flags | unused locals/params; dangling ref after delete | `tsc --noEmit --noUnusedLocals --noUnusedParameters` | High (compiler is definitive) |
| `eslint` | `no-unused-vars`, `import/no-unresolved` | `eslint . --rule '...'` | High for unresolved |

Fast static gate (seconds, run first): `tsc --noEmit` — a deleted module that is
still referenced fails type-resolution immediately, before any test runs.
`knip --production` is the primary candidate-nominator and fixpoint engine.

### Rust

| Tool | What it proves | Command shape | Confidence |
|---|---|---|---|
| `cargo machete` | unused dependencies | `cargo machete` | High |
| `cargo +nightly udeps` | unused deps (compile-accurate) | `cargo +nightly udeps` | High |
| `dead_code` lint | unused funcs/structs/modules | `cargo build` with `#![warn(dead_code)]` / `cargo clippy` | High (compiler-backed) |

Fast static gate (seconds-to-minutes, run first): `cargo check` — a deleted module
referenced by a `mod`/`use` fails to compile immediately.

## Reachability-from-entrypoints

**Dead code = unreachable in the import graph from the complete set of
entrypoints.** Not "no grep hits." The method:

1. **Enumerate ALL entrypoints.** Miss one and the graph lies (false-positive
   dead). The full set:
   - App `main` / server bootstrap / `asgi`/`wsgi` app object.
   - CLI bins: `[project.scripts]` / `console_scripts`, `package.json#bin`,
     `[[bin]]` in Cargo.toml.
   - Every test file + `conftest.py` + test setup/fixtures.
   - Plugin registrations: `[project.entry-points.*]`, setuptools `entry_points`,
     pytest plugins, eslint/babel plugins.
   - Dynamic / string-path loaders: `importlib`, `__import__`, `import_module`,
     `require(variable)`, `Class.forName`, scaffolding that reads a `templates/`
     dir by path.
   - Framework auto-discovery: Django/FastAPI route modules, Celery task
     autodiscover, Next.js `pages/`/`app/` file-routing, Vite glob imports,
     decorators that register on import.
2. **Build the import graph** (`grimp` / `madge` / `knip` / compiler).
3. **Compute the reachable set** from the entrypoint roots.
4. **Everything unreachable is a candidate** — feed it to the delete-and-prove
   loop, do not auto-delete.

**False-negative traps (the graph cannot see these — hand-add to the entrypoint
set or the analyzer reports a live file as dead):** dynamic imports, reflection,
`entry_points`, framework magic, config-named providers/adapters, monkeypatch
registries. For each, add the real root to the analyzer config (knip
`entry`/`project`, vulture whitelist, an explicit entrypoint list for grimp) so
the reachable set is honest. This is the same coupling surface as the main
checklist's §5/§7 — see [coupling-checklist.md](coupling-checklist.md).

## The delete-and-prove loop

Per **target** — a single file/module OR a single package. One target at a time;
never batch (failures must be attributable). The static gate is the **fast
failure** that precedes the expensive test gate.

```
1. SNAPSHOT      clean tree, on a branch (git status clean; commit point known)
2. DELETE one    rm the one file / dir (+ its manifest/CI/infra co-changes for a package)
3. STATIC GATE   run the FAST analyzer — typecheck/lint/dead-code — SECONDS:
                   Python: ruff check --select F  (+ mypy/pyright if typed)
                   TS/JS:  tsc --noEmit           (+ knip)
                   Rust:   cargo check
                 → dangling reference? FAIL FAST → git revert, re-classify KEEP. STOP.
4. TEST GATE     ONLY if static gate clean: run kept test suites (G6) — minutes.
                 → fail? git revert, investigate. STOP.
5. COMMIT/REVERT clean both gates → commit this one target. else → git revert.
6. REPEAT        next target (and see fixpoint loop below).
```

Map to the existing gate sequence: this loop inserts a **static gate between G1
and the build/test gates**. Ordering becomes:

`G1 grep → G1.5 STATIC (typecheck/lint/dead-code) → G2 manifest → G3 install →
G4 build → G5 boot → G6 test → G7 infra-lint`.

G1.5 is new and cheap; it catches dangling refs in seconds so you never spend
minutes on G3–G6 for a delete that was never safe. For a **file-level** target
inside a KEEP package, G1.5 + G6 are usually the whole loop (no manifest/install/
infra co-change needed); for a **package-level** target, run the full sequence.

## Iterate-to-fixpoint

Removing a leaf file can orphan the module it was the sole importer of —
**cascading dead code**. A single pass is not enough.

```
loop:
  candidates = analyzer.orphans()          # knip / madge --orphans / vulture / grimp
  if candidates is empty: break            # FIXPOINT reached — stop
  pick one leaf candidate
  run the delete-and-prove loop on it
  # its removal may create NEW orphans — that's why we re-run the analyzer
repeat
```

Always remove **leaves first** (consistent with SKILL.md strip order): a file
nothing reachable imports. After each accepted removal, re-run the analyzer; new
orphans that appear are the next round's candidates. Stop only when the analyzer
reports **zero** new orphans (fixpoint). Record each round in the prune plan's
file-level removal log.

## Confidence tiers

Every candidate (file or package) gets a tier; the tier dictates the evidence
required before deletion is allowed.

| Tier | Definition | Evidence required to proceed |
|---|---|---|
| **High — statically-proven-unreachable** | Analyzer (knip/grimp/madge/vulture/compiler) proves it is not reachable from the full entrypoint set | Delete-and-prove loop: G1.5 static gate clean + G6 tests green. Proceed. |
| **Medium — no-grep-hits only** | grep finds no references but no analyzer proof yet (graph not built, or tool not run) | Promote to High by running the analyzer with a complete entrypoint set **before** deleting. Do not delete on grep alone. |
| **Low — reachable only via dynamic load** | Referenced only through `importlib` / reflection / `entry_points` / config key / framework magic | Needs runtime/coverage evidence (below) **and** human confirmation that no config/plugin path activates it, before delete. Default: KEEP-because-coupled. |

A candidate cannot be deleted from the Low tier directly — first gather evidence
to move it up, or leave it KEEP-because-coupled.

## Coverage as corroborating evidence

Coverage is **corroboration, never sole justification**. The rule:

- **zero runtime coverage + zero static inbound reference (analyzer-proven) =
  strong delete signal** (High tier confirmed from two independent angles).
- **untested ≠ unused.** Zero coverage alone means the code may simply lack a
  test — it can still be reachable and live. Deleting on coverage alone removes
  working code. Coverage NEVER promotes a candidate by itself.
- Correct combination: use the static analyzer to establish unreachability
  (primary), then use `coverage report --show-missing` to confirm the runtime
  path was never exercised either (secondary). Two agreeing signals = delete with
  confidence. Disagreement (zero coverage but statically reachable) = KEEP and
  flag for a test, not a delete.

For the Low tier specifically: run the app and full test suite under coverage; if
the dynamically-loaded module still shows zero hits across every realistic
config/plugin activation, that is the runtime evidence needed to consider it dead
— combined with human confirmation.

## The CI ratchet

Pruning only sticks if dead code cannot regrow. After the prune is green, wire the
dead-code analyzer into CI as a required check so any new orphan/unused-dep fails
the build:

| Ecosystem | CI check | Fails on |
|---|---|---|
| Python | `vulture src/ --min-confidence 90` · `deptry .` · `ruff check --select F` | new dead code / unused dep / unused import |
| TS/JS | `knip --no-exit-code` gated, or `knip` strict in CI · `tsc --noEmit` | new unused file/export/dep / dangling ref |
| Rust | `cargo machete` · `cargo clippy -- -D warnings` (dead_code) | new unused dep / dead code |

Seed each tool's config with the legitimate dynamic-load whitelist (knip `entry`,
vulture whitelist, deptry `ignore`) so the ratchet does not false-positive on the
entrypoint traps above. Add the check as a required status in branch protection.
This is the durable-quality payoff: the analyzer that proved each deletion now
guards the boundary you pruned to.
