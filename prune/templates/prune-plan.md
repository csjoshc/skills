# Prune Plan — <repo name>

## Contents

- Context
- 0. Baseline
- 1. Workspace inventory
- 2. Reference & coupling matrix
- 3. Strip order (leaves first)
- 4. Per-target co-changes
- 5. Gate results per target (package-level)
- 5b. File-level removal log
- 6. Final parity gate
- 7. CI ratchet


> Fill one of these per prune invocation. Save to `.prune/prune-plan.md` in the
> target repo. It is the auditable record of what was stripped and why.

## Context

- Repo: `<path>`
- Derived from base: `<template/base repo + version, or "unknown">`
- Live app(s): `<app dir(s) that define the real dependency set>`
- Stacks: `<uv | pnpm | cargo | ...>`
- Date: `<YYYY-MM-DD>`

## 0. Baseline

| Check | Command | Result | Artifact |
|---|---|---|---|
| Tests | `<...>` | <pass N / fail M> | `.prune/baseline-tests.txt` |
| Build | `<...>` | <pass/fail> | `.prune/baseline-build.txt` |
| App boot | `<...>` | <pass/fail> | — |

Baseline green? `<yes/no>` — if no, do not proceed until resolved/recorded.

## 1. Workspace inventory

| Package | Dir | Import name | Manifest name | Declared how | Member? |
|---|---|---|---|---|---|
| | | | | explicit/glob | yes/no |

Dirs present but NOT workspace members: `<...>`

## 2. Reference & coupling matrix

Run `../references/coupling-checklist.md` per
candidate. One row per candidate.

| Package | App imports (app/test) | Manifest dep of kept? | tsconfig ref | CI refs | Container/helm | String-path/dynamic | Re-export | Verdict |
|---|---|---|---|---|---|---|---|---|
| `<name>` | 0/0 | no | no | none | none | none | **STRIP** |
| `<name>` | 0/0 | **yes (cli)** | — | — | — | — | **KEEP-coupled** |
| `<name>` | 9/3 | — | — | — | — | — | **KEEP** |

Verdict legend: STRIP (delete) · STRIP (extract-to-base) · KEEP · KEEP-because-coupled.

## 3. Strip order (leaves first)

1. `<leaf candidate>` — nothing kept depends on it.
2. `<leaf candidate>`
3. `<coupled candidate>` — only after de-wiring `<kept pkg>`'s dependency.

## 4. Per-target co-changes

For each STRIP target, every file that must change in the same commit:

### `<target>`
- [ ] Remove from `<workspace manifest>`
- [ ] Delete dir `<path>`
- [ ] Remove tsconfig reference(s): `<file:line>`
- [ ] Remove CI job(s) / path filter(s) / needs / matrix / `for pkg in` loop: `<file:line>`
- [ ] Remove compose service / depends_on / env URL: `<file>`
- [ ] Remove helm subchart + Chart.yaml dependency + values flag: `<path>`
- [ ] Remove Dockerfile COPY: `<file>`
- [ ] Regenerate lockfile: `<uv lock | pnpm install | ...>`
- [ ] Scrub docs/diagrams/.env mentions
- [ ] Extract-to-base (if applicable): PR to `<base repo>` first

## 5. Gate results per target (package-level)

| Target | G1 | G1.5 static | G2 | G3 install | G4 build | G5 boot | G6 test | G7 infra | PR |
|---|---|---|---|---|---|---|---|---|---|
| `<name>` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | #__ |

## 5b. File-level removal log

Dead files/modules removed from KEEP packages, via the delete-and-prove loop,
iterated to fixpoint. Confidence tier: High (statically-proven-unreachable) /
Medium (no-grep-hits only) / Low (dynamic-load — needs runtime evidence).
See `../references/static-analysis.md`.

| Round | Target file | Confidence tier | G1.5 static result | G6 test result | Commit / revert |
|---|---|---|---|---|---|
| 1 | `<path>` | High | clean | green | commit `<sha>` |
| 1 | `<path>` | Low | clean | green | **revert** (dynamic-load, kept) |
| 2 | `<orphaned-by-round-1>` | High | clean | green | commit `<sha>` |

Fixpoint reached (analyzer reports no new orphans)? `<yes/no>`

## 6. Final parity gate

| Check | Baseline | Post-prune | Delta explained? |
|---|---|---|---|
| Tests pass | N | N − (stripped-pkg tests) | yes |
| Build | pass | pass | — |
| App boot | pass | pass | — |

## 7. CI ratchet

- [ ] Dead-code analyzer wired as a required CI check so dead code cannot regrow
      (`knip` / `vulture` + `deptry` / `cargo machete` — pick per stack), with the
      dynamic-load whitelist seeded. See
      `../references/static-analysis.md`.
