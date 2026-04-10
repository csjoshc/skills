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

### Rule 7: Maximum 5 Files Per Ticket (Context Budget)

No single ticket may modify or create more than 5 files (excluding test
files). This bounds the implementing agent's context load — combined with
AP-4 (God Function) which prevents individual files from growing too large,
it keeps any one ticket within a single agent session's effective window.

If a ticket's scope exceeds 5 production files, split it. The planner
subagent must enforce this during DAG construction.

**Detection:** Count MODIFY + CREATE lines in each ticket's scope (test
files excluded). If >5, the challenger flags it for splitting.

### Rule 8: Assumption Validation Must Be Ticketed

Every assumption in the Assumption Register whose "Validation method" column
names a specific action (tracer bullet, proof script, curl test, runtime
check) must have a corresponding AC in the DAG that executes that validation.

An assumption whose validation method is "tracer bullet" but no ticket runs
the tracer bullet is still **Inferred**, not resolved — regardless of what
the source tag says. The validation is aspirational until it is scheduled.

**Detection:** For each assumption tagged Inferred→User-stated with a
validation method, grep the DAG for a ticket AC that matches. If not found,
the challenger flags it as unscheduled validation.

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

## Constitution Compliance
- [ ] Diff `pyproject.toml` / `package.json` against baseline commit — no
  new runtime dependencies unless explicitly approved by user
- [ ] No new packages created unless justified against Constitution and
  approved during Phase 2

## Pass Criteria
All tests pass. No exceptions.
Zero tests marked as skipped without a linked follow-up ticket.
At least one negative-path test per `[FALLIBLE_IO]`-tagged boundary
(dependency unreachable, invalid response, timeout).

## Expected Test Artifacts
Minimum test files that must exist when this gate completes:
- [ ] `[test file path]` — ≥[N] test cases covering [scope]
- [ ] `[test file path]` — ≥[N] test cases covering [scope]
- [ ] `[conftest or fixture file]` — shared fixtures for [scope]

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

**Tracer bullet scheduling (Rule 8 integration):**

Tracer bullets may be executed in two ways:

1. **Pre-DAG proof scripts** (preferred for HIGH-impact assumptions) — run
   before the DAG is constructed. If they fail, the architecture decision is
   revisited in Phase 2. The proof artifact is recorded and IG-1 references it.
