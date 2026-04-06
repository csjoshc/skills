# Pre-Flight Checklist — Blocker Detection

**Purpose:** Catch blocking issues during ticket review, not during implementation. Run this checklist BEFORE marking a ticket READY.

## 1. Dependency Detection

**Trigger:** Ticket mentions functionality that may not exist yet.

**Check for these patterns:**
- [ ] "Already returns X" without file reference
- [ ] "Backend provides X" without endpoint specification
- [ ] "Frontend calls X" without API contract
- [ ] "Uses existing X" without linking to existing implementation
- [ ] Depends on another ticket that's not merged

**If any match → Add to ticket:**

```markdown
### Dependencies
**Blocking Dependencies:**
- [ ] #TicketNumber — [what's needed, e.g., "POST /api/workflow/load endpoint"]
- [ ] #TicketNumber — [what's needed]

**Dependency Status:**
- [ ] All dependencies merged to main
- [ ] API contracts stable (no pending changes)
- [ ] OR Task 0 added: "Verify [dependency] exists"
```

**Action:** Create linked dependency ticket or add Task 0 verification.

---

## 2. Redesign / Redarchitecture Triggers

**Trigger:** Original design has flaws that block implementation.

**Check for these patterns:**
- [ ] "OUT of scope: X" but X is required for feature to work
- [ ] Security vulnerability (user input → sensitive operation without validation)
- [ ] Subprocess execution from HTTP endpoint
- [ ] Direct file path exposure (path traversal risk)
- [ ] Architecture contradicts existing patterns
- [ ] Layer confusion (domain logic + infrastructure in same module)

**If any match → Add to ticket:**

```markdown
### Design Issues
**Critical Flaws:**
- [ ] [Describe flaw, e.g., "Security: user input to subprocess without validation"]
- [ ] [Describe flaw, e.g., "Scope gap: X is OUT of scope but required for Y"]

**Required Redesign:**
- [ ] Security review completed
- [ ] Scope boundary updated (move X from OUT to IN scope)
- [ ] OR Task 0 added: "Redesign [component] to address [flaw]"

**Proposed Solution:** [brief description of fix]
```

**Action:** Redesign before implementation, or add Task 0 for redesign spike.

---

## 3. Contradicting Ticket Detection

**Trigger:** Multiple tickets make conflicting recommendations.

**Check for these patterns:**
- [ ] Ticket A says "split X", Ticket B says "keep X cohesive"
- [ ] Both tickets approved for same system with different approaches
- [ ] No coordinating ticket for related refactors
- [ ] Refactor tickets without dependency sequencing

**If any match → Add to ticket:**

```markdown
### Architectural Contradictions
**Conflicts With:**
- [ ] #TicketNumber — [describe contradiction]

**Resolution Required:**
- [ ] Coordinating ticket (#TicketNumber) approves this approach
- [ ] STANDARDS.md updated with architectural decision
- [ ] OR Task 0 added: "Resolve contradiction with #TicketNumber"

**Coordinating Ticket:** #TicketNumber (if applicable)
```

**Action:** Designate coordinating ticket, resolve contradiction before implementation.

---

## 4. Research / Vagueness Detection

**Trigger:** Ticket lacks detail needed for implementation.

**Check for these patterns:**
- [ ] "Open questions" section with unanswered items
- [ ] "TBD" or "FIXME" in spec
- [ ] Multiple approaches listed without selection
- [ ] UI location, API pattern, or data model undecided
- [ ] Success criteria without baseline/target/measurement
- [ ] "Works correctly" (not binary)
- [ ] No tests specified for refactor

**If any match → Add to ticket:**

```markdown
### Research Needed
**Unanswered Questions:**
- [ ] [Question 1]
- [ ] [Question 2]

**Required Research:**
- [ ] STANDARDS.md checked for resolved questions
- [ ] Task 0 added: "Research [topic]"
- [ ] OR decision made and documented in ticket

**Research Type:** [dependency / redesign / contradiction / vagueness]
```

**Action:** Add Task 0 research spike, or answer questions before implementation.

---

## Quick Reference: Blocker Patterns

| Pattern | Example | Action |
|---------|---------|--------|
| **Dependency** | "Backend returns X" without endpoint | Add dependency ticket or Task 0 |
| **Security** | User input → subprocess | Redesign + security review |
| **Scope Gap** | "OUT of scope: X" but X required | Move to IN scope or split ticket |
| **Contradiction** | Ticket A vs Ticket B conflict | Coordinating ticket resolves |
| **Vagueness** | "Works correctly" | Define binary criteria |
| **No Baseline** | "≥90% coverage" | Measure baseline first |
| **No Tests** | Refactor without tests | Add verification tests |
| **Layer Confusion** | Domain + infrastructure mixed | Clarify layer ownership |

