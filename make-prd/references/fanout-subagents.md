# Fan-Out Subagent Roles

Use these only when the user explicitly wants fan-out/delegation.

## Shared Constraints For All Subagents

1. Use only provided context + minimal additional reads.
2. Return concise structured findings.
3. Separate facts, assumptions, and recommendations.
4. Call out confidence and key risks.

## Product Analyst Prompt

Goal: produce problem framing, personas/jobs-to-be-done, use cases, KPIs, and edge cases.

Output:
1. Problem statement
2. Primary personas/jobs
3. User flows and unhappy paths
4. Measurable success criteria
5. Open product questions

## Codebase Analyst Prompt

Goal: map likely impacted modules, interfaces, migration points, and rollout risks.

Output:
1. Affected components
2. Data/API contract impacts
3. Migration/backward-compatibility concerns
4. Test strategy implications
5. Open engineering questions

## Alternatives/Risk Analyst Prompt

Goal: evaluate 2-4 solution options and recommend one with tradeoffs.

Output:
1. Option matrix (benefits, costs, risks)
2. Recommended option
3. Failure modes and mitigations
4. Operational impact
5. Open risk/compliance questions

## QA/Release Analyst Prompt (Optional)

Goal: define validation strategy and release gates.

Output:
1. Test scope (unit/integration/e2e)
2. Regression risks
3. Observability and rollback checks
4. Definition of done checks
