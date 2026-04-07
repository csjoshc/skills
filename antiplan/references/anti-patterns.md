# Anti-Patterns

Detection checklist for the Challenger subagent (Phase 3) and for the main
agent during any phase. When an anti-pattern is detected, name it explicitly,
quote the detection signal, and demand resolution before proceeding.

Each anti-pattern includes:
- **Detection signals** — what to look for in the plan or user's statements
- **Challenge questions** — what to ask the user or flag to the planner
- **Historical example** — how this anti-pattern manifested in the original
  plan-rebuild-discard incident that motivated this skill

---

## AP-1: Speculative Architecture

**Definition:** Building components, services, or abstractions for use cases
that have not been explicitly demanded by a user story.

**Detection signals:**
- Component exists but maps to no Phase 1 feature
- Justification uses future tense: "will need", "might want", "could support"
- Component name contains "base", "abstract", "generic", "extensible"
- Architecture diagram shows a component with no data flowing through it

**Challenge questions:**
- "Which Phase 1 user story requires this component?"
- "What happens if we delete this and build it later when actually needed?"
- "How many of the 'future' use cases have been explicitly requested?"

**Historical example:** Building a REST BFF, WebSocket layer, and MCP bridge
simultaneously when only one communication path was needed. The "flexible
multi-protocol architecture" was never validated against actual requirements.

---

## AP-2: Post-Hoc Rationalization Documents

**Definition:** Creating planning documents that describe what was already
built rather than guiding what should be built. The documents justify existing
decisions rather than making forward-looking choices.

**Detection signals:**
- Plan describes the system as-is rather than as-intended
- Document was created AFTER implementation started
- Multiple plan versions exist (v1, v2, v3, v4) with increasing scope
- Plan references code that already exists rather than code to be written

**Challenge questions:**
- "Was this plan written before or after the code it describes?"
- "Does this plan make any decisions, or does it merely describe what exists?"
- "If I gave this plan to a new developer, could they build the system from
  scratch — or would they need to look at the existing code?"

**Historical example:** Four design documents created across plan versions,
each rationalizing the current state of a partially-built system rather than
directing its evolution. The documents grew in complexity but not in clarity.

---

## AP-3: Ticket-Closure Loop

**Definition:** Agents optimize for completing tickets rather than producing
a working system. Each ticket is "done" in isolation, but the system doesn't
work when assembled.

**Detection signals:**
- High ticket completion rate but no end-to-end passing test
- Tickets are validated by unit tests with mocks, not integration tests
- "All tickets complete" but manual testing reveals fundamental issues
- Ticket acceptance criteria reference internal implementation details rather
  than user-visible behavior

**Challenge questions:**
- "After completing these 5 tickets, will the system actually run and serve
  a user request end-to-end?"
- "Where in this ticket sequence does someone actually start the system and
  try to use it?"
- "What is the first ticket that produces something a human could click on?"

**Historical example:** 29 tickets planned and executed sequentially. Ticket
completion rate was high, but the system had dead code paths, unreachable
routes, and broken streaming — all discovered only during manual testing after
all tickets were "done."

---

## AP-4: God Function

**Definition:** A single function, module, or service that accumulates
responsibilities because "it's easier to put it here." Eventually becomes
untestable and un-refactorable.

**Detection signals:**
- A component described as "orchestrating" or "managing" multiple unrelated
  concerns
- Function signature with >5 parameters or >3 type union parameters
- Component name is vague: "handler", "manager", "processor", "engine"
- Test for the component requires >3 mocked dependencies

**Challenge questions:**
- "Name this component's single responsibility in one sentence without 'and'."
- "If I split this into two components, where is the natural seam?"
- "Why do these [N] concerns need to live in the same module?"

**Historical example:** A BFF service that handled WebSocket connections, REST
endpoints, MCP tool registration, session management, and streaming — making it
impossible to test any concern independently.

---

## AP-5: Mock-Validated Integration

**Definition:** Integration between components is "tested" by mocking the other
side, so the test validates the mock's behavior rather than the actual system.

