---
name: mutation-critic
description: >-
  Detects tautological tests that assert "code does what code does" instead
  of user intent. Generates small mutants of changed code (boolean flip,
  off-by-one, return-early, negation) and re-runs the test suite. Tests
  that survive all mutants are flagged as suspect. Use after TDD cycles,
  before PR creation, and during pr-review test analysis.
---

# mutation-critic

Kills circular tests. A test that passes while the code under test is
deliberately broken is not a test — it's a restatement of the
implementation. This skill injects small, semantically meaningful
mutations into changed functions and reports which tests failed to catch
them.

## When to invoke

- **Auto-fire** after the `tdd` green step for any TOQ entry with
  `mutation_candidate: true` (set in `.tickets/tdd/toq-<ticket-id>.yaml` when
  tier is T1 AND score > 60 — see [SCOPING.md](./SCOPING.md)). This is the
  default path; no opt-in required.
- After `tdd` green step for any other entry, **optional** — invoke on demand
  when test quality is in question
- During `pr-review` Test Analyzer agent
- During `pr-fix` after any fix to code that claims test coverage

Targeting: run mutants against `TOQ[i].target` only, not the full changed-file
set. This keeps the mutant pass scoped to the obligation that just turned green.

## When to skip

- Pure data files (JSON, YAML, fixtures)
- Migrations
- Files with only type declarations
- First 24 hours of a brand-new module (let TDD stabilize)

## Mutant catalogue

Apply these minimal, semantics-preserving-at-a-glance mutations one at a
time per function:

| Mutation | Example before | Example after |
|---|---|---|
| Boolean flip | `if (user.active)` | `if (!user.active)` |
| Off-by-one low | `for i in range(n)` | `for i in range(n-1)` |
| Off-by-one high | `for i in range(n)` | `for i in range(n+1)` |
| Return early | function body | `return; // rest untouched` |
| Negate comparison | `x > 0` | `x < 0` |
| Swap operator | `a + b` | `a - b` |
| Constant twiddle | `timeout = 5000` | `timeout = 0` |
| Skip invariant | `assert x is not None` | (remove line) |

Apply exactly one mutation per run. Run the full relevant test suite.
Record whether any test failed.

## Workflow

### Phase 1: Target selection

From the diff, extract functions that have tests claiming to cover them:

```bash
git diff --name-only HEAD~1 | xargs -I {} echo "changed: {}"
# Map each changed file to its test file by convention
```

Skip anything that doesn't have a claimed test. Those belong to `tdd` or
the Test Analyzer, not here.

### Phase 2: Mutation pass

For each target function, pick 3 mutations from the catalogue (boolean
flip, off-by-one, return-early are the cheapest high-signal set).

Use a real mutation runner where available:

```bash
# Python
pip install mutmut
mutmut run --paths-to-mutate "$CHANGED_FILE" --tests-dir tests/

# JS / TS
npx stryker run
```

Fallback when no runner exists: apply the mutation with a one-line
Python/Node AST rewrite, re-run pytest / jest on the target test file,
revert.

### Phase 3: Interpretation

For each mutant:

| Outcome | Meaning |
|---|---|
| Test fails | Good — test catches the mutant |
| Test passes | **SURVIVOR** — test is tautological for this branch |
| Test errors out | Unrelated — skip |

Build `MUTATION_SURVIVORS.md`:

```markdown
| File | Fn | Mutation | Line | Test that should have caught it |
|---|---|---|---|---|
| src/cart.ts | totalPrice | boolean-flip `hasDiscount` | 42 | cart.test.ts::"applies discount" |
```

### Phase 4: Remediation guidance

For each survivor, suggest an intent-oriented assertion:

```markdown
Current test:
  expect(total).toBe(90)          // value-only; passes even with discount logic removed

Intent assertion:
  // "10% discount applies when hasDiscount is true"
  expect(withDiscount).toBeLessThan(withoutDiscount)
  expect(withDiscount / withoutDiscount).toBeCloseTo(0.9, 2)
```

## Integration points

- `pr-review` Test Analyzer: runs mutation-critic and incorporates
  survivors into its report.
- `pr-fix`: for every fixed comment, re-run mutation-critic on that
  function to confirm the fix is tested.
- `tdd` green-step: optional gate — run a 3-mutant pass before calling
  the cycle complete.
- `verify-claim`: a survivor rate above a threshold (e.g., > 25%) flips
  "VERIFIED" to "CLAIM_UNVERIFIED" for that claim.

## Hard rules

- Never mutate files the user has flagged as no-mutate (add to
  `.claude/no-mutate.txt`).
- Never leave mutated code in the working tree. Always revert.
- Never count "takes forever, skipped" as a pass.
- If a test suite takes longer than 60s for a single mutant, reduce
  scope via `--findRelatedTests` / `pytest -k`.

## Output contract

```
MUTATION RESULT: F targets, M mutants applied, S survivors (K%)
<MUTATION_SURVIVORS.md written if S > 0>
```
