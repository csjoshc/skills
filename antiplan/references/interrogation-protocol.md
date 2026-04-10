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

If **brownfield**, the agent should have already scanned the codebase in
Phase 0. Present the discovered conventions:
- "I found [framework], [test runner], [architecture pattern]. These are
  tagged Observed in the Assumption Register. In Phase 2, you must justify
  deviations from these, not justify them."
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
- "For every output path in the user-visible flow, what does the user see? If
  the system completes an internal operation but produces no text output, what
  is shown — empty response, synthesized summary, or error?"
- "What is the latency target? Throughput target? Error budget?"
- "What is your deploy target: local, staging, production? In what order?"

When a feature involves **computation, conditional logic, pricing rules, or
data transformation**: demand at least one worked example with concrete
input values and expected output values. Prose-only ACs for logic-heavy
features are ambiguous by default — the implementing agent will pick one
interpretation and write tests that validate it, producing code that runs
correctly but computes the wrong result.

- "Walk me through a concrete example: given input [X], what is the exact
  output? Show me the numbers."
- "Is the rule applied per-item or per-aggregate? Give me both cases with
  specific values so we can see the difference."

Every feature must exit Phase 1 with at least one concrete acceptance criterion
written as given/when/then. Features with computation or conditional logic must
include at least one **worked example with literal values**. No exceptions.

#### 5b. Prompt Composition (for LLM-driven features)

For any feature that involves composing a system prompt, context injection, or
model behavioral constraints:

- "What sections does the prompt contain? List them."
- "Does any section change per-turn (e.g., current date, prior tool results,
  user context)? Or is it static?"
- "What behavioral constraints does the prompt impose on the model (e.g.,
  'do not narrate wire protocol,' 'summarize tool results in prose')?"
- "What happens after a tool call returns? Does the prompt include formatting
  rules for how the model should present tool results to the user?"

Do not accept: "system prompt includes a catalog." That is one section. Ask:
"What else? Date context? Behavioral framing? Post-tool formatting rules?"
Every section is a design decision that should be explicit in the plan, not
invented by the implementing agent.

#### 6. Measurable Success Criteria

After features are established, demand non-functional success metrics:

- "What does success look like numerically? Latency, throughput, adoption,
  error rate — give me at least 2 concrete thresholds."
- "If this project ships and all acceptance criteria pass, but nobody uses it,
  did it succeed? What is the adoption target?"

At least 2 measurable success criteria (SC-001, SC-002, etc.) must be defined
before Phase 1 completes.

#### 7. Priority Tiers

Require the user to assign P1/P2/P3 to each surviving feature:

- **P1 (MTP):** Must be in the first vertical slice. Ship-blocking.
- **P2 (First release):** Needed for the product to be useful beyond demo.
- **P3 (Nice-to-have):** Can be deferred without user pain.

For each assignment: "Why is [feature] P2 and not P3? What user story breaks
if we defer it?" P3 features are cut from the initial DAG by default — they
become a follow-up epic.

#### 8. Statefulness Questions (for interactive systems)

For any system with a user-facing UI or multi-step interaction:

- "Does the user interact once, or do they have a conversation / multi-step flow?"
- "If conversational: who holds the state — client, server, or both?"
- "What is the maximum session length? What happens at the boundary?"
- "When the user sends message N, does the backend see messages 1 through N-1?"
- "How does conversation/session state flow through the ENTIRE stack — from the
  client, through the API layer, to the processing layer?"
- "What happens if the user refreshes the page? Is state lost?"

Do not accept: "It's a chat interface" without specifying the state management
model. Single-turn vs. multi-turn is an architectural decision that affects
every layer of the stack. This is the most commonly under-specified aspect of
interactive systems.

**Hard rule:** If the system is interactive, the statefulness model must be
explicitly resolved (client-side / server-side / hybrid) before Phase 1 exits.

#### 9. Security Boundary Questions

For every HTTP endpoint, tool execution path, or data flow in the system:

- "What authentication does this endpoint require? Bearer token, mTLS,
  API key, none?"
- "What happens when an unauthenticated request arrives? 401? Silent drop?
  Default behavior?"
- "For every runtime that executes tool calls, what policy governs which
  tools can run? Is this configurable or hardcoded?"