---

## Ticket Review Workflow

**Before marking ticket READY:**
1. Run blocker detection checklist (4 sections above)
2. For each blocker found: add appropriate section to ticket, add Task 0 if needed, link coordinating ticket
3. Update ticket status: READY / NEEDS_REVISION / BLOCKED

**During ticket review meeting:**
1. Review blocker sections in each ticket
2. Make decisions on open questions
3. Assign coordinating tickets for contradictions
4. Approve Task 0 research spikes
5. Update STANDARDS.md with new decisions

---

## Examples from Recent Audit

### Example 1: Dependency Detection (Ticket 01)

**Pattern Found:** "Backend already returns `faceRefPath`" but no endpoint to serve image

**Added to Ticket:**
```markdown
### Dependencies
**Blocking Dependencies:**
- [ ] NEW — Backend endpoint to serve face reference images
  - Required: `GET /api/static/uploads/faces/:filename` or similar
  - Security: Path validation to prevent traversal attacks

**Dependency Status:**
- [ ] Endpoint implemented and merged
- [ ] OR Task 0 added: "Verify/create static file serving endpoint"
```

### Example 2: Security Redesign (Ticket 03)

**Pattern Found:** Subprocess execution from HTTP endpoint (`pytest` via `subprocess.Popen`)

**Added to Ticket:**
```markdown
### Design Issues
**Critical Flaws:**
- [ ] Security: `POST /api/admin/tests/run` executes pytest via subprocess
  - Risk: Remote code execution if auth bypassed
  - Risk: Command injection via test name parameter

**Required Redesign:**
- [ ] Security review completed
- [ ] Choose mitigation: Option A (separate service), Option B (strict validation), Option C (DEV-ONLY + auth layers)
```

### Example 3: Contradiction Detection (Tickets 32 vs 36)

**Pattern Found:** Ticket 32 says "split api_types.py", Ticket 36 says "keep as-is"

**Added to Both Tickets:**
```markdown
### Architectural Contradictions
**Conflicts With:**
- [ ] #36 — Says "Keep as-is — DTOs are cohesive", this ticket says split

**Resolution Required:**
- [ ] Coordinating ticket (#36) approves split approach
```

### Example 4: Research/Vagueness (Ticket 22)

**Pattern Found:** "OUT of scope: changing ComfyUI JSON" but workflow must affect backend somehow

**Added to Ticket:**
```markdown
### Research Needed
**Unanswered Questions:**
- [ ] What does workflow selection actually DO at backend level?

**Required Research:**
- [ ] Task 0 added: "Research workflow-to-backend mapping"
```

### Example 5: No Baseline (Ticket 28)

**Pattern Found:** "≥90% line coverage" without baseline measurement

**Added to Ticket:**
```markdown
### Research Needed
**Unanswered Questions:**
- [ ] What is current baseline coverage for target files?

**Required Research:**
- [ ] Task 0b added: "Measure baseline coverage"
```

---

## Ticket Review Template

**Copy this template into tickets that need blocker sections added:**

```markdown
---

## SECTION 4: BLOCKING ISSUES & SCOPE CLARIFICATIONS

### Status: READY / NEEDS_REVISION / BLOCKED

### Dependencies
**Blocking Dependencies:**
- [ ] #TicketNumber — [what's needed]
- [ ] OR Task 0 added: "Verify [dependency] exists"

**Dependency Status:**
- [ ] All dependencies merged to main
- [ ] API contracts stable

---

### Design Issues
**Critical Flaws:**
- [ ] [Describe flaw]

**Required Redesign:**
- [ ] Security review completed
- [ ] Scope boundary updated
- [ ] OR Task 0 added: "Redesign [component]"

**Proposed Solution:** [brief description]

---

### Architectural Contradictions
**Conflicts With:**
- [ ] #TicketNumber — [describe contradiction]

**Resolution Required:**
- [ ] Coordinating ticket (#TicketNumber) approves
- [ ] STANDARDS.md updated with decision
- [ ] OR Task 0 added: "Resolve contradiction"

**Coordinating Ticket:** #TicketNumber

---

### Research Needed
**Unanswered Questions:**
- [ ] [Question 1]
- [ ] [Question 2]

**Required Research:**
- [ ] STANDARDS.md checked
- [ ] Task 0 added: "Research [topic]"
- [ ] OR decision made

**Research Type:** [dependency / redesign / contradiction / vagueness]

---

### Pre-Flight Checklist
- [ ] Task 0 (verify dependencies) completed
- [ ] Task 0b (research/redesign) completed
- [ ] STANDARDS.md checked for resolved questions
- [ ] Coordinating ticket approved (if applicable)
```
