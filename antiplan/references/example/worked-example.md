# Worked Example: Canonical Antiplan Output

This is the complete set of artifacts that antiplan would have produced for
an enterprise chat agent project. It is reverse-engineered from a working
codebase that took 29+ tickets and 4 design documents to reach, but which
antiplan would have planned in 8 tickets with 3 integration gates.

Use this as the one-shot reference for what antiplan's output looks like.

## Contents

- [brownfield-context.md](brownfield-context.md) — codebase
  state at planning time, existing packages, conventions (Phase 0 research
  artifact — the agent's understanding of the codebase, written to file and
  reviewed by the user before Phase 1 began)
- [prd.md](prd.md) — PRD sections 1-17 including the new
  §8b Implementation Topology
- [tickets.md](tickets.md) — Ticket Pack: T-1 through T-7
  + T-4a + IG-1, IG-2, IG-3 (full ticket bodies with file-level scope,
  execution modes, and verify commands)

## How to Read This Example

1. **Start with brownfield-context.md** — this is what Phase 0 produces.
   It is the research artifact: the agent's written understanding of the
   existing codebase, reviewed and corrected by the user. Without it, an
   implementing agent cannot distinguish MODIFY from CREATE.
2. **Read the PRD** — note §8b (Implementation Topology) which maps every
   ticket to concrete file paths and MODIFY/CREATE actions. Note the DAG
   includes execution modes (autopilot/confirm/validate) per ticket.
3. **Read the tickets** — each ticket's Scope line references specific files
   and states whether they are modified or created. Each ticket includes a
   `Verify` section with an executable command. Each ticket has an execution
   mode that determines how much oversight the implementing agent receives.

## Key Design Principle

The worked example demonstrates a **brownfield modification** — all 8
tickets modify existing packages. Zero new packages or directories are
created. This is the common case for enterprise codebases and the case
that agents most frequently get wrong (see AP-9: Greenfield Hallucination).

## Structural Features to Note

- Every ticket has **Read First** and **Exemplar Files** sections pointing
  the implementing agent at existing code (AP-13 prevention)
- Every AC has a **Verify** line with a grep-testable command (AP-10 prevention)
- Every ticket has at least one failure-path AC with user-visible assertion
- Integration gates include **Silent Failure Detection** criteria and
  **Dev Agent Record** metadata
- Ticket scope is bounded to ≤5 production files per ticket (AP-12 prevention)
- The DAG passes the **Requirements Coverage Gate** — every PRD §5 feature
  and acceptance criterion maps to at least one ticket
