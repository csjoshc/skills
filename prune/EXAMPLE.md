# Worked Example — starter-derived monorepo

A real audit of a `starter`-derived repo (uv + pnpm monorepo, one live app under
`apps/patent-search/`). Shows the numbers a clean scan produced **and the
corrections the naive "zero-import → strip" approach missed**.

## Setup

- Python workspace (uv): `core`, `adapters/*`, `guardrails`, `hitl`, `eval`,
  `rag`, plus `apps/*/backend`. `templates/` present but **not** a member
  (cookiecutter fixtures, pytest-ignored).
- TS workspace (pnpm): `cli`, `eval-dashboard`, `mcp-data-server`, `docs-gen`,
  `ui`, plus `apps/*` + `apps/*/frontend`.
- Prior hand-audit had flagged six "0-reference" strip candidates:
  `docs-gen, eval, eval-dashboard, hitl, mcp-data-server, templates`.

## Direct-reference scan (app tree only)

| Module | Pkg | App imports | Where |
|---|---|---|---|
| `agent_core` | core | 9 (incl. 3 tests) | characterizer, llm_env, service, retry, scripted_provider, routes |
| `@acme/ui` | ui | 10 | routes/*, components/*, styles |
| `agent_rag` | rag | 2 (incl. 1 test) | chunk_stage |
| `agent_checks` | guardrails | 2 | service, characterizer |
| `agent_adapters_genai` | adapters/genai | 1 | service |
| `agent_adapters_langchain` | adapters/langchain | **0** | — |
| `agent_adapters_claude` | adapters/claude | **0** | — |
| `agent_hitl` | hitl | **0** | — |
| `agent_eval` | eval | **0** | — |
| `@acme/toolkit-cli` | cli | **0** | — |
| `@acme/mcp-data-server` | mcp-data-server | **0** | — |
| `@acme/docs-gen` | docs-gen | **0** | — |
| `@acme/eval-dashboard` | eval-dashboard | **0** | — |

Ground truth = the app's own Dockerfiles: backend COPYs exactly
`core, rag, guardrails, adapters/genai`; frontend COPYs `ui`. That five-package
set is the real app dependency — everything else is a candidate.

## What the coupling scan corrected

**1. `cli` is zero-import but NOT strippable as a leaf.** `packages/cli/package.json`
declares `"@acme/docs-gen": "workspace:*"`. So:
- `docs-gen` is a **declared dependency of a kept-ish package** (rule 3) — deleting
  it breaks `pnpm install --frozen-lockfile` and the cli build, despite 0 app imports.
- Either keep `docs-gen`, or de-wire cli's dependency first, or strip cli too.

**2. `templates` is loaded by string path, not import.** `cli/src/commands/new.ts`
and `scripts/new-project.mjs` resolve `templates/` and `packages/templates/` by
**path string** (rule 5). An import grep returns zero; the coupling is real. The
templates dir is only strippable after de-wiring those scaffolding commands.

**3. Two more genuine leaves the hand-audit missed.** `adapters/langchain` and
`adapters/claude` have 0 app imports and are absent from the backend manifest —
valid strip candidates the original six-item list omitted.

**4. CI hardcodes package names in five places per package.** `ci.yml` had: a
per-package `test-<name>` job, `paths:` filters, a `needs:` list, a `JOB_MAP`,
**and** a `for pkg in cli docs-gen eval-dashboard ... ` coverage-summary loop.
Miss any one and a required job dangles, blocking every merge.

**5. `mcp-data-server` is wired into three infra layers.** A `docker-compose.yaml`
service (with `depends_on` + `MCP_SERVER_URL` env), a `containers/mcp-data-server/
Dockerfile`, and a `helm/base-app` **subchart** (Chart.yaml dependency +
`mcp-data-server.enabled` condition + full `charts/` tree). Deleting only the
package dir leaves `helm dep build` and compose broken.

**6. Root dirs were genuinely uncoupled.** `plugin_marketplace/`, `helm/`,
`containers/` had zero references from the app (which ships via the compose
`patent` profile using its own Dockerfiles). Safe to strip from this pilot.

## Resulting classification

| Package | Verdict | Reason |
|---|---|---|
| core, ui, rag, guardrails, adapters/genai | KEEP | direct app deps (Dockerfile-confirmed) |
| eval, hitl | STRIP (extract-to-base) | 0 refs; generic, valuable to other pilots |
| eval-dashboard, mcp-data-server | STRIP (delete) | 0 refs, pure leaves |
| adapters/langchain, adapters/claude | STRIP (delete) | 0 refs, not in manifest |
| docs-gen | KEEP-because-coupled | cli `workspace:*` dep — or de-wire cli first |
| templates | KEEP-because-coupled | cli/new-project string-path loader — de-wire first |

## Strip order that fell out

1. **Leaves:** eval-dashboard, mcp-data-server, hitl, eval, adapters/langchain,
   adapters/claude. Each also removes its CI job, and mcp-data-server removes its
   compose service + container Dockerfile + helm subchart.
2. **docs-gen:** only after removing `@acme/docs-gen` from cli's package.json and
   re-locking (or stripping cli).
3. **templates:** only after de-wiring cli `new`/`validate` + `new-project.mjs`.

## Lesson

The hand-audit's six-item "zero-reference" list was **two-thirds right**: it
correctly caught the four true leaves but (a) missed two more leaves, (b)
wrongly listed `docs-gen` as a clean strip when a kept package depends on it, and
(c) wrongly listed `templates` as clean when a kept CLI loads it by path. The
coupling checklist (rules 2–5) is exactly what converts a plausible list into a
safe, ordered one.
