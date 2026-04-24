# Testing as a design signal

Not coverage. The testability properties of a codebase are an
architectural signal: hard-to-test code has a design problem, not a
test problem. These smells surface when tests are present but the
shape of the tests reveals that the system is over-coupled,
over-mocked, or silent about its failure modes.

## Contents

- Smells
- Proof recipes
- Few-shot: good finding
- Few-shot: good dismissal
- Decidable-at matrix

---

## Smells (4)

### Behavior untestable without mocking the world

**Shape (language-agnostic):** A unit test for one behavior must
stand up or mock five-plus collaborators, inject fakes for unrelated
subsystems, or patch global state to run at all. The unit has too
many implicit dependencies for the behavior it owns.

**Decidable at:** `diff`

**Why it compounds:** Refactors break tests even when behavior is
unchanged, because the tests encode the dependency graph rather than
the behavior. Each new feature adds another collaborator; setup grows
without bound until the test file is unreadable.

**Category mapping:** `category: Test Gap` / severity `MEDIUM` /
`rule_code: ARCH-TEST-MOCK-WORLD`

---

### Tests assert implementation, not behavior

**Shape (language-agnostic):** Tests verify that a specific internal
call was made (mock-assertion on a collaborator), in a specific order,
with specific arguments that duplicate the implementation. Any refactor
that preserves behavior but changes the internal structure breaks the
tests.

**Decidable at:** `diff`

**Why it compounds:** The test suite becomes a change-preventer rather
than a safety net. Engineers avoid refactors because "the tests will
break," entrenching the original shape even when it's wrong.

**Category mapping:** `category: Test Gap` / severity `MEDIUM` /
`rule_code: ARCH-TEST-IMPL-ASSERT`

---

### Integration boundaries asserted only in unit tests with mocks

**Shape (language-agnostic):** The contract between the system and an
external dependency (vendor API, message broker, database) is
exercised only in unit tests where the dependency is mocked. No
end-to-end or contract test verifies the real interface. The mock is
a fiction that can silently drift from reality.

**Decidable at:** `both` — /antiplan should require a contract or
end-to-end test at every external-dependency boundary.

**Why it compounds:** The vendor changes a field name, an error
code, or a timing semantic — the unit tests stay green because the
mock is unchanged, and the break ships to production. Each new
integration inherits the "mock-only" pattern.

**Category mapping:** `category: Test Gap` / severity `MEDIUM` /
`rule_code: ARCH-TEST-MOCK-CONTRACT`

---

### No test covers the failure path at a critical boundary

**Shape (language-agnostic):** A payment flow, webhook consumer, auth
handler, or other critical path has tests for the happy path only.
Timeout, duplicate delivery, malformed payload, downstream-error — none
of these are asserted against. Failures only surface in production
incidents.

**Decidable at:** `both` — /antiplan should enumerate failure modes
to test for any critical path.

**Why it compounds:** An incident reveals a missing failure-path
test; the fix ships; three months later a neighbor of that code path
repeats the same pattern. Absent an explicit policy, happy-path-only
coverage is the default.

**Category mapping:** `category: Test Gap` / severity `MEDIUM` (HIGH if
the boundary is money/auth/data) / `rule_code: ARCH-TEST-NO-FAILURE-PATH`

---

## Proof recipes

| Smell | Proof recipe |
| --- | --- |
| Mocking the world | `rg -nc "mock\|patch\|Mock\(\|jest\.mock" <test-file>` showing mock count per test > ~3; OR setup/fixture size > ~50 lines for a single behavior assertion. |
| Implementation-not-behavior asserts | `rg -n "assert_called_with\|toHaveBeenCalledWith\|verify\(" <tests>/` cross-referenced with absence of output/state assertions on the same test. |
| Mock-only integration boundary | `rg -l "<vendor-sdk>\|<external-url>" tests/` showing no `tests/integration/\|tests/contract/` directory; OR CI config showing no job runs against a real or record/replay instance of the dependency. |
| No failure-path coverage | Test-file diff-coverage on a critical file showing 100% of new tests exercise success cases; OR `rg -n "raises\|throws\|to\.reject\|expect.*Error" <critical-tests>/` returning zero. |

Prose alone never satisfies proof.

---

## Few-shot: good finding

````markdown
```REVIEW-FINDINGS
- id: F-001
  category: Test Gap
  lens: testing-as-design
  file: tests/services/test_checkout.py
  line: 1
  rule_code: ARCH-TEST-NO-FAILURE-PATH
  severity: HIGH
  source: lens-derived
  decidable_at: diff
  checklist_score: 4/5
  status: VALIDATED
  evidence: |
    tests/services/test_checkout.py covers 6 cases, all asserting
    successful checkout against various cart shapes. There is no test
    for: payment-gateway timeout, payment-gateway decline, duplicate
    webhook delivery, inventory-reservation failure mid-checkout. The
    production handler catches these and continues; no test asserts
    what the caller sees on failure.
  proof: |
    $ rg -n "raises|pytest.raises|assertRaises" tests/services/test_checkout.py
    → 0 matches.
    $ rg -n "timeout|decline|duplicate|reservation.*fail" tests/services/test_checkout.py
    → 0 matches.
    Incident INC-2031 (2026-03-14) was a production outage rooted in
    payment-gateway-timeout behavior that these tests do not exercise.
  suggested_fix: |
    Add parameterized failure-path tests: timeout → 504 to caller +
    no charge persisted; decline → 402 + structured error; duplicate
    webhook → idempotent no-op + single charge. Document the failure
    modes in .plans/checkout.md so future edits must extend the list.
```
````

---

## Few-shot: good dismissal

A reviewer sees a test using 6 mocks and flags "mocking the world."
It is **not** a violation when the unit under test is an orchestration
layer whose job is to coordinate 6 collaborators, and the test asserts
the orchestration contract (sequence, fan-out shape, error
translation). The smell applies when the test covers a single logical
behavior and most of the mocks are setup for unrelated dependencies
the behavior doesn't care about. Similarly, an `assert_called_with`
is not an implementation-assertion violation when the call itself is
the contract — e.g., a notifier module whose job is to call a
downstream API with specific arguments; the call is the behavior.

---

## Decidable-at matrix

| Smell | antiplan (Phase 2) | pr-review | cleanup |
| --- | --- | --- | --- |
| Mocking the world | ❌ — emerges in code | ✅ | ✅ |
| Implementation-not-behavior asserts | ❌ | ✅ | ✅ |
| Mock-only integration boundary | partial — should mandate contract tests | ✅ | ✅ |
| No failure-path coverage | partial — should enumerate failure modes | ✅ | ✅ |

**partial** means /antiplan sets the policy but cannot see the code.
When `plan_present: true` and the plan enumerated failure modes or
mandated contract tests, pr-review/cleanup may emit
`category: Architectural Drift` with `decidable_at: design`.
