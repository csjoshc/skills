---
name: prune
description: "Strips inherited, unused packages from a template-derived repo down to load-bearing code. Use when a forked or scaffolded repo carries packages the live app never uses."
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

Full procedure, commands and examples: [references/workflow.md](references/workflow.md). Read it before step 1.

0. **Baseline.** Discover the project's own smoke/live-fire harness (it is load-bearing; never strip the ability to validate) and capture a green baseline in `.prune/`. If baseline is red, stop.
1. **Inventory** every workspace member from the manifests, not the directory listing.
2. **Direct-reference scan** by importable name; separate app code from test-only references; run the static analyzer for reachability.
3. **Coupling scan**: every check in [references/coupling-checklist.md](references/coupling-checklist.md) for each candidate.
4. **Classify and order** in [templates/prune-plan.md](templates/prune-plan.md): STRIP / KEEP / KEEP-because-coupled, evidence and co-files per candidate. Strip leaves first; a candidate a kept package depends on is not a leaf.
5. **Strip one target per branch/PR** (a package or one dead file). Delete-and-prove loop: snapshot, delete one, G1.5 static gate, then tests (G6), commit or `git revert`. Only High-confidence candidates are deleted; Medium needs the analyzer first; Low is KEEP-because-coupled. Scrub README, docs, diagrams and `.env.example` in the same commit. Repeat file-level removals to fixpoint. Tiers and loop: [references/static-analysis.md](references/static-analysis.md).
6. **Final parity gate**: same tests pass as step 0 minus tests inside stripped packages; same build; app boots.

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

**G5 rules (hard):**

- Run G5 against a **freshly rebuilt** artifact. Stop any pre-existing or duplicate-project containers first; a green health check against an old container built from un-pruned code is a false green.
- **Authorization gate:** stopping a stack you did not start needs an explicit HITL question first. State what you will stop, that its data volume is preserved (`stop`, not `down -v`), and the rebuilt stack's data state. Never skip the teardown to avoid the disruption; an unvalidated prune is not done.
- Prefer reusing the existing data volume (same compose project name) over re-ingesting, and confirm the app uses the real provider, not the mock.

Details, commands and provenance check: [references/live-fire-gate.md](references/live-fire-gate.md).

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

- [references/workflow.md](references/workflow.md): steps 0-6 with commands; read before step 1.
- [references/coupling-checklist.md](references/coupling-checklist.md): exhaustive non-obvious coupling checks across uv / pnpm / cargo / docker / helm / CI; read at step 3.
- [references/static-analysis.md](references/static-analysis.md): per-ecosystem dead-code tooling, reachability, delete-and-prove loop, fixpoint, confidence tiers, CI ratchet; read at steps 2 and 5.
- [references/live-fire-gate.md](references/live-fire-gate.md): G5 rebuild, teardown authorization and data-volume reuse; read when G5 runs against containers.
- [templates/prune-plan.md](templates/prune-plan.md): fill-in plan and checklist for one invocation.
- [EXAMPLE.md](EXAMPLE.md): worked example with real numbers, including corrections naive grep missed.

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
