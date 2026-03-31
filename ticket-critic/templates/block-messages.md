# Block Message Templates

Use these templates when blocking a ticket. Replace bracketed placeholders with specific values.

## Stage Header Gate (lines 51-64)

```markdown
❌ BLOCKED: Missing or Invalid Stage Header

Issue: Ticket is missing canonical `Stage:` field (or value is outside allowed enum).

Required before Task 1:
- [ ] Patch ticket header using [$spec-writer](/Users/joshc/.skills/spec-writer/SKILL.md)
- [ ] Add canonical YAML header with an allowed stage value
- [ ] If implementation-ready, set exactly `Stage: BUILD`

Allowed enum: `NEW | SPEC | SPEC_SPLIT | PLAN | BLOCKED | BUILD | REVIEW | COMPLETE | FAILED`
```

## Pattern 1: Unimplemented Dependencies (lines 91-102)

```
❌ BLOCKED: Unimplemented Dependency

Issue: Ticket assumes [X] exists, but [X] is [not started / in progress / not merged / no stable API]

Required before Task 1:
- [ ] Dependency merged and stable, OR
- [ ] API contract defined and agreed, OR
- [ ] Task 0 added: "Implement [X]" or "Define API contract for [X]"

Evidence: [specific line/section in ticket that assumes existence]
```

## Pattern 2: Architecture Contradictions (lines 125-136)

```
❌ BLOCKED: Architecture Contradiction

Issue: This ticket says [X], but [Ticket Y / STANDARDS.md] says [not-X]

Required before Task 1:
- [ ] Coordinating ticket resolves contradiction, OR
- [ ] Architectural decision documented in STANDARDS.md, OR
- [ ] One ticket marked authoritative, others updated/withdrawn

Evidence: This ticket line [N] vs [Ticket Y line M / STANDARDS.md section]
```

## Pattern 3: Scope Gaps (lines 159-175)

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

## Pattern 4: Unverified Assumptions (lines 199-213)

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

## Pattern 5: Security Vulnerabilities (lines 238-255)

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

## Pattern 6: Missing Decisions (lines 278-293)

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

## Pattern 7: Unclear Success Criteria (lines 317-334)

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

## Pattern 8: Missing Tests (lines 358-374)

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

## Pattern 9: Layer Confusion (lines 398-414)

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

## Pattern 10: Resource Concerns (lines 440-457)

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
