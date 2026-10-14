# E2E Validation Gap (The Hidden Blocker)

## Contents

- The failure pattern
- How to detect the gap
- Bug classification framework
- Minimal Reproducible Artifact (MRA) strategy
- Required remediation

A ticket can pass all unit tests and still fail when run through a complex pipeline
(orchestration, deployment, integration).
This gap is not a bug in the ticket; it's a systems-level correctness issue that
must be caught **before** handoff to implementation.

## The Failure Pattern

- Thousands of unit tests pass locally ✓
- Single real ticket fails in pipeline ✗
- Root cause: Infrastructure assumptions (state, initialization, contracts), not application logic

## How to Detect the Gap

Audit the ticket's test strategy:

1. **Are there E2E tests that run the ticket through the full pipeline?**
   - If no: **WARN**. Unit tests verify implementation; they don't verify system-level correctness.
   - If yes: Ask — are they run on realistic conditions (branches, state, dependencies)?
     Are they testing actual artifacts or mocks?

2. **Classify test coverage:**

   | Coverage Type | What It Validates | When It Fails |
   |---|---|---|
   | Unit tests | Implementation logic in isolation | Never catches infrastructure issues |
   | Integration tests (local) | Multiple modules together | Never catches pipeline constraints |
   | E2E tests (real pipeline) | Full artifact through system | Catches infrastructure + integration + state bugs |

3. **If this is a first-time pipeline ticket (e.g., smoke test):**
   - Declare it as such in the ticket body: `<!-- SMOKE TEST: validates E2E pipeline -->`
   - Require a minimal implementation (10–20 lines of code max)
   - Ensure acceptance criteria test against the real system, not stubs

## Bug Classification Framework

When volume (many tests) conflicts with quality (single ticket fails):

| Bug Type | Indicator | Root Cause | Fix Owner |
|----------|-----------|-----------|-----------|
| **Application-level** | Fails in isolated unit test; fails locally | Implementation error | Builder/Developer |
| **Integration-level** | Passes unit tests; fails local integration test | Module contract mismatch | Architect/Developer |
| **Infrastructure-level** | Passes local tests; fails in real pipeline | State not initialized, contracts broken, assumptions violated | Architect/Infrastructure |

**Key insight:** If a ticket passes all *local* tests but fails in the *real* pipeline, the
root cause is infrastructure, not application code.

## Minimal Reproducible Artifact (MRA) Strategy

When debugging pipeline failures:

1. Create the **simplest possible ticket** that exercises the same failure mode
   - Minimal code (10–20 lines)
   - Minimal dependencies
   - Isolated to a single concern

2. Run it through the **real pipeline** (not unit tests or stubs)

3. Classify the result:
   - **Fails in MRA**: Root cause is infrastructure/system-level. Fix there first.
   - **Passes in MRA, fails in complex ticket**: Root cause is interaction/state. Debug systematically.
   - **Both pass**: Root cause may be load, timing, or environmental. Escalate.

4. After infrastructure is proven correct, re-run the full ticket suite.

## Required Remediation

If a ticket lacks E2E validation strategy:

- [ ] Document whether this is a smoke test or a regular feature ticket
- [ ] If regular: list any existing E2E tests. If none exist, escalate for architecture review.
- [ ] If smoke test: ensure the implementation is minimal and acceptance criteria test against the real system
- [ ] If this is the first ticket of a new feature area: require it to be an MRA (minimal) to prove the pipeline infrastructure works before scaling to complexity
