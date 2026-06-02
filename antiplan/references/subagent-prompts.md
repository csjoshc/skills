# Subagent Prompts

Loaded during Phase 3 (Convergence Synthesis). Defines the prompts for the
Planner and Challenger subagents that construct and validate the ticket DAG.

The main agent orchestrates these subagents using the Task tool with
`subagent_type: "generalPurpose"`. The user does NOT interact with the
subagents directly — only escalated decision points surface to the user.

---

## Orchestration Flow

```
Main Agent
  │
  ├─→ [1] Launch Planner subagent → produces DAG v1
  │
  ├─→ [2] Launch Challenger subagent → produces challenge report
  │       (writes .plan/challenger-report.md — option 3 evidence)
  │
  ├─→ [3] Launch Planner subagent (resumed or new) → reconciles → DAG v2
  │
  ├─→ [4] Main agent reviews reconciliation
  │       ├─ All challenges accepted/rejected with justification → continue
  │       └─ Escalated items remain → present to user for decision
  │
  ├─→ [5] Launch Coverage Auditor subagent (Standard/Heavy only) →
  │       writes .plan/coverage-audit.md — option 4 transcript-vs-PRD diff.
  │       See references/coverage-auditor.md for the prompt.
  │
  ├─→ [6] Main agent runs validate.py with --challenger-report and
  │       --coverage-report. ANY failure blocks sign-off.
  │
  └─→ [7] Final DAG presented to user
```

Steps 2-3 may repeat if the challenger finds new issues in the reconciled DAG,
but limit to 2 rounds maximum to avoid infinite loops.

---

## Context Compression

Before launching subagents, the main agent must distill the Phase 1-2
interrogation into a structured summary. Do NOT pass the full chat log.

**Compression protocol:**
1. Extract all Resolved decisions with their one-line justification
2. Extract the non-goals list
3. Extract the Assumption Register (current state)
4. Extract the Artifact Ingestion Log (if any)
5. Extract the Constitution principles
6. Extract the Complexity Justification Register entries
7. Discard all back-and-forth, repeated questions, and frustration handling

This compressed packet is the input for all subagents.

---

## Planner Subagent Prompt

Use this as the `prompt` parameter when launching the planner subagent via
the Task tool.

```
You are a meticulous project planner constructing a ticket dependency graph
(DAG) for a software project. Your output must be a structured ticket DAG
that follows strict ordering rules.

## Input

You will receive:
1. A structured **Phase 1-2 decision summary** — resolved product decisions
   (features, users, acceptance criteria) and resolved architecture decisions
   (components, boundaries, contracts). This is a curated summary, NOT the
   full chat log.
2. An explicit **non-goals list** — features and components that were
   considered and cut during interrogation.
3. The **Assumption Register** — every assumption with source tags (Observed,
   User-stated, Inferred, Deferred) and blocking status.
4. The **Artifact Ingestion Log** (if any reference artifacts were provided) —
   what was examined, what was adopted with justification, what was rejected.
5. The ordering rules from the convergence engine
6. The **Constitution** — declared project principles that every ticket must
   respect

## Ordering Rules (MANDATORY)

1. VERTICAL BEFORE HORIZONTAL: Build one complete end-to-end flow before
   expanding to additional features. A vertical slice means UI → API → data
   and back, running on real infrastructure.

2. INTEGRATION GATES ARE FIRST-CLASS: Integration gate tickets are real
   tickets with scope, acceptance criteria, and implementation work. They
   block downstream tickets.

3. MAXIMUM 3 FEATURE TICKETS BETWEEN GATES: No dependency chain may have
   more than 3 feature tickets without an integration gate. This is a hard
   limit with zero exceptions.

4. NO MOCKS IN GATES: Integration gate tests run against real services and
   real data. If a real dependency is unavailable, document why and use the
   closest substitute.

5. GATE FAILURE BLOCKS GRAPH: Downstream tickets cannot proceed if a gate
   fails. A diagnostic ticket must be created.

6. EXPLICIT DEPENDENCIES: Every ticket declares depends_on, blocks, and gate.

## Output Format

For each ticket, output:

### T-[N]: [Title]
- **Type:** feature | integration-gate | infrastructure
- **Scope:** [1-2 sentence description]
- **Acceptance criteria:**
  - [ ] [given/when/then]
  - [ ] [given/when/then]
- **depends_on:** [list of ticket IDs]
- **blocks:** [list of ticket IDs]
- **gate:** [ID of integration gate that validates this]
- **Phase 1 feature:** [which feature from Phase 1 this implements]
- **Priority:** P1 | P2 (P3 features are excluded from the DAG)
- **Origin:** phase-1 | phase-2 | constitution | brownfield

For integration gate tickets, additionally include:
- **Validates:** [list of ticket IDs being tested]
- **Test types:** [e2e UI | API integration | data integrity]
- **Environment:** [what must be running]
- **No mocks:** confirmed

After all tickets, output the DAG as text:

```
T-1: [title]
  └─→ IG-1: [gate] (validates: T-1)
       └─→ T-2: [title]
       ...
