---
name: tdd
description: "Red-green-refactor at agreed seams, including the Prove-It path for bugs. Use when building or fixing something test-first."
---

# Test-Driven Development (TDD)

## What a good test is

A good test checks behavior through a public interface and survives any refactor that keeps that behavior.
It reads like a spec: "user can checkout with valid cart" names a capability, not a mechanism.
Examples: [TESTS.md](TESTS.md).

## Anti-patterns

- **Implementation-coupled:** mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of the interface). The tell: a refactor with no behavior change breaks it.
- **Tautological:** the expected value is recomputed the way the code computes it (`expect(add(a, b)).toBe(a + b)`), so it passes by construction. Take expected values from an independent source: a known literal, a worked example, the spec.
- **Horizontal slicing:** all tests first, then all code. Bulk tests check imagined behavior and the shape of things, and you commit to test structure before you understand the code. Work in vertical slices: each test is a tracer bullet shaped by what the last cycle taught you.

More: [shared/TEST_ANTIPATTERNS.md](../shared/TEST_ANTIPATTERNS.md).

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it, with no speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactor only on green**, as its own phase after the slices pass, running tests after each step.

## Test paths, dry-run, commits

- **Write the test to its permanent path immediately.** Never use `tests/tickets/` (deprecated staging area). The ticket's AC→Test table names the path; otherwise follow the repo's existing test layout.
- **Dry-run is not completion proof.** Tests default to non-dry-run; see [DRY_RUN.md](DRY_RUN.md).
- **Commit only when the user asks**, at proven call-stack boundaries; see [COMMIT_DISCIPLINE.md](COMMIT_DISCIPLINE.md).

Fallback layout when the repo has no convention (project AGENTS.md wins):

| Test type | Permanent committed path |
|---|---|
| Dockerfile / Helm / nginx / CI workflow regression | `tests/infra/test_<artifact>.py` |
| Documentation consistency | `tests/docs/test_<topic>.py` |
| Package unit/integration | `packages/<pkg>/tests/test_<module>.py` |
| E2E | `tests/e2e/` |

## Workflow

Phase detail, discovery halt and bug-fix procedure: [WORKFLOW.md](WORKFLOW.md). Read it before Phase 1.

Pick the path first:

- **Bug fix** - skip to the Prove-It steps below. No TOQ.
- **No ticket** (ad-hoc feature or change) - skip Phase 0. List up to 5 behaviors to test, in order, in chat; start once the user confirms (or right away if they already said go). Nothing is written to `.tickets/`.
- **Ticket build** (a `.tickets/*.md` is in scope) - run every phase below.

0. **Scoping (ticket builds).** Load [SCOPING.md](SCOPING.md); it produces the ranked Test Obligation Queue (TOQ) at `.tickets/tdd/toq-<ticket-id>.yaml`. Signals are deterministic; the model only ranks and shapes. Reuse a fresh TOQ.
1. **Planning.** Present the TOQ (or the inline list) and have the user confirm, reprioritize or reject entries. Caps: top 5 unit, 3 integration, 1 e2e per ticket; the rest is deferred, not discarded.
2. **Tracer bullet.** Take the top TOQ entry, write ONE test for its `done_when`, make it pass.
3. **Incremental loop.** One TOQ entry at a time, in score order. While iterating, run only `TOQ[i].target` plus its `existing_tests`; run the full suite once at end of ticket, before Stage COMPLETE.
4. **Refactor** after all tests pass, running tests after each step. Candidates: [REFACTORING.md](REFACTORING.md).

One source file per cycle (plus its support set). If a cycle needs a second source file, stop and report; see the discovery halt in [WORKFLOW.md](WORKFLOW.md).

**Bug fixes:** write a test that reproduces the bug through the public interface. It MUST fail first; a passing reproduction is not a reproduction. Then fix, re-run, run the relevant suite. Steps: [WORKFLOW.md](WORKFLOW.md) (Prove-It pattern).

<!-- pattern: common-rationalizations -->
## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll add the test after the code works" | You won't. And tests written after the fact test implementation, not behavior. |
| "This change is too small to test" | Small changes accumulate. The test documents the expected behavior. |
| "Manual testing covered it" | Manual coverage doesn't persist. Tomorrow's change might break it silently. |
| "Mocking the DB is enough" | Mocked tests pass while real migrations fail. Integration > confidence. |

## Companion files

Read only when the situation matches:

- [SCOPING.md](SCOPING.md): Phase 0 for ticket builds, builds the TOQ
- [WORKFLOW.md](WORKFLOW.md): phase detail, one-file cycles, discovery halt, bug fixes
- [TESTS.md](TESTS.md): good/bad examples, red flags, naming, frontend and async/streaming patterns
- [TEST_CRAFT.md](TEST_CRAFT.md): FIRST, flaky tests, smells, coverage, doubles, integration/e2e, black-box techniques, pyramid
- [INTERFACE_DESIGN.md](INTERFACE_DESIGN.md): testable surfaces, interaction specs, Deps/Params/Payload, fractal companions
- [MOCKING.md](MOCKING.md) / [MOCK_CONTRACT.md](MOCK_CONTRACT.md): boundary mocks and canonical doubles; MOCK_CONTRACT is required when the red-step test introduces an external boundary mock
- [MUTATION.md](MUTATION.md): auto-fires at green for TOQ entries with `mutation_candidate: true` (T1 + score > 60); optional otherwise
- [REFACTORING.md](REFACTORING.md): the refactor step after green
- [CI_CD.md](CI_CD.md): running tests locally or in CI
- [DRY_RUN.md](DRY_RUN.md): a test or run uses dry-run mode
- [COMMIT_DISCIPLINE.md](COMMIT_DISCIPLINE.md): committing finished work

Good-test, anti-pattern and loop rules adapted from mattpocock/skills (MIT).
