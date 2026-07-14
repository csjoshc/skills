# Coupling Checklist

## Contents

- How to use
- 1. Workspace manifest coupling
- 2. Lockfile coupling
- 3. Transitive / declared dependency coupling
- 4. Build-graph coupling (tsconfig, project refs)
- 5. CI / CD coupling
- 6. Container / orchestration coupling
- 7. Runtime string-path & dynamic-load coupling
- 8. Re-export & namespace coupling
- 9. Test-harness coupling
- 10. Non-code / docs / diagram coupling
- Edge-case catalogue (things that defeat naive grep)

## How to use

For each strip **candidate**, run every section that applies to the repo's
stack. A candidate is only safe to strip when **all** sections come back clean
or their hits are resolved (removed/updated/re-classified). Record each result
in the prune plan. Substitute `NAME` = the package's import name **and** its
directory name **and** its published/manifest name — they can differ, and a hit
under any alias counts.

These checks exist because **zero direct import references is not sufficient**.
Every section below is a way a package stays load-bearing despite no `import`.

## 1. Workspace manifest coupling

The package may be a declared workspace member or a member's dependency.

```bash
# Python (uv/hatch)
git grep -nE "\b${NAME}\b" -- pyproject.toml '**/pyproject.toml'
# JS/TS
git grep -nE "\b${NAME}\b" -- package.json '**/package.json' pnpm-workspace.yaml
# Rust
git grep -nE "\b${NAME}\b" -- Cargo.toml '**/Cargo.toml'
```

Check both `[tool.uv.workspace].members` / `workspaces` / `[workspace].members`
**and** `[tool.uv.sources]` / `dependencies` / `[dependencies]`. A package listed
as a *source* or *dependency* of a kept package is load-bearing (rule 3).

## 2. Lockfile coupling

Deleting a member without regenerating the lockfile breaks `--frozen-lockfile`
installs in CI even when nothing imports it.

- After deletion, **always** regenerate: `uv lock`, `pnpm install`, `cargo update`.
- Commit the regenerated lockfile in the **same** commit as the deletion.
- Never hand-edit a lockfile.

## 3. Transitive / declared dependency coupling

For each **kept** package, read its manifest dependencies and check whether it
lists any strip candidate. This is the single most common false-positive: a kept
CLI/tool depending on a "0-app-reference" helper package.

```bash
# for each kept package manifest, list its deps and intersect with candidates
```

If a kept package depends on a candidate → the candidate is **not a leaf**.
Either KEEP it, or remove the dependency from the kept package first (and
re-lock), which demotes it to strippable in a later step.

## 4. Build-graph coupling (tsconfig, project refs)

Composite/project-reference builds break if a referenced dir is deleted but the
reference remains.

```bash
git grep -nE "\b${NAME}\b" -- tsconfig.json '**/tsconfig*.json'
```

Remove the `references[]` entry and any path alias in `compilerOptions.paths`.
Analogues in other stacks: `go.work` `use` directives, `.csproj`
`<ProjectReference>`, gradle `include`.

## 5. CI / CD coupling

CI configs frequently hardcode package names in **multiple** places that all
must be edited together. Missing one leaves a dangling required job that blocks
every merge.

```bash
git grep -nE "\b${NAME}\b" -- '.github/workflows/' '.gitlab-ci.yml' '.circleci/' 'ci/'
```

Check for **all** of:

- Dedicated per-package jobs (`test-<name>`, `build-<name>`).
- `paths:` / path-filter triggers scoped to the package dir.
- `needs:` lists that reference the job.
- Job-map / matrix entries (`JOB_MAP`, `strategy.matrix`).
- **Hardcoded shell loops** — `for pkg in a b c <name> ...` in a coverage or
  publish step. These are easy to miss with a structural read; grep the literal.
- Required-check / branch-protection names (may live in repo settings, not files
  — flag for the human if a job name is a required status check).

## 6. Container / orchestration coupling

```bash
git grep -nE "\b${NAME}\b" -- 'Dockerfile*' '**/Dockerfile*' 'docker-compose*' \
  'helm/' 'k8s/' 'manifests/' 'kustomize/'
```

