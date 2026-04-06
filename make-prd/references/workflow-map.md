# Workflow Map (Interactive In-Session)

This maps the original pipeline intent to an interactive skill flow.

## Stage Mapping

1. Intake normalization
- Convert raw request into: problem, outcomes, constraints, non-goals.

2. Intent and ambiguity classification
- Score ambiguity as low/medium/high.
- If medium/high, open a bounded clarification round.

3. Facet analysis
- Product facet: users, jobs, UX flows, success metrics.
- Codebase facet: touched systems, risks, migration and compatibility concerns.
- Alternatives facet: options, tradeoffs, operational concerns.

4. Synthesis
- Merge facets into one coherent PRD narrative.
- Resolve conflicts and flag unresolved decisions.

5. Ticket generation
- Produce implementation tickets with dependencies, AC, and test intent.

## Status Model (for conversation)

- `intake_ok`
- `needs_human_feedback`
- `ready_for_synthesis`
- `tickets_drafted`
- `final_review`
- `completed`

## Interaction Model

- Prefer one context, not repeated fresh sessions.
- Batch clarification prompts.
- Keep question rounds intentionally small.
