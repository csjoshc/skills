# AC to Test Traceability

Every acceptance criterion must name the test function or verification command that will verify it before the ticket can move to `Stage: BUILD`. The test does not have to exist yet (TDD's red phase creates it), but the name, file, and behavior to be asserted must be chosen in advance. This prevents tautological tests: the assertion is committed before the implementation exists to copy from.

The block conditions live in [SKILL.md](../SKILL.md).

## Contents

- Required section template
- Why this works

## Required section in every ticket

```markdown
## Acceptance Criteria → Tests

| AC | Test file / Command | Test name | Assertion shape | Risk Tier |
|---|---|---|---|---|
| AC-1 Given a logged-in user, when they click "Save", then a toast appears | src/ui/__tests__/SaveButton.test.tsx | "shows toast on save" | `expect(screen.getByRole('alert'))` | T2 |
| AC-2 Given a 5xx response, retry up to 3 times | src/api/__tests__/retry.test.ts | "retries 3× on 5xx then throws" | counter-based mock | T1 |
| AC-3 Export CSV contains header row | `pytest -k test_csv_header` | "emits header as first line" | string match | T3 |
```

The Risk Tier column feeds `/tdd` Phase 0 scoping. Values mirror
the ticket's **Test Obligation Profile** (spec-writer output) — the critic's job
is to enforce that the mirror is honest, not to re-derive tiers.

## Why this works

A test named and described before the implementation describes **user
intent**. A test written after the implementation describes **what the
code happens to do**. Locking the name and assertion shape at ticket
time forces the intent-first orientation.