- "Where do secrets (API keys, tokens, shared secrets) live at runtime?
  Environment variables? YAML config? Vault?"

Do not accept: "demo scope — no auth needed" without the user explicitly
acknowledging the risk. If endpoints will eventually need auth, the plan
must include placeholder auth that can be upgraded, not zero auth that must
be retrofitted.

### Phase 1 Completion Criteria

All of the following must be true:
- [ ] Every feature has a named user with a stated need
- [ ] Every feature has at least one given/when/then acceptance criterion
- [ ] Features with computation or conditional logic include at least one
  worked example with literal input/output values
- [ ] Every feature has a priority tier (P1/P2/P3) with justification
- [ ] At least 2 measurable success criteria (SC-001, SC-002) are defined
- [ ] The user has named at least 3 things explicitly NOT in scope
- [ ] The Minimum Testable Product (MTP) has been identified
- [ ] Greenfield/brownfield is determined; if brownfield, existing behaviors
  that must not break are listed
- [ ] If interactive: statefulness model is explicitly resolved
- [ ] Every HTTP endpoint has stated auth requirements (even if "none — demo
  scope, acknowledged risk")
- [ ] The Convergence Ledger shows zero Unresolved items in the product domain
- [ ] No `[NEEDS CLARIFICATION]` markers remain in any Phase 1 artifact

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
- "For every error type, what specific status code or error shape is returned?
  'Returns error response' is not a contract — name the code and the body."
- "How do errors propagate across layer boundaries? Does the orchestration
  layer raise typed exceptions that the BFF maps to HTTP status codes? Or
  does each layer handle errors independently? If exceptions propagate, name
  the exception types and what each maps to at the HTTP boundary."
- "For every callback or hook parameter at an async boundary, what is the
  exact type signature? If the caller is async and the callback is sync, how
  is event-loop blocking prevented?"

API contracts must be defined BEFORE implementation tickets are created. Not
after. Not "TBD." Now.

### Contract Precision Demands

For every tool definition, external API call, or upstream service integration:

- "What are the EXACT field names the upstream system expects? Show me the
  source — OpenAPI spec, actual API response, or curl transcript."
- "Is there a known mismatch between common/intuitive names and the actual API
  field names? Document it explicitly." (e.g., `fromAirport` not `origin`)
- "What does the upstream return on success vs. error? Show me a real response
  payload, not a guess."
- "What is the authentication mechanism? Header name, token format, where does
  the token come from at runtime?"

Do not accept: Plausible-sounding field names without verification. LLM-generated
API schemas are wrong by default until proven against the real API or spec.

**Internal seams:** Contract precision applies to internal function signatures
at critical boundaries, not just external APIs. If a function accepts
configuration, ask: "Does the caller pass a loaded config object, or a
path/locator? Where do security-relevant settings (classification,
permissions, guardrail config) come from at runtime — hardcoded, env var,
or loaded from file?" A bag type (e.g., `config: Any`, `options: dict`) at a
module boundary defers the design question into implementation.

**Hard rule:** Tool definitions with unverified field names are flagged as
Inferred in the Assumption Register and cannot enter the DAG until verified.

### Trace and Log Data Safety

For any data model that appears in logs, traces, audit events, or debug output:

- "Does this object carry raw values (arguments, responses, user content) or
  digested summaries (sorted-key hash, truncated preview)?"
- "Are these objects immutable/frozen? Could a downstream consumer mutate them?"
- "Could raw values in traces leak sensitive information (PII, secrets, API
  keys, classified data)? If so, the trace model must carry summaries, not
  raw values."

### Implementation Topology Demands (Brownfield)

For brownfield projects, after all components and contracts are resolved:

- "For each feature in the MTP, which EXISTING file(s) will change?"
- "Will any new packages, directories, or modules need to be created? If yes,
  justify why the existing structure can't absorb the work."
- "For each proposed component in the Component Map, does a module with that
  responsibility already exist? Name the file path."
- "What is the existing function signature closest to what you're building?
  Can you add a parameter to it instead of creating a parallel function?"

**Hard rule:** If the user says "create new package X" and a package with
overlapping responsibility already exists, challenge with AP-9: "Why can't
this live in [existing package]?" The result is PRD §8b (Implementation
Topology) — a table mapping every ticket to MODIFY/CREATE + file paths.