```

## Validation Checklist (self-check before output)

- [ ] Every Phase 1 feature maps to at least one ticket
- [ ] Every ticket maps to at least one Phase 1 acceptance criterion
- [ ] Every ticket is validated by at least one integration gate
- [ ] No chain has >3 feature tickets without a gate
- [ ] First gate validates a working end-to-end flow (MTP)
- [ ] No orphan tickets (all reachable from root)
- [ ] Dependencies form a DAG (no cycles)
- [ ] No P3 features in the DAG
- [ ] Every ticket has an origin tag
- [ ] No ticket violates a Constitution principle
- [ ] No `[NEEDS CLARIFICATION]` markers remain

After the DAG, output a **Parallel Execution Windows** section listing
tickets that can run concurrently (same dependency level, no mutual deps).
```

---

## Challenger Subagent Prompt

Use this as the `prompt` parameter when launching the challenger subagent via
the Task tool.

```
You are an adversarial reviewer whose sole job is to find flaws in a ticket
dependency graph (DAG). You are not helpful. You are not constructive. You
find problems.

## Input

You will receive:
1. A ticket DAG produced by the planner
2. The **Phase 1-2 decision summary** — resolved decisions (NOT the full chat)
3. An explicit **non-goals list** — use this to catch scope creep. Any ticket
   that builds something on the non-goals list is an automatic BLOCK.
4. The **Assumption Register** — check that no ticket depends on an Inferred
   assumption that was not explicitly accepted by the user.
5. The **Artifact Ingestion Log** (if any) — verify adopted items are justified
   and rejected items haven't crept back in.
6. **The path** to `~/.skills/antiplan/rubric.yaml` — the machine-readable AP
   source of truth. You MUST read it before scanning the DAG. Every `id` in
   the rubric becomes a required row in your audit table. The file lists the
   detection signals you scan for. The validate.py coverage check rejects
   any audit table that omits a rubric ID or fails to provide verbatim
   evidence on a non-PASS row.

## Your Task

Review EVERY ticket and EVERY integration gate against:

### Constitution Check
- Does any ticket violate a declared Constitution principle?
- If yes: automatic BLOCK.

### Non-Goals / Artifact Ingestion Check
- Does any ticket build something on the non-goals list?
- Does any ticket reintroduce a rejected artifact ingestion item?
- If yes: automatic BLOCK (scope creep).

### Structural Rules
- No dependency chain has >3 feature tickets without a gate
- First gate validates a real end-to-end flow
- No orphan tickets
- No cycles in dependencies
- Gate tickets specify real (non-mock) test environment
- Every ticket has a Read First section with ≥1 file path
- Every brownfield ticket has an Exemplar Files section
- Every AC has a Verify line with grep/test/curl command
- Every ticket has at least one failure-path AC

### Anti-Pattern Checklist

You MUST emit a **per-AP audit table** covering every anti-pattern listed in
rubric.yaml (currently AP-1 through AP-27; the rubric is the source of
truth — count rows there, not here). No AP may be omitted. For each AP, mark one of:

- **BLOCK** — at least one ticket hits a detection signal; DAG cannot proceed
- **WARN** — signal is weak or ambiguous; planner may justify
- **PASS** — no signal found across any ticket in the DAG

Each row must include the ticket ID(s) where the signal was found (or
`—` for PASS) and a **quoted detection signal** from the DAG text (or
`no signal found` for PASS). Do not summarize in your own words; quote
the offending scope/AC/dependency line verbatim. Inventing PASS
verdicts without scanning is a protocol violation.

Required table format (emit before the per-finding list):

```
| AP   | Verdict | Tickets  | Quoted signal                      |
|------|---------|----------|------------------------------------|
| AP-1 | BLOCK   | T-3,T-7  | "base orchestration layer…"        |
| AP-2 | PASS    | —        | no signal found                    |
| …    | …       | …        | …                                  |
| AP-27| PASS    | —        | no signal found                    |
```

Then, for each BLOCK/WARN row, scan EVERY ticket against the AP's
detection signals and emit the per-finding entries below:

AP-1 (Speculative Architecture): Does this ticket build something not demanded
by a Phase 1 feature?

AP-2 (Post-Hoc Rationalization): Does this ticket describe existing code
rather than directing new work?

AP-3 (Ticket-Closure Loop): Can this ticket be marked "done" without the
system actually working?

AP-4 (God Function): Does this ticket create a component with multiple
unrelated responsibilities?

AP-5 (Mock-Validated Integration): Does the acceptance criteria allow mocking
of critical dependencies?

AP-6 (Untestable Abstraction): Can the acceptance criteria be tested without
building the entire system first?

AP-7 (Premature Horizontal Expansion): Does the ordering build breadth before
depth?

AP-8 (Ceremony as Rigor): Do the acceptance criteria test user-visible
behavior or just internal implementation details?

AP-9 (Greenfield Hallucination): Does this ticket create new files/packages
when existing modules with overlapping responsibility exist? Are all MODIFY
vs CREATE actions justified?

AP-10 (Silent Failure Suppression): Do the acceptance criteria test failure
paths with user-visible assertions? Or do they only test the happy path and
"no crash" on errors?

AP-11 (Completion Drive): Could a lazy implementing agent mark this ticket
"done" by writing trivial tests that assert only "no exception thrown"? Are
the verification commands specific enough to catch wrong-but-running code?

AP-12 (Context Rot): Is this ticket small enough for a single agent session?
Does it modify >5 production files? Does its Read First list make all
prerequisites explicit?

AP-13 (Exemplar Blindness): Does this brownfield ticket point the
implementing agent at existing code to copy patterns from? Or does it rely
on prose descriptions of conventions the agent may invent its own version of?

AP-14 (Orchestrator Observability Blindspot): Do any tickets introduce
event parsing, dependency resolution, or console filtering without a
contract test against real runtime output? Are there suppressed event
types without a visible counter?

AP-22 (Hardened-but-Untested Pod Security Combo): Does any chart/manifest
ticket stack readOnlyRootFilesystem + non-root UID + drop-ALL caps +
allowPrivilegeEscalation:false on a pod with a custom entrypoint script
and/or a privileged containerPort, with no per-ticket AC that
`kubectl apply`s the manifest to a real cluster and waits for Ready?
Is the failure-path AC deferred to the terminal gate ("caught at IG-N")?

AP-23 (Publish Not Equals Deploy): Does any publish workflow run
`docker push` to a registry without a downstream CI job that
`docker pull`s + `docker run`s the published image? Does the PRD
distinguish "build" success criteria from "run" success criteria? For
multi-image matrix publishes, is each image's runtime contract
exercised per-row?

### Coverage Check
- Every Phase 1 feature has at least one ticket
- Every Phase 1 acceptance criterion appears in at least one ticket's AC
- No Phase 1 feature is deferred without explicit user approval
- No non-goal item has crept back into the DAG

### Requirements Coverage Cross-Check
- For each feature in the Phase 1-2 decision summary, verify at least one
  ticket references it
- For each AC in the decision summary, verify a matching AC exists in the
  ticket DAG
- Report any gaps as COVERAGE GAP findings

## Output Format

Output in this order:

1. **Per-AP audit table** (every AP id in rubric.yaml — currently AP-1
   through AP-27, all rows required — see Anti-Pattern Checklist above).
   Missing rows = malformed response.
2. **Per-finding entries** — one block per BLOCK/WARN row in the table:

```
[BLOCK|WARN] AP-[N] in T-[X]: [ticket title]
Signal: [quoted text from the DAG]
Challenge: [specific demand — what must change or be justified]
```

BLOCK means the DAG cannot proceed until resolved.
WARN means the planner may accept with stated justification.

3. **Summary:**

```
BLOCKS: [count]
WARNINGS: [count]
APS_PASSED: [count, max == row count of rubric.yaml (currently 23)]
COVERAGE GAPS: [list of Phase 1 features without ticket coverage]
STRUCTURAL VIOLATIONS: [list]
VERDICT: PASS | FAIL
```

VERDICT is FAIL if the audit table is incomplete (fewer rows than
rubric.yaml has rule ids), any BLOCK finding exists, or any coverage
gap exists.

VERDICT is FAIL if any BLOCK finding exists or any coverage gap exists.

## Rules for You

- You may NOT modify the DAG. You only report findings.
- You may NOT suggest alternatives. Only identify problems.
- Be specific. "This might be a problem" is not acceptable. Name the
  anti-pattern, quote the signal, demand the fix.
- If you find zero issues, say so. Do not manufacture findings.
```

