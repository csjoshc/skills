# Assumption Tiers — Shared Definition

Used by all planning skills to classify and escalate assumptions.

## Tier 1: Reversible (LOW impact)

- Naming conventions, file locations, UI copy
- Library choices with easy migration path
- **Action:** Proceed, flag for post-review

## Tier 2: Architecture (MEDIUM impact)

- API patterns, data model structure, layer ownership
- Harder to change but not breaking
- **Action:** Check Architecture Decisions, block if unresolved

## Tier 3: Safety/Security (HIGH impact)

- Authentication, authorization, data sensitivity
- Public API contracts, database schema
- **Action:** Always block for human confirmation

## When to Block vs. Proceed

**Proceed without blocking if:**
- Question answered in Architecture Decisions
- Assumption is Tier 1 (reversible, low impact)
- Change is behind feature flag
- Test coverage exists to catch mistakes

**Block for human clarification if:**
- Security vulnerability possible
- Architecture contradiction (conflicting tickets)
- Dependency not implemented/merged
- Success criteria undefined
- Tier 3 assumption (auth, data model, public API)

---

## Assumption Register Format

Tracks every assumption made during planning. An assumption is any statement that is not directly observed in running code, runtime output, or verified documentation.

### Source Tags

Every assumption must carry exactly one source tag:

| Tag | Definition | May block tickets? |
|-----|-----------|-------------------|
| **Observed** | Confirmed in code, runtime output, logs, or documentation the agent has read | No — this is fact, not assumption |
| **User-stated** | Explicitly stated by the user during interrogation | No — user takes ownership |
| **Inferred** | Reasoned by the agent but not confirmed by user or runtime evidence | **Yes** — must be accepted by user or validated before dependent tickets proceed |
| **Deferred** | Unresolved by explicit choice. Both agent and user agree to defer. | **Yes** — must name the ticket or gate that will eventually validate it |

### Template

| ID | Statement | Source | Confidence | Impact if wrong | Validation method | Blocking? |
|----|-----------|--------|------------|----------------|-------------------|-----------|
| A-1 | [the assumption] | Observed / User-stated / Inferred / Deferred | HIGH / MED / LOW | [what breaks if this is wrong] | [how to validate: test, tracer bullet, user confirmation] | Yes / No |

### Rules

**Inferred Assumptions**
- Any Inferred assumption that is **blocking** (≥1 ticket depends on it) must be presented to the user for explicit acceptance before Phase 3 generates tickets.
- Present as: "I am assuming [X]. If this is wrong, [Y] breaks. Do you confirm this assumption?"
- Accepted → change tag to User-stated. Rejected → becomes Unresolved and blocks Phase 3.

**Deferred Assumptions**
- Must name the specific ticket ID or integration gate ID that will validate it.
- If no ticket/gate can validate it, the assumption is not deferrable — resolve it or cut the dependent feature.
- Reviewed during each integration gate; if the gate passes without testing it, escalate.

**From Artifact Ingestion**
- Facts extracted by directly reading the artifact → **Observed**
- User claims about artifacts the agent cannot inspect → **Inferred** until verified
- "We want this from that repo" → **User-stated** for the desire, **Inferred** for feasibility until tracer bullet or code inspection confirms

### When to Update

- Phase 1: assumptions about users, workflows, and requirements
- Phase 2: assumptions about component boundaries, API contracts, and infrastructure
- Phase 3: Planner receives register; Challenger checks no ticket depends on unaccepted Inferred assumptions
- Artifact ingestion: add assumptions extracted from reference material

### Assumption Approval Gate

When the agent suggests an approach, this gate determines whether explicit user approval is required.

**Gate Criteria (approval required if ANY are true)**

| Criterion | Examples | Action |
|-----------|----------|--------|
| **Side effects** | Affects 2+ files; modifies public API; breaks existing tests | Require approval |
| **Blast radius ≥ 2** | Changes affect multiple modules or layers | Require approval |
| **Reverts prior decision** | Contradicts a Phase 1 or Phase 2 approved item | Require approval |
| **Hidden assumption** | Depends on inferred decision not yet tested | Require approval |
| **Infers stack/vendor choice** | Assumes specific database, framework, library | Require approval |
| **Scope expansion** | Suggests adding feature not in Phase 1 requirements | Require approval |

**Gate Execution Format**

```markdown
**SUGGESTION:** <approach description>

**Assumption:** This assumes:
- A1: <e.g., "no breaking changes to UserService contract">
- A2: <e.g., "we're committed to PostgreSQL">

**Blast Radius:** affects <files/modules>, potential impact on <layer>

**User Approval Required:** Yes / No (based on gate criteria above)

Proceed only if user approves all assumptions, or explicitly overrides the gate.
```

**No Approval Needed (proceed without asking)**
- Local variable naming, function organization within a file
- Cosmetic UI styling choices
- Test structure (as long as it doesn't expand scope)
- Comments, documentation improvements
- Suggestions marked explicitly as "low-blast-radius" (self-contained, easily reversible)

**When the User Rejects an Assumption**
1. Remove the suggestion from the plan.
2. Update the Convergence Ledger: move from Inferred to Contested.
3. Ask a follow-up: "Help me understand why <assumption> won't work. Is it <A>, <B>, or something else?"
4. Continue interrogation until you find a suggestion that fits.

### Complexity Justification Register

When the user successfully defends a complex choice during Phase 2, record it:

```
| Violation | Why needed | Simpler alternative rejected because |
```

This audit trail prevents re-litigating settled complexity decisions.

### Inline Clarification Markers

Any ambiguity in a PRD or ticket artifact must be marked inline as `[NEEDS CLARIFICATION: specific question]` at the point of ambiguity, in addition to the ledger entry. No ticket may enter the Phase 3 DAG if it contains any `[NEEDS CLARIFICATION]` markers.
