---
name: make-prd
description: >-
  Interactive PRD drafting via fan-out dialogue with human checkpoints. Use when
  the idea is fuzzy and needs collaborative exploration. Not for adversarial
  pushback (use antiplan) or defined features (use spec-writer).
  In: rough idea.
  Process: fan-out questions, human checkpoints, synthesize.
  Out: .plan/PRD.md + .plan/task-sequence.md.
metadata:
  short-description: Interactive PRD + ticket orchestrator
---

# Make PRD

Use this skill when the user wants to convert rough ideas into a high-quality PRD and ticket set while staying in one interactive conversation.

## TL;DR (Quick Start)

Interactive PRD expansion and ticket drafting workflow with explicit in-session fan-out, human checkpoints, and final synthesis.

**When to use:** "write a PRD", "plan this feature", "draft tickets", "turn ideas into implementation-ready tickets".

**Invocation:** `/make-prd <feature-description>`

## Decision Tree

1. **Is the request a vague idea or a structured spec?**
   - Vague idea → Start with intake and ambiguity triage
   - Structured spec → Skip to synthesis pass

2. **Does the user want fan-out analysis?**
   - YES → Run subagents for product, codebase, alternatives/risk facets
   - NO → Continue with main thread only

3. **Are there irreversible architectural choices?**
   - YES → Escalate at HITL gate before finalizing
   - NO → Proceed to ticket drafting

## Workflow

See companion files in `references/` for detailed templates and subagent prompts.

## Goals

1. Keep the workflow interactive and transparent.
2. Keep one shared context in-session.
3. Use explicit fan-out (subagents) only for bounded sidecar analysis.
4. Synthesize a single coherent final output with resolved ambiguities and clear acceptance criteria.

## Progressive Disclosure

Load companion files only when needed:
- `references/orchestra-alignment.md`: exact mapping to current `write_prd_langgraph` behavior
- `references/workflow-map.md`: stage map and gate rules
- `references/fanout-subagents.md`: role definitions and subagent prompts
- `references/ambiguity-and-acceptance.md`: ambiguity resolution and acceptance criteria rubric
- `~/.skills/shared/PRD_TEMPLATES.md`: PRD and ticket output format (see "make-prd-specific templates" section)

## Operating Rules

1. Start with a short intake summary of what you understood.
2. Ask only high-leverage questions; batch questions to reduce start/stop overhead.
3. **If antiplan output exists**, reference its findings on counterarguments and ruled-out alternatives. Do not re-debate settled decisions.
4. **If no prior analysis**, ask high-leverage questions to surface doubts and assumptions — avoid repeating antiplan's work.
5. Keep a visible `Decision Ledger` with:
- decided
- assumed
- open (needs human)
6. If the user asked for fan-out or delegated analysis, run explicit subagent tasks for non-blocking facets.
7. Do not block the main thread on every subagent result; continue local synthesis while they run.
8. Reconcile conflicts explicitly before finalizing outputs.

## Session Flow

1. Intake and framing
2. Ambiguity triage (what must be answered now vs later)
3. Fan-out facet analysis (product, codebase, alternatives/risk, optional QA/release)
4. Synthesis pass (single narrative PRD)
5. Ticket drafting pass (clear AC, dependencies, unknowns)
6. Final review with the user (targeted edits)

## Divergent thinking lenses

<!-- merged from addyosmani/agent-skills idea-refine -->

Apply during fan-out / ambiguity triage to expand the option space before converging. Pick lenses that fit the idea — don't run all mechanically. Generate 5-8 variations, not 20.

| Lens | Prompt |
|---|---|
| Inversion | What if we did the opposite? |
| Constraint removal | What if budget / time / tech weren't factors? |
| Audience shift | What if this were for a different user? |
| Combination | What if we merged this with an adjacent feature? |
| Simplification | What's the version that's 10x simpler? |
| 10x version | What does this look like at massive scale? |
| Expert lens | What would domain experts find obvious that outsiders miss? |

After expansion, cluster into 2-3 distinct directions and stress-test against user value, feasibility, and differentiation before the synthesis pass.

## HITL Policy

Escalate to user only at these gates:
1. Scope boundary decisions
2. KPI / success metric definitions
3. Irreversible architectural choices
4. Compliance/security/privacy-impacting behavior
5. Launch criteria and rollback policy

For each gate, present:
1. Recommendation
2. 1-2 alternatives
3. Impact on timeline/risk

## Expected Deliverables

Two durable artifacts written to disk:

1. **`.plan/PRD.md`** — PRD draft with explicit assumptions and unresolved
   questions. Conforms to orchestra's `docs/PRD_CONTRACT.md` (v1).
2. **`.plan/task-sequence.md`** — ordered task placeholders (title +
   one-line intent + dependencies + 2–3 invariant ACs). **Placeholders, not
   tickets.** `spec-writer` consumes these and expands each into
   `.tickets/NN-<slug>.md`.

Plus session-only outputs:
- Follow-up question pack for unresolved blockers
- All prose passes `/stop-slop` before delivery

## First Response Contract (When Skill Is Invoked)

In the first response after invocation:
1. Confirm objective and constraints in 3-6 bullets.
2. Propose the immediate plan for this session.
3. Ask the smallest set of clarification questions needed to start drafting.
3.5. Confirm the PRD output will conform to PRD_CONTRACT.md v1 unless user opts out.

## Assumptions & Escalation

See [`~/.skills/shared/ASSUMPTION_TIERS.md`](~/.skills/shared/ASSUMPTION_TIERS.md) for canonical tier definitions.

**Domain-specific examples for make-prd:**
- **Tier 1 (reversible):** Ticket naming, ordering — proceed, flag for review
- **Tier 2 (architecture):** Feature scope boundaries, dependency sequencing — check STANDARDS.md
- **Tier 3 (security):** Compliance/privacy-impacting features — always block for human confirmation

## Examples (Few-Shot)

**Example 1: New feature PRD**
Input: "We need a user onboarding flow with email verification"
Output: Intake → Ambiguity triage → PRD draft → Ticket pack (onboarding page, email service, verification endpoint, analytics)

**Example 2: Feature expansion**
Input: "Turn this 2-line idea into a full PRD with tickets"
Output: Intake → Fan-out analysis → Synthesis → 8-ticket pack with dependencies and acceptance criteria

---

**Editing this skill?** Use [`~/.skills/skillsmith`](~/.skills/skillsmith) for skill creation guidelines.
