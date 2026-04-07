# Convergence Engine

Loaded during Phase 3 (Convergence Synthesis). Defines how the resolved
decisions from Phase 1-2 are transformed into a ticket dependency graph that
surfaces integration failures as early as possible.

---

## Core Principle: Negative Feedback Loop

The ticket graph is structured as a negative feedback loop: work is ordered so
that each step either **confirms** the design is converging toward the intended
system, or **reveals** that it isn't. Failures surface early, before more code
is built on top of a broken foundation.

This is the opposite of how LLM agents typically plan: they produce a flat list
of tickets optimized for parallel throughput, then discover integration
failures at the end when everything has already been built.

---

## Ordering Rules

### Rule 1: Vertical Before Horizontal

Build one complete vertical slice (UI → API → data → back) before expanding
horizontally. A "vertical slice" means a single user-visible flow that works
end-to-end on real infrastructure, not mocks.

**Bad ordering:**
```
T1: Build API layer for all 5 endpoints
T2: Build data layer for all 5 models
T3: Build UI for all 5 pages
T4: Integrate everything
```

**Good ordering:**
```
T1: Build endpoint A (API + data + UI) — vertical slice
IG-1: Integration gate — test flow A end-to-end
T2: Build endpoint B (API + data + UI)
T3: Build endpoint C (API + data + UI)
IG-2: Integration gate — test flows A + B + C together
T4: Build endpoints D + E
IG-3: Integration gate — test all flows
```

### Rule 2: Integration Gates Are First-Class

Integration gate tickets are NOT optional checkpoints. They are real tickets
with their own scope, acceptance criteria, and implementation work. They appear
in the dependency graph as hard blockers — downstream tickets cannot start
until the gate ticket reaches `Stage: COMPLETE`.

**Gate completion rules:**
- A gate may only be marked COMPLETE by a CI artifact (green status check) or
  a human toggle. Never by the implementing agent's self-report.
- Implementer != verifier: the agent/session that built the feature tickets
  should not be the one that certifies the gate passed. Use a separate session,
  the challenger subagent re-running on test output, or CI.

### Rule 3: Maximum 3 Feature Tickets Between Gates

No more than 3 feature/implementation tickets may exist between consecutive
integration gate tickets in any dependency chain. This is a hard limit.

If a dependency chain has 4+ feature tickets without a gate, insert one.
The planner subagent must enforce this during DAG construction.

### Rule 4: No Mocks in Gate Tickets

Integration gate tests run against real running services, real databases
(can be test instances), and real network calls. Mocks are forbidden in
gate tickets.

**Substitute tier (what counts as "real enough"):**

| Substitute | Acceptable? | Notes |
|-----------|-------------|-------|
| Testcontainers / local Docker | Yes | Real processes, real protocols |
| Recorded fixtures from real API/LLM calls | Yes (PARTIAL) | Must be from actual staging/prod calls. Mark gate PARTIAL. |
| Budgeted live LLM calls | Yes | Acceptable when cost-controlled |
| Pure in-memory doubles / fakes | **No** | Does not validate real I/O or protocol behavior |

If a real dependency is genuinely unavailable (e.g., a third-party API with
no sandbox), the gate ticket must:
1. Document why the real dependency is unavailable
2. Use the closest available substitute (local container, recorded responses)
3. Create a follow-up ticket for real integration when the dependency is
   available
4. Mark the gate as PARTIAL in the convergence ledger

### Rule 5: Gate Failure Blocks the Graph

When an integration gate fails:
1. All downstream tickets are BLOCKED
2. A diagnostic ticket is created to investigate the failure
3. The diagnostic ticket's resolution determines whether the failure is:
   - A bug in the implementation → fix ticket, re-run gate
   - A design flaw → escalate back to Phase 2 interrogation
   - An environmental issue → document and retry
4. The graph does NOT proceed until the gate passes

**Stability policy:**
- Maximum 2 retries per gate before the failure must be diagnosed
- Flaky tests: quarantine immediately. A quarantined test cannot count toward
  gate pass criteria until the flake is resolved with its own fix ticket.
- 2 consecutive gate failures for the **same architectural reason** → pause
  the graph entirely and return to Phase 2 re-interrogation. The architecture
  assumption that caused the failure is invalid.

### Rule 6: Ticket Dependencies Are Explicit

