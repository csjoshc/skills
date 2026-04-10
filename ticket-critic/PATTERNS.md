# Ticket-Critic Pattern Library

## Contents

- Pattern scoring rubric
- Pattern 1: Unimplemented dependencies
- Pattern 2: Architecture contradictions
- Pattern 3: Scope gaps
- Pattern 4: Unverified assumptions
- Pattern 5: Security vulnerabilities
- Pattern 6: Missing decision points
- Pattern 7: Unclear success criteria
- Pattern 8: Missing tests and verification
- Pattern 9: Layer and architecture confusion
- Pattern 10: Resource and performance blind spots

## Pattern Scoring Rubric

For each pattern, assign one of:

- `PASS`: No blocker found.
- `AUTO-RESOLVED`: Question was answered by `~/.skills/STANDARDS.md` or local `./STANDARDS.md`.
- `BLOCKER`: Must be resolved before `Stage: BUILD` execution starts.

Every `BLOCKER` finding must include evidence.

## Pattern 1: Unimplemented Dependencies

**Check:** Ticket assumes services/endpoints/jobs/features that are missing or unstable.

**Red flags:**
- "Already implemented" with no commit/PR reference
- API dependency with no contract
- Dependency ticket still in progress

**Verification:**
1. List explicit dependencies in the ticket.
2. Verify each dependency in codebase or merged PRs.
3. If missing, require merge, contract, or explicit Task 0.

**Block template:**
```markdown
❌ BLOCKED: Unimplemented Dependency

Issue: Ticket assumes [X] exists, but [X] is not merged/stable.

Required before Task 1:
- [ ] Merge dependency, OR
- [ ] Define stable API contract, OR
- [ ] Add Task 0 to implement/verify dependency

Evidence: [ticket line/section + verification result]
```

## Pattern 2: Architecture Contradictions

**Check:** Ticket conflicts with approved architecture decisions or related tickets.

**Red flags:**
- Conflicting implementation directions for same subsystem
- Contradiction with STANDARDS architecture sections
- Multiple tickets changing same layer with incompatible strategy

**Verification:**
1. Identify overlapping tickets and target files.
2. Check `STANDARDS.md` architecture decisions.
3. Require a single authoritative direction when conflict exists.

## Pattern 3: Scope Gaps

**Check:** Required functionality for end-to-end flow is marked out of scope.

**Red flags:**
- Critical backend work marked out of scope for frontend feature
- Required UI/API contract steps omitted
- Security considerations excluded for untrusted input paths

**Verification:**
1. Trace full user flow from trigger to result.
2. Mark each step in-scope or out-of-scope.
3. Block if any mandatory step is missing from scope.

## Pattern 4: Unverified Assumptions

**Check:** Ticket assumes current system behavior without evidence.

**Red flags:**
- "Field already exists" with no schema reference
- "MSW already configured" with no config evidence
- "Pattern already used" with no file link

**Verification:**
1. Extract assumptions from ticket text.
2. Attach file/test evidence for each assumption.
3. Require Task 0 verification for critical assumptions.

## Pattern 5: Security Vulnerabilities

**Check:** Design introduces security risk without mitigation.

**Red flags:**
- User input reaches privileged operations without validation
- Path traversal or arbitrary file access risk
- Missing authz/authn constraints for protected operations
- Missing abuse/rate limiting for exposed endpoints

**Verification:**
1. Identify untrusted input touchpoints.
2. Identify validation, authorization, and containment controls.
3. Block if controls are absent or unspecified.

## Pattern 6: Missing Decision Points

**Check:** Ticket contains unresolved "TBD" or open questions that block implementation.

**Red flags:**
- Open architecture choice with no owner/decision date
- Undefined third-party integration behavior
- Undecided schema or API contract

**Verification:**
1. Collect open questions.
2. Check if resolved in STANDARDS.
3. If unresolved and non-trivial, block for decision.

## Pattern 7: Unclear Success Criteria

**Check:** Acceptance criteria are non-binary or non-testable.

**Red flags:**
- "Works correctly" style criteria
- Missing observable verification conditions
- Missing unhappy-path requirements
- Ticket carries `[FALLIBLE_IO]` tag but no AC specifies failure behavior →
  auto-escalate to BLOCKER

**Verification:**
1. Convert AC to explicit pass/fail behavior.
2. Require measurable outputs and edge cases.
3. Block if criteria remain subjective.

## Pattern 8: Missing Tests and Verification

**Check:** Ticket changes behavior but omits validation strategy.

**Red flags:**
- No test plan for public API changes
- No regression checks for refactor-heavy ticket
- No command-level verification evidence

**Verification:**
1. Require minimum test strategy by layer impacted.
2. Require verification commands and expected results.
3. Block if verification is absent.

## Pattern 9: Layer and Architecture Confusion

**Check:** Responsibilities are mixed across layers.

**Red flags:**
- Domain logic in infrastructure boundary files
- API/controller logic mixed into persistence modules
- Missing ownership boundaries in tasks

**Verification:**
1. Map each task to architecture layers.
2. Compare against architecture decisions.
3. Block if ownership boundaries are ambiguous.

## Pattern 10: Resource and Performance Blind Spots

**Check:** Ticket ignores scalability, latency, memory, or throughput risks.

**Red flags:**
- Unbounded queries or loops
- No pagination or limits for list endpoints
- No timeout/retry/backoff rules for network boundaries
- Ticket carries `[FALLIBLE_IO]` tag but spec has no `## Failure Paths`
  section → auto-escalate to BLOCKER

**Verification:**
1. Identify potential unbounded operations.
2. Require limits, constraints, and failure handling.
3. Block if high-risk performance paths are unaddressed.

