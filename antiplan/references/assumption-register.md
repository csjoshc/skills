# Assumption Register

Tracks every assumption made during the antiplan planning process. An assumption
is any statement that is not directly observed in running code, runtime output,
or verified documentation. Assumptions are the primary source of plan-rebuild-
discard loops — work built on unvalidated assumptions fails at integration time.

---

## Source Tags

Every assumption must carry exactly one source tag:

| Tag | Definition | May block tickets? |
|-----|-----------|-------------------|
| **Observed** | Confirmed in code, runtime output, logs, or documentation the agent has read | No — this is fact, not assumption |
| **User-stated** | Explicitly stated by the user during interrogation | No — user takes ownership |
| **Inferred** | Reasoned by the agent but not confirmed by user or runtime evidence | **Yes** — must be accepted by user or validated before dependent tickets proceed |
| **Deferred** | Unresolved by explicit choice. Both agent and user agree to defer. | **Yes** — must name the ticket or gate that will eventually validate it |

---

## Template

Maintain this register throughout Phases 1-3. Present it in every response
alongside the Convergence Ledger.

| ID | Statement | Source | Confidence | Impact if wrong | Validation method | Blocking? |
|----|-----------|--------|------------|----------------|-------------------|-----------|
| A-1 | [the assumption] | Observed / User-stated / Inferred / Deferred | HIGH / MED / LOW | [what breaks if this is wrong] | [how to validate: test, tracer bullet, user confirmation] | Yes / No |

---

## Rules

### Inferred Assumptions

- Any Inferred assumption that is **blocking** (i.e., at least one ticket
  depends on it) must be presented to the user for explicit acceptance before
  Phase 3 generates tickets.
- Present Inferred items as: "I am assuming [X]. If this is wrong, [Y] breaks.
  Do you confirm this assumption?"
- If the user accepts, change the source tag to User-stated.
- If the user rejects, the assumption becomes Unresolved and blocks Phase 3.

### Deferred Assumptions

- Every Deferred assumption must name the specific ticket ID or integration
  gate ID that will validate it.
- If no ticket or gate can validate it, the assumption is not deferrable — it
  must be resolved or the dependent feature must be cut.
- Deferred assumptions are reviewed during each integration gate. If the gate
  that was supposed to validate a deferred assumption passes without testing
  it, escalate.

### From Artifact Ingestion

When reference artifacts (repos, screenshots, links) are provided:
- Facts the agent extracts by directly reading the artifact → tagged **Observed**
- Claims the user makes about an artifact the agent cannot inspect → tagged
  **Inferred** until the agent can verify
- Features the user says "we want this from that repo" → tagged **User-stated**
  for the desire, but the feasibility is **Inferred** until a tracer bullet or
  code inspection confirms it

---

## When to Update

- Phase 1: Add assumptions about users, workflows, and requirements
- Phase 2: Add assumptions about component boundaries, API contracts, and
  infrastructure
- Phase 3: Planner subagent receives the register; Challenger subagent checks
  that no ticket depends on unaccepted Inferred assumptions
- Artifact ingestion: Add assumptions extracted from reference material

---

## Assumption Approval Gate

When the agent suggests an approach (architectural, technical, process), this
gate determines whether explicit user approval is required before proceeding.

### Gate Criteria (approval required if ANY are true)

| Criterion | Examples | Action |
|-----------|----------|--------|
| **Side effects** | Affects 2+ files; modifies public API; breaks existing tests | Require approval |
| **Blast radius ≥ 2** | Changes affect multiple modules or layers | Require approval |
| **Reverts prior decision** | Contradicts a Phase 1 or Phase 2 approved item | Require approval |
| **Hidden assumption** | Depends on inferred decision not yet tested | Require approval |
| **Infers stack/vendor choice** | Assumes specific database, framework, library | Require approval |
| **Scope expansion** | Suggests adding feature not in Phase 1 requirements | Require approval |

### Gate Execution Format

```markdown
**SUGGESTION:** <approach description>

**Assumption:** This assumes:
- A1: <e.g., "no breaking changes to UserService contract">
- A2: <e.g., "we're committed to PostgreSQL">

**Blast Radius:** affects <files/modules>, potential impact on <layer>

**User Approval Required:** Yes / No (based on gate criteria above)

Proceed only if user approves all assumptions, or explicitly overrides the gate.
```

### No Approval Needed (proceed without asking)

- Local variable naming, function organization within a file
- Cosmetic UI styling choices
- Test structure (as long as it doesn't expand scope)
- Comments, documentation improvements
- Suggestions marked explicitly as "low-blast-radius" (self-contained, easily reversible)

### When the User Rejects an Assumption

1. Remove the suggestion from the plan.
2. Update the Convergence Ledger: move from Inferred to Contested.
3. Ask a follow-up to understand the constraint: "Help me understand why
   <assumption> won't work. Is it <A>, <B>, or something else?"
4. Continue interrogation until you find a suggestion that fits.

---

## Complexity Justification Register

When the user successfully defends a complex choice during Phase 2, record it:

```
| Violation | Why needed | Simpler alternative rejected because |
```

This audit trail prevents re-litigating settled complexity decisions on
subsequent passes or in future sessions.

---

## Inline Clarification Markers

Any ambiguity in a PRD or ticket artifact must be marked inline as
`[NEEDS CLARIFICATION: specific question]` at the point of ambiguity, in
addition to the ledger entry. No ticket may enter the Phase 3 DAG if it
contains any `[NEEDS CLARIFICATION]` markers.
