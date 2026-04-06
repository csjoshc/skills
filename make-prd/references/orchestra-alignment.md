# Alignment With Current `write_prd_langgraph` Flow

This file keeps the skill behavior anchored to the implementation in this repository.

## Pipeline Semantics To Preserve

1. Intake first
- Normalize issue text before PRD synthesis.
- If intake fails: stop with blocked status.

2. Status vocabulary
- `blocked`
- `short_circuited`
- `needs_human_feedback`
- `completed`
- `error`

3. Ambiguity gate
- Current implementation gates HITL question DAG at ambiguity score > 0.3.
- Skill should mimic this with a practical low/medium/high ambiguity triage and explicit question rounds.

4. Multi-round HITL
- Round 1 asks root questions.
- Later rounds ask only unresolved dependent questions.
- Resume should preserve prior answers and continue without re-asking answered items.

5. Synthesis order
- Intent classification
- Product facet analysis
- Codebase facet analysis
- Alternatives analysis
- Facet synthesis
- PRD compose
- Ticket synthesis

6. Artifact expectations
- PRD draft plus ticket bundle.
- Include assumptions and open questions in both PRD and ticket output where relevant.

## Where The Skill Intentionally Differs

1. Interactive continuity
- Skill stays in one conversational context by default.

2. Explicit fan-out
- Subagent fan-out is explicit and visible when the user requests delegation.

3. Human-friendly checkpoints
- HITL prompts are batched and recommendation-first to reduce session churn.
