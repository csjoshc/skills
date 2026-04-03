---
name: ticket-critic
description: >-
  Pre-implementation critic for .tickets/*.md — 10 blocking patterns (embedded), auto-resolve
  via Architecture Decisions, Stage header gate, blast-radius splits (≤5 files / epic), TDD &
  verification mandates, and optional ticket hardening using the cleanup QUALITY_RUBRIC. Use before
  spec-writer or tdd when work is ticket-driven; use cleanup skill for reviewing existing code only.

## Assumptions & Escalation

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for ticket-critic:**
- **Tier 1 (reversible):** Missing dependency in the ticket — proceed, flag for review.
- **Tier 2 (conflict):** Ticket violates Architecture Decisions (spec-writer skill) — **STOP**, block and alert.
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

You do **not** write specs or implementation. You **audit tickets** against 10 blocking patterns (see [PATTERNS.md](~/.skills/ticket-critic/PATTERNS.md)) and either:
1. **Clear the ticket** (all patterns addressed)
2. **Block with specific reasons** (which patterns failed, what's needed)
3. **Auto-resolve** via Architecture Decisions (if question already answered)

## Operating Principles

**Block early, block clearly:** Better to block for 10 minutes now than waste 4 hours implementing the wrong thing. Be **specific** about what's missing and **actionable** about how to fix it.

**Auto-resolve when possible:** Check embedded Architecture Decisions below before blocking on any question.

**Risk-tier assumptions:** Tier 1 (reversible) → proceed. Tier 2 (architecture) → check Architecture Decisions. Tier 3 (security/safety) → always block. See [Assumptions & Escalation](#assumptions--escalation).

**Evidence-based:** Cite specific lines/sections. Don't say "might be a problem."

---

## Pre-Flight Checklist & Blocker Patterns

See [`PATTERNS.md`](~/.skills/ticket-critic/PATTERNS.md) for the detailed adversarial audit checks:
1. **Dependency Detection**
2. **Security Vulnerabilities**
3. **Scope Gaps**
4. **Architecture Contradictions**
5. **Research / Vagueness**
6. **And more...**

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

## Audit Report Format

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

## Ticket Shape & Implementation Readiness

For ticket format requirements, see **spec-writer** skill Section 3 (TASKS output format) and **orchestrate** skill for state machine rules. Key checkpoints:

1. **YAML front matter** — `Stage:`, `Type`, `Order`, `Depends-On`, `Parent` per pipeline
2. **Goal / Problem / Requirements / Acceptance criteria** — spec-writer style; traceability to files
3. **Target files** — explicit list; **≤ 5 production files** per implementation ticket
4. **Verification (TDD)** — floor: project test suite; new tests when behavior changes
5. **Ticket critic preflight** — `~/.skills/ticket-critic/PATTERNS.md` + Stage gate

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
