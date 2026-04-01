# Ticket-Critic — Blocking Patterns & Checklist

This companion file contains the detailed adversarial audit checks for `.tickets/*.md`.

## Pre-Flight Checklist

**Purpose:** Catch blocking issues during ticket review, not during implementation. Run this checklist BEFORE marking a ticket READY.

### 1. Dependency Detection
**Trigger:** Ticket mentions functionality that may not exist yet.

- [ ] "Already returns X" without file reference
- [ ] "Backend provides X" without endpoint specification
- [ ] "Frontend calls X" without API contract
- [ ] "Uses existing X" without linking to existing implementation
- [ ] Depends on another ticket that's not merged

**If any match → Add to ticket:**
```markdown
### Dependencies
**Blocking Dependencies:**
- [ ] #TicketNumber — [what's needed]
```

### 2. Redesign / Redarchitecture Triggers
**Trigger:** Original design has flaws that block implementation.

- [ ] "OUT of scope: X" but X is required for feature to work
- [ ] Security vulnerability (e.g., unvalidated user input to subprocess)
- [ ] Layer confusion (domain logic + infrastructure in same module)

### 3. Contradicting Ticket Detection
**Trigger:** Multiple tickets make conflicting recommendations.

- [ ] Ticket A vs Ticket B conflict on same system
- [ ] No coordinating ticket for related refactors

### 4. Research / Vagueness Detection
**Trigger:** Ticket lacks detail needed for implementation.

- [ ] "Open questions" section with unanswered items
- [ ] "Works correctly" (not binary success criteria)
- [ ] No tests specified for refactor

---

## The 10 Blocking Patterns

Audit every ticket against these 10 patterns.

### Pattern 1: Unimplemented Dependencies
Does the ticket assume a feature/service exists that doesn't? Verify existence in codebase or PR status.

### Pattern 2: Architecture Contradictions
Does this ticket conflict with other approved tickets or Architecture Decisions?

### Pattern 3: Scope Gaps
Is essential functionality marked "out of scope" that's required for the flow?

### Pattern 4: Unverified Assumptions
Does the ticket assume current implementation works a certain way without auditing (Task 0)?

### Pattern 5: Security Vulnerabilities
Does the design introduce risks (input validation, path traversal, auth)?

### Pattern 6: Missing Decision Points
Are there "TBD" or unanswered questions blocking implementation?

### Pattern 7: Unclear Success Criteria
Is the definition of "done" binary and measurable? (Given/When/Then).

### Pattern 8: Missing Tests/Verification
Are refactors or public API changes missing verification tests?

### Pattern 9: Layer/Architecture Confusion
Is it unclear which layer a function/module belongs to? (Domain vs Infra).

### Pattern 10: Resource/Performance Concerns
Are there considerations for scale, memory, or response time? (Pagination, limits).