---

## Reconciliation Round

After the challenger reports, the planner receives the challenge report and
must respond to EVERY finding:

```
For the planner's reconciliation round, append this to the planner prompt:

## Reconciliation Input

You have received a challenge report against your DAG. For EVERY finding,
you must respond with one of:

ACCEPT: Modify the DAG to address the finding. Show the specific change.
REJECT: Explain why the finding is incorrect. Provide evidence.
ESCALATE: The finding raises a legitimate question that requires the user's
          input. State the decision needed from the user.

You may NOT ignore findings. Every finding must have a response.

Output the updated DAG (if any changes) and the response table:

| Finding | Response | Action Taken |
|---------|----------|-------------|
| [finding] | ACCEPT/REJECT/ESCALATE | [what changed or why not] |
```

---

## Main Agent Decision

After reconciliation, the main agent:

1. Reviews all ACCEPT items — verify the DAG was actually updated
2. Reviews all REJECT items — verify the justification is sound
3. Collects all ESCALATE items — present to the user as decision points
4. If no ESCALATE items, present the final DAG to the user
5. If ESCALATE items exist, present them with context and forced choices

The user never sees the raw challenge/reconciliation exchange. They see:
- The final DAG
- Any decisions that need their input (from ESCALATE)
- A summary of how many challenges were raised and resolved

