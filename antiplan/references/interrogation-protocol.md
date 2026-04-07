# Interrogation Protocol

Loaded during Phase 1 and Phase 2. Provides the adversarial questioning
framework. Every question is designed to surface ambiguity, unjustified
decisions, and untestable requirements BEFORE any tickets are created.

---

## Phase 1: Product Interrogation

### Objective

Establish what the user is building, for whom, and what the minimum viable
feature set is — with zero speculation about implementation.

### Question Categories

#### 1. Why Questions (Purpose Justification)

For each stated feature or goal:

- "What user-observable outcome does this produce?"
- "If we shipped everything else but this, what breaks for the user?"
- "Who specifically asked for this? Is this a user need or an engineer's guess?"
- "What is the simplest thing that could possibly work here?"

Do not accept:
- "It would be nice to have" → force a concrete use case
- "Users might want" → demand evidence or cut it
- "Best practice says" → ask whose practice and what problem it solved for them

#### 2. Who Questions (User Identification)

- "Who are the 1-3 actual humans who will use this system?"
- "What do they do today without this system? What specific pain are they in?"
- "Walk me through their exact workflow — start to finish, step by step."
- "What is the first thing they will try to do when they see this?"

Do not accept:
- Abstract personas ("admin users") → demand names, roles, or concrete examples
- "Various stakeholders" → ask for the top 2 by frequency of use

#### 3. Minimum Questions (Scope Reduction)

- "If you had to ship this in 3 days, what would you cut?"
- "Which of these features can ship independently — not depending on the others?"
- "What is the ONE flow that must work end-to-end for this to be useful?"
- "If I deleted [feature X], what user story breaks?"

The goal is to force the user to name the **minimum testable product** (MTP) —
the smallest thing that proves the design works on real data, end to end.

#### 3b. Greenfield vs Brownfield

After identifying the MTP, determine the project context:

- "Is this greenfield (new codebase) or brownfield (changes to existing code)?"

If **brownfield**:
- "List every existing behavior that must NOT break."
- "What is the current test coverage for those behaviors?"
- A **regression gate ticket** is mandatory before the first new vertical slice.
  The regression gate proves existing behavior still works before any new code
  is layered on.
- "Show me the existing code paths this feature touches. Which of those paths
  have integration tests today?"

If the user cannot list existing behaviors that must be preserved, treat this as
an Unresolved item — it blocks Phase 3.

#### 4. Boundary Questions (Scope Enforcement)

- "What is explicitly NOT in scope? Name three things you will NOT build."
- "Where does this system end and another system begin?"
- "What data does this system own? What data does it borrow from elsewhere?"
- "What happens when [adjacent system] is down or returns garbage?"

Do not accept: silence on boundaries. If the user doesn't define what's out of
scope, the scope is unbounded and will grow. Make them draw the line.

#### 5. Success Questions (Testable Acceptance)

For each feature surviving minimum + boundary questions:

- "How will you know this works? Describe the test in given/when/then."
- "What does the user see when this succeeds? What do they see when it fails?"
- "What is the latency target? Throughput target? Error budget?"
- "What is your deploy target: local, staging, production? In what order?"

Every feature must exit Phase 1 with at least one concrete acceptance criterion
written as given/when/then. No exceptions.

### Phase 1 Completion Criteria

All of the following must be true:
- [ ] Every feature has a named user with a stated need
- [ ] Every feature has at least one given/when/then acceptance criterion
- [ ] The user has named at least 3 things explicitly NOT in scope
- [ ] The Minimum Testable Product (MTP) has been identified
- [ ] The Convergence Ledger shows zero Unresolved items in the product domain

---

## Phase 2: Architecture Interrogation

### Objective

Challenge every proposed component, service, layer, and abstraction. Anything
that survives Phase 2 has earned its right to exist. Everything else is cut.

### The Four Tests

Apply each test to every proposed component or abstraction:

#### Deletion Test
- "If I delete this entirely, what user-visible feature from Phase 1 breaks?"
- If the answer is "nothing user-visible" → cut it
- If the answer is "it improves developer experience" → it's not Phase 1
  scope; defer or cut

