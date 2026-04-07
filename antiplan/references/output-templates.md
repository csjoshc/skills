# Output Templates

Templates for the deliverables produced by the antiplan skill. These are
populated after Phase 3 completes and the DAG is approved by the user.

---

## PRD Template

```markdown
# PRD: [Product Name]

## Status: APPROVED | DRAFT
## Date: [date]
## Author: [user] + antiplan skill

---

## 1. Problem Statement

[What problem exists for what user. 2-3 sentences max. No implementation.]

## 2. Users

| User | Role | Primary workflow | Pain without this system |
|------|------|-----------------|-------------------------|
| [name/type] | [role] | [what they do] | [what hurts] |

## 3. Minimum Testable Product (MTP)

The smallest set of features that proves the design works end-to-end:

1. [Feature A] — [1-sentence description]
2. [Feature B] — [1-sentence description]

**MTP validation:** After [ticket IDs], integration gate IG-1 confirms:
- [given/when/then]
- [given/when/then]

## 4. Features

### 4.1 [Feature Name]

**User story:** As a [user], I want [action] so that [outcome].

**Acceptance criteria:**
- [ ] Given [precondition], when [action], then [result]
- [ ] Given [precondition], when [action], then [result]

**Out of scope:** [what this feature explicitly does NOT do]

**Ticket(s):** T-[N], T-[M]
**Gate:** IG-[K]

### 4.2 [Feature Name]
[repeat structure]

## 5. Architecture Decisions

| Decision | Options considered | Chosen | Justification |
|----------|-------------------|--------|---------------|
| [decision] | [A, B, C] | [B] | [why B, from Phase 2] |

## 6. Component Map

| Component | Responsibility (one sentence, no 'and') | Owner tickets |
|-----------|------------------------------------------|---------------|
| [name] | [what it does] | T-[N] |

## 7. API Contracts

### [Component A] → [Component B]

```
[method] [path]
Request: [type signature]
Response: [type signature]
Errors: [error types and when]
```

## 8. Explicitly Out of Scope

1. [thing] — deferred because [reason]
2. [thing] — not requested by any identified user
3. [thing] — cut during Phase 2 architecture interrogation

## 9. Risks and Open Questions

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [risk] | H/M/L | H/M/L | [what we do] |

## 10. Ticket Dependency Graph

[paste DAG from Phase 3]

## 11. Convergence Ledger (Final)

- Resolved: [count]
- Cut: [count]
- Deferred: [count] — [items with justification]

## 12. Assumption Register

| ID | Statement | Source | Confidence | Impact if wrong | Validation method | Blocking? |
|----|-----------|--------|------------|----------------|-------------------|-----------|
| A-1 | [assumption] | Observed / User-stated / Inferred / Deferred | HIGH/MED/LOW | [consequence] | [how to validate] | Yes/No |

All Inferred assumptions that are blocking were explicitly accepted by user
before ticket generation.

## 13. Artifact Ingestion Log

*Omit this section if no reference artifacts were provided.*

| Artifact | Type | Items enumerated | Items adopted | Items rejected |
|----------|------|-----------------|--------------|----------------|
| [repo/link/screenshot] | git repo / screenshot / docs / API spec | [count] | [list with justification] | [list with reason] |
```

---

## Feature Ticket Template

```markdown
# T-[N]: [Title]

## Stage: NEW
## Type: feature

## Scope
[1-2 sentences. What this ticket produces that didn't exist before.]

## User Story
As a [user from PRD §2], I want [action] so that [outcome from PRD §4].

## Acceptance Criteria
- [ ] Given [precondition], when [action], then [result]
- [ ] Given [precondition], when [action], then [result]
- [ ] Given [error condition], when [action], then [graceful handling]

## API Contract (if applicable)
[method] [path]
Request: [type]
Response: [type]
Errors: [types]

## Technical Notes
[Implementation guidance from Phase 2 decisions. Keep brief.]

## Dependencies
- **depends_on:** [ticket IDs]
- **blocks:** [ticket IDs]
- **gate:** IG-[K] — this ticket's work is validated by this gate

## Definition of Done
- [ ] Acceptance criteria pass on real (not mocked) infrastructure
- [ ] Code reviewed
- [ ] No new linter warnings
- [ ] Integration gate IG-[K] is unblocked and ready to run
```

---

## Integration Gate Ticket Template

```markdown
# IG-[N]: Integration Gate — [Scope Description]

## Stage: NEW
## Type: integration-gate

## Scope
Validates that the following user-visible flows work end-to-end on real
infrastructure after tickets [list] are complete.

## Validates Tickets
- T-[X]: [title]
- T-[Y]: [title]

## Flows Under Test

### Flow 1: [Name from PRD §4]
- Given [precondition — real data, real services]
- When [user action or API call]
- Then [expected observable result]

### Flow 2: [Name]
[repeat]

## Test Implementation

### E2E UI Tests
- [ ] [test description — Playwright/browser, real backend]

### API Integration Tests
- [ ] [endpoint + method + expected response]
- [ ] [error scenario + expected error response]

### Data Integrity
- [ ] [query on real DB + expected result given seed data]

## Environment
- [ ] [Service] running at [address/port]
- [ ] [Database] seeded with [dataset name or script]
- [ ] [External dependency] available at [address] (or documented exception)
- [ ] **No mocks.** [list any exceptions with justification and follow-up
      ticket for real integration]

## Pass Criteria
ALL tests pass. Zero skipped tests without a linked follow-up ticket.

## Proof Artifacts (required for IG-1, recommended for all gates)
At least one of:
- [ ] curl transcript (request + response)
- [ ] Playwright run output
- [ ] Server log snippet showing the flow executed
- [ ] Screenshot or video artifact
- [ ] Exact request/response pair from real service

## Verified By
[CI job name/URL or human reviewer — NOT the implementing agent/session]

## Failure Protocol
1. Block: [downstream ticket IDs]
2. Create diagnostic ticket with failure output
3. Categorize: implementation bug | design flaw | environment issue
4. If design flaw: escalate to Phase 2 re-interrogation
5. Do NOT proceed until gate passes

## Dependencies
- **depends_on:** [ticket IDs this gate validates — all must be COMPLETE]
- **blocks:** [downstream ticket IDs]
```

---

## Infrastructure Ticket Template

```markdown
# T-[N]: [Title]

## Stage: NEW
## Type: infrastructure

## Scope
[What infrastructure this sets up. Not a feature — enables features.]

## Justification
Required by tickets: [list of feature tickets that depend on this]
Without this, the following cannot be tested on real infrastructure: [list]

## Acceptance Criteria
- [ ] [Service/resource] is running and accessible at [address]
- [ ] [Health check endpoint] returns 200
- [ ] [Seed data] is loaded and queryable

## Dependencies
- **depends_on:** [ticket IDs, if any]
- **blocks:** [ticket IDs that need this infrastructure]

## Definition of Done
- [ ] Infrastructure is running
- [ ] At least one downstream ticket's test can execute against it
```
