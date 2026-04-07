# Artifact Ingestion Protocol

Defines how the antiplan skill handles user-provided reference material during
planning. Nothing from an artifact is adopted by default. Every item must be
explicitly whitelisted and interrogated before it enters the plan.

---

## Core Rule

Every artifact is **evidence to be examined**, not **spec to follow**. The agent
treats reference material the same way a dissertation committee treats a cited
paper: it may contain useful information, but citing it does not make it true,
relevant, or appropriate for this project.

---

## Supported Artifact Types

| Type | What the agent can do | Assumption tag for extracted facts |
|------|----------------------|----------------------------------|
| **Git repo** (URL or local path) | Read code, inspect structure, identify patterns | Observed (if read directly) |
| **Screenshot / image** | Describe UI elements, flows, and layout | Observed (what agent sees), Inferred (behavior behind the UI) |
| **Documentation link** | Read and extract claims, architecture, patterns | Observed (if read directly), Inferred (if summarized by user) |
| **API spec** (OpenAPI, protobuf, etc.) | Read endpoints, types, contracts | Observed (if read directly) |
| **Video demo** | Describe flows and interactions observed | Observed (what agent sees), Inferred (implementation details) |
| **User description** ("this repo does X") | Record the claim | Inferred (until agent verifies) |

---

## Ingestion Workflow

### Step 1: Inventory

When the user provides an artifact, the agent examines it and produces a
structured inventory at the appropriate scope level:

- For a git repo: major features, components, architecture patterns, key files
- For a screenshot: UI elements, flows, layout patterns, navigation structure
- For documentation: features described, architecture decisions, constraints
- For an API spec: endpoints, data models, auth patterns

Present the inventory to the user: "I see the following [N] items in this
artifact. Nothing is adopted yet."

### Step 2: Whitelist Pass

For each item in the inventory, ask:

- "Do you want to adopt this? Yes or no."
- If yes: "What specifically — the pattern, the implementation, the API shape,
  the UI layout, the data model? Be precise."
- If no: record as non-goal.

Do NOT accept "adopt all" or "just do what that repo does." That is AP-1
(Speculative Architecture) — adopting components without individual justification.
Push back: "Which specific items from this list do you want, and why does each
one map to a user story from Phase 1?"

### Step 3: Interrogation

Every adopted item enters the normal Phase 1-2 interrogation pipeline as if the
user had proposed it fresh:

- Phase 1: "Why do we need this? Which user story does it serve? What is the
  testable acceptance criterion?"
- Phase 2: "Does this survive the Deletion Test? The Merge Test? The
  Reinvention Test? Can we test it without mocks?"

Adopted items receive no special treatment for having come from a reference
artifact. If an item cannot justify its existence through interrogation, it
is cut — regardless of whether it works in the reference artifact.

### Step 4: Rejection Recording

Items NOT adopted are recorded as explicit non-goals in the Convergence Ledger:

```
- Cut: "Auth middleware pattern from [repo-name] — not needed; our auth
  is handled by [existing component]"
```

This prevents the same items from creeping back in during Phase 3 subagent
work. The Challenger subagent receives the non-goals list and flags any ticket
that reintroduces rejected artifact items.

### Step 5: Assumption Tagging

All facts from the artifact enter the Assumption Register with appropriate
source tags:

- Agent read the code/docs directly → **Observed**
- User described what the artifact does → **Inferred** (until agent verifies)
- User says "I want this specific thing" → **User-stated** (for the desire),
  **Inferred** (for feasibility until proven by tracer bullet or code review)

---

## Anti-Pattern Guards

### Bulk Adoption

"Just copy that repo's architecture" is the most common trigger for AP-1
(Speculative Architecture). The entire purpose of the whitelist pass is to
prevent this. If the user insists on bulk adoption:

1. Name the anti-pattern: "This is AP-1 — adopting architecture without
   individual feature justification."
2. Offer the alternative: "Let's go through the inventory. Which items
   specifically map to your Phase 1 user stories?"
3. If the user persists after two challenges, record the risk in the
   Assumption Register as a HIGH-impact Inferred assumption and proceed —
   but the first integration gate must validate the adopted architecture
   with a runtime proof artifact.

### Screenshot Fidelity Trap

"Make it look like this" without itemization leads to speculative UI work.
For visual artifacts:

1. Describe what you see: elements, layout, flows, interactions
2. Ask which specific elements the user wants to replicate
3. For each element: "Is this the visual style, the interaction pattern,
   the data it displays, or all three?"
4. Non-selected elements are recorded as non-goals

### Outdated Reference

If the artifact is a repo or docs from an older version, tech stack, or
different context:

1. Note the divergence: "This repo uses [X]; your project uses [Y]."
2. For each adopted item, ask: "Does this pattern translate to our stack,
   or does it need adaptation?"
3. Adaptations are Inferred assumptions until validated by a tracer bullet.