Every ticket declares:
- `depends_on`: list of ticket IDs that must be COMPLETE before this starts
- `blocks`: list of ticket IDs that cannot start until this is COMPLETE
- `gate`: the ID of the integration gate ticket that validates this ticket's
  work (may be shared with other tickets)

---

## Integration Gate Ticket Template

```markdown
# IG-[N]: Integration Gate — [Scope Description]

## Stage: NEW

## Scope
What user-visible flow(s) this gate validates:
- Flow A: [description from Phase 1 acceptance criteria]
- Flow B: [description]

## Validates Tickets
- T-[X]: [ticket title]
- T-[Y]: [ticket title]
- T-[Z]: [ticket title]

## Test Plan

### E2E UI Tests (Playwright / browser)
- [ ] [Given/when/then from Phase 1 acceptance criteria]
- [ ] [Given/when/then]

### API Integration Tests
- [ ] [Endpoint + method + expected response + error cases]
- [ ] [Endpoint + method]

### Data Integrity Tests
- [ ] [Query + expected result given test seed data]

## Environment Requirements
- [ ] Service A running at [address]
- [ ] Database seeded with [dataset]
- [ ] No mocks (list any exceptions with justification)

## Pass Criteria
All tests pass. No exceptions.
Zero tests marked as skipped without a linked follow-up ticket.

## Failure Protocol
If this gate fails:
1. Block: [list downstream ticket IDs]
2. Diagnose: create diagnostic ticket
3. Categorize: implementation bug | design flaw | environment issue
4. Resolve before proceeding

## Dependencies
- depends_on: [list of ticket IDs this gate validates]
- blocks: [list of downstream ticket IDs]
```

---

## Tracer Bullets

Before committing to the DAG, identify any **unverified technical integration**
in the architecture: streaming protocols, SSE, novel transports, third-party API
behaviors, unfamiliar framework patterns, or any assumption about how two systems
communicate that has not been proven in this codebase.

For each unverified integration:
1. Write a standalone proof script (~100 lines max, throwaway code)
2. The script must demonstrate the integration working end-to-end with real
   infrastructure (not mocks)
3. Run it. Capture the output as a proof artifact.
4. If the tracer bullet **fails**, the architecture assumption is immediately
   invalid. Return to Phase 2 to re-interrogate the boundary.
5. If it **passes**, record the proof artifact and proceed. The first
   integration gate (IG-1) must reference this proof.

Tracer bullets are NOT feature code. They are disposable validation scripts.
Do not refactor them, do not commit them to the main branch. Their only
purpose is to prove that an architecture assumption holds before tickets
are created on top of it.

---

## DAG Construction Process

The planner subagent constructs the DAG in this order:

1. **Identify the Minimum Testable Product (MTP)** from Phase 1
2. **Order MTP features as vertical slices** — each slice is a ticket
3. **Insert IG-1** after the first vertical slice (validates the foundation).
   IG-1 must require at least one **runtime proof artifact**: curl transcript,
   Playwright run output, server log snippet, screenshot, or exact
   request/response pair. A written test plan alone is not sufficient for IG-1.
4. **Add remaining feature tickets** in dependency order
5. **Insert integration gates** every ≤3 feature tickets
6. **Validate ordering rules** — all 6 rules must hold
7. **Output the DAG** as a text dependency graph

### DAG Text Format

```
T-1: [title]
  └─→ IG-1: [gate title] (validates: T-1)
       └─→ T-2: [title]
       └─→ T-3: [title]
            └─→ IG-2: [gate title] (validates: T-2, T-3)
                 └─→ T-4: [title]
                 └─→ T-5: [title]
                 └─→ T-6: [title]
                      └─→ IG-3: [gate title] (validates: T-4, T-5, T-6)
```

---

## Convergence Verification

After the DAG is constructed and challenged, verify:

1. **Completeness:** Every Phase 1 feature maps to at least one ticket
2. **Traceability:** Every ticket maps to at least one Phase 1 acceptance
   criterion
3. **Gate coverage:** Every ticket is validated by at least one integration gate
4. **Ordering validity:** No dependency chain has >3 feature tickets without a
   gate
5. **MTP first:** The first integration gate validates a working end-to-end flow
6. **No orphans:** No ticket exists that is not reachable from the MTP root

If any check fails, the DAG must be revised before it is presented to the user.
