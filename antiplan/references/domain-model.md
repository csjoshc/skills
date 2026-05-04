# Domain Model Reference

## Contents

- Purpose
- CONTEXT.md structure
- Domain term extraction
- ADR criteria

---

## Purpose

Load during Phase 2 when the conversation involves: naming domain concepts,
resolving terminology conflicts, deciding whether to write an ADR, or
anchoring architectural decisions to existing glossary definitions.

Applies DDD-style discipline: one-at-a-time questions with recommended
answers, codebase-first validation, and glossary enforcement.

---

## CONTEXT.md structure

**Single-context repos:** one `CONTEXT.md` at the repo root.

**Multi-context repos:** `CONTEXT-MAP.md` at the root, pointing to
context-specific directories (e.g., `src/orders/CONTEXT.md`). Each
context directory holds its own `CONTEXT.md` and, optionally, `docs/adr/`.

When `CONTEXT.md` exists, treat it as the authoritative glossary. Any
user terminology that conflicts with a term in `CONTEXT.md` triggers an
immediate clarification question before proceeding. Do not let conflicting
terminology coexist silently.

When `CONTEXT.md` does not exist: proceed silently — don't flag its
absence. Create it lazily when the first domain term is resolved.

**Adding terms:** When a term is resolved during interrogation, add it to
`CONTEXT.md` immediately — not batched at session end. Include:

- **Term** (bold)
- One-sentence definition
- Aliases to avoid (if any)
- Relationship to adjacent terms (if non-obvious)

---

## Domain term extraction

When terminology is ambiguous or multiple words are used for the same
concept:

1. Identify all candidate terms from the conversation and codebase
2. Be opinionated: pick the best term, list the others as **aliases to avoid**
3. Group related terms by domain cluster (lifecycle, people, relationships)
4. For each term, capture: canonical name, definition, aliases, cardinality
5. Save resolved terms to `CONTEXT.md` immediately

**Table format for `CONTEXT.md` or `UBIQUITOUS_LANGUAGE.md`:**

| Term | Definition | Aliases to Avoid |
|------|-----------|-----------------|
| **Order** | A confirmed Customer request for one or more Items | Purchase, Cart, Basket |
| **Customer** | A registered user who has placed at least one Order | User, Buyer, Client |

Ambiguities unresolvable in-session: flag with `[?]` and record as
Unresolved in the Convergence Ledger.

---

## ADR criteria

Write an Architecture Decision Record **only when all three conditions hold:**

1. **Costly to reverse** — undoing requires significant rework
2. **Unintuitive without context** — a future engineer would reasonably
   choose differently without knowing why
3. **Genuine trade-off** — real alternatives existed and were considered

If any condition is absent, skip the ADR. Note the decision in `CONTEXT.md`
instead.

When a user rejects an architecture candidate with a load-bearing reason
("we tried X and it failed because Y"), offer: "Want me to record this so
future reviewers don't re-suggest it?" Only offer when the reason would
actually guide future exploration — skip ephemeral reasons like "not worth
it right now."

**ADR format (minimal):**

```markdown
## ADR-NN: [Decision title]
**Status:** Accepted
**Context:** Why this decision was needed
**Decision:** One sentence
**Alternatives considered:** What else was evaluated
**Consequences:** The tradeoffs accepted
```
