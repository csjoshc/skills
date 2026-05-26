# `.docs/` — Local Analysis of `<owner/repo>`

> **This folder is local-only.** `.docs/` is gitignored. Nothing here ships upstream — it's a reading guide for the snapshot of `<owner/repo>@<branch>` committed as `<initial-commit-sha>`.

The canonical reference for the upstream project (if any) lives outside this folder:

- <reference 1 — PDF path / Confluence URL / wiki>
- <reference 2>
- <reference 3>

This `.docs/` folder is the same kind of write-up, applied to **this** fork / divergent branch.

---

## How to read this

Start at the level of detail that matches your audience, then drop into a topic breakout when you need to go deeper:

| Read | Audience | Length | What you'll get |
|---|---|---|---|
| [L0 — Executive Summary](./L0-executive-summary.md) | Product, exec, programme owner | ~1 page | Identity, problem/constraint/solution, the divergent commits in plain prose, where to go next |
| [L1 — Technical Overview](./L1-technical-overview.md) | Architect, staff+ engineer, platform lead | ~5 pages | Component boundaries, novel pattern, request flow, reuse map, CI/CD, architectural risks. Mermaid diagrams. |
| [L2 — Deep Dive](./L2-deep-dive.md) | IC engineer doing implementation review | ~5–10 pages | File-by-file walkthrough of each divergent commit |

### Topic breakouts

Standalone, deep-on-one-thing pages:

| Topic | When to read |
|---|---|
| [`topics/<novel-pattern>.md`](./topics/<novel-pattern>.md) | <when this topic matters> |
| [`topics/<distinctive-feature>.md`](./topics/<distinctive-feature>.md) | <when this topic matters> |
| [`topics/<package-diff>.md`](./topics/<package-diff>.md) | <when this topic matters> |

### Diagrams (Mermaid)

Source `.mmd` files (rendered to `.svg`):

- [`l1-system-context`](./diagrams/l1-system-context.svg) — component boundaries
- [`l1-data-flow`](./diagrams/l1-data-flow.svg) — the novel pipeline / orchestration
- [`l1-request-flow`](./diagrams/l1-request-flow.svg) — sequence diagram of the primary use case

Re-render: `mmdc -i <file>.mmd -o <file>.svg -b transparent`

---

## The diff in one screen

| | Upstream | Fork |
|---|---|---|
| **Default branch HEAD** | `<base-sha>` (`<base-date>`) | `<head-sha>` (`<head-date>`) |
| **Identity** | <upstream identity> | <fork identity> |
| **`apps/`** | <base apps/> | <head apps/> |
| **`packages/`** | <base packages/> | <head packages/> |
| **`.github/workflows/`** | <base workflows> | <head workflows> |
| **Divergent commits** | — | `<sha>` #N (<title>, <files-changed> files), … |

---

## Plan for this folder

### Written

- ✅ `README.md` (this file) — index and reading guide
- ✅ `L0-executive-summary.md` — product/exec summary
- ✅ `L1-technical-overview.md` — architect-audience reframe (via `/reframe` contract)
- ✅ `L2-deep-dive.md` — engineer-audience file-by-file walkthrough
- ✅ `topics/*.md` — single-topic breakouts
- ✅ `diagrams/*.{mmd,svg}` — Mermaid sources + rendered SVGs

### Intentionally not written (lives elsewhere)

- <in-repo doc that already covers this topic>
- <upstream doc that's the canonical reference>

---

## Local repo posture

- This is a **silent local git repo**: `git remote -v` is empty, no upstream configured.
- The snapshot was committed as `<initial-commit-sha>` ("<initial-commit-msg>").
- `.docs/` is in `.gitignore` — running `git status` should show no untracked files in this folder.
