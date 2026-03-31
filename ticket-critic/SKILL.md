---
name: ticket-critic
description: >-
  Pre-implementation critic for .tickets/*.md — 10 blocking patterns, STANDARDS.md auto-resolve,
  Stage header gate, blast-radius splits (≤5 files / epic), TDD & verification mandates, and
  optional ticket hardening using the cleanup QUALITY_RUBRIC. Use before
  spec-writer or tdd when work is ticket-driven; use cleanup skill for reviewing existing code only.

## Assumptions & Escalation

- **Tier 1 (reversible):** Missing dependency in the ticket — proceed, flag for review.
- **Tier 2 (conflict):** Ticket violates `STANDARDS.md` core patterns — **STOP**, block and alert.
- **Tier 3 (security):** Ticket implementation touches sensitive auth logic without a plan — **STOP**, block immediately.

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
3. **Auto-resolve** via STANDARDS.md (if question already answered)

## Operating Principles

**Block early, block clearly:** Better to block for 10 minutes now than waste 4 hours implementing the wrong thing. Be **specific** about what's missing and **actionable** about how to fix it.

**Auto-resolve when possible:** Check `./STANDARDS.md` and `~/.skills/STANDARDS.md` before blocking on any question.

**Risk-tier assumptions:** Tier 1 (reversible) → proceed. Tier 2 (architecture) → check STANDARDS.md. Tier 3 (security/safety) → always block. See [Assumption Tiers](#assumption-tiers).

**Evidence-based:** Cite specific lines/sections. Don't say "might be a problem."

## Mandatory Preflight: Stage Header Gate

Before running the 10 patterns, validate ticket stage metadata.

**Required field:** `Stage:` (canonical; do not rely on `Status:` for new tickets)

If implementation-ready, must contain:
```yaml
---
Stage: BUILD
---
```

Allowed enum: `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`.

If `Stage:` is missing or invalid, block immediately. Block message: see [templates/block-messages.md](templates/block-messages.md) — Stage Header Gate section.

## The 10 Blocking Patterns

Audit every ticket against these 10 patterns. For each: ✅ (pass), ⚠️ (warning, auto-resolvable), ❌ (blocker).

### Pattern 1: Unimplemented Dependencies

**Check:** Does the ticket assume a feature/endpoint/service exists that doesn't?

**Red flags:** "Already implemented" without link; "Backend returns X" without endpoint spec; dependency on ticket in progress or not started.

**Verification:** List all external dependencies → verify existence (codebase, PR status, merge state) → if not merged, check for stable API contract → if no contract, add Task 0 or block.

**Auto-resolve:** If dependency is a standard pattern defined in STANDARDS.md → proceed.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 1.

### Pattern 2: Architecture Contradictions

**Check:** Does this ticket conflict with other approved tickets or STANDARDS.md?

**Red flags:** Ticket proposes X, another proposes not-X; multiple tickets with different approaches for same system; no coordinating ticket for related refactors.

**Verification:** Search for tickets affecting same files/systems → check STANDARDS.md for resolved decisions → if contradiction, determine authoritative ticket → if unclear, block.

**Auto-resolve:** If STANDARDS.md already decides this question → apply that decision.

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

**Auto-resolve:** If assumption matches STANDARDS.md default → proceed.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 4.

### Pattern 5: Security Vulnerabilities

**Check:** Does the design introduce security risks that aren't mitigated?

**Red flags:** User input → backend without validation spec; file path exposure; subprocess from HTTP endpoint; auth requirements not specified; rate limiting not mentioned.

**Verification:** Identify all user input touchpoints and sensitive operations → check for validation/isolation → apply STANDARDS.md security checklist.

**Auto-resolve:** If STANDARDS.md security checklist covers this → apply those requirements.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 5.

### Pattern 6: Missing Decision Points

**Check:** Are there open questions that should be decided before implementation?

**Red flags:** "Open questions" section unanswered; "TBD" or "FIXME" in spec; multiple approaches listed without selection.

**Verification:** List all open questions → check if each blocks implementation → if yes, check STANDARDS.md → if not answered, block.

**Auto-resolve:** If question answered in STANDARDS.md → apply that answer.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 6.

### Pattern 7: Unclear Success Criteria

**Check:** Is there no definition of what "done" looks like or how to measure it?

**Red flags:** "Works correctly" (not binary); "Improve performance" (no baseline/target); no Given/When/Then acceptance criteria.

**Verification:** Check each criterion is binary (pass/fail) → check metrics have baseline, target, measurement method → check verification plan exists.

**Auto-resolve:** If metric is a project default per STANDARDS.md → apply default.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 7.

### Pattern 8: Missing Tests/Verification

**Check:** Are refactors or changes without tests to catch regressions?

**Red flags:** "No new tests required" for refactor; public API changes without verification tests; domain layer split without domain tests.

**Verification:** Identify all public API/behavior changes → check for verification tests → check test strategy matches change type.

**Auto-resolve:** If STANDARDS.md defines test requirements → apply those.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 8.

### Pattern 9: Layer/Architecture Confusion

**Check:** Is it unclear which layer a function/class/module belongs to?

**Red flags:** Function does domain logic + DB calls + HTTP; "Service" layer with no orchestration; domain layer with external dependencies.

**Verification:** List all new/modified modules → determine layer ownership → check dependencies match layer rules → apply STANDARDS.md layer ownership.

**Auto-resolve:** If STANDARDS.md defines layers → apply those rules.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 9.

### Pattern 10: Resource/Performance Concerns

**Check:** Is there no consideration for scale, memory, response time?

**Red flags:** In-memory storage without cleanup; unbounded list/collection; no response time target; no size limits for uploads; no pagination.

**Verification:** Identify all data storage and user-triggered operations → check for cleanup strategy, performance budgets, size limits.

**Auto-resolve:** If STANDARDS.md defines defaults (e.g., "LRU eviction, max 100 entries") → apply those.

**Block message:** see [templates/block-messages.md](templates/block-messages.md) — Pattern 10.

## Workflow

1. **Read ticket** — Identify purpose, scope, dependencies, assumptions, open questions, success criteria, test strategy.
2. **Check STANDARDS.md** — Before blocking, check `./STANDARDS.md` and `~/.skills/STANDARDS.md`. If answered → auto-resolve.
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

## Auto-Resolved via STANDARDS.md
- [Question X]: Applied STANDARDS.md section [Y]

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
[ ] STANDARDS.md checked for each open question
[ ] Evidence cited for each blocker (specific line/section)
[ ] Required actions are specific and actionable
[ ] Risk assessment completed
[ ] Escalation flagged if CRITICAL risks found
```

## Assumption Tiers

| Tier | Impact | Examples | Action |
|------|--------|----------|--------|
| 1: Reversible | LOW | Naming, file locations, UI copy, easy-migration libraries | Proceed, flag for post-review |
| 2: Architecture | MEDIUM | API patterns, data model, layer ownership | Check STANDARDS.md, block if unresolved |
| 3: Safety/Security | HIGH | Auth, data sensitivity, public API contracts | Always block for human confirmation |

## Ticket Shape & Implementation Readiness

When creating or auditing tickets (orchestrate + spec-writer alignment), ensure:

1. **YAML front matter** — `Stage:`, `Type`, `Order`, `Depends-On`, `Parent` per pipeline.
2. **Goal / Problem / Requirements / Acceptance criteria** — spec-writer style; traceability to files.
3. **Target files** — explicit list; **≤ 5 production files** per implementation ticket (see blast radius below).
4. **Verification (TDD)** — floor: project test suite; new tests when behavior changes.
5. **Ticket critic preflight** — this skill's 10 patterns + Stage gate.

## Blast Radius & Epic Split

- If implementation touches **> 5 production files**, split: `01a-ticket-slug.md`, `01b-…`, same directory.
- Set **parent** ticket to epic/tracker (`Stage: COMPLETE` when it only tracks children, per **orchestrate** skill).
- Children start **`Stage: NEW`** with their own target file lists.

## Strict TDD & Verification (BUILD-bound tickets)

When the ticket implies implementation:

- **TDD:** State explicitly: tests written first (red → green → refactor) unless docs/planning-only.
- **Frontend:** Mandate Playwright (or project E2E standard) for new/changed user-visible behavior.
- **Backend (Python):** pytest for contracts, I/O boundaries, happy + unhappy paths.
- **Other stacks:** Name the actual test runner.
- **Verification section:** Concrete commands (e.g., `pytest tests/ -q`, `npx playwright test`) plus linters/typecheck.
- **Self-review (pre-REVIEW):** DRY, maintainability, boundaries per QUALITY_RUBRIC.md; no unjustified god files.
- **Principal staff lens:** Prioritize code deletion and pragmatic modularity; unify scattered AI patterns into one predictable standard per concern.

## Integration & Reference Files

- **Integration with other skills:** See [reference/integration.md](reference/integration.md)
- **Super-prompts (harden tickets, generate new tickets):** See [reference/super-prompts.md](reference/super-prompts.md)
- **Block message templates:** See [templates/block-messages.md](templates/block-messages.md)
- **Audit finding examples:** See [examples/audit-findings.md](examples/audit-findings.md)

## Maintenance

**Update this skill when:** New blocking pattern identified; STANDARDS.md structure changes; audit process refined.

**Metrics to track:** Blocker detection rate; false positive rate; auto-resolution rate.