#### Merge Test
- "Why can't this be a method/function in [existing component]?"
- "What forces this to be a separate service/module/class?"
- "Show me two concrete scenarios where this MUST differ from [existing
  component]'s behavior"

If the user can't name a concrete behavioral divergence, merge it.

#### Mock Test
- "Can you test this component's integration with [dependency] without mocks?"
- "If not, why not? What makes a real connection infeasible?"
- "If we must mock, what is the plan to run the real integration before ship?"

If the only way to test the component is with extensive mocking, the
abstraction boundary is in the wrong place. Challenge the boundary.

#### Naming Test
- "What does this component do in one sentence without using 'manage',
  'handle', 'process', 'service', or 'util'?"
- "If you can't name it precisely, do you actually know what it does?"

Vague names are a signal of vague responsibility. Push until the name is
specific or the component is merged into something with a clear name.

#### Reinvention Test
- "Does an existing library, framework feature, or known pattern already do
  this? Show me you searched."
- "If a well-maintained dependency handles this, why build a custom version?"
- "What specifically about the existing solution is insufficient for your
  use case?"

If the user proposes building something that a standard library or framework
already provides, demand concrete evidence of insufficiency. "We might need to
customize it later" is AP-1 (Speculative Architecture).

### Activation Checklist

For every new service, environment variable, route, or infrastructure boundary
proposed in Phase 2, demand:

- "Who sets this in dev? In staging? In production?"
- "What is the default state — on or off?"
- "Default-off is invalid unless you name the feature-flag ticket and the
  first integration gate that proves it works when turned on."

Any new boundary that cannot answer these questions is either premature or
speculative. Challenge it with AP-1.

### API Contract Demands

For every boundary between components:

- "What is the exact request/response shape?"
- "What happens on error? What status codes or error types are returned?"
- "Show me the type signature (TypeScript interface, Python Protocol, etc.)"
- "Is this contract tested independently of the implementations on each side?"

API contracts must be defined BEFORE implementation tickets are created. Not
after. Not "TBD." Now.

### Anti-Pattern Detection

During Phase 2, actively scan for anti-patterns AP-1 through AP-8 from
[anti-patterns.md](anti-patterns.md). When you detect one:

1. Name it explicitly: "This looks like AP-4: God Function."
2. Quote the detection signal that triggered it
3. Ask the targeted challenge question from the anti-pattern entry
4. Do not proceed until the user resolves the anti-pattern or explicitly
   acknowledges the risk

### Phase 2 Completion Criteria

All of the following must be true:
- [ ] Every component has passed the Deletion Test (justifies its existence)
- [ ] Every component has passed the Merge Test (can't be absorbed)
- [ ] Every component has passed the Reinvention Test (no existing solution)
- [ ] Every new boundary has passed the Activation Checklist
- [ ] Every inter-component boundary has a defined API contract
- [ ] Mock dependencies have been identified with real-integration-test plans
- [ ] No unresolved anti-patterns remain
- [ ] The Convergence Ledger shows zero Unresolved items in the architecture
  domain

---

## Interrogation Style Guide

### Batch Size
Ask 3-5 questions per response, grouped by theme. State what you understand,
what's ambiguous, and what you need.

### Forced Choices
When the answer space is bounded (e.g., "REST vs gRPC", "SSR vs SPA",
"Postgres vs SQLite"), offer the choices explicitly:

> "Your data access pattern looks like [X]. This means your realistic choices
> are A or B. A gives you [tradeoff]. B gives you [tradeoff]. Which is it, and
> why?"

### Acknowledging Good Answers
When the user gives a concrete, testable, justified answer — acknowledge it and
move on. Don't re-interrogate resolved decisions. Update the Convergence Ledger.

### Handling Frustration
If the user pushes back on the interrogation:
- Acknowledge the friction
- Remind them this phase exists because the alternative is 50 tickets, 100
  commits, and 2 million tokens of rebuilding
- Offer to show the Convergence Ledger to demonstrate progress
- Never back down on demanding testable answers. That is non-negotiable.

### Handling "I Don't Know"
Acceptable. "I don't know" is vastly better than a bad assumption.
- Record it as Unresolved in the Convergence Ledger
- Ask: "Is this a decision you need to make, or can we cut the feature that
  depends on it?"
- If it blocks other decisions, it must be resolved before Phase 3
