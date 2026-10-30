---
name: mutation-critic
description: >-
  Checks test sensitivity to plausible incorrect behavior using targeted
  mutations of changed code. Investigates survivors rather than treating
  them as proof of tautology. Use after TDD cycles,
  before PR creation, and during pr-review test analysis.
---

# mutation-critic

## Contents

- When to invoke
- When to skip
- Mutant catalogue
- Workflow
- Integration points
- Hard rules
- Output contract


Mutation checks test sensitivity to specific incorrect behavior.
A survivor may indicate a coverage gap, an equivalent mutation, or an invalid experiment; it does not by itself prove tautology.
A killed mutant does not establish an independent basis for the expected result.

## When to invoke

- **Auto-fire** after the `tdd` green step for any TOQ entry with
  `mutation_candidate: true` (set in `.agent-local/tickets/tdd/toq-<ticket-id>.yaml` when
  tier is T1 AND score > 60 — see `./SCOPING.md`). This is the
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

Apply exactly one mutation per run and select the relevant tests for that obligation.
Record whether the intended assertion detected the incorrect behavior, not merely whether any test failed.

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

For each selected obligation, start with one mutation representing a plausible wrong implementation.
Add another only when it probes a distinct consequential failure.
Use a temporary copy or controlled fixture so the user's working code stays intact.

Use a real mutation runner where available:

```bash
# Python
pip install mutmut
mutmut run --paths-to-mutate "$CHANGED_FILE" --tests-dir tests/

# JS / TS
npx stryker run
```

Fallback when no runner exists: apply a targeted rewrite in the temporary copy,
then re-run the relevant tests there.

### Phase 3: Interpretation

For each mutant:

| Outcome | Meaning |
|---|---|
| Relevant assertion fails | The check detects this incorrect behavior |
| Test passes | **SURVIVOR** — investigate equivalence, reachability, and a possible coverage gap |
| Compilation, setup, or unrelated failure | Invalid or inconclusive experiment; repair it or report the gap |

Build `MUTATION_SURVIVORS.md`:

```markdown
| File | Fn | Mutation | Line | Test that should have caught it |
|---|---|---|---|---|
| src/cart.ts | totalPrice | boolean-flip `hasDiscount` | 42 | cart.test.ts::"applies discount" |
```

### Phase 4: Remediation guidance

For each meaningful survivor, suggest an assertion grounded in the contract.
A literal expected value can be strong evidence; relational assertions are not inherently better.

```markdown
Current test:
  expect(Number.isFinite(total)).toBe(true) // shape-only; passes with discount logic removed

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
- `tdd` green-step: follow the invocation criteria above and the planned evidence obligations.
- `verify`: an unresolved meaningful survivor is an evidence gap for the affected claim, not an automatic failure based on a survivor percentage.

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