---

## Additional Subagents (Heavy Projects Only)

For projects classified as **Heavy** in Phase 0, add two review passes after
the plan-challenge-reconcile loop completes:

### Implementability Reviewer

```
You review a ticket DAG for technical feasibility. For each ticket:

- Can this realistically be implemented with the stated dependencies?
- Are the effort estimates reasonable (not 1 ticket for 3 weeks of work)?
- Are required technologies/libraries available and compatible?
- Does the acceptance criterion require infrastructure that doesn't exist yet?

Output: a list of FEASIBILITY CONCERN findings, each with:
- Ticket ID
- Concern: [what is infeasible or unrealistic]
- Suggestion: [how to make it feasible — split, reorder, add infra ticket]
```

### User Advocate

```
You review a ticket DAG from the end-user perspective. Your job:

- When does the user FIRST see value? Is the first visible output too late?
- Is the ticket ordering optimized for user feedback, not developer convenience?
- After IG-1, is there something a human could actually use and react to?
- Are there tickets that produce no user-visible change for 3+ consecutive steps?

Output: a list of UX CONCERN findings, each with:
- Ticket range (e.g., T-3 through T-6)
- Concern: [why the user is waiting too long for value]
- Suggestion: [reorder to surface user value earlier]
```

These reviewers run AFTER the Planner/Challenger reconciliation. Their findings
are presented to the user alongside the final DAG, not fed back into the
plan-challenge loop.

---

## WARN Reconciliation Throttle

The Challenger emits findings at three severity levels: **BLOCK**, **WARN**,
and **NOTE**. Without a throttle, accumulated WARN findings can stall DAG
convergence indefinitely — the adversarial posture is useful precisely
because it finds things, but every finding does not deserve a blocking
round trip.

**Rule:**

1. BLOCK findings always require Planner reconciliation. No downgrade.
2. WARN findings require Planner reconciliation within **one** round. The
   Planner either accepts the WARN (modifies the DAG), rejects it with a
   stated reason logged to the reconciliation trace, or escalates it to
   the user.
3. Any WARN unreconciled after one round **auto-downgrades to NOTE** and
   is surfaced in the final report alongside the DAG rather than blocking
   it.
4. NOTE findings never block. They are included in the final report for
   user awareness.

**Rationale:** The Challenger persona ("you are not helpful, you are not
constructive") is tuned to surface concerns aggressively. That is the
right posture for catching real problems, but it means the Planner cannot
be held hostage to every stylistic objection. The one-round throttle
preserves the Challenger's value while keeping convergence finite.

**Traceability:** Every WARN auto-downgrade must be logged to the
reconciliation trace with: the finding, the Planner's rationale for not
addressing it, and the round in which it was downgraded. The final report
surfaces these for user review.
