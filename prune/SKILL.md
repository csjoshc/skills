---
name: prune
description: Strips inherited-but-unused packages and modules from a template-derived monorepo down to load-bearing code. Use when a repo was forked or scaffolded from a base template and carries packages the live app never uses, or to reduce repo surface for an AI agent. Covers load-bearing detection, strip ordering, and coupling checks (workspace manifests, lockfiles, CI matrices, tsconfig refs, string-path loaders). Not for general code-health cleanup (use cleanup).
---

# prune

Strip a template-derived monorepo down to the code its live application actually
depends on. The target repo was scaffolded or forked from a base (a starter
template, a generator, a starter monorepo) and inherited packages the use case
never exercises. Pruning removes that dead weight so CI is faster, the security
scan surface shrinks, and an AI coding agent reads less irrelevant context.

This skill produces a **prune plan** and executes it through verification gates.
It is pure subtraction — it never rewrites surviving code. Transforming the
survivors (porting to a platform, renaming env vars, swapping infra) is a
separate concern; do that after the prune is clean, not interleaved.

## When to use

| Trigger | This skill? |
|---|---|
| Repo forked from a template, carries unused inherited packages | **Yes** |
| Reducing repo surface for an AI agent / for onboarding | **Yes** |
| Monorepo where one app uses a fraction of the workspace | **Yes** |
| Deprecating one feature/library that has live consumers | No → migrate callers, then delete it directly |
| General code smell / quality audit of code you keep | No → `cleanup` |
| One-shot removal of a single obvious dead file | No → just edit |
| Porting survivors to a new platform / conventions | No → separate migration |

## The load-bearing test

A package or module is **load-bearing** — keep it — if **any one** holds:

