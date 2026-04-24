# Anti-Patterns

Detection checklist for the Challenger subagent (Phase 3) and for the main
agent during any phase. When an anti-pattern is detected, name it explicitly,
quote the detection signal, and demand resolution before proceeding.

Each anti-pattern includes:
- **Detection signals** — what to look for in the plan or user's statements
- **Challenge questions** — what to ask the user or flag to the planner
- **Historical example** — how this anti-pattern manifested in the original
  plan-rebuild-discard incident that motivated this skill

**Cross-reference.** AP codes are the design-time altitude of the
pattern taxonomy. For the diff-time (ARCH-\*) and mechanical (M-code,
P5) counterparts of each AP, see
[`~/.skills/reviews/cross-reference.md`](../../reviews/cross-reference.md).
When an AP is flagged at Phase 2, the cross-reference gives the
downstream code smell the speculation is flirting with — cite it in
the challenge to make the design-time consequence concrete.

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
- Ticket touches an external boundary (API, LLM, database, stream protocol)
  but no AC specifies what happens when that boundary fails or is unreachable
- All ACs describe happy-path outcomes; no AC uses "given [dependency] is
  unavailable/unreachable/returns error" or equivalent negative-path language
- Error handling described only as "return error response" with no specificity
  about what the user sees, what gets logged, or whether the error propagates
- A single AC uses "wire X into Y" or "integrate X with Y" without naming
  specific function calls, constructor parameters, or event emissions at the
  module boundary — each crossing point must be a separate AC

**Risk tagging (Phase 3):** When the planner constructs the DAG, any ticket
whose scope includes a call across a process, network, or provider boundary
should carry an inline risk tag: `[FALLIBLE_IO: <boundary name>]`. This tag
signals downstream skills (spec-writer, ticket-critic) to require explicit
failure-path coverage. If a tagged ticket has zero negative-path ACs, the
challenger flags it as AP-3.

**Challenge questions:**
- "After completing these 5 tickets, will the system actually run and serve
  a user request end-to-end?"
- "Where in this ticket sequence does someone actually start the system and
  try to use it?"
- "What is the first ticket that produces something a human could click on?"
- "This ticket calls [external boundary]. What does the user see when that
  call fails?"

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

## AP-9: Greenfield Hallucination

**Definition:** The implementing agent treats a brownfield modification as a
greenfield build, creating new packages, directories, or files that duplicate
functionality already present in existing modules.

**Detection signals:**
- Ticket says "create package X" when a package with overlapping responsibility
  already exists in the codebase
- New directory structure doesn't match the project's existing naming convention
- New files duplicate functions, types, or classes already present in existing modules
- The plan doesn't reference any existing file paths — only abstract component names
- Package/module names diverge from the project's established naming pattern
- Scope lines use vague component names instead of concrete file paths

**Challenge questions:**
- "Which EXISTING files does this ticket modify? If the answer is 'none — it
  creates new files,' justify why the existing modules can't absorb this work."
- "Is there an existing module that already does 60%+ of what this ticket proposes?
  Why not extend it?"
- "Does this new package/directory name follow the project's naming convention?
  What is the convention?"
- "Show me the existing function signature that is closest to what you're building.
  Why can't you add a parameter to it instead of creating a parallel function?"

**Historical example:** A plan specified `packages/chat-orchestration/` as a new
package when the codebase already had `packages/c3-ai-orchestration/` with
`run_chat_turn()` — the exact function the plan described. The implementing
agent created a parallel package with duplicate types, duplicate config loading,
and wrong package names, producing code that couldn't integrate with the existing
BFF because it imported from the wrong module.

**Negative example from evaluation:** An implementing agent was given a
brownfield-context that used conceptual paths (`packages/orchestration/`)
instead of `ls`-verified paths (`packages/c3-ai-orchestration/`). The agent
created `packages/chat-orchestration/` importing `chat_orchestration` —
a package that didn't exist. Every downstream ticket failed to integrate
because imports pointed to the invented package name.

**Prevention:** Every ticket scope line must specify MODIFY or CREATE at the file
level. If a ticket has zero MODIFY lines and only CREATE lines for a brownfield
project, it triggers AP-9 review. The Phase 0 brownfield scan and §8b
Implementation Topology exist specifically to prevent this.

---

## AP-10: Silent Failure Suppression

**Definition:** The implementing agent writes code that catches errors silently
— logging them to a developer console or swallowing them entirely — instead of
surfacing them to the user or halting visibly. The system appears to work
because it doesn't crash, but it is producing wrong or missing results.

**Detection signals:**
- Acceptance criteria use "the system should handle errors gracefully" without
  specifying what the user sees on failure
