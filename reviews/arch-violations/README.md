# Architectural violations catalog

Shared index for `pr-review` and `cleanup`. Each row points at a file with
the full shape, proof recipes, and few-shot examples for a cluster of
violations. All 11 files are built; regenerate any one by pasting
[`_prompt.md`](_prompt.md) plus the relevant section of the catalog into
a fresh session.

## How to use

- **pr-review** loads relevant file(s) when a lens needs arch-violation
  context (especially the Architectural-Drift lens).
- **cleanup** loads file(s) by lens: each of the 4 cleanup lenses owns 2–3
  violation files (see the *Owning lens* column).
- Every file follows [`TEMPLATE.md`](TEMPLATE.md). The validator enforces
  shape consistency on the `REVIEW-FINDINGS` few-shot inside each file.

## Index

| # | File | Decidable at | REVIEW-FINDINGS category | Severity range | Owning lens (cleanup) | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | [dependency-direction](01-dependency-direction.md) | both | Layer, Architectural Drift | MEDIUM–HIGH | Layer & Dependency | built |
| 02 | [boundary-contracts](02-boundary-contracts.md) | design | Architectural Drift, Standards | MEDIUM–HIGH | Layer & Dependency | built |
| 03 | [state-concurrency](03-state-concurrency.md) | diff | Bug, Error Handling | HIGH–CRITICAL | Error Handling & State | built |
| 04 | [error-handling](04-error-handling.md) | diff | Error Handling | MEDIUM–HIGH | Error Handling & State | built |
| 05 | [data-layer](05-data-layer.md) | both | Bug, Standards | MEDIUM–HIGH | Data & Security | built |
| 06 | [security](06-security.md) | both | Bug, Architectural Drift | HIGH–CRITICAL | Data & Security | built |
| 07 | [observability](07-observability.md) | design | Architectural Drift | LOW–MEDIUM | (shared) | built |
| 08 | [modularity](08-modularity.md) | diff | Modularity, Redundancy | LOW–MEDIUM | Redundancy & Modularity | built |
| 09 | [evolution](09-evolution.md) | design | Architectural Drift | MEDIUM–HIGH | (shared) | built |
| 10 | [testing-as-design](10-testing-as-design.md) | diff | Test Gap | MEDIUM | (shared) | built |
| 11 | [ai-specific](11-ai-specific.md) | diff | Redundancy, Modularity | LOW–MEDIUM | Redundancy & Modularity | built |

## Decidable-at legend

- **design** — `/antiplan` Phase 2 should catch this before code exists. If
  `pr-review` finds one with `plan_present: true`, emit as
  `category: Architectural Drift` with `decidable_at: design`.
- **diff** — Only visible once code exists. Regular lens finding.
- **both** — `/antiplan` sets the policy; `pr-review`/`cleanup` enforces it
  against the diff/codebase.

## Cross-reference

For the mapping between these codes and the AP/M/P5 taxonomies, see
[`../cross-reference.md`](../cross-reference.md).

## Generator

To add a new entry or regenerate an existing file, paste
[`_prompt.md`](_prompt.md) plus the relevant section of the 11-point
violation catalog into a fresh session.