### Pre-Existing Component Audit

For every component marked "pre-existing (not a ticket)" in the Component Map
or brownfield scan — i.e., something the plan depends on but does not modify:

- "What specific operations does this component currently support? List them."
- "Does it support the operations the new tickets require? Show me the code
  path, API endpoint, or test that proves it."
- "If a required capability is missing, does this component need a modification
  ticket — or is the architecture decision that depends on it wrong?"

Do not accept: "Component X handles Y" without evidence that it handles
the *specific* operations the new tickets require (correct auth mechanism,
correct schemas, correct response format).

**Hard rule:** Every pre-existing component that new tickets depend on must
have its assumed capabilities verified against code or runtime evidence. If
verification reveals a capability gap, either add a modification ticket for
that component or revisit the Phase 2 architecture decision that assumed
the capability existed.

**Scope estimation:** When a capability gap is found, enumerate every
operation the component currently supports AND every operation the plan
requires. The delta between these two sets is the real ticket scope. If the
delta is large (>50% of the component's existing code), challenge whether
modifying this component is the right approach — the architecture decision
that selected it may need revisiting.

### Anti-Pattern Detection

During Phase 2, actively scan for anti-patterns AP-1 through AP-13 from
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
- [ ] Tool/API field names are verified against upstream source (not guessed)
- [ ] Mock dependencies have been identified with real-integration-test plans
- [ ] No unresolved anti-patterns remain (AP-1 through AP-13)
- [ ] If brownfield: Implementation Topology (§8b) maps every ticket to
  MODIFY/CREATE + file paths; zero unjustified CREATE actions
- [ ] If brownfield: every pre-existing component's assumed capabilities are
  verified against code or runtime evidence (Pre-Existing Component Audit)
- [ ] If brownfield: Exemplar files identified for each ticket (AP-13) —
  at least one existing file per ticket that demonstrates the correct pattern
- [ ] Every proposed ticket is scoped to ≤5 production files (context budget,
  AP-12 prevention)
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

**Edge-case unknowns within approved features:** If the user committed to a
feature but can't detail a specific edge case or behavioral choice, offer
2-3 common patterns as a forced choice instead of blocking. The feature is
already approved — the user needs help specifying behavior, not deciding
scope. Present options concretely:

> "You said the system calls tools. When a tool call completes but the model
> returns no text, common patterns are: (a) empty response, (b) synthesized
> summary from tool results, (c) error message. Which matches your intent?"

This is NOT suggesting features (Persona Rule #2) — the feature exists. It
is offering bounded implementation options for an acknowledged requirement
the user can't detail from memory alone. If none of the offered options fit,
the user describes what they want. If the user still can't decide, record as
Deferred with a named validation gate.

---

## Focused Re-Interrogation

After the initial Phase 1 or Phase 2 pass, either the agent or user may
request a focused re-interrogation on a specific area (e.g., security,
performance, error handling, data model). This adds depth without restarting:

1. Agent identifies the focus area from Contested or low-confidence items
2. Ask 3-5 targeted questions on that area only
3. New resolutions add to the Convergence Ledger without resetting it
4. Repeat for additional focus areas as needed

Use when: persistent Contested items, user seems uncertain about a specific
domain, or Phase 2 reveals a deep technical area that Phase 1 skimmed.

---

## Advanced Elicitation Methods

When the standard adversarial challenge isn't breaking through a Contested
item, offer the user an alternative reasoning lens:

- **Pre-mortem:** "Assume this already failed. Why did it fail?"
- **Inversion:** "How would you guarantee this project fails?"
- **Constraint Removal:** "What if you had no constraints? What would change?"
- **Analogical:** "What other domain solved a similar problem? What did they do?"

These are optional — offered only when the user seems stuck and the standard
interrogation isn't resolving the issue.

---

## Constitution Gate

During Phase 2, every proposed component must pass the user's declared
constitution principles (from Phase 0) in addition to the standard tests.

- "Your constitution says '[principle]'. Does this component violate it?"
- If yes: the component must be cut or the constitution must be amended
  (amendments require explicit user acknowledgment and are recorded in the
  Complexity Justification Register)
