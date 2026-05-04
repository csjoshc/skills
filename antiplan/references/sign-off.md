# Human Sign-off Protocol

Loaded between Phase 2 and Phase 3. Five (or six for brownfield) artifacts
must be explicitly approved before ticket generation begins.

---

## The Approval Artifacts

Present each as a summary and ask for `/approve` or objections. No tickets
are generated until all are signed.

1. **Approved problem statement** — from Phase 1 Why/Who questions
2. **Approved thin vertical slice (MTP)** — the minimum testable product
3. **Approved cuts / non-goals** — what is explicitly NOT being built
4. **Approved architecture boundaries** — components, contracts, and layers
5. **Approved first integration gate scope** — what IG-1 will test
6. **Approved implementation topology** (brownfield only) — §8b MODIFY/CREATE
   map. Every ticket must have file-level scope before the user signs off.

---

## Sign-off Output Contract

Emit a fenced `SIGNOFF-APPROVALS:` block listing each artifact and its
approval state. See `~/.skills/shared/PRD_TEMPLATES.md` → Phase-Block Contracts for the
exact shape.

---

## Handling Objections

If the user objects to any artifact, return to the relevant Phase 1 or 2
interrogation. Do not negotiate wording — re-interrogate. Record the
unresolved artifact as `Contested` in the Convergence Ledger until resolved.

---

## Phase-Gate Audit Line

Before entering Phase 3, emit:

```
PHASE-GATE: Sign-off → Phase 3. Criteria: [all 5 (or 6) artifacts /approve: <met|not met — list missing>]. Proceeding: <yes|no>.
```

---

## Context Hygiene After Sign-Off

Once all artifacts are signed and the Phase-Gate audit line emits `Proceeding: yes`,
instruct the user to start a **fresh conversation** before Phase 3.

Carry forward ONLY these blocks (paste them into the new context):
- `BROWNFIELD-CONTEXT` / `GREENFIELD-CONTEXT` (Phase 0 output)
- `PROBLEM-STATEMENT` (Phase 1 output)
- `ARCHITECTURE-DECISIONS` (Phase 2 output)
- `SIGNOFF-APPROVALS` (this gate's output)

The interrogation Q&A lives in the session log (retrievable by session ID) —
it does not need to be re-loaded. Carrying the full transcript into Phase 3
re-introduces resolved debates and degrades DAG synthesis quality.
