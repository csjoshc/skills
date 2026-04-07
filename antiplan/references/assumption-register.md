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