- **Dockerfile `COPY`**: the app's own Dockerfile COPY list is ground truth for
  what it needs; a candidate appearing there is load-bearing for the image.
- **compose services**: a candidate may be a service with `depends_on`, a
  `build:` context, or referenced via an env var (`X_SERVER_URL`). Remove the
  service and every reference to it.
- **helm**: a candidate may be a **subchart** with a `Chart.yaml` dependency, a
  `condition: <name>.enabled` flag, and a `charts/<name>/` tree. Deleting the
  dir without removing the dependency breaks `helm dep build`. Also check the
  parent `values.yaml`.

## 7. Runtime string-path & dynamic-load coupling

The killer that import-grep cannot see: code that loads the package by a **path
string** or **dynamic import**, not a static import.

```bash
# path-string references to the dir (e.g. a CLI that scaffolds from templates/)
git grep -nE "['\"][^'\"]*${NAME}[^'\"]*['\"]"
# dynamic loaders
git grep -nE "importlib|__import__|import_module|require\(|System\.|Class\.forName"
```

Inspect each hit: does it resolve the candidate by name/path at runtime? Plugin
registries, scaffolding commands that read a `templates/` directory, config keys
that name a provider/adapter, and `entry_points` all hide here. A candidate
reachable this way is load-bearing even with zero static imports.

## 8. Re-export & namespace coupling

A kept package's `__init__.py` / `index.ts` barrel may re-export from a
candidate, making it an indirect public dependency.

```bash
git grep -nE "\b${NAME}\b" -- '**/__init__.py' '**/index.ts' '**/index.js' '**/mod.rs'
```

Also watch for **namespace packages** (PEP 420 / shared top-level package) where
two dirs contribute to one import namespace — deleting one can break the import
of the other.

## 9. Test-harness coupling

```bash
git grep -nE "\b${NAME}\b" -- 'conftest.py' '**/conftest.py' 'tests/' 'test/' '__tests__/'
```

- `conftest.py` may import a candidate to build shared fixtures — deleting it
  breaks unrelated test collection.
- **Separate app references from test-only references**: a module imported only
  by its own test is *not* load-bearing for the app (its tests leave with it).
  A module imported by a *kept* package's tests is coupling.
- A self-referential extra (`pkg[extra]` pointing at itself) is **not** external
  coupling — don't misread it.

## 10. Non-code / docs / diagram coupling

Deletions classically leave doc/diagram debris. (The `deprecate` skill's Step 3b
scrub covers this in full — reuse it.)

```bash
git grep -nE "\b${NAME}\b" -- '*.md' '*.rst' '*.txt' '*.mmd' '*.puml' '.env*' 'config/'
```

Resolve each: remove if it described only the stripped thing; update if it points
at a survivor; escalate ambiguous architecture diagrams (old+new side-by-side) to
the human. Image-format diagrams (SVG/PNG) won't grep — eyeball `docs/` if present.

## Edge-case catalogue (things that defeat naive grep)

| Edge case | Why grep misses it | Check |
|---|---|---|
| Manifest dep, no import | no `import` statement exists | §1, §3 |
| Lockfile pin | not a source file | §2 |
| tsconfig project ref | structural, not an import | §4 |
| CI `for pkg in ...` loop | name is a loop literal | §5 |
| Required status check name | lives in repo settings | §5 (flag human) |
| helm subchart condition | YAML key, not code | §6 |
| compose `depends_on` / env URL | indirect service ref | §6 |
| String-path scaffolding (templates dir) | path string, not import | §7 |
| `importlib` / `require(var)` | dynamic, name may be computed | §7 |
| Barrel re-export | indirect public surface | §8 |
| PEP 420 namespace package | shared import namespace | §8 |
| `conftest.py` fixture import | test-collection-time coupling | §9 |
| Self extra `pkg[extra]` | looks like a dep, isn't external | §9 (ignore) |
| Test-only import | not app-load-bearing | §9 (separate counts) |
| Doc / diagram / `.env` mention | not executed | §10 |
