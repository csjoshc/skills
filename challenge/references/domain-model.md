# Domain Model Reference

## Contents

- Purpose
- File structure
- During the session
- ADR criteria

---

## Purpose

Load during Phase 2 when the conversation involves: naming domain concepts,
resolving terminology conflicts, deciding whether to write an ADR, or
anchoring architectural decisions to existing glossary definitions.

This is the active discipline: challenge terms, invent edge-case scenarios,
and write the glossary and decisions down the moment they settle.
Ask questions in rounds per `~/.skills/shared/GRILLING.md`.
Merely reading `GLOSSARY.md` for vocabulary is a habit any phase can have; load this file when you're changing the model.

Adapted from Matt Pocock's `domain-modeling` skill (MIT).

---

## File structure

Most repos have a single context:

```
/
├── GLOSSARY.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `GLOSSARY-MAP.md` exists at the root, the repo has multiple contexts.
The map points to where each one lives:

```
/
├── GLOSSARY-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── GLOSSARY.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── GLOSSARY.md
│       └── docs/adr/
```

Create files lazily, only when you have something to write.
If no `GLOSSARY.md` exists, proceed without flagging its absence and create one when the first term is resolved.
If no `docs/adr/` exists, create it when the first ADR is needed.

---

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with `GLOSSARY.md`, call it out in the current round:
"Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"
Conflicting terminology gets resolved before you proceed.

### Sharpen fuzzy language

When the user uses a vague or overloaded term, propose a precise canonical term:
"You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships come up, stress-test them with specific scenarios.
Invent scenarios that probe edge cases and force precision about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees.
Surface contradictions:
"Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update GLOSSARY.md inline

When a term is resolved, update `GLOSSARY.md` right then, not batched at session end.
Use the format in [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md).

`GLOSSARY.md` holds domain language only.
Implementation details, specs and scratch notes go in the PRD, tickets or ADRs.

Ambiguities unresolvable in-session: flag with `[?]` and record as
Unresolved in the Convergence Ledger.

---

## ADR criteria

Offer an ADR only when all three hold:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR.
Use the format in [ADR-FORMAT.md](ADR-FORMAT.md).

When a user rejects an architecture candidate with a load-bearing reason
("we tried X and it failed because Y"), offer: "Want me to record this so
future reviewers don't re-suggest it?"
Offer only when the reason would guide future exploration, not for ephemeral reasons like "not worth it right now".
