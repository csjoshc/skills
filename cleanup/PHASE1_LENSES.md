# Phase 1 — Parallel Specialist Lenses

## Contents

- Lens table (focus, rubric codes, arch-violations files)
- Lens execution
- Checklist threshold
- Deduplication and ordering
- When to skip parallel execution

After Phase 0 clears its gate, Phase 1 runs **4 lenses in parallel**,
each scoped to a domain of architectural concern. Each lens has a narrow
focus, an N-of-M checklist threshold, and loads only the rubric codes
and `arch-violations/` files it owns.

| Lens | Focus | Owns rubric codes | Owns arch-violations |
| --- | --- | --- | --- |
| **Layer & Dependency** | Upward/sideways imports, cycles, leaking implementation types, boundary contracts | M-pattern layer violations; Tier A (architectural) | [01-dependency-direction](../reviews/arch-violations/01-dependency-direction.md), [02-boundary-contracts](../reviews/arch-violations/02-boundary-contracts.md) |
| **Redundancy & Modularity** | Duplicate cross-cutting concerns, parallel implementations, god modules, speculative generality | Tier A (modularity), AI anti-patterns | [08-modularity](../reviews/arch-violations/08-modularity.md), [11-ai-specific](../reviews/arch-violations/11-ai-specific.md) |
| **Error Handling & State** | Swallowed errors, over-broad catches, shared mutable state, race conditions, transactional boundaries | M1, M2, M5, M7; Tier G | [03-state-concurrency](../reviews/arch-violations/03-state-concurrency.md), [04-error-handling](../reviews/arch-violations/04-error-handling.md) |
| **Data & Security** | Unbounded queries, N+1, missing timeouts, auth scattering, trust-boundary confusion | M3, M4; Tier B | [05-data-layer](../reviews/arch-violations/05-data-layer.md), [06-security](../reviews/arch-violations/06-security.md) |

### Lens execution

Launch each lens as a sub-agent in parallel (one message, multiple
`Agent` tool calls). Each lens receives:

- The files in scope (Phase 0 may have narrowed the set).
- Its owning rubric codes from [`~/.skills/shared/QUALITY_RUBRIC.md`](~/.skills/shared/QUALITY_RUBRIC.md).
- Its owning `arch-violations/` files.
- The Phase 0 table (tool-flagged rows may be promoted into lens findings).

Each lens emits its own `REVIEW-FINDINGS` block. A lens can also emit
zero findings — legitimate when the scope doesn't contain anything
relevant.

### Checklist threshold

Each lens adopts the N-of-M pattern from `pr-review/reference/review-lenses.md`:

| Lens | Threshold |
| --- | --- |
| Layer & Dependency | 4 of 4 YES |
| Redundancy & Modularity | 3 of 4 YES |
| Error Handling & State | 3 of 4 YES |
| Data & Security | 4 of 5 YES (add severity-escalation criterion) |

A finding that does not meet threshold is dropped, not downgraded.

### Deduplication and ordering

After all lenses emit, merge and sort before the ledger:

1. Drop duplicates (same file + line + rule_code).
2. If a rubric-derived finding overlaps an arch-violation finding, prefer
   the arch-violation (stronger architectural signal).
3. Sort by category: Layer → Architectural Drift → Error Handling → Bug
   → Redundancy → Modularity → Standards → Test Gap.

### When to skip parallel execution

For a scope of ≤ 3 files, running 4 lenses is overhead without benefit.
Fall back to a single-lens pass using whichever lens most closely matches
the scope.
