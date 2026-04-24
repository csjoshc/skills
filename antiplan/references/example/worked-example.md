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

---

## Scenario: Brownfield Scan + User Correction

Demonstrates a Phase 0 `BROWNFIELD-CONTEXT` block produced by the agent,
followed by user correction of an inferred path — and how the ledger and
register update in response.

### Agent's initial Phase 0 output

````
```yaml
ledger:
  phase: 0
  resolved: 0
  contested: 0
  unresolved: 4
  cut: 0
  confidence: LOW
  reclassified: false
```

```BROWNFIELD-CONTEXT
constitution:
  - "no new runtime dependencies"
  - "existing test suite must stay green"
packages:
  | Package     | Directory (ls-verified) | Import name   | Key modules           |
  | ---         | ---                     | ---           | ---                   |
  | api         | api/                    | api           | routes/, handlers/    |
  | data-layer  | src/data/               | data_layer    | repositories/, orm/   |
  | web-client  | web/                    | web           | pages/, components/   |
conventions:
  - repositories extend BaseRepo
  - routes declared in api/routes/__init__.py
must_not_break:
  - /users/me endpoint (consumed by mobile client)
  - existing auth middleware
architecture_interpretation: |
  3-tier: api → data-layer → Postgres. web-client is SPA hitting api/*.
  auth middleware wraps every route except /health.
topology_preview:
  - feature: user-preferences
    files_to_modify: [api/routes/users.py, src/data/repositories/user_repo.py]
    files_to_create: [web/pages/preferences.tsx]
```

PHASE-GATE: Phase 0 → 1. Criteria: [constitution declared: met; research
artifact written: met; ls-verified paths: met]. Proceeding: yes.
````

### User correction

> The `data_layer` import name is wrong — it's actually `app.data`. And
> `BaseRepo` doesn't exist; we use a `Repository` protocol defined in
> `src/data/protocols.py`. Fix both before we move on.

### Agent's corrected response

````
Correction acknowledged. Updating research artifact and register.

```yaml
ledger:
  phase: 0
  resolved: 0
  contested: 0
  unresolved: 4
  cut: 0
  confidence: LOW
  reclassified: false
```

Assumption Register updates:
| ID  | Statement                                    | Source (was → now)            | Action |
| A-7 | Import name for data-layer is `data_layer`   | Inferred → Rejected           | Corrected to `app.data` (User-stated) |
| A-8 | Repositories extend a `BaseRepo` base class  | Inferred → Rejected           | Corrected to `Repository` protocol in src/data/protocols.py (User-stated) |

`BROWNFIELD-CONTEXT` patched:
  packages: data-layer import name = `app.data`
  conventions: "repositories implement Repository protocol (src/data/protocols.py)"
````

### Why this scenario matters

- The `BROWNFIELD-CONTEXT` block made the agent's inferences visible and
  correctable *before* any Phase 1 feature was discussed.
- Both corrections flipped Inferred items to User-stated, not to Observed —
  the agent has not yet read the corrected files, only trusted the user.
  Observed tags require direct filesystem confirmation.
- The hard rule on `ls`-verified paths caught the `BaseRepo` fiction at
  convention level: the file existed, but the *pattern* the agent claimed
  was inside it did not. This is AP-9 (Greenfield Hallucination) applied
  to a single symbol, caught at Phase 0 rather than at IG-1.

---

## Scenario: Integration Gate Failure + Recovery

Demonstrates the gate failure protocol: IG-1 fails, the DAG is blocked, a
diagnostic ticket is created, and the architecture is revisited rather than
the implementation being re-patched.

### Setup

- DAG contains T-1 (orchestration: add `conversation_prefix`),
  T-2 (BFF: wire prefix), IG-1 (validates T-1 + T-2 end-to-end), and
  T-3, T-4 downstream of IG-1.
- T-1 and T-2 complete. IG-1 runs a Playwright test that sends 3 messages
  and asserts the server sees messages 1-2 in the context of message 3.

### Gate run output (abbreviated)

```
E2E assertion FAILED:
  expected orchestrator payload[messages] to have length 3
  actual length: 1
  recent prompt only contains the current user turn
```

### Agent response

````
IG-1 FAILED. Blocking downstream: T-3, T-4.

```yaml
ledger:
  phase: 3
  resolved: 14
  contested: 1
  unresolved: 0
  cut: 0
  confidence: MEDIUM
  reclassified: false
```

Diagnostic ticket D-1 created:
  scope: investigate why orchestrator receives only the latest message
  scope: do NOT patch — categorize first

Categorization (from D-1 investigation):
  - implementation bug?  NO  — BFF correctly forwards full history
  - environment issue?   NO  — staging + local repro identical
  - DESIGN FLAW?         YES — web-client only sends the latest user turn;
                         statefulness model was assumed server-side but the
                         client holds conversation state and drops it

Rule 5 invoked: 1 consecutive failure for architectural reason.
Assumption A-3 ("conversation state is server-side") is invalidated.

RETURNING TO PHASE 2: re-interrogate the statefulness boundary.
  - Who owns conversation state: client, server, or both?
  - If client-owned: the DAG needs a new ticket to serialize history into
    every request body, and T-1's prefix injection is redundant.
  - If server-owned: web-client must be changed to send conversation_id
    only, and a server-side store ticket must be added.

Register update:
| A-3  | state is server-side | Inferred → Rejected | blocks rest of DAG until resolved |

PHASE-GATE: Phase 3 → Phase 2. Criteria: [IG-1 passing: not met —
architectural reason]. Proceeding: no.

RECLASSIFY: Standard → Heavy. Reason: architectural failure at statefulness
boundary + 1 Contested item that will expand scope.
````

### Why this scenario matters

- The agent did not attempt a retry before categorization. Rule 5's
  "architectural reason → revisit Phase 2" prevents a patch-and-retry
  loop that would compound cost without resolving the real issue.
- The failure routing used the ticket's `origin:` tag. Because
  `conversation_prefix` was tagged `origin: phase-2`, the re-interrogation
  went back to the phase that produced the assumption, not the phase that
  produced the implementation.
- Reclassification (Standard → Heavy) is a first-class output. The
  subsequent subagent round will include the Implementability Reviewer
  and User Advocate per `subagent-prompts.md`.
- The Assumption Register's `Rejected` state is not a silent drop — it
  blocks the DAG until the replacement assumption is User-stated and
  dependent tickets are revised.