2. **Feature ticket ACs** (acceptable for MEDIUM-impact assumptions) — folded
   into the first ticket that depends on the assumption. The AC must include
   explicit fallback behavior if the assumption proves false at runtime
   (e.g., "if the model does NOT emit structured tool_calls, a synthetic
   parsing fallback must extract tool name + args from assistant text").

The DAG Readiness Gate checks that every assumption with "Validation: tracer
bullet" is covered by one of these two approaches. An assumption with no
scheduled validation remains Inferred regardless of its source tag.

---

## Ticket Execution Modes

Every ticket is assigned an execution mode that determines how much oversight
the implementing agent receives. This is per-ticket, not per-project — a
single DAG may contain tickets at all three levels.

| Mode | Checkpoints | Criteria | Use when |
|------|------------|----------|----------|
| **Autopilot** | 0 — agent executes directly | ≤2 files modified, no new APIs, no architecture changes, exemplar file exists with near-identical pattern | Trivial MODIFY: config tweak, add test case, rename, update docs |
| **Confirm** | 1 — agent presents plan, human confirms before code | 3-5 files, new function signatures, API contract changes, or touches a file without an exemplar | Standard feature work: new endpoint, new React component, new guardrail |
| **Validate** | 2 — agent writes design doc, human reviews, then agent presents implementation plan, human confirms | >5 files, new architectural boundary, cross-package changes, or any ticket that failed in a prior iteration | Architecture-touching: new stream event types, provider changes, cross-layer refactors |

**Assignment rules:**
- The planner subagent assigns the initial mode during DAG construction
- The challenger subagent may escalate (autopilot→confirm, confirm→validate)
  but never downgrade
- Any ticket that touches a file flagged in a prior gate failure is
  automatically escalated to validate
- The user may override any mode during sign-off

**DAG annotation:** Each ticket in the text DAG includes its mode:

```
T-1: Orchestration: add conversation_prefix [confirm]
  └─→ T-2: BFF: wire prefix [confirm]
       └─→ T-3: React: send full history [autopilot]
```

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
6. **Assign execution modes** to each ticket using the criteria above
7. **Validate ordering rules** — all 8 rules must hold
8. **Output the DAG** as a text dependency graph with mode annotations

### DAG Text Format

```
T-1: [title] [confirm]
  └─→ IG-1: [gate title] (validates: T-1)
       └─→ T-2: [title] [confirm]
       └─→ T-3: [title] [autopilot]
            └─→ IG-2: [gate title] (validates: T-2, T-3)
                 └─→ T-4: [title] [confirm]
                 └─→ T-5: [title] [validate]
                 └─→ T-6: [title] [autopilot]
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

---

## DAG Readiness Gate

After convergence verification and all subagent rounds, run this final
structural checklist. Output: **READY** or **BLOCKED** (with specific blockers).

- [ ] Every ticket traces to an approved Phase 1 feature (traceability)
- [ ] No ticket depends on an Inferred assumption not accepted by user
- [ ] Every dependency chain has an integration gate within 3 feature tickets
- [ ] Total ticket count ≤ 10 per epic (scope-boxing)
- [ ] No ticket modifies/creates more than 5 production files (context budget)
- [ ] Every assumption with a named validation method has a corresponding
  ticket AC that executes that validation (Rule 8)
- [ ] Every integration gate lists expected test files with minimum assertion
  counts
- [ ] No ticket introduces a new runtime dependency not present before
  (Constitution compliance — diff `pyproject.toml` / `package.json` at gate)
- [ ] No ticket contains `[NEEDS CLARIFICATION]` markers
- [ ] Every ticket has at least one given/when/then acceptance criterion
- [ ] Every AC has a `Verify:` line with a grep/test/curl command (AP-10)
- [ ] Every ticket has a `Read First` section with ≥1 file path (AP-12)
- [ ] Every brownfield ticket has an `Exemplar Files` section (AP-13)
- [ ] Every ticket has at least one failure-path AC with user-visible assertion (AP-10)
- [ ] IG-1 has at least one runtime proof artifact requirement
- [ ] No ticket builds anything on the explicit non-goals list
- [ ] All P3 features are excluded from the DAG (deferred to follow-up epic)
- [ ] Every ticket has a **failure origin tag** (see below)
- [ ] Every ticket has an **execution mode** (autopilot/confirm/validate)
  assigned per the criteria in § Ticket Execution Modes
- [ ] Requirements Coverage Gate passes (see below)

If BLOCKED, list the specific blockers. Do not present the DAG to the user
until all blockers are resolved.

---

## Requirements Coverage Gate

After the DAG is constructed and before it is presented to the user, verify
that every resolved Phase 1 feature and acceptance criterion is covered by at
least one ticket. This prevents silent scope erosion during Phase 3 synthesis.

### Step 1: Feature Coverage

For each feature in PRD §5:
- Does at least one ticket in the DAG reference this feature?
- If not: **COVERAGE GAP** — the feature was silently dropped.

### Step 2: Acceptance Criterion Coverage

For each acceptance criterion in PRD §5:
- Does at least one ticket's AC match this criterion (exact or equivalent)?
- If not: **AC GAP** — the criterion was silently dropped.

### Step 3: Non-Goals Leak Check

For each item in PRD §10 (Explicitly Out of Scope):
- Does any ticket build something that overlaps with a non-goal?
- If yes: **SCOPE LEAK** — a cut feature crept back in.

### Output Format

```
## Requirements Coverage Report
- Features: [N]/[M] covered
- Acceptance Criteria: [N]/[M] covered
- Non-Goals Leaks: [count]

COVERAGE GAPS:
- Feature 5.X "[name]" — no ticket covers this
- AC "[given/when/then]" from Feature 5.Y — not present in any ticket AC

SCOPE LEAKS:
- T-[N] builds "[description]" which overlaps with non-goal #[K]

VERDICT: PASS | FAIL
```

If FAIL: the planner must either add missing tickets, justify the omission
with user approval, or explicitly defer the feature with a follow-up epic.

---

## Failure Origin Tagging

Every ticket must carry an origin tag indicating which planning phase
produced its requirement. This enables failure routing — when a gate fails,
the diagnostic ticket can trace the failure back to the right phase.

| Tag | Meaning | Failure routing |
|-----|---------|----------------|
| `origin: phase-1` | Requirement came from product interrogation | Re-interrogate the Phase 1 feature |
| `origin: phase-2` | Architecture decision from Phase 2 | Re-interrogate the Phase 2 boundary |
| `origin: constitution` | Required by a declared project principle | Challenge the principle or accept the cost |
| `origin: brownfield` | Regression protection for existing behavior | Check existing test coverage |

---

## Parallel Execution Markers

After the DAG is constructed, annotate parallelizable ticket groups:

```
## Parallel Execution Windows
- Window 1: T-2, T-3 (both depend only on IG-1, no mutual dependency)
- Window 2: T-5, T-6 (both depend only on IG-2)
```

This helps the `orchestrate` skill schedule work efficiently. Tickets in the
same window can run concurrently.