1. **Direct import** by the live app (`import X`, `from X`, `import "@scope/x"`).
2. **Transitive dependency** of a kept package (kept package's manifest lists it).
3. **Declared workspace/manifest dependency** of a kept package — *even with zero
   source imports*. A `workspace:*` or path dependency breaks `install
   --frozen-lockfile` and the dependent's build when its target vanishes.
4. **Build / infra / CI reference by name or path** — Dockerfile `COPY`,
   tsconfig project reference, CI job/matrix entry, helm subchart, compose service.
5. **Runtime string-path or dynamic load** — code that resolves it via a path
   string, `importlib`, `require(variable)`, plugin registry, or config key.

Everything else is a **strip candidate**. The same five rules apply at **file/
module granularity** inside packages you KEEP, not just at package granularity — a
KEEP package can still carry dead files. For file-level candidates, the rigorous
test of rule 1 is **reachability from entrypoints** proven by a static analyzer,
not a grep. See: [references/static-analysis.md](references/static-analysis.md).

> **The trap that defeats naive pruning:** zero direct import references does
> **not** mean safe to strip. The most common false-positive is a kept package
> that declares a strip candidate as a manifest dependency (rule 3) or a kept
> CLI that loads a "stripped" templates dir by path string (rule 5). Always run
> the full coupling scan, not just an import grep.

## Workflow

### 0. Baseline + discover the project's validation harness

First **discover the project's own live-fire / smoke validation** — it is more
meaningful than a generic "boot the app," and it becomes the G5/G6 gate you run
after every strip (as-you-go validation). Look for: `Makefile`/`Justfile` targets
(`smoke`, `test`, `verify`, `db-stats`, `compose-*`, `health`), a QA/validation
pattern doc (e.g. `.docs/qa-validation-pattern.md`), smoke/validation scripts, and
`package.json`/`pyproject` script entries. Record the exact commands in the plan.

> **The validation harness and everything it references are load-bearing.** If a
> strip candidate is invoked by a smoke target, QA script, or live-fire gate, it
> is KEEP — never strip the project's ability to validate itself. Verify each
> candidate against the harness before deleting.

Then capture the current green state so parity can be proven later — prefer the
project's own harness commands; fall back to these only if none exists:

```bash
<project-smoke-or-test>  2>&1 | tee .prune/baseline-tests.txt   # e.g. make test / make smoke
<build-all>              2>&1 | tee .prune/baseline-build.txt    # e.g. pnpm -r build
<project-live-fire-up>                                          # e.g. make compose-patent + health curl
```

If the baseline is already red, stop — fix or record that before pruning, or you
cannot attribute later failures.

### 1. Inventory the workspace

Read the workspace manifests and list **every** declared member and **how** it is
declared (explicit path vs glob). This is the authoritative package set — not the
directory listing, which may contain non-members.

- Python (uv/hatch): `[tool.uv.workspace].members`, `[tool.uv.sources]`
- JS/TS (pnpm/npm/yarn): `pnpm-workspace.yaml`, root `package.json#workspaces`
- Rust: `[workspace].members` in `Cargo.toml`
- Also note: dirs present but **not** members (often templates/fixtures) and the
  importable module name per package (may differ from the dir name).

### 2. Direct-reference scan

For each package's **importable name** (not dir name), grep the live app tree for
imports. Record the count **and the referencing files**, and **separate app code
from test-only references** — a module used only by a test of itself is not
load-bearing for the app.

Ground-truth shortcut: the app's own **Dockerfile `COPY` list** and the app
manifest's **declared dependencies** are usually the real dependency set. Diff
your grep results against them; mismatches are bugs in your scan.

Grep is the coarse pass. For rigor, run the ecosystem's **static analyzer**
(knip / vulture+grimp / cargo-machete) to compute **reachability from the full
entrypoint set** and nominate dead packages **and dead files within kept
packages**. This proves what grep only guesses. See:
[references/static-analysis.md](references/static-analysis.md).

### 3. Coupling scan (the part that prevents broken deletes)

Run every check in **[references/coupling-checklist.md](references/coupling-checklist.md)**
for each strip candidate. This is where rules 2–5 of the load-bearing test get
verified: manifest deps, lockfiles, tsconfig/project references, CI
job-matrices and hardcoded package-name loops, container/compose/helm wiring,
string-path and dynamic loaders, `__init__`/index re-exports, and `conftest`/test
fixtures. Do not skip — this is the difference between a clean strip and a red CI.

### 4. Classify and order

Produce the plan in **[templates/prune-plan.md](templates/prune-plan.md)**. For
each candidate record: verdict (STRIP / KEEP / KEEP-because-coupled), the evidence,
and every co-file that must change with it (manifests, CI, lockfile, infra).

**Strip order — leaves first.** Strip packages that nothing kept depends on
before packages that a kept package consumes. If a kept package depends on a
candidate, that candidate is **not** a leaf: either keep it, or de-wire the
dependency first (then it becomes strippable in a later step).

### 5. Strip — one target per branch/PR (package OR file)

Never batch. Failures must be attributable. A **target** is one package **or** one
dead file/module inside a kept package. Assign each candidate a **confidence
tier** (High = statically-proven-unreachable / Medium = no-grep-hits only / Low =
reachable only via dynamic load) — only High proceeds to delete; promote Medium
by running the analyzer first, treat Low as KEEP-because-coupled until runtime
evidence clears it. See: [references/static-analysis.md](references/static-analysis.md).

Run the **delete-and-prove loop** per target: snapshot → delete one → **fast
static gate (G1.5)** → only if clean run tests (G6) → commit, else `git revert`.

For a **package** target:

1. Remove from workspace manifest + delete the directory.
2. Apply every co-change from the plan (tsconfig refs, CI jobs/matrix/loops,
   compose services, helm subcharts, Dockerfiles).
3. **Scrub references in the long-lived tree in the same commit** — README,
   AGENTS.md/CLAUDE.md, `docs/`, architecture diagrams, `.env.example`. A strip
   is not done while prose still describes deleted code (it poisons the next
   reader, human or agent). Remove lines that described only the stripped target;
   update lines that named it alongside survivors. Exception: *generated* docs
   (docs-gen output) regenerate — don't hand-edit them. Use the
   sweep in `references/coupling-checklist.md` (doc and diagram debris) for the file-type list.
4. Regenerate the lockfile (`uv lock`, `pnpm install`, `cargo update -p`).
5. Run the full gate sequence below.
6. Commit only when gates pass green.

For a **file/module** target inside a kept package: delete the one file → G1.5
static gate → G6 tests → commit/revert (manifest/install/infra gates usually
don't apply). After **each** accepted removal, re-run the analyzer — a removed
leaf can orphan its dependency. Repeat **to fixpoint** (analyzer reports no new
orphans). Log each removal in the plan's file-level removal log.

### 6. Final parity gate

After all targets are stripped, run the full baseline commands again. Pass
condition: the same tests pass as in step 0, minus the tests that lived inside
stripped packages. Same build, app still boots.

## Gate sequence (fast-failure smoke tests)

Run per strip in this order; stop at the first failure and investigate.

| Gate | Command shape | Catches |
|---|---|---|
| G1 Static | grep import name across app | direct references (rule 1), coarse |
| G1.5 Analyzer | typecheck/lint/dead-code: `tsc --noEmit` · `ruff check --select F` (+mypy) · `cargo check` · `knip` | dangling refs the instant you delete — **fast failure before tests** |
| G2 Manifest | read kept manifests for the name | declared deps (rule 3) |
| G3 Install | `install --frozen-lockfile` / `uv sync` | lockfile + workspace coupling |
| G4 Build | build all kept packages | tsconfig/project-ref + compile coupling |
| G5 Boot / live-fire | run the **project's own smoke/live-fire harness** (Makefile `smoke`/`compose-*`, QA-pattern doc, health curl) — fall back to mock-provider boot only if none exists | runtime/dynamic-load coupling (rule 5); real regressions a generic boot misses |
| G6 Test | run kept test suites (the project's `make test` / runner) | indirect behavioral coupling |
| G7 Infra-lint | render/validate compose, helm, CI config | dangling infra references (rule 4) |

G1–G2 are seconds and run before deletion. G1.5 runs **right after** the delete
and is the fast failure (seconds) that precedes the expensive test/build gates —
a dangling reference fails here before you ever spend minutes on G3–G6. G3–G7 run
after each deletion. A candidate that clears G1+G2 but fails G3 is the classic
"zero imports but manifest-coupled" case — re-classify it as KEEP-because-coupled
or de-wire first. Full analyzer command shapes and the CI ratchet that keeps dead
code from regrowing: [references/static-analysis.md](references/static-analysis.md).

> **G5 must run against a freshly rebuilt artifact — never a stale one.** If the
> live-fire harness uses containers, rebuild images from the working tree
> (`docker compose up -d --build`) and **stop any pre-existing/duplicate-project
> containers first** — a health check that passes against a 4-day-old container
> built from the *un-pruned* code is a **false green** that proves nothing. Verify
> the thing serving the port is the rebuilt artifact (check the compose project
> name and image build time; the dir-derived project name differs between a
> worktree and the main checkout, so both stacks can exist at once and collide on
> ports). Same rule for a dev server, a reinstalled venv, or a cached build:
> restart it from the pruned tree before trusting the result. Note that a
> container DB volume is per-project — a freshly rebuilt stack starts with an
> **empty** corpus, so the data-dependent gates (pipeline row-counts, corpus
> search) need a re-ingest or a baseline run on the un-pruned stack for comparison.

**Tearing down the old stack is a required G5 step — not optional.** Full e2e
validation is only real against the rebuilt artifact, so a pre-existing/long-running
stack holding the ports **must be stopped** and the pruned stack brought up in its
place (then migrate + seed/ingest so the data-dependent gates can run). This
disrupts a running environment (and the operator may be watching it), so it is an
**authorization gate: raise an HITL question before stopping a stack you did not
start** — state what you'll stop, that its data volume is preserved (`docker
compose stop`/`stop <containers>`, not `down -v`, so it is restartable), and that
the rebuilt stack starts with an empty DB. Proceed once authorized; never skip the
teardown just to avoid the disruption — an unvalidated prune is not done. Record
the authorization and the e2e result in the plan.

**Reuse the existing data volume — don't re-ingest into an empty one.** The
data-dependent gates (row-counts, corpus search, provenance) are far cheaper to
validate against the corpus you already have. Run the rebuilt stack so it attaches
the *existing* DB volume rather than a fresh empty one: easiest is to bring it up
under the **same compose project name** (project name defaults to the directory
basename, so a git **worktree** gets a *different* name and a *different* volume —
that is the usual reason a rebuilt stack comes up empty; override with `-p
<old-project>` or `COMPOSE_PROJECT_NAME`). Alternatives: an `external: true` shared
volume, or point `DATABASE_URL` at the running DB. **Postgres is single-writer** —
only one server per data volume at a time, so stop the old app/server first; the
two stacks can't both be live on one volume. After attaching, **confirm the app
reports the real provider/embedding model, not the mock** (a rebuilt-for-boot
stack often defaults to a mock provider, which makes corpus-search scores
meaningless — the query vector won't match a corpus embedded by the real model).
For provenance, embed a probe query with the real model yourself and compare your
pgvector similarity to the app's score; matching to ~3 dp proves the same path.

## Strip vs. extract

Not everything stripped is worthless. A use-case-agnostic package that other
pilots will want (eval harness, HITL, generic templates) should be **stripped
from this repo but preserved in the base template** it came from — otherwise the
next pilot re-inherits it and re-prunes it forever. Mark each STRIP as
`delete` (dead everywhere) or `extract-to-base` (valuable upstream) in the plan.
This is the signal that the real fix may be publishing the base as versioned
dependencies rather than forking it — note it, but it is out of scope here.

## Hard constraints

- **Never delete on zero-import alone.** Clear the full coupling checklist first.
- **One strip target per PR.** No batching.
- **Lockfile + CI co-change in the same commit** as the deletion, never after —
  a deletion that leaves a dangling required CI job blocks the merge.
- **Archive, don't hard-delete, anything with <6 months of history** or unclear
  provenance — move to a branch or `_archive/` so rollback is `git revert`.
- **Don't rewrite survivors.** Renames, ports, and infra swaps are out of scope.
- **Re-baseline if the app boot is red** before starting; never prune on red.

## Outputs

- `.prune/baseline-*.txt` — pre-change green state.
- `.prune/prune-plan.md` — filled from the template; the auditable record.
- One branch/PR per strip target (package or file), each green through the gate
  sequence (G1 → G1.5 static → G2–G7).
- CI ratchet check committed so pruned dead code cannot regrow.

## References

- [references/coupling-checklist.md](references/coupling-checklist.md) — exhaustive
  non-obvious coupling checks across uv / pnpm / cargo / docker / helm / CI.
- [references/static-analysis.md](references/static-analysis.md) — per-ecosystem
  dead-code tooling, reachability-from-entrypoints, the delete-and-prove loop,
  fixpoint iteration, confidence tiers, coverage guidance, and the CI ratchet.
- [templates/prune-plan.md](templates/prune-plan.md) — fill-in plan + checklist
  for one invocation.
- [EXAMPLE.md](EXAMPLE.md) — worked example with real numbers from a starter-derived
  repo, including the corrections that naive grep missed.

## Final checklist (retrieval anchor)

- [ ] Baseline captured green (tests, build, app boot)
- [ ] Workspace members inventoried from manifests, not dir listing
- [ ] Importable name (not dir name) used for every scan
- [ ] App vs test-only references separated
- [ ] Coupling checklist run for every candidate (not just import grep)
- [ ] Static analyzer run with full entrypoint set (reachability, not grep) for packages AND files
- [ ] Each candidate assigned a confidence tier (High / Medium / Low)
- [ ] Candidates classified STRIP / KEEP / KEEP-because-coupled
- [ ] STRIPs marked delete vs extract-to-base
- [ ] Strip order is leaves-first
- [ ] One target per PR; lockfile + CI + infra co-changed in the same commit
- [ ] Each strip green through gates G1 → G1.5 static → G2–G7 (static gate before tests)
- [ ] File-level removals iterated to fixpoint (analyzer reports no new orphans)
- [ ] Final parity gate matches baseline minus stripped-package tests
- [ ] CI ratchet wired (dead-code analyzer required check) so dead code can't regrow
