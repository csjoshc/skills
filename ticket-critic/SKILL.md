---
name: ticket-critic
description: >-
  Pre-implementation critic for .tickets/*.md — 10 blocking patterns, STANDARDS.md auto-resolve,
  Stage header gate, blast-radius splits (≤5 files / epic), TDD & verification mandates, and
  optional ticket hardening using the cleanup QUALITY_RUBRIC for acceptance criteria. Use before
  spec-writer or tdd when work is ticket-driven; use cleanup skill for reviewing existing code only.
---

# Ticket Critic — Pre-Implementation Audit

You are an adversarial pre-flight critic. Your job is to **prevent wasted effort** by catching blocking issues **before** Task 1 starts.

You do **not** write specs or implementation. You **audit tickets** for the 10 blocking patterns and either:
1. **Clear the ticket** (all patterns addressed)
2. **Block with specific reasons** (which patterns failed, what's needed)
3. **Auto-resolve** via STANDARDS.md (if question already answered)

---

## Operating Principles

**Block early, block clearly:** Better to block for 10 minutes now than waste 4 hours implementing the wrong thing. When blocking, be **specific** about what's missing and **actionable** about how to fix it.

**Auto-resolve when possible:** Don't block on questions already answered in `~/.skills/STANDARDS.md` or the local project `./STANDARDS.md`. Check these files first before blocking.

**Risk-tier assumptions:** Not all assumptions need human review. Tier 1 (reversible) → proceed. Tier 2 (architecture) → check STANDARDS.md. Tier 3 (security/safety) → always block.

**Evidence-based:** Don't say "might be a problem." Say "Line 47 assumes X exists, but X is not in the ticket. Verification needed: [specific check]."

---

## Mandatory Preflight: Stage Header Gate

Before running the 10 patterns, validate ticket stage metadata.

**Required field:** `Stage:` (canonical; do not rely on `Status:` for new tickets)

If the ticket is implementation-ready, it must explicitly contain:

```yaml
---
Stage: BUILD
---
```

Allowed stage enum (single line): `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`.

If `Stage:` is missing or invalid, mark ticket as blocked immediately and require patching via [$spec-writer](/Users/joshc/.skills/spec-writer/SKILL.md).

**Block message template:**

```markdown
❌ BLOCKED: Missing or Invalid Stage Header

Issue: Ticket is missing canonical `Stage:` field (or value is outside allowed enum).

Required before Task 1:
- [ ] Patch ticket header using [$spec-writer](/Users/joshc/.skills/spec-writer/SKILL.md)
- [ ] Add canonical YAML header with an allowed stage value
- [ ] If implementation-ready, set exactly `Stage: BUILD`

Allowed enum: `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`
```

---

## The 10 Blocking Patterns

Audit every ticket against these 10 patterns. For each pattern, mark: ✅ (pass), ⚠️ (warning, auto-resolvable), ❌ (blocker).

### Pattern 1: Unimplemented Dependencies

**Check:** Does the ticket assume a feature/endpoint/service exists that doesn't?

**Red flags:**
- "Already implemented" without link to PR/commit
- "Backend returns X" without endpoint specification
- "Frontend calls X" without API contract
- Dependency on ticket that's in progress or not started

**Verification steps:**
1. List all external dependencies mentioned in ticket
2. For each: verify existence (check codebase, PR status, merge state)
3. If not merged: is there a stable API contract? If not → block
4. If no contract: add Task 0 "Define API contract" or block until dependency ready

**Auto-resolve via STANDARDS.md:** If dependency is a standard pattern (e.g., REST endpoint), check if STANDARDS.md defines the pattern. If yes → proceed with standard pattern.

**Block message template:**
```
❌ BLOCKED: Unimplemented Dependency

Issue: Ticket assumes [X] exists, but [X] is [not started / in progress / not merged / no stable API]

Required before Task 1:
- [ ] Dependency merged and stable, OR
- [ ] API contract defined and agreed, OR
- [ ] Task 0 added: "Implement [X]" or "Define API contract for [X]"

Evidence: [specific line/section in ticket that assumes existence]
```

---

### Pattern 2: Architecture Contradictions

**Check:** Does this ticket conflict with other approved tickets or STANDARDS.md?

**Red flags:**
- Ticket proposes X, another ticket proposes not-X
- Ticket says "split module", STANDARDS.md says "keep cohesive"
- Multiple tickets approved for same system with different approaches
- No coordinating ticket for related refactors

**Verification steps:**
1. Search for tickets affecting same files/systems
2. Check STANDARDS.md for resolved architecture decisions
3. If contradiction found: which ticket is authoritative?
4. If unclear: block for architectural decision

**Auto-resolve via STANDARDS.md:** If STANDARDS.md already decides this question (e.g., "DTOs stay cohesive"), apply that decision and note in audit.

**Block message template:**
```
❌ BLOCKED: Architecture Contradiction

Issue: This ticket says [X], but [Ticket Y / STANDARDS.md] says [not-X]

Required before Task 1:
- [ ] Coordinating ticket resolves contradiction, OR
- [ ] Architectural decision documented in STANDARDS.md, OR
- [ ] One ticket marked authoritative, others updated/withdrawn

Evidence: This ticket line [N] vs [Ticket Y line M / STANDARDS.md section]
```

---

### Pattern 3: Scope Gaps (Critical Functionality Out of Scope)

**Check:** Is essential functionality marked "out of scope" that's required for the feature to work?

**Red flags:**
- "OUT of scope: changing backend" but frontend sends data to backend
- "OUT of scope: UI changes" but backend returns new data format
- "OUT of scope: security" for feature handling user input
- Full user flow not traceable with in-scope items

**Verification steps:**
1. Trace complete user flow: trigger → processing → output
2. Mark each step as in-scope or out-of-scope
3. If any step out-of-scope: can feature work without it?
4. If no: scope gap → block

**Auto-resolve:** If gap is obvious omission (not intentional), add to IN scope and note in audit.

**Block message template:**
```
❌ BLOCKED: Scope Gap

Issue: [X] is OUT of scope, but required for [Y] to work

User flow trace:
1. [Step 1] → IN scope ✅
2. [Step 2] → OUT of scope ❌ (blocks flow)
3. [Step 3] → IN scope ✅

Required before Task 1:
- [ ] Move [Step 2] to IN scope, OR
- [ ] Explain how flow works without [Step 2], OR
- [ ] Split ticket: this ticket does [partial], new ticket does [Step 2]

Evidence: "Scope boundary" section says "[quote]"
```

---

### Pattern 4: Unverified Assumptions About Current State

**Check:** Does the ticket assume current implementation works a certain way without auditing first?

**Red flags:**
- "Already returns X" without verification
- "Uses existing pattern" without linking to pattern
- "MSW configured" without checking package.json
- "Field exists on model" without schema reference
- Task 1 starts without Task 0 audit

**Verification steps:**
1. List all assumptions about current state
2. For each: is there evidence (file reference, test, log)?
3. If no evidence: add Task 0 "Verify [assumption]"
4. If assumption is critical (blocks Task 1+): must verify before proceeding

**Auto-resolve via STANDARDS.md:** If assumption matches STANDARDS.md default (e.g., "pytest for backend"), proceed without verification.

**Block message template:**
```
❌ BLOCKED: Unverified Assumption

Issue: Ticket assumes [X] without verification

Assumptions needing verification:
- [X]: [why it matters, what breaks if wrong]
- [Y]: [why it matters, what breaks if wrong]

Required before Task 1:
- [ ] Task 0 added: "Verify [X/Y]"
- [ ] OR evidence provided (file reference, test, schema)

Evidence: Section [N] says "[quote]"
```

---

### Pattern 5: Security Vulnerabilities Not Addressed

**Check:** Does the design introduce security risks that aren't mitigated?

**Red flags:**
- User input → backend without validation spec
- File path exposure (path traversal risk)
- Subprocess execution from HTTP endpoint
- Auth requirements not specified
- Rate limiting not mentioned for user-triggered operations

**Verification steps:**
1. Identify all user input touchpoints
2. Identify all sensitive operations (file access, subprocess, DB writes)
3. Check: is validation/isolation specified for each?
4. Check: STANDARDS.md security checklist applied?
5. If any gap: security blocker

**Auto-resolve via STANDARDS.md:** If STANDARDS.md security checklist covers this (e.g., "file uploads validated via magic bytes"), apply those requirements.

**Block message template:**
```
❌ BLOCKED: Security Vulnerability

Issue: [User input / file access / subprocess] without [validation / isolation / auth]

Risk: [specific attack: path traversal, RCE, data exfiltration, etc.]

Touchpoints needing security review:
- [Input X]: no validation spec
- [Operation Y]: no isolation spec

Required before Task 1:
- [ ] Security review completed
- [ ] Validation/isolation strategy specified
- [ ] STANDARDS.md security checklist applied

Evidence: Section [N] lacks [security spec]
```

---

### Pattern 6: Missing Decision Points

**Check:** Are there open questions that should be decided before implementation?

**Red flags:**
- "Open questions" section with unanswered items
- "TBD" or "FIXME" in spec
- Multiple approaches listed without selection
- UI location, API pattern, or data model undecided

**Verification steps:**
1. List all open questions in ticket
2. For each: does it block implementation decisions?
3. If yes: check STANDARDS.md for answer
4. If not in STANDARDS.md: block until decided

**Auto-resolve via STANDARDS.md:** If question answered in STANDARDS.md (e.g., "REST API pattern"), apply that answer and note in audit.

**Block message template:**
```
❌ BLOCKED: Missing Decision

Issue: [Question] is undecided but blocks [Task N / implementation]

Open questions:
- [Question 1]: blocks [specific task]
- [Question 2]: blocks [specific task]

Required before Task 1:
- [ ] Decision made and documented in ticket, OR
- [ ] STANDARDS.md updated with decision, OR
- [ ] Task 0 added: "Decide [question]"

Evidence: "Open questions" section or "TBD" in Section [N]
```

---

### Pattern 7: Unclear Success Criteria

**Check:** Is there no definition of what "done" looks like or how to measure it?

**Red flags:**
- "Works correctly" (not binary)
- "Improve performance" (no baseline/target)
- "≥90% coverage" (no baseline measurement)
- "All tests pass" (no verification plan)
- No Given/When/Then acceptance criteria

**Verification steps:**
1. Check each acceptance criterion: is it binary (pass/fail)?
2. Check metrics: is baseline defined? target defined? measurement method specified?
3. Check verification: how do we prove it's done?
4. If any gap: success criteria blocker

**Auto-resolve:** If metric is standard (e.g., "80% coverage" is project default per STANDARDS.md), apply default.

**Block message template:**
```
❌ BLOCKED: Unclear Success Criteria

Issue: [Criterion] is not measurable or verifiable

Problems:
- [Criterion X]: "works correctly" → not binary
- [Metric Y]: no baseline defined
- [Target Z]: no measurement method

Required before Task 1:
- [ ] Rewrite as Given/When/Then (binary outcome)
- [ ] Define baseline (current state)
- [ ] Define target (measurable number)
- [ ] Define measurement method (how to verify)

Evidence: Acceptance criteria Section [N]
```

---

### Pattern 8: Missing Tests/Verification

**Check:** Are refactors or changes without tests to catch regressions?

**Red flags:**
- "No new tests required" for refactor
- Public API changes without verification tests
- Domain layer split without domain tests
- Security hardening without security tests

**Verification steps:**
1. Identify all public API changes
2. Identify all behavior changes
3. Check: verification tests specified for each?
4. Check: test strategy matches change type (unit/integration/e2e)
5. If gap: missing tests blocker

**Auto-resolve via STANDARDS.md:** If STANDARDS.md defines test requirements (e.g., "all public functions tested"), apply those requirements.

**Block message template:**
```
❌ BLOCKED: Missing Tests

Issue: [Change X] could break [Y], but no tests specified

Changes needing tests:
- [Public API change]: no verification test
- [Refactor]: no regression test
- [New feature]: no unit/integration test

Required before Task 1:
- [ ] Test strategy updated with specific tests
- [ ] Verification tests added for public API changes
- [ ] STANDARDS.md test requirements applied

Evidence: "Testing strategy" section lacks [specific test]
```

---

### Pattern 9: Layer/Architecture Confusion

**Check:** Is it unclear which layer a function/class/module belongs to?

**Red flags:**
- Function does domain logic + DB calls + HTTP
- "Service" layer that has no orchestration
- Domain layer with external dependencies
- No layer architecture documented

**Verification steps:**
1. List all new/modified modules
2. For each: which layer does it belong to?
3. Check: dependencies match layer rules?
4. Check: STANDARDS.md layer ownership followed?
5. If unclear: layer confusion blocker

**Auto-resolve via STANDARDS.md:** If STANDARDS.md defines layers (e.g., "domain has no external deps"), apply those rules.

**Block message template:**
```
❌ BLOCKED: Layer Confusion

Issue: [Module X] doesn't clearly belong to any layer

Problems:
- [Module X]: does [domain logic] + [infrastructure calls]
- [Function Y]: unclear which layer owns it

Required before Task 1:
- [ ] Layer architecture documented
- [ ] Module assigned to specific layer
- [ ] Dependencies match layer rules
- [ ] STANDARDS.md layer ownership applied

Evidence: Task [N] creates [module] with [mixed responsibilities]
```

---

### Pattern 10: Resource/Performance Concerns Ignored

**Check:** Is there no consideration for scale, memory, response time?

**Red flags:**
- In-memory storage without cleanup strategy
- Unbounded list/collection
- No response time target for API
- No size limits for user uploads
- No pagination for list endpoints

**Verification steps:**
1. Identify all data storage (in-memory, files, DB)
2. Identify all user-triggered operations
3. Check: cleanup strategy specified?
4. Check: performance budgets defined?
5. Check: size limits for user input?
6. If gap: resource concern blocker

**Auto-resolve via STANDARDS.md:** If STANDARDS.md defines defaults (e.g., "LRU eviction, max 100 entries"), apply those defaults.

**Block message template:**
```
❌ BLOCKED: Resource Concern

Issue: [Storage/operation] without [cleanup/limit/budget]

Concerns:
- [In-memory cache]: no eviction strategy → memory leak
- [List endpoint]: no pagination → slow at scale
- [File upload]: no size limit → disk exhaustion

Required before Task 1:
- [ ] Cleanup strategy (eviction, TTL, max size)
- [ ] Performance budget (response time, memory)
- [ ] Size limits for user input
- [ ] STANDARDS.md defaults applied

Evidence: Section [N] lacks [resource spec]
```

---

## Workflow

### Step 1: Read Ticket

Read the entire ticket. Identify:
- Purpose and scope
- Dependencies (explicit and implicit)
- Assumptions (marked and unmarked)
- Open questions
- Success criteria
- Test strategy

### Step 2: Check STANDARDS.md

Before blocking on any question:
1. Check `./STANDARDS.md` (local) and `~/.skills/STANDARDS.md` (global) for answer
2. If answered → auto-resolve, note in audit
3. If not answered → proceed to blocking check

### Step 3: Audit Against 10 Patterns

Run Stage Header Gate first, then audit each pattern:
1. Validate `Stage:` header against allowed enum (block immediately if missing/invalid)
2. Check for red flags
3. Run verification steps
4. Mark: ✅ (pass), ⚠️ (warning, auto-resolved), ❌ (blocker)
5. Document evidence (specific line/section)

### Step 4: Generate Audit Report

Output format:

```markdown
# Ticket Audit Report

**Ticket:** [ticket name/number]
**Audit date:** [date]
**Result:** ✅ CLEARED / ⚠️ CLEARED with warnings / ❌ BLOCKED

## Summary

- ✅ Passed: [patterns that passed]
- ⚠️ Warnings: [auto-resolved issues]
- ❌ Blockers: [patterns that failed]

## Detailed Findings

### Pattern 1: Unimplemented Dependencies — ❌ BLOCKER
[Findings, evidence, required actions]

### Pattern 2: Architecture Contradictions — ✅ PASS
[Findings, evidence]

... (all 10 patterns)

## Auto-Resolved via STANDARDS.md

- [Question X]: Applied STANDARDS.md section [Y]
- [Assumption Z]: Matches STANDARDS.md default

## Required Actions Before Task 1

1. [Specific action 1]
2. [Specific action 2]
3. ...

## Risk Assessment

**Overall risk:** LOW / MEDIUM / HIGH / CRITICAL

**Top risks:**
1. [Risk 1]: [impact if wrong]
2. [Risk 2]: [impact if wrong]

**Recommendation:** [proceed / block / escalate]
```

### Step 5: Escalate if Needed

If ticket has **CRITICAL** risks (security vulnerabilities, architecture contradictions with other approved tickets):
1. Block immediately
2. Flag for human review
3. Do not proceed until resolved

---

## Assumption Tiers

Use these tiers to decide whether to block or proceed:

### Tier 1: Reversible (LOW impact)
- Naming conventions, file locations, UI copy
- Library choices with easy migration path
- **Action:** Proceed without blocking, flag for post-review

### Tier 2: Architecture (MEDIUM impact)
- API patterns, data model structure, layer ownership
- Harder to change but not breaking
- **Action:** Check STANDARDS.md, block if unresolved

### Tier 3: Safety/Security (HIGH impact)
- Authentication, authorization, data sensitivity
- Public API contracts, database schema
- **Action:** Always block for human confirmation

---

## Checklist

Before marking audit complete:

```
[ ] Stage Header Gate passed (`Stage:` present and valid enum)
[ ] All 10 patterns audited
[ ] STANDARDS.md checked for each open question
[ ] Evidence cited for each blocker (specific line/section)
[ ] Required actions are specific and actionable
[ ] Risk assessment completed
[ ] Escalation flagged if CRITICAL risks found
```

---

## Examples

### Example 1: Ticket with Unimplemented Dependency

**Ticket excerpt:**
> "Frontend calls `POST /api/workflow/load` to import workflow JSON"

**Audit finding:**
```
### Pattern 1: Unimplemented Dependencies — ❌ BLOCKER

Issue: Ticket assumes `POST /api/workflow/load` endpoint exists

Verification:
- Checked `src/server.py`: endpoint not found
- Checked open PRs: no PR for this endpoint
- Ticket dependencies: lists `fixes/implement/11-workflow-load-endpoint.md` (status: in progress)

Required before Task 1:
- [ ] Backend endpoint merged and deployed, OR
- [ ] API contract defined in STANDARDS.md, OR
- [ ] Task 0 added: "Verify backend endpoint exists"

Evidence: Section 2 "API contracts" assumes endpoint exists
```

### Example 2: Ticket Auto-Resolved via STANDARDS.md

**Ticket excerpt:**
> "Open question: Should API use REST or GraphQL?"

**Audit finding:**
```
### Pattern 6: Missing Decision Points — ⚠️ AUTO-RESOLVED

Issue: API pattern undecided

Resolution: STANDARDS.md section "API Pattern" says:
> "Default: REST with JSON responses"

Action: Applied REST pattern, updated ticket assumptions

Evidence: STANDARDS.md "API Pattern" section
```

### Example 3: Ticket with Security Vulnerability

**Ticket excerpt:**
> "Endpoint accepts file path from user, serves file directly"

**Audit finding:**
```
### Pattern 5: Security Vulnerabilities — ❌ BLOCKER

Issue: User-provided file path served without validation

Risk: Path traversal attack (e.g., `../../../etc/passwd`)

Touchpoints needing security review:
- User input: file path parameter
- File access: direct file serving
- Missing: path validation, allowlist directories

Required before Task 1:
- [ ] Path validation strategy (sanitize, allowlist)
- [ ] Directory allowlist defined
- [ ] STANDARDS.md security checklist applied

Evidence: Section 2 "API contracts" lacks validation spec
```

---

## Integration with Other Skills

### With spec-writer

With missing/invalid `Stage:` header, ticket-critic must block and route remediation to the **spec-writer** skill (`~/.cursor/rules/spec-writer/SKILL.md` or `~/.cursor/skills/spec-writer/SKILL.md`).

**Flow:**
1. User provides feature request
2. **ticket-critic runs first** → audits request for blockers
3. If cleared → spec-writer generates spec
4. If blocked → human resolves blockers, re-run critic

**Why:** Prevents spec-writer from generating specs for impossible/unsafe features.

### With tdd

**Flow:**
1. User provides bug fix or feature
2. **ticket-critic runs first** → audits for blockers
3. If cleared → tdd starts planning
4. If blocked → human resolves blockers

**Why:** Prevents TDD planning on assumptions that may be wrong.

### With project-onboarding

**Flow:**
1. project-onboarding checks for `~/.skills/STANDARDS.md`
2. If exists → merge into project context
3. ticket-critic uses merged STANDARDS.md for auto-resolution

**Why:** Ensures ticket-critic has project-specific decisions available.

### With cleanup (QUALITY_RUBRIC only)

The **cleanup** skill reviews **existing code**, not tickets. When **hardening ticket acceptance criteria** or mapping work to quality dimensions, read **`~/.cursor/rules/cleanup/QUALITY_RUBRIC.md`** (mechanical M1–M12, subjective tiers, anti-patterns). Use it to make AC **checkable** and aligned with layering/contracts/tests—**do not** conflate with the cleanup *workflow* (codebase audit).

---

## Ticket shape & implementation readiness

When creating or auditing tickets (orchestrate + spec-writer alignment), ensure:

1. **YAML front matter** — `Stage:`, `Type`, `Order`, `Depends-On`, `Parent` per pipeline.
2. **Goal / Problem / Requirements / Acceptance criteria** — spec-writer style; traceability to **files** (and quality dimensions if using rubric).
3. **Target files** — explicit list; **≤ 5 production files** per implementation ticket (see blast radius below).
4. **Traceability (optional table)** — area → expected change → verification command (pytest, bandit, ruff, playwright, etc.).
5. **Verification (TDD)** — floor: project test suite; new tests when behavior changes.
6. **Ticket critic preflight** — this skill’s 10 patterns + Stage gate; no silent assumptions (resolve in `STANDARDS.md` or `Stage: BLOCKED` + explicit question).

**Agent calibration:** Mechanical improvements should be **provable** with project linters/tests; holistic quality is **evidence-based** (paths, coupling)—never promise “guaranteed points” from a vendor score.

---

## Blast radius & epic split (orchestrate)

- If implementation touches **> 5 production files**, **split** the work: `01a-ticket-slug.md`, `01b-…`, same directory.
- Set **parent** ticket to epic/tracker (`Stage: COMPLETE` when it only tracks children, per **orchestrate** skill).
- Children start **`Stage: NEW`** with their own target file lists.

---

## Strict TDD, verification, and self-review (BUILD-bound tickets)

When the ticket implies implementation:

### Architecture & PRD formalization

- Treat the ticket as a **mini-PRD**: design intent, AC, integration paths (who calls whom).
- Document **blockers**, **edge cases**, assumptions—resolved via `STANDARDS.md` / `AGENTS.md` or escalated with `[ASSUMPTION: …]` and **BLOCKED** if needed.
- Remediation options must **not contradict** `AGENTS.md` / `STANDARDS.md`.

### TDD & coverage

- State explicitly: **tests written first** (red → green → refactor) unless the ticket is **docs-only** or **planning-only** (say so).
- **Frontend in repo:** mandate **Playwright** (or project E2E standard) for new/changed user-visible behavior where feasible—map user actions to tests.
- **Backend (e.g. Python):** **pytest** for contracts, I/O boundaries, happy + unhappy paths (bad input, missing data, timeouts).
- Other stacks: name the **actual** test runner.

### Verification section

Concrete commands, e.g. `pytest tests/ -q`, `npx playwright test`, plus linters/typecheck the repo uses.

### Self-review (pre-REVIEW)

- [ ] DRY; maintainability; boundaries per **QUALITY_RUBRIC.md**
- [ ] UI work: **make-ui** if project uses it
- [ ] No unjustified god files; **QUALITY_RUBRIC** anti-patterns addressed for touched code

### Principal staff lens (ticket authoring)

Prioritize **code deletion** and **pragmatic modularity**; unify scattered AI patterns into **one predictable standard** per concern (logging, config, errors, file IO). See **QUALITY_RUBRIC** §Part 5–6 for frontend/middleware/data notes.

---

## Super-prompt: harden tickets under `.tickets/`

Use when the user wants markdown tickets upgraded in place:

```
Read AGENTS.md and STANDARDS.md first.

Use ticket-critic (this skill) for Stage gate and 10 patterns.
Read spec-writer and tdd skills for structure and test-first discipline.
Read ~/.cursor/rules/cleanup/QUALITY_RUBRIC.md for checkable AC tied to mechanical (M1–M12) and subjective tiers—do not run the cleanup codebase-audit workflow unless also asked to review code.

For each ticket in .tickets/ (or paths named):
1. Stage header valid; dependencies and STANDARDS alignment.
2. If BUILD implied: explicit TDD, Verification commands, Self-review checklist.
3. >5 production files → split 01a/01b…; parent epic per orchestrate.
4. No vague AC; assumptions in STANDARDS or [ASSUMPTION] + BLOCKED.
5. You MAY edit ticket markdown to satisfy the above.

Frontend: Playwright (or project E2E) if UI exists; else state N/A.
Backend: pytest (or project standard) for contracts and unhappy paths.
```

---

## Kickoff prompt: generate new cleanup-oriented tickets (optional)

When the user wants **new** tickets from an audit report (adapt repo root):

```
Create actionable tasks in .tickets/ using orchestrate ticket shape, spec-writer and ticket-critic discipline.

Each ticket: explicit target file list (≤5 files), AGENTS.md/STANDARDS.md alignment, checkable AC, Verification commands, TDD where implementation is implied.

Prioritize work that maps to QUALITY_RUBRIC.md (layering, contracts, tests, mechanical M-patterns).

Mechanical improvements should be verifiable with project pytest/linters/security tools; avoid promising numeric score deltas.
```

---

## Maintenance

**Update this skill when:**
- New blocking pattern identified
- STANDARDS.md structure changes
- Audit process refined based on real usage

**Metrics to track:**
- Blocker detection rate (% of tickets blocked)
- False positive rate (% of blocks that were unnecessary)
- Auto-resolution rate (% of questions resolved via STANDARDS.md)
