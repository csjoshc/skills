# Prune Workflow (Steps 0-6)

## Contents

- 0. Baseline and validation harness
- 1. Inventory the workspace
- 2. Direct-reference scan
- 3. Coupling scan
- 4. Classify and order
- 5. Strip, one target per branch/PR
- 6. Final parity gate

Gate definitions (G1-G7) live in SKILL.md; the live-fire gate rules live in [live-fire-gate.md](live-fire-gate.md).

## 0. Baseline + discover the project's validation harness

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

## 1. Inventory the workspace

Read the workspace manifests and list **every** declared member and **how** it is
declared (explicit path vs glob). This is the authoritative package set — not the
directory listing, which may contain non-members.

- Python (uv/hatch): `[tool.uv.workspace].members`, `[tool.uv.sources]`
- JS/TS (pnpm/npm/yarn): `pnpm-workspace.yaml`, root `package.json#workspaces`
- Rust: `[workspace].members` in `Cargo.toml`
- Also note: dirs present but **not** members (often templates/fixtures) and the
  importable module name per package (may differ from the dir name).

## 2. Direct-reference scan

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

## 3. Coupling scan (the part that prevents broken deletes)

Run every check in **[references/coupling-checklist.md](references/coupling-checklist.md)**
for each strip candidate. This is where rules 2–5 of the load-bearing test get
verified: manifest deps, lockfiles, tsconfig/project references, CI
job-matrices and hardcoded package-name loops, container/compose/helm wiring,
string-path and dynamic loaders, `__init__`/index re-exports, and `conftest`/test
fixtures. Do not skip — this is the difference between a clean strip and a red CI.

## 4. Classify and order

Produce the plan in **[templates/prune-plan.md](templates/prune-plan.md)**. For
each candidate record: verdict (STRIP / KEEP / KEEP-because-coupled), the evidence,
and every co-file that must change with it (manifests, CI, lockfile, infra).

**Strip order — leaves first.** Strip packages that nothing kept depends on
before packages that a kept package consumes. If a kept package depends on a
candidate, that candidate is **not** a leaf: either keep it, or de-wire the
dependency first (then it becomes strippable in a later step).

## 5. Strip — one target per branch/PR (package OR file)

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
5. Run the full gate sequence (G1-G7 in SKILL.md).
6. Commit only when gates pass green.

For a **file/module** target inside a kept package: delete the one file → G1.5
static gate → G6 tests → commit/revert (manifest/install/infra gates usually
don't apply). After **each** accepted removal, re-run the analyzer — a removed
leaf can orphan its dependency. Repeat **to fixpoint** (analyzer reports no new
orphans). Log each removal in the plan's file-level removal log.

## 6. Final parity gate

After all targets are stripped, run the full baseline commands again. Pass
condition: the same tests pass as in step 0, minus the tests that lived inside
stripped packages. Same build, app still boots.