**Detection signals:**
- Integration test file imports mock/stub/fake of the dependency
- Test passes but the actual system call fails with a different contract
- No test in the suite makes a real HTTP/DB/queue call
- "Integration" test runs in <100ms (suspiciously fast for real I/O)

**Challenge questions:**
- "This test mocks [dependency]. How do you know the mock matches the real
  behavior?"
- "When was the last time someone ran this against the real [dependency]?"
- "If the real [dependency] changes its contract, which test catches it?"

**Historical example:** All component tests passed with mocked dependencies.
The actual streaming protocol, WebSocket handshake, and data server queries
all failed on real connections — failures invisible until manual testing.

---

## AP-6: Untestable Abstraction

**Definition:** A requirement or component that cannot be verified with a
concrete test without first building significant infrastructure that doesn't
yet exist.

**Detection signals:**
- Acceptance criteria reference behavior of components not yet built
- Testing requires "set up the entire system first"
- The component's test would be the same as the end-to-end test of the
  whole system
- No one can write a given/when/then for this component alone

**Challenge questions:**
- "Write me one test for this component that I can run today."
- "What infrastructure must exist before this component can be tested?"
- "Can we break this into a part that's testable now and a part for later?"

**Historical example:** Requirements written at the "system" level ("the agent
should respond with context-aware answers using tools") with no way to validate
individual components without the full pipeline running.

---

## AP-7: Premature Horizontal Expansion

**Definition:** Building breadth (many features at the same abstraction level)
before building depth (one feature working end-to-end).

**Detection signals:**
- Tickets are grouped by layer (all API endpoints, then all UI pages, then
  all data models) rather than by feature
- Phase 1 features are being built in parallel across all layers
- No single user flow works end-to-end until late in the ticket sequence
- The word "scaffold" appears in ticket titles

**Challenge questions:**
- "After ticket 3, can a user complete one entire flow start to finish?"
- "Why are we building 5 API endpoints before we know if endpoint 1 works
  with the UI?"
- "Can we reorder to finish one flow completely before starting the next?"

**Historical example:** Building the full REST API surface (5 endpoints), then
the full UI (5 pages), then "integration" — discovering at the integration
phase that the API shape didn't match what the UI needed.

---

## AP-8: Ceremony as Rigor Substitute

**Definition:** Process artifacts (tickets, design docs, review checklists,
test plans) that create the appearance of rigor without actually enforcing
quality. The ceremony is confused with the outcome.

**Detection signals:**
- Many tickets, detailed acceptance criteria, multiple plan documents — but
  the system doesn't work
- Review gates exist but are passed by the same agent that did the work
- "TDD" claimed but tests were written after implementation
- Quality metrics (code coverage, lint pass) are all green but user-visible
  bugs exist
- More time spent on planning documents than on running code

**Challenge questions:**
- "Which of these process steps actually caught a real bug or design flaw?"
- "If we removed this review step, would the outcome change?"
- "Is this documentation read by anyone, or is it write-only?"
- "Can you show me a case where this gate prevented a bad change?"

**Historical example:** 14 FRs, 43 tickets, 4 design documents, ticket-critic
reviews, TDD enforcement — all gates passed by the same LLM agent. The working
system was ultimately discovered through commits named "fix stuff", "fix",
"cleanup", after ripping out the majority of generated code.

---

## Usage by Phase

### Phase 1-2 (Main Agent)
Scan the user's responses for anti-pattern signals. When detected, name the
anti-pattern, explain the risk, and challenge the user directly.

### Phase 3 (Challenger Subagent)
Systematically review the planner's DAG against ALL 8 anti-patterns. For each
ticket and each gate, check if any detection signal applies. Report findings
as a structured list:

```
AP-[N] detected in T-[X]:
  Signal: [quoted detection signal]
  Challenge: [specific question or demanded change]
  Severity: BLOCK | WARN
```

- BLOCK: DAG cannot proceed until resolved
- WARN: Planner can accept with justification or escalate to user