- Try/catch blocks that log and continue without returning error state to caller
- Default/fallback values that mask missing data (empty string, placeholder text,
  hardcoded "Loading..." that never resolves)
- Test assertions that check "no exception thrown" without checking the output
  is correct
- Error-handling code paths that suppress the error rather than propagating it

**Challenge questions:**
- "What does the user SEE when this fails? Not what does the log say — what
  does the person at the keyboard see?"
- "If the LLM call times out, does the UI show a stuck spinner forever, or
  does it show an error within N seconds?"
- "Show me the acceptance criterion that tests the failure path with a
  user-visible assertion, not just 'no crash'."

**Source:** DAPLab Columbia (Category 9: Exception & Error Handling), observed
across Claude, Cline, Cursor, V0, and Replit. Agents prioritize runnable code
over correct code by suppressing errors that make the app appear functional.

---

## AP-11: Completion Drive

**Definition:** The implementing agent optimizes for marking tickets "done"
rather than producing a working system. Manifests as: rewriting tests to match
broken behavior, loosening assertions, adding retries to mask flaky failures,
or declaring "ready" without reading linked dependencies.

**Detection signals:**
- Test was modified in the same commit as the implementation to make it pass
  (test changed to match code, not code changed to match test)
- Assertion thresholds relaxed without justification ("changed from assertEqual
  to assertAlmostEqual" or "increased timeout from 5s to 60s")
- PR description says "all tests pass" but the test is trivial (e.g., asserts
  only that the function doesn't throw)
- Ticket marked complete but no integration gate has run
- Agent summary says "task complete" but the system doesn't actually run

**Challenge questions:**
- "Was this test written before or after the implementation it validates?"
- "If I run this ticket's output against the NEXT ticket's preconditions,
  does it actually work — or does it only work in isolation?"
- "Show me the commit where the test was added vs. the commit where it was
  modified. Are they the same?"

**Source:** ctoth/claude-failures ("completion drive", "hiding bugs instead of
fixing them"). Also observed as AP-3 (Ticket-Closure Loop) at the individual
ticket level rather than the graph level.

---

## AP-12: Context Rot

**Definition:** As the implementing agent's context window fills with code,
diffs, and prior conversation, it progressively loses track of constraints
declared earlier — project constitution, naming conventions, existing test
patterns, module boundaries. The agent's output quality degrades silently
as the session length increases.

**Detection signals:**
- Early tickets follow conventions; later tickets drift (different naming,
  different patterns, different test structure)
- Agent creates a file that duplicates functionality already present in a file
  it modified earlier in the same session
- Constitution principles or AGENTS.md rules are violated in late-session
  tickets despite being respected in early ones
- Agent asks a question that was already answered earlier in the session
- Import paths or package names are wrong in ways that suggest the agent
  forgot the project structure

**Challenge questions:**
- "Is this ticket small enough that an implementing agent can complete it
  within a single context window, including reading all prerequisite files?"
- "What is the maximum number of files the implementing agent needs open
  simultaneously to complete this ticket? If >10, the ticket is too large."
- "Does this ticket require the agent to remember decisions from a prior
  ticket, or is it self-contained with explicit file references?"

**Prevention:** Ticket scope must be bounded to fit within a single agent
session. Each ticket's `read_first` list (see ticket template) makes
prerequisites explicit rather than relying on session memory. The worked
example's 7-ticket decomposition was calibrated for single-session execution.

**Source:** GSD/get-shit-done ("context rot" — quality degradation as context
window fills), DAPLab (Category 8: Codebase Awareness & Refactoring Issues),
ctoth/claude-failures ("feedback loops — same problems rediscovered 4 times
across sessions").

---

## AP-13: Exemplar Blindness

**Definition:** The plan describes what code should do in prose, but does not
point the implementing agent at existing code that demonstrates the correct
pattern. The agent then invents its own pattern — which may be plausible but
incompatible with the codebase's established conventions.

**Detection signals:**
- Ticket says "create a new endpoint following project conventions" without
  naming which existing endpoint to copy from
- Ticket says "add tests" without pointing to an existing test file that
  demonstrates the test pattern (fixtures, assertions, setup/teardown)
- Component description uses abstract language ("a service that manages X")
  instead of referencing an existing similar service
- The plan has no `Exemplar files` entries despite being brownfield
- Implementing agent produces code that works but uses a different style,
  different import pattern, or different error-handling approach than the
  rest of the codebase

**Challenge questions:**
- "Which existing file in the codebase is the closest analog to what this
  ticket produces? Name it — the implementing agent should read it first."
- "If I showed this ticket to a new developer with no other context, could
  they find the right file to copy patterns from? Or would they guess?"
- "Does the test for this ticket follow the same fixture/assertion pattern
  as the existing test suite? Which test file is the exemplar?"

**Prevention:** Every ticket in a brownfield project must have an `Exemplar
files` field listing 1-3 existing files that demonstrate the correct pattern.
The implementing agent reads these BEFORE writing any code. This is the
strongest available defense against AP-9 (Greenfield Hallucination) at the
execution level.

**Source:** ralph-wiggum-brownfield (`exemplars/` directory concept —
canonical pattern files the agent must copy from rather than invent).

---

## Usage by Phase

### Phase 1-2 (Main Agent)
Scan the user's responses for anti-pattern signals. When detected, name the
anti-pattern, explain the risk, and challenge the user directly.

**Planning-phase anti-patterns** (AP-1 through AP-9): detected during
requirements and architecture interrogation.

**Implementation-phase anti-patterns** (AP-10 through AP-13): detected during
ticket construction. These manifest when the implementing agent executes the
plan, but the planner can prevent them by structuring tickets correctly:
- AP-10 → require failure-path ACs with user-visible assertions
- AP-11 → require test-before-implementation ordering in ticket scope
- AP-12 → bound ticket scope to single-session size with explicit read_first
- AP-13 → require exemplar file references in every brownfield ticket

### Phase 3 (Challenger Subagent)
Systematically review the planner's DAG against ALL 14 anti-patterns. For each
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

### Implementation-Phase Detection (for integration gates)

AP-10 through AP-14 are primarily caught DURING implementation, not during
planning. Integration gate tickets should include detection criteria:

- **AP-10 check:** Gate must test at least one failure path with a user-visible
  assertion (not just "no crash")
- **AP-11 check:** Gate verifier must not be the same agent/session that
  implemented the feature tickets
- **AP-12 check:** If late-session tickets show convention drift, flag for
  re-implementation in a fresh session
- **AP-13 check:** Code review step in gate verifies new code matches exemplar
  patterns (imports, naming, test structure)
- **AP-14 check:** Orchestrator console output is compared against the raw
  subprocess log; any event present in the log but absent from console output
  is a fidelity gap that must be investigated

---

## AP-14: Orchestrator Observability Blindspot

**Definition:** The orchestration layer's own monitoring, logging, dependency
wiring, or event parsing silently loses fidelity — making healthy runs look
broken and broken runs look identical to healthy ones. The operator acts on
false signals (killing a working process, missing a real failure).

**Detection signals:**
- Console output shows fewer event types than the raw subprocess log contains
- Parsed event objects have empty/default fields that the raw JSON populated
- Dependency edges declared in ticket frontmatter are absent from the scheduler
  DB with no warning emitted
- A pipeline control-flow decision (scheduling order, retry, timeout) depends
  on a parsed value that was silently defaulted due to schema mismatch
- Operator cannot distinguish a productive agent (doing grep/glob/read) from
  a stuck agent (zero-work loop) by watching the console

**Challenge questions:**
- "If I compare the raw subprocess log to what the operator sees on the
  console, is every event type represented? Which are filtered, and what is
  the justification for each filter?"
- "If the upstream CLI tool changes its JSON schema, which test catches the
  parse failure? Is there a contract test with a real output fixture?"
- "When a `Depends-On` edge fails to resolve, does the operator see a warning,
  or is the edge silently dropped?"
- "Can the operator distinguish 'agent is working but using cached tokens
  (cost=0)' from 'agent is stuck in a zero-work loop (cost=0)'?"

**Historical example:** Orchestra's JSONL parser assumed a flat `data` key
structure, but opencode nests events under `part` with camelCase keys. All
tool events parsed to empty objects. The console filter then hid grep/glob
events entirely. The operator saw only `[step_start]` / `[step_finish]
reason=None cost=0.0` — identical output for a productive agent and a stuck
one. Separately, `Depends-On: [T1, T2, T3]` silently resolved to zero edges
because short prefixes didn't match full slugs, causing an integration gate
to run before its dependencies with no warning.

**Prevention:**
- Contract-test every event parser against frozen real output fixtures from
  each supported runtime CLI
- Console event filter must justify every suppressed event type; suppressed
  types must still increment a visible counter ("12 events, 8 shown")
- Dependency edge resolution must warn on zero-match slugs
- Integration gates should include an orchestrator-fidelity check: compare
  raw log event count to parsed event count and fail on >5% discrepancy

---

## AP-15: I/O in the Pure Layer

**Definition:** Planning a domain / "pure" module that reaches directly for
I/O primitives — HTTP clients, filesystem handles, subprocesses, sockets,
the wall clock, random — instead of receiving the effect behind a port
the surrounding code injects. The module is declared pure in intent but
couples to infrastructure in shape, and every downstream problem
(untestability, mock-chained tests, swallowed exceptions around
`requests.get`, see also [ARCH-DEP-IO-IN-PURE](../../reviews/arch-violations/01-dependency-direction.md))
is pre-ordained at plan time.

**Detection signals:**
- Plan describes a domain/pure module whose function signatures contain
  URL strings, filenames, socket addresses, or client handles directly
- Module's dependency list is empty, yet the module performs network /
  disk / subprocess / clock reads at call time
- Testability section proposes mocking stdlib primitives (`requests`,
  `open`, `time.time`, `subprocess.run`) rather than substituting an
  injected protocol
- Plan uses phrases like "we'll add a port later" or "for now the
  function just calls the API directly"
- Ports are named in the architecture diagram but the domain function's
  parameters don't include any of them

**Challenge questions:**
- "Which injected protocols does this pure module depend on? If zero,
  where does its data come from?"
- "Can this function run in a process with no network, no filesystem,
  and no subprocess access? If not, why does it need them?"
- "When you unit-test this function, what are you mocking — your own
  protocol, or `requests`/`open`/`socket`/`datetime.now`?"
- "If the external service is rate-limiting us, who decides the retry
  policy — this function, or the adapter above it?"

**Historical example:** A review of a statistics module flagged "missing
error handling around `requests.get()`" — a diff-level nitpick. The
design-altitude question was never asked: why does a statistics module
know about HTTP at all? Had the plan named an injected `MetricsPort`
with a single `fetch(series_id) -> Series` method, the HTTP client would
have lived in an adapter, the retry and timeout policies would have had
a clear owner, and the test suite would have substituted an
in-memory implementation instead of monkey-patching `requests`.

**Prevention:**
- For every module labeled pure/domain in the plan, enumerate its ports;
  if the count is zero, assert "no I/O" and verify signatures take values
  not resource identifiers
- Function signatures in pure modules take domain values — never URL
  strings, file paths, socket handles, or a "client" argument whose type
  is stdlib
- Test plan for pure modules mocks only declared protocols; any
  stdlib-primitive mock is an escape hatch flagged in review
- When a port is genuinely deferred, mark the signature as `TODO(port)`
  and block merge until the port exists — do not allow an interim
  direct call

---

## AP-16: Eager Construction of Infrastructure

**Definition:** Planning a class or module that builds its own
infrastructure — database client, HTTP session, file handle, thread
pool — during construction or at import time, instead of receiving it
from a composition root. The class "supports DI" nominally (often a
defaulted constructor parameter) but reaches for the real dependency
whenever the default path is taken, which is always in production. See
also [ARCH-BND-EAGER-INIT](../../reviews/arch-violations/02-boundary-contracts.md).

**Detection signals:**
- Plan shows a class whose constructor takes `db=None` / `client=None`
  and falls back to a real constructor (`db or PostgresClient()`)
- Module-level statements like "the connection pool is initialized at
  import" or "the settings object is a singleton created on first
  import"
- Plan says "we'll add a DI framework later" — construction is eager
  today, parked forever
- Testability plan says "monkey-patch the class attribute" or "patch
  `module.DB_CLIENT`" for tests — patching infrastructure that shouldn't
  have been a module-level concern
- Architecture diagram has no composition root or bootstrap module; the
  question "where is Service X first assembled?" has no answer

**Challenge questions:**
- "At process start, in what order do things come up? Which module's
  import triggers which I/O connection?"
- "If I want to run this class in a unit test with no real database,
  what do I pass in?"
- "Name the composition root. Where in the code is this class first
  handed its real collaborators?"
- "Who closes the connections this class opens? Is lifecycle symmetric
  with construction?"

**Historical example:** A service class was written as
`def __init__(self, db=None): self.db = db or PostgresClient()`. The
plan said "supports dependency injection" because of the `db=None`
parameter, but every production caller invoked `Service()` without
arguments. The default path ran the real constructor, which opened a
TCP connection at object-creation time. Test suites monkey-patched
`module.PostgresClient` — leaking global state between tests and
masking a coupling that belonged at the composition root.

**Prevention:**
- Plan names the composition root explicitly: "Service X is assembled
  in `app/bootstrap.py` and handed to the HTTP router."
- Constructor parameters for infrastructure are required, not
  defaulted. If a default makes sense, it's a null-object or in-memory
  fake, never a real client.
- Module-level code never opens I/O. Connection pools, sessions, and
  singletons are created by the composition root and passed down.
- Class diagrams show arrows IN (received) and OUT (called); any "self
  creates X internally" arrow is the antipattern made visible.
