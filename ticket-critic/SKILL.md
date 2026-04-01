---
name: ticket-critic
description: >-
  Pre-implementation critic for .tickets/*.md — 10 blocking patterns (embedded), auto-resolve
  via Architecture Decisions, Stage header gate, blast-radius splits (≤5 files / epic), TDD &
  verification mandates, and optional ticket hardening using the cleanup QUALITY_RUBRIC. Use before
  spec-writer or tdd when work is ticket-driven; use cleanup skill for reviewing existing code only.

## Assumptions & Escalation

- **Tier 1 (reversible):** Missing dependency in the ticket — proceed, flag for review.
- **Tier 2 (conflict):** Ticket violates Architecture Decisions (spec-writer skill) — **STOP**, block and alert.
- **Tier 3 (security):** Ticket implementation touches sensitive auth logic without a plan — **STOP**, block immediately.

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

## TL;DR (Quick Start)

Adversarial pre-flight audit for tickets in `.tickets/`. Prevents wasted effort by catching blocking issues (dependencies, scope, architecture) before implementation begins.

**When to use:** "criticize this ticket", "audit ticket", "preflight check".

**Invocation:**
```bash
/ticket-critic <ticket-path>
```

## Decision Tree

1. **Does the ticket have a `Stage:` header?**
   - YES → Proceed to audit.
   - NO → **BLOCK** immediately.

2. **Are there out-of-scope items?**
   - YES → Are they critical for functionality? If YES, **BLOCK**.
   - NO → Continue.

3. **Does the implementation touch > 5 production files?**
   - YES → **MANDATORY** split into child tickets.
   - NO → Proceed.

4. **Is there a verification plan?**
   - YES → Does it match project standards? If NO, **WARN**.
   - NO → **BLOCK**.

## Workflow

You do **not** write specs or implementation. You **audit tickets** for the 10 blocking patterns and either:
1. **Clear the ticket** (all patterns addressed)
2. **Block with specific reasons** (which patterns failed, what's needed)
3. **Auto-resolve** via Architecture Decisions (if question already answered)

## Operating Principles

**Block early, block clearly:** Better to block for 10 minutes now than waste 4 hours implementing the wrong thing. Be **specific** about what's missing and **actionable** about how to fix it.

**Auto-resolve when possible:** Check embedded Architecture Decisions below before blocking on any question.

**Risk-tier assumptions:** Tier 1 (reversible) → proceed. Tier 2 (architecture) → check Architecture Decisions. Tier 3 (security/safety) → always block. See [Assumption Tiers](#assumption-tiers).

**Evidence-based:** Cite specific lines/sections. Don't say "might be a problem."

---

## Pre-Flight Checklist (Embedded from STANDARDS.md)

**Purpose:** Catch blocking issues during ticket review, not during implementation. Run this checklist BEFORE marking a ticket READY.

### 1. Dependency Detection

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

### 2. Redesign / Redarchitecture Triggers

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

### 3. Contradicting Ticket Detection

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

- [ ] #TicketNumber — [describe contradiction, e.g., "says split api_types.py, this says keep as-is"]

**Resolution Required:**

- [ ] Coordinating ticket (#TicketNumber) approves this approach
- [ ] Architecture Decisions updated with architectural decision
- [ ] OR Task 0 added: "Resolve contradiction with #TicketNumber"

**Coordinating Ticket:** #TicketNumber (if applicable)
```

**Action:** Designate coordinating ticket, resolve contradiction before implementation.

---

### 4. Research / Vagueness Detection

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

- [ ] [Question 1, e.g., "Where does import UI live: Generator tab or settings modal?"]
- [ ] [Question 2, e.g., "What's the baseline coverage for target files?"]

**Required Research:**

- [ ] Architecture Decisions checked for resolved questions
- [ ] Task 0 added: "Research [topic]"
- [ ] OR decision made and documented in ticket

**Research Type:** [dependency / redesign / contradiction / vagueness]
```

**Action:** Add Task 0 research spike, or answer questions before implementation.

---

### Quick Reference: Blocker Patterns

| Pattern             | Example                              | Action                           |
| ------------------- | ------------------------------------ | -------------------------------- |
| **Dependency**      | "Backend returns X" without endpoint | Add dependency ticket or Task 0  |
| **Security**        | User input → subprocess              | Redesign + security review       |
| **Scope Gap**       | "OUT of scope: X" but X required     | Move to IN scope or split ticket |
| **Contradiction**   | Ticket A vs Ticket B conflict        | Coordinating ticket resolves     |
| **Vagueness**       | "Works correctly"                    | Define binary criteria           |
| **No Baseline**     | "≥90% coverage"                      | Measure baseline first           |
| **No Tests**        | Refactor without tests               | Add verification tests           |
| **Layer Confusion** | Domain + infrastructure mixed        | Clarify layer ownership          |

---

## Mandatory Preflight: Stage Header Gate

Before running the 10 patterns, validate ticket stage metadata.

**Required field:** `Stage:` (canonical; do not rely on `Status:` for new tickets)

If implementation-ready, must contain:
```yaml
---
Stage: BUILD
---
```

For the canonical stage enum and transitions, see the **orchestrate** skill.

## The 10 Blocking Patterns

Audit every ticket against these 10 patterns. For each: ✅ (pass), ⚠️ (warning, auto-resolvable), ❌ (blocker).

### Pattern 1: Unimplemented Dependencies

**Check:** Does the ticket assume a feature/endpoint/service exists that doesn't?

**Red flags:** "Already implemented" without link; "Backend returns X" without endpoint spec; dependency on ticket in progress or not started.

**Verification:** List all external dependencies → verify existence (codebase, PR status, merge state) → if not merged, check for stable API contract → if no contract, add Task 0 or block.

**Auto-resolve:** If dependency is a standard pattern defined in Architecture Decisions → proceed.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 1.

### Pattern 2: Architecture Contradictions

**Check:** Does this ticket conflict with other approved tickets or Architecture Decisions?

**Red flags:** Ticket proposes X, another proposes not-X; multiple tickets with different approaches for same system; no coordinating ticket for related refactors.

**Verification:** Search for tickets affecting same files/systems → check Architecture Decisions for resolved decisions → if contradiction, determine authoritative ticket → if unclear, block.

**Auto-resolve:** If Architecture Decisions already decides this question → apply that decision.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 2.

### Pattern 3: Scope Gaps

**Check:** Is essential functionality marked "out of scope" that's required for the feature to work?

**Red flags:** "OUT of scope: changing backend" but frontend sends data; "OUT of scope: security" for user input feature; full user flow not traceable.

**Verification:** Trace complete user flow (trigger → processing → output) → mark each step in/out of scope → if any out-of-scope step blocks flow → block.

**Auto-resolve:** If gap is obvious omission (not intentional), add to IN scope and note in audit.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 3.

### Pattern 4: Unverified Assumptions

**Check:** Does the ticket assume current implementation works a certain way without auditing first?

**Red flags:** "Already returns X" without verification; "Uses existing pattern" without linking; Task 1 starts without Task 0 audit.

**Verification:** List all assumptions → for each, check for evidence (file reference, test, log) → if no evidence, add Task 0 "Verify [assumption]".

**Auto-resolve:** If assumption matches Architecture Decisions default → proceed.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 4.

### Pattern 5: Security Vulnerabilities

**Check:** Does the design introduce security risks that aren't mitigated?

**Red flags:** User input → backend without validation spec; file path exposure; subprocess from HTTP endpoint; auth requirements not specified; rate limiting not mentioned.

**Verification:** Identify all user input touchpoints and sensitive operations → check for validation/isolation → apply Security Checklist in Architecture Decisions.

**Auto-resolve:** If Security Checklist in Architecture Decisions covers this → apply those requirements.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 5.

### Pattern 6: Missing Decision Points

**Check:** Are there open questions that should be decided before implementation?

**Red flags:** "Open questions" section unanswered; "TBD" or "FIXME" in spec; multiple approaches listed without selection.

**Verification:** List all open questions → check if each blocks implementation → if yes, check Architecture Decisions → if not answered, block.

**Auto-resolve:** If question answered in Architecture Decisions → apply that answer.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 6.

### Pattern 7: Unclear Success Criteria

**Check:** Is there no definition of what "done" looks like or how to measure it?

**Red flags:** "Works correctly" (not binary); "Improve performance" (no baseline/target); no Given/When/Then acceptance criteria.

**Verification:** Check each criterion is binary (pass/fail) → check metrics have baseline, target, measurement method → check verification plan exists.

**Auto-resolve:** If metric is a project default per Architecture Decisions → apply default.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 7.

### Pattern 8: Missing Tests/Verification

**Check:** Are refactors or changes without tests to catch regressions?

**Red flags:** "No new tests required" for refactor; public API changes without verification tests; domain layer split without domain tests.

**Verification:** Identify all public API/behavior changes → check for verification tests → check test strategy matches change type.

**Auto-resolve:** If Architecture Decisions defines test requirements → apply those.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 8.

### Pattern 9: Layer/Architecture Confusion

**Check:** Is it unclear which layer a function/class/module belongs to?

**Red flags:** Function does domain logic + DB calls + HTTP; "Service" layer with no orchestration; domain layer with external dependencies.

**Verification:** List all new/modified modules → determine layer ownership → check dependencies match layer rules → apply Layer Ownership in Architecture Decisions.

**Auto-resolve:** If Layer Ownership in Architecture Decisions defines layers → apply those rules.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 9.

### Pattern 10: Resource/Performance Concerns

**Check:** Is there no consideration for scale, memory, response time?

**Red flags:** In-memory storage without cleanup; unbounded list/collection; no response time target; no size limits for uploads; no pagination.

**Verification:** Identify all data storage and user-triggered operations → check for cleanup strategy, performance budgets, size limits.

**Auto-resolve:** If Architecture Decisions defines defaults (e.g., "LRU eviction, max 100 entries") → apply those.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 10.

## Workflow

1. **Read ticket** — Identify purpose, scope, dependencies, assumptions, open questions, success criteria, test strategy.
2. **Check Architecture Decisions** — Before blocking, check embedded Architecture Decisions in spec-writer skill. If answered → auto-resolve.
3. **Stage Header Gate** — Validate `Stage:` field against allowed enum. Block immediately if missing/invalid.
4. **Audit 10 patterns** — For each: check red flags, run verification, mark ✅/⚠️/❌, document evidence.
5. **Generate report** — Use the format below.
6. **Escalate if CRITICAL** — Block immediately for security vulnerabilities or architecture contradictions with other approved tickets.

### Audit Report Format

```markdown
# Ticket Audit Report

**Ticket:** [name/number]
**Result:** ✅ CLEARED / ⚠️ CLEARED with warnings / ❌ BLOCKED

## Summary
- ✅ Passed: [patterns]
- ⚠️ Warnings: [auto-resolved]
- ❌ Blockers: [patterns]

## Detailed Findings
### Pattern N: [Name] — [STATUS]
[Findings, evidence, required actions]

## Auto-Resolved via Architecture Decisions
- [Question X]: Applied Architecture Decisions section [Y]

## Required Actions Before Task 1
1. [Specific action 1]
2. [Specific action 2]

## Risk Assessment
**Overall risk:** LOW / MEDIUM / HIGH / CRITICAL
**Top risks:** [Risk + impact]
**Recommendation:** [proceed / block / escalate]
```

## Checklist

```
[ ] Stage Header Gate passed (`Stage:` present and valid enum)
[ ] All 10 patterns audited
[ ] Architecture Decisions checked for each open question
[ ] Evidence cited for each blocker (specific line/section)
[ ] Required actions are specific and actionable
[ ] Risk assessment completed
[ ] Escalation flagged if CRITICAL risks found
```

## Assumption Tiers

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for ticket-critic:**
- **Tier 1:** Missing dependency in ticket — proceed, flag for review
- **Tier 2:** Ticket violates Architecture Decisions — **STOP**, block and alert
- **Tier 3:** Ticket touches sensitive auth logic without a plan — **STOP**, block immediately

## Ticket Shape & Implementation Readiness

For ticket format requirements, see **spec-writer** skill Section 3 (TASKS output format) and **orchestrate** skill for state machine rules. Key checkpoints:

1. **YAML front matter** — `Stage:`, `Type`, `Order`, `Depends-On`, `Parent` per pipeline
2. **Goal / Problem / Requirements / Acceptance criteria** — spec-writer style; traceability to files
3. **Target files** — explicit list; **≤ 5 production files** per implementation ticket (see blast radius below)
4. **Verification (TDD)** — floor: project test suite; new tests when behavior changes
5. **Ticket critic preflight** — this skill's 10 patterns + Stage gate

## Blast Radius & Epic Split

- If implementation touches **> 5 production files**, split: `01a-ticket-slug.md`, `01b-…`, same directory.
- Set **parent** ticket to epic/tracker (`Stage: COMPLETE` when it only tracks children, per **orchestrate** skill).
- Children start **`Stage: NEW`** with their own target file lists.

## Strict TDD & Verification (BUILD-bound tickets)

When the ticket implies implementation, follow the **tdd** skill for test-first development. Key mandates:

- **TDD:** Tests written first (red → green → refactor) unless docs/planning-only
- **Frontend:** Mandate Playwright (or project E2E standard) for new/changed user-visible behavior
- **Backend (Python):** pytest for contracts, I/O boundaries, happy + unhappy paths
- **Verification section:** Concrete commands (e.g., `pytest tests/ -q`) plus linters/typecheck
- **Self-review (pre-REVIEW):** DRY, maintainability, boundaries per QUALITY_RUBRIC.md

## Integration & Reference Files

- **Integration with other skills:** See [reference/integration.md](reference/integration.md)
- **Super-prompts (harden tickets, generate new tickets):** See [reference/super-prompts.md](reference/super-prompts.md)
- **Block message templates:** See [templates/block-messages.md](templates/block-messages.md)
- **Audit finding examples:** See [examples/audit-findings.md](examples/audit-findings.md)

## Maintenance

**Update this skill when:** New blocking pattern identified; Architecture Decisions structure changes; audit process refined.

**Metrics to track:** Blocker detection rate; false positive rate; auto-resolution rate.
