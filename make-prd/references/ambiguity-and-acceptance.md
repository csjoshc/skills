# Ambiguity Resolution + Acceptance Criteria Rubric

## Ambiguity Ledger

Track each ambiguity as:
- `id`
- `question`
- `why_now` (why resolution is needed now)
- `default_assumption` (if user defers)
- `impact`

## Clarification Round Rules

1. Ask at most 3 high-impact questions per round.
2. Provide recommendation first.
3. If user defers, record explicit assumption and continue.

## Acceptance Criteria Rubric

Each ticket AC should be:
1. Behavioral: observable user/system behavior.
2. Verifiable: testable without ambiguous language.
3. Bounded: clear scope and exclusions.
4. Instrumented: logs/metrics where relevant.
5. Recoverable: failure/rollback behavior when relevant.

## Anti-Patterns To Avoid

- "Works as expected"
- "Fast enough"
- "Should support X" without explicit threshold or test
- Hidden cross-ticket dependencies
