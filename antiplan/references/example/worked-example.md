# Worked Example: Canonical Antiplan Output

This is the complete set of artifacts antiplan produces for a representative
brownfield feature: adding threaded comments with reply notifications to
a fictional multi-package application called **TaskBoard**. The example
uses a neutral fictional domain so it transfers to any project — substitute
your own package names, paths, and signatures when you reuse it.

The example demonstrates how antiplan converts a cross-layer feature into
8 feature tickets + 3 integration gates with zero new packages, and hands
off to `spec-writer` via a formal Ticket Contract that `ticket-critic`
validates before any ticket transitions to `Stage: BUILD`.

## Which artifact does antiplan produce?

Antiplan's output boundary is three files:

| File | Purpose |
| --- | --- |
| [brownfield-context.md](brownfield-context.md) | Phase 0 research artifact — agent's written understanding of the existing codebase, reviewed and corrected by the user |
| [prd.md](prd.md) | Convergence-verified PRD — §1 problem statement through §17 Implementation Readiness Checklist, including §8b Implementation Topology |
| [ticket-dag.md](ticket-dag.md) | Phase 3 output — ordered DAG, per-ticket stubs (YAML frontmatter + 1-paragraph scope + 2-3 invariant ACs), and the Ticket Contract every fleshed ticket must satisfy |

[ticket-pack.md](ticket-pack.md) is **downstream** — it is what `spec-writer`
produces when it expands each stub using the Ticket Contract. It is
included here as the quality bar `ticket-critic` validates against, and
as a few-shot reference for `spec-writer`'s output shape.

## Contents

- [brownfield-context.md](brownfield-context.md) — codebase state at
  planning time, existing packages, conventions, key function signatures
  (the agent's interpretation of the architecture, written to file and
  reviewed by the user before Phase 1 began)
- [prd.md](prd.md) — PRD §1-§17 including the §8b Implementation Topology
  table that anchors every ticket to concrete file paths
- [ticket-dag.md](ticket-dag.md) — Phase 3 DAG + ticket stubs + **Ticket
  Contract** (the formal schema that bridges antiplan → spec-writer → ticket-critic)
- [ticket-pack.md](ticket-pack.md) — spec-writer's downstream output:
  fleshed ticket bodies T-1 through T-7 + T-4a + IG-1/IG-2/IG-3, each
  satisfying every Ticket Contract hard gate

## How to Read This Example

1. **Start with brownfield-context.md** — this is what Phase 0 produces.
   It is the research artifact: the agent's written understanding of the
   existing codebase, reviewed and corrected by the user. Without it, an
   implementing agent cannot distinguish MODIFY from CREATE.
2. **Read the PRD** — note §8b (Implementation Topology) which maps every
   ticket to concrete file paths and MODIFY/CREATE actions. Note the DAG
   in §12 includes execution modes (autopilot/confirm/validate) per ticket.
3. **Read ticket-dag.md** — this is antiplan's Phase 3 output. Note that
   tickets are stubs, not fleshed bodies. Note §3 "Ticket Contract" — it
   defines exactly what `spec-writer` must produce for every ticket. This
   is the skill boundary: antiplan stops here.
4. **Read ticket-pack.md** — this is downstream. Each ticket body
   demonstrates Ticket Contract compliance: Read-First ≥2 files,
   Exemplar-Files ≥1, ≥3 grep-verifiable ACs, ≥1 failure-path AC with
   user-visible assertion, Verify command, Technical Notes, Failure
   Protocol. Integration gates additionally show Silent Failure
   Detection, Dev Agent Record, and Proof Artifacts.

## Key Design Principle

The worked example demonstrates a **brownfield modification** — all 8
tickets modify existing packages. Zero new packages or directories are
created. This is the common case for feature work in mature codebases
and the case that agents most frequently get wrong (see AP-9: Greenfield
Hallucination).

## Structural Features to Note

- Every ticket has **Read First** and **Exemplar Files** pointing the
  implementing agent at existing code (AP-13 prevention)
- Every AC has a grep/pytest/curl-testable command (AP-10 prevention)
- Every ticket has at least one failure-path AC with user-visible assertion
- Integration gates include **Silent Failure Detection** criteria, a
  **Dev Agent Record** template, and **Proof Artifacts** requirements
- Ticket scope is bounded to ≤5 production files per ticket (AP-12 prevention)
- The DAG passes the **Requirements Coverage Gate** — every PRD §5
  feature and acceptance criterion maps to at least one ticket
- The Ticket Contract in ticket-dag.md §3 promotes these demonstrations
  into contractual requirements that ticket-critic enforces at gate time
