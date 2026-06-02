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

**Planning-phase anti-patterns** (AP-1 through AP-9, plus AP-15 through
AP-23 on the design side of the catalog): detected during requirements
and architecture interrogation.

**Implementation-phase anti-patterns** (AP-10 through AP-14, plus AP-18):
detected during ticket construction. These manifest when the implementing
agent executes the plan, but the planner can prevent them by structuring
tickets correctly:
- AP-10 → require failure-path ACs with user-visible assertions
- AP-11 → require test-before-implementation ordering in ticket scope
- AP-12 → bound ticket scope to single-session size with explicit read_first
- AP-13 → require exemplar file references in every brownfield ticket

### Phase 3 (Challenger Subagent)
Systematically review the planner's DAG against ALL anti-patterns listed in
`rubric.yaml` (the machine-readable source of truth — count rows there).
For each ticket and each gate, check if any detection signal applies. Report
findings as a structured list:

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

---

## AP-17: Cross-Package Consumer Integration Untested

**Definition:** Planning a package that ships a built artifact (`dist/`,
`lib/`, `build/`) without an acceptance criterion that exercises the
artifact through a real sibling consumer. Tests run against the
package's own source; the build emits dist; no one ever asks "does an
import from this dist actually resolve in someone else's toolchain?"
Path aliases (`@/`, `~/`, `#/`), `package.json#exports` mismatches, and
mis-bundled CSS / asset paths are the canonical failure surface.

**Detection signals:**
- Ticket produces a `dist/` artifact but every AC names files inside
  the package itself; no AC names a consumer
- Package source uses tsconfig path aliases but the build pipeline
  doesn't run `tsc-alias`, `vite-tsconfig-paths`, `rollup-plugin-alias`,
  or equivalent — the aliases ship verbatim
- `package.json#exports` map advertises subpath exports the build
  doesn't actually emit (e.g. `"./chat": "./dist/chat/index.js"` but
  build only writes `dist/index.js`)
- Brownfield context lists a package as "out of scope" but a Phase 1
  ticket adds it as a `workspace:*` dependency of an in-scope package —
  the package is now in scope as a transitive dep
- Slice gate runs producer-side unit tests + maybe a `/health` boot,
  but never a `pnpm dev` or `import` from a sibling that actually
  consumes the artifact

**Challenge questions:**
- "Name the file in another workspace package that imports from this
  package's `dist/`. What does it import? Does that import path exist
  in the emitted output?"
- "Does the build pipeline rewrite path aliases? Show the script line
  that does the rewriting."
- "Does any AC in this ticket boot a consumer? Or do all ACs check
  the producer in isolation?"
- "If a sibling package's `pnpm dev` fails on an import-analysis error
  pointed at this package's dist, which AC would have caught it?"

**Historical example:** A UI component library shipped 262 unrewritten
`@/components/...` import lines in `dist/`. The package's own tests
passed, the build emitted dist, every per-package gate was green. The
bug was dormant because the only consumer didn't depend on the package
yet. When a downstream ticket added the dependency, every consumer
boot crashed at Vite import-analysis — but the slice that introduced
the dep had already closed, and the next gate that booted a consumer
was three slices later.

**Prevention:**
- Every ticket that produces a `dist/` carries this AC verbatim:
  `! grep -rE "from ['\"](@/|~/|#/)" packages/<pkg>/dist/`
- Every ticket that produces a `dist/` carries a "consumer round-trip"
  AC: a sibling package or test scaffold imports from the producer's
  `package.json#exports` paths and the import resolves under
  `pnpm dev` (not just `pnpm build`)
- Brownfield context Phase 0 enumerates the transitive consumer/
  dependency graph for every in-scope package; out-of-scope packages
  that are workspace deps of in-scope ones get a "smoke status" field
  (green/red/unknown) and unknowns become baseline tickets

---

## AP-18: Gate-Closure Without Green Proof

**Definition:** A gate ticket marked `Stage: COMPLETE` whose proof
artifact contradicts the closure. The frontmatter says green, the
artifact says BLOCKED / FAIL / MISSING. Auto-commit on agent silence,
gate scope that forbids the changes its own ACs require, and proofs
that "explicitly catalog" failures without surfacing them as blockers
are the canonical mechanisms.

**Detection signals:**
- Gate ticket frontmatter `Stage: COMPLETE` AND its proof file
  contains `BLOCKED`, `FAIL`, `FAILED`, `ERROR`, `did not commit`,
  `no-op`, `cannot be executed`
- Gate ticket lists a proof file that does not exist on disk
- Orchestrator commit message reads "Agent did not commit" and the
  ticket is still COMPLETE
- Gate's Failure Protocol allows passing with "explicit cataloging"
  of the failure rather than blocking
- Gate ticket scope explicitly forbids the code changes its ACs
  require (deadlock that "passes" by skipping)

**Challenge questions:**
- "Open the proof file at the path this gate names. What's the
  literal verdict line? Does it match Stage: COMPLETE?"
- "Did an actual implementation commit land for this gate, or did the
  orchestrator auto-commit on silence?"
- "If the gate's proof says BLOCKED, why is Stage COMPLETE? Where is
  the follow-up ticket that resolves the block?"

**Historical example:** A Slice 3 frontend gate ticket required a
Playwright run, but Playwright wasn't installed and the ticket scope
forbade installing it. The proof file said "BLOCKED — gate cannot be
executed without code changes that are explicitly OUT of scope." The
orchestrator auto-committed on agent silence. Frontmatter went to
COMPLETE. Three slices later, the regression the gate was supposed
to catch surfaced in dev. The "green" pipeline was fictional.

**Prevention:**
- Gate Stage: COMPLETE requires a green-verdict proof file. Anything
  containing the deny-list strings above blocks closure.
- ticket-critic checks every gate ticket's proof artifact at
  closure time, not just at planning time.
- Orchestrator never auto-commits a gate ticket on silence. Gate
  closure is human-or-explicit-pass only.
- Gate scope must allow the changes its ACs require. If installing
  Playwright is required, the gate ticket includes that work.

---

## AP-19: Slice-Local Gate Blindness (Cumulative Gate Missing)

**Definition:** Each slice gate validates only its own slice. No gate
re-runs prior slices' smoke. A regression introduced by Slice 1 that
breaks Slice 0's proof hides until Slice 0's proof is re-run — which
no one does, because the only existing artifact is from Slice 0's
original closure. The first gate is also narrower than the existing-
system smoke baseline, so a brownfield migration starts mutating
without ever asserting the baseline boots.

**Detection signals:**
- Each slice gate's `Verify` runs slice-local commands only
- Gate artifact list does not include "all prior gates green at this
  commit"
- First gate in a brownfield DAG is narrower than the existing-system
  smoke (e.g. tests one new module + `/health` instead of booting the
  whole stack)
- Stack with multiple consumer/producer boundaries but only one gate
  boots the user-facing surface — and that gate is at the END

**Challenge questions:**
- "If Slice 1 introduces a regression that breaks a Slice 0 invariant,
  which gate catches it?"
- "Does the first gate boot what the user actually touches, or only
  the smallest changed unit?"
- "When Slice 3 closes, do you re-run Slice 0's, 1's, and 2's smoke
  against current HEAD? If not, how do you know none have regressed?"

**Historical example:** Four slice gates. Each ran its own slice's
checks. A Slice 0 / 1 workspace change re-emitted a sibling package's
dist with broken alias references. Slices 0, 1, 2 all closed green
because none of them booted the React frontend. Slice 3 was the first
gate that consumed the broken dist — and Slice 3's gate was bypassable
(see AP-18). The regression went undetected for the entire pipeline.

**Prevention:**
- Every gate's Verify section ends with `# rerun all prior gates`
  followed by the prior gates' smoke commands. Cumulative.
- BASELINE-FIRST rule for brownfield: the first ticket asserts the
  current system passes its existing smoke before any mutation.
  Anything that fails baseline becomes a precondition, not a
  prerequisite assumed-green.
- First gate boots the user-facing surface (browser / API consumer /
  CLI), even if running against pre-mutation code, so subsequent
  gates have a known-good baseline to diff against.

---

## AP-20: Runtime Service Dependency Untested

**Definition:** A package's runtime configuration (env vars, proxy
paths, OAuth redirect URIs, hardcoded URLs, docker-compose links)
references another package's service, but no AC boots both packages
together and exercises at least one round-trip of the dependent
contract. AP-17 covers build-time consumer integration (import from
dist); AP-20 covers runtime service contracts (HTTP, gRPC, queue,
OAuth) that AP-17 cannot see.

The canonical manifestation: a SPA's `vite.config.ts` proxies
`/auth/*` to `http://localhost:8000`. The plan treats the auth
service as out-of-scope. The local-stack script boots Vite on port
8000 (claiming the same port). The SPA renders cleanly; auth is
completely broken. Every per-package gate passes; the demo is
fictional.

**Detection signals:**
- Env var references between packages: `VITE_<X>=http://...:<port>`
  or `BACKEND_ORIGIN`, `API_URL`, `OAUTH_ISSUER`, `KEYCLOAK_URL`,
  `REDIS_URL` resolving to a port owned by another package — and no
  AC POSTs to that URL
- `proxy:` / `rewrite` block in vite/next/nginx config points at a
  sibling service, with no AC asserting that sibling is up and
  responding
- OAuth `client_id` / `client_secret` in one package; OAuth server
  in another; no AC completes a token exchange end-to-end
- docker-compose `depends_on:` chain where only one service is in
  scope and no ticket boots the full chain
- Plan moves auth / audit / classification responsibility to a
  sibling service but the gate's user-journey AC only "renders"
  the SPA without completing the auth flow
- Two entry points / packages default to the same port; no
  reconciliation in the plan
- First-five-minutes operator walkthrough requires booting services
  the plan didn't enumerate as in-scope

**Challenge questions:**
- "Name the file that owns each endpoint your in-scope package
  calls at runtime. Is that file in scope, or assumed-working?"
- "What is the first env var an operator sets to make your package
  work? What service does its value resolve to? Is that service
  booted by your plan?"
- "If `<other-package>` is out of scope but your runtime config
  references it, what AC asserts the runtime contract holds?"
- "Start fresh on a clean machine. Run only the commands in your
  README quickstart. Does the canonical user journey complete?"

**Historical example:** A SPA rebase added a workspace dep on a UI
library (caught by AP-17). The plan also moved auth-proxy paths to
point at an out-of-scope gateway service. AP-17's `dist/` ACs all
passed; the gateway was never booted by the local-stack script. The
SPA's user-surface AC only asserted HTTP 200 on `/`, which served
the SPA shell. Login was untested end-to-end. The pipeline closed
green; the demo never worked. Discovery only happened when an
operator tried to log in manually after Slice 5 closed.

**Prevention:**
- For every cross-package env var reference, an AC POSTs at least
  one canonical request through the dependency chain. URL is read
  from the env var, not hardcoded.
- For every docker-compose multi-service stack, one ticket boots
  the full stack and curls / scripts the integration boundary.
- "Runtime service" is a first-class scope category alongside
  "build artifact" and "test data" in brownfield-context Phase 0.
- Gate user-journey ACs complete a real loop (login → authed page,
  send → receive, request → response with claims), not just
  "shell renders."
- First-five-minutes operator walkthrough is recorded in
  brownfield-context and the first gate replays it verbatim.

---

## AP-21: Requirement Drift / Apologetic Workaround

**Definition:** A component, service, or config default stays in the
base plan after operational reality forced a workaround. The
workaround is captured as an override / overlay file whose comments
apologize for diverging from the base ("to restore the original
path…") instead of folding the divergence back into the base. The
idle service, the apologetic block, and the silently-broken
`depends_on` edge are the signals that the original requirement was
never validated against a named operator and that the workaround
became permanent without ever updating the design of record.

This anti-pattern is closely related to AP-1 (Speculative
Architecture) but distinct in timing: AP-1 is a component built for
hypothetical use; AP-21 is a component that *was* targeted at a real
use, met reality, lost the use, and stayed alive on a post-hoc
justification ("Linux operators / CI runners need it"). AP-2
(Post-Hoc Rationalization Documents) is the planning-doc cousin;
AP-21 is the same disease in configuration and runtime topology.

**Detection signals:**
- Override / overlay file contains prose like "to restore the X
  path", "this is no longer used", "we kept it because…", or "the
  bind-mount below was used in an earlier attempt but is no longer
  needed"
- Idle service: a container/process boots on the default profile but
  serves no traffic in the canonical operator flow (healthcheck
  passes; round-trips do not flow through it)
- `depends_on` / `requires` / `blocks` edge in the base file is
  silently removed or rerouted by the override
- Doc paragraph explaining "why we keep X" is longer than the cost
  of removing X
- Config default (model name, URL, endpoint, port) references a
  value the canonical operator path doesn't use, with the operator
  path documented in an override / `.local` / gitignored file
- A "production-ish" path documented alongside the actual dev path
  with no operator persona named for the production-ish path today
  ("Linux operators or CI runners" without naming a CI job or
  teammate)
- Gitignored file that exists in the working tree and documents how
  the system actually works (the divergence is load-bearing but
  unversioned)
- Base file and override file describe two different topologies and
  the operator only ever runs the override topology

**Challenge questions:**
- "If we strip `<component>`, name the operator persona who breaks
  *today*. Cite a CI job by file, a teammate by handle, or a
  deployment by environment — not 'Linux operators / CI runners'
  in the abstract."
- "Which compose profile / build flag / env path keeps `<component>`
  alive on the canonical dev machine? If none, why is it in the
  default profile instead of behind its own profile?"
- "Read the override file's prose aloud. If it apologizes for
  diverging from the base file ('to restore…'), the base file no
  longer reflects the actual design — the override does. Which one
  is authoritative?"
- "When did the workaround land relative to the base spec? If the
  workaround came after, what triggered it (memory limit, missing
  model, broken auth), and did that trigger get fed back to the
  spec or only to the override?"
- "How would a new operator distinguish a working `<component>`
  from a dead one? If `docker ps` / `ps aux` / `systemctl status`
  shows it healthy regardless, the healthcheck is lying about
  participation."

**Historical example:** A docker-compose `chat` profile defined an
`ollama` service in the base file. The dev mac couldn't allocate
the 16-32 GB Docker Desktop memory required for the 14B/35B models
the chat app expected, so an override file silently redirected
c3-chat to `host.docker.internal:11434` and removed the `depends_on:
ollama` edge. The dockerized `ollama-1` container kept booting on
`--profile chat up`, kept passing its `ollama list` healthcheck,
and served zero traffic — for the entire life of the override.
The override file's preamble apologized for the divergence with 15
lines of "to restore the dockerized ollama" instructions. New
operators looked at `docker ps`, saw ollama healthy, and debugged
the wrong process when responses misbehaved. The "Linux operators
or CI runners need an in-network inference target" justification
named no specific consumer. Antiplan never flagged the dead
container because the workaround landed *after* the base spec, in a
separate commit, with no re-interrogation of the base file.

**Prevention:**
- **Override-triggers-reinterrogation rule.** Adding a
  `*.override.*`, `*.local.*`, `docker-compose.override.yaml`, or
  equivalent overlay file is a design event, not a configuration
  event. It re-opens the base file for interrogation. The base
  file is not authoritative until the override is folded in or
  rolled back.
- **Named-operator rule.** Every component in the default boot
  path must have a named operator persona *today*. "Future Linux
  / CI runners" is a Tier 3 assumption (see ASSUMPTION_TIERS) and
  gates a separate ticket — it does not justify keeping the
  component in the default profile.
- **Apologetic-comment marker.** A comment block in a config file
  that explains how to "restore" the original design is an
  explicit AP-21 signal. Name it in the Challenger report and
  demand resolution: fold the override in, or move the
  unused-on-this-host service behind its own profile.
- **Profile-isolation for docker-compose.** Idle services move
  behind their own profile. If `--profile <X>` brings up `Y` and
  `Y` serves no canonical flow on the dev mac, `Y` belongs to
  `--profile <X>-full` (or `--profile linux-fallback`) or is
  deleted. `docker ps` on the canonical dev flow shows only
  services that do work.
- **Gitignored-but-load-bearing scan.** Any file in `.gitignore`
  that the operator must create to make the canonical flow work
  is a Tier 1 assumption and a ticket — not a footnote in
  README.

---

## AP-22: Hardened-but-Untested Pod Security Combo

**Definition:** A helm/k8s manifest stacks restrictive `securityContext`
flags — `readOnlyRootFilesystem: true`, `runAsNonRoot: true`,
`runAsUser: <non-zero>`, `capabilities.drop: [ALL]`,
`allowPrivilegeEscalation: false` — on a pod whose entrypoint is a
custom shell script and/or whose `containerPort` is a privileged port
(<1024), and the cycle never deploys the manifest against a real
cluster before the terminal gate. Each flag is defensible alone. The
combination is a runtime contract — emptyDir mounts that nginx PIDs
need, file ownership the non-root user actually has, busybox `cp`
quirks the script doesn't tolerate, port binds the dropped capabilities
no longer permit — and `helm lint` / `helm template` cannot exercise
any of it. The chart passes static review, the image passes its own
build, and CrashLoopBackOff is the first feedback the operator gets.

AP-22 is the design-time cousin of AP-19 (Slice-Local Gate Blindness):
AP-19 says "no gate booted the user-facing surface until the end";
AP-22 says "even the gate that does boot it is the *first* moment any
human will know whether your hardened pod actually starts." It also
sits adjacent to AP-3 (Ticket-Closure Loop) — every per-ticket AC
("helm template emits the Deployment", "image builds green") was a
mock for the question that actually mattered ("does this pod start in
a real kubelet").

**Detection signals:**
- Manifest combines `readOnlyRootFilesystem: true` + `runAsUser:` non-zero
  + `capabilities.drop: [ALL]` + `allowPrivilegeEscalation: false`,
  AND `containerPort:` <1024, AND a custom entrypoint script (`start-*.sh`,
  `entrypoint.sh`, `docker-entrypoint.sh`) that does file I/O at startup
- Chart's per-ticket ACs are all static (`helm lint`, `helm template`,
  `grep -E 'readOnlyRootFilesystem'`) — no AC `kubectl apply`s the
  manifest to a real kind/k3d/minikube cluster and waits for `Ready`
- Failure-path AC for the security context is hypothetical ("Given
  emptyDir volumes are missing, when deployed, then CrashLoopBackOff
  caught by IG-7G4") — the "caught at the terminal gate" clause is
  the smell; the terminal gate is the *first* deploy
- Image base + non-root UID combination is novel for the cycle
  (`nginx:1.27-alpine` + `runAsUser: 101`, `python:3.13-slim` +
  `runAsUser: 1000`) and the PRD does not name a prior cycle, prior
  image, or prior chart that has booted this exact combination green
- Chart inherits a security baseline from a sibling chart (c3-chat,
  c3-flight-mcp) but the new image runs a *different* entrypoint
  (nginx + start-nginx.sh vs python + uvicorn) — the baseline was
  validated against the sibling's entrypoint, not yours
- Cycle budget assumes one `make local-up` succeeds first try; no
  buffer for image-rebuild iteration (rc1 → rc2 → ... → rcN)

**Challenge questions:**
- "Name the prior cluster deploy where this exact combination of
  securityContext flags ran against this exact entrypoint script on
  this exact base image. Cite the proof artifact path, the cluster,
  the date — not 'we did this for c3-chat'."
- "`helm lint` and `helm template` will pass a chart that
  CrashLoopBackOff on first pod start. Which AC in this DAG runs
  `kubectl apply` (or `helm install`) against a real cluster and waits
  for `kubectl get pod -l app=... -o jsonpath='{...status.phase}'` to
  equal `Running`? If that AC is in the terminal gate, the terminal
  gate is the *first* deploy — name the budget for image-rebuild
  iteration in the cycle timeline."
- "Your `containerPort: 80` is privileged. `capabilities.drop: [ALL]`
  removes `CAP_NET_BIND_SERVICE`. What binds the socket? If the
  answer is 'nginx as user 101 because the alpine image grants the
  capability via file caps', cite the file-caps line in the base
  image. If the answer is 'it just works in our other charts', the
  other charts are running a different entrypoint."
- "Your entrypoint is `start-nginx.sh`. Read it line by line. Which
  lines do filesystem writes? Are the target directories covered by
  the `emptyDir` mounts you declared, or do they live under paths the
  `readOnlyRootFilesystem` flag blocks?"
- "If this pod CrashLoopBackOff's at terminal-gate time, what is the
  cost of the iteration loop? Image rebuild + workflow rerun + image
  pull + helm rollout — name the wall-clock budget. Is it inside the
  cycle's SC for time-to-green?"

**Historical example:** The `ui-ghcr-publish` cycle's c3-ui subchart
stacked `readOnlyRootFilesystem: true` + `runAsUser: 101` (nginx user
in nginx-alpine) + `capabilities.drop: [ALL]` + `allowPrivilegeEscalation:
false` + `containerPort: 80` + a custom `start-nginx.sh` entrypoint
that did `cp /etc/nginx/conf-templates/*.conf /etc/nginx/conf.d/` at
startup. Per-ticket ACs were all static — `helm lint`, `helm
template`, `grep -E 'readOnlyRootFilesystem'`. The failure-path AC
for the security context read literally:
"**Failure path:** **Given** emptyDir volumes are missing, **when**
deployed, **then** the c3-ui pod CrashLoopBackOff because nginx
cannot write its PID — caught at IG-7G4 by the make local-up wait
+ `detect_imagepullbackoff` extended message." The "caught at
IG-7G4" clause is AP-22 — IG-7G4 was the cycle's *first* deploy.
The terminal gate took two image rebuilds (rc1 → rc4 fix-cp,
rc4 → rc5 fix-port) plus a helm chart fix (emptyDir mount path) plus
a namespace-label fix to reach green. ~90 min of unplanned
iteration was eaten by the absence of a per-ticket deploy-smoke AC.

**Prevention:**
- **Real-cluster AC for every hardened-pod ticket.** Any ticket whose
  Files: list creates or modifies a manifest with the AP-22 flag
  combination (the four-flag signal above) carries this AC verbatim:
  `kubectl apply -f <rendered> --dry-run=server` AND
  `kind create cluster --name <ephemeral> && helm install --wait
  --timeout 90s` AND `kubectl wait --for=condition=Ready
  pod -l app=<x> --timeout=120s` — the wait is what proves it boots,
  not the apply.
- **Cycle budget rule.** PRD §6 Success Criteria must include a
  named buffer for image-rebuild iteration on any cycle that
  introduces a novel base-image + securityContext combination.
  Two rebuilds is the realistic floor on the first cycle; one is
  optimistic; zero is AP-22.
- **Entrypoint-script line-read.** Brownfield context includes a
  line-by-line read of every entrypoint script that runs under the
  proposed `securityContext`. Each filesystem write the script
  performs maps to a declared emptyDir mount or is a BLOCKING
  finding.
- **Privileged-port hand-off.** Any pod with `containerPort: <1024`
  AND `capabilities.drop: [ALL]` AND `runAsUser: <non-zero>` either
  (a) cites the file-caps line in the base image that grants the
  bind, (b) changes the port to >=1024 in the chart, or (c) is a
  documented Tier-3 assumption with a named ticket that proves the
  bind works on a real cluster *before* the terminal gate.

---

## AP-23: Publish ≠ Deploy

**Definition:** A cycle publishes container images to a registry
(GHCR, Docker Hub, ECR, internal Harbor) via a CI workflow whose
success criteria stop at `docker push` exit 0. No downstream job
runs the published image — even minimally — so the workflow is
green on images that `docker run` immediately exits 1 on. The DAG
treats "image in registry" and "image starts" as the same fact.
The first time anyone confirms the second is when an operator
pulls the image into a cluster and watches CrashLoopBackOff.

AP-23 is the build-artifact cousin of AP-17 (Cross-Package Consumer
Integration Untested) and AP-19 (Slice-Local Gate Blindness). AP-17
says "your dist/ is never imported by a real sibling"; AP-23 says
"your image is never *run* by a real consumer (a kubelet, a `docker
run --health-cmd`, a second job in the same workflow)." Like AP-17,
the failure surface is dormant until a downstream consumer pulls —
and like AP-19, the consumer is usually the terminal gate, which
means the bug has the entire cycle's runway to ship green.

**Detection signals:**
- CI workflow that runs `docker build` and `docker push` (or
  `docker/build-push-action`, `kaniko`, `buildah`) but has no
  subsequent step that runs the published image — not even
  `docker run --rm <pushed-image> --version` or a `crane validate`
  / `docker run --health-cmd` check
- PRD success criteria measure "image is pullable" or "tag exists in
  registry" but not "image starts and responds on its declared port"
- Per-ticket AC for the publish workflow lists `gh run view --log
  shows docker push exit 0` as the strongest postcondition; no AC
  pulls the image and runs it
- Multi-image matrix publish (N images per tag push) where each
  image's runtime is exercised only by a separate, later, manual
  ticket (`docker run` in a follow-up ticket's scope, or a "smoke"
  step in the terminal gate)
- Dockerfile changes a runtime layer (base image, entrypoint, user,
  workdir) but no AC in the publish ticket exercises the runtime —
  only the build
- Workflow's `permissions:` includes `packages: write` (push capable)
  but no companion job uses `actions/checkout` + `docker pull` +
  `docker run` to validate the artifact it just pushed

**Challenge questions:**
- "Name the workflow step (or ticket AC) that runs the *published*
  image — not the locally-built one, the one from the registry —
  before the terminal gate. If none, the publish workflow is
  asserting build-time facts about a runtime artifact."
- "`docker build` succeeding is not `docker run` succeeding. A
  Dockerfile can produce an image whose entrypoint exits 1 on first
  invocation. Which AC catches that? If the answer is 'the operator
  notices when helm install hangs', the operator is the test."
- "Your publish workflow pushes N images in parallel via a matrix.
  Each image has a different runtime contract (port, entrypoint,
  health endpoint). Which AC proves each image starts? If a single
  AC lumps all N together ('all 3 images pullable'), the verification
  density is N× too thin."
- "If a future contributor introduces a regression in `start-*.sh`
  or a Dockerfile `RUN` step that succeeds at build but fails at
  run, which gate catches it before merge? The publish gate? The
  terminal gate? Or production?"
- "Your `permissions: packages: write` workflow can push. Does it
  have `actions: read` + a follow-up job that pulls + runs what it
  pushed? Or is push-without-run the contract?"

**Historical example:** The `ui-ghcr-publish` cycle's
`publish-chat-images.yml` workflow ran a 3-row matrix
(c3-flight-mcp, c3-chat, c3-ui) producing
`ghcr.io/c3-joshchiu/c3-ui:v0.0.0-ui-rcN` on every `v*` tag. The
workflow's strongest success criterion was:
"Given the repo at a clean working tree with a working
`react/Dockerfile`, when the operator runs
`git tag v0.0.0-rcN && git push origin v0.0.0-rcN`, then
`publish-chat-images.yml` runs 3 matrix jobs producing
`ghcr.io/c3-joshchiu/{c3-flight-mcp, c3-chat, c3-ui}` each tagged
`:v0.0.0-rcN` and `:sha-<short>` ... *Verify:* `gh run view <id>
--log` shows three `docker push` steps with exit 0."
The next AC ran `docker run --rm -p 8080:80 <image>` — but only
"on a clean mac", manually. No CI job did this. The `v0.0.0-ui-rc2`
image shipped to GHCR with a broken `cp` invocation in
`start-nginx.sh` (busybox cp errored on existing target); workflow
green. The first signal was IG-7G4's `make local-up` watching the
pod CrashLoopBackOff. Three rc-tag iterations later the image
actually started. Between `docker push` and "image starts in
kubelet" the workflow contributed exactly zero evidence.

**Prevention:**
- **Run-the-pushed-image rule.** Any publish workflow that pushes
  to a registry includes a follow-up job (same workflow file,
  same tag-trigger, `needs:` the push job) that runs the
  *published* image — `docker pull && docker run --rm
  --health-cmd ... --health-interval 5s --health-retries 3
  <image>` is the floor. For multi-image matrices, the follow-up
  is itself a matrix that pulls + runs each image.
- **Image-runtime AC at publish-ticket level.** The ticket that
  authors the publish workflow carries an AC of the form: "the
  workflow run for tag T produces a pod-equivalent run record
  (workflow log, GitHub Actions job) showing each pushed image
  exited 0 from a non-trivial health probe within N seconds." Not
  "the operator runs docker run on their mac" — that AC is manual
  and not blocking.
- **Per-image runtime contract enumeration.** When the publish
  workflow is a matrix, the PRD enumerates each image's runtime
  contract (port, entrypoint, expected health endpoint, expected
  startup time) and the follow-up job exercises each contract by
  matrix row. A green push of one row does not validate another's
  runtime.
- **Build-vs-run separation in success criteria.** PRD §6
  distinguishes "build" SCs (image is pullable, layers are
  cached, multi-arch, signed) from "run" SCs (entrypoint exits
  0, health endpoint returns 2xx, declared port binds). A cycle
  that publishes an image without at least one "run" SC is
  AP-23 by construction.

## AP-24: Cycle-Path Coupling

**Definition:** Long-lived committed paths — proof directories, test
artifact roots, verify scripts, fixture folders, or doc filenames —
are named after the *cycle, ticket, gate, or slice* that created them
rather than the *test scope or feature* they actually exercise. The
name rots the moment the cycle closes, the ticket is renumbered, or
the gate is renamed; downstream readers see a path that points
nowhere conceptual ("what's `4G-ui-cycle`?") and cannot tell whether
the artifact is still load-bearing.

AP-24 is the path-and-filename cousin of constitutional-leakage
findings in source comments. Both come from authors importing the
planning artifact's organizing principle (cycle/gate/slice IDs) into
the long-lived tree where it has no audience.

**Detection signals:**
- Committed paths matching `proof/<N>G<n>-*`, `proof/[Ss]lice-<n>/`,
  `evidence/<cycle-slug>/`, or any artifact root whose top-level
  directory contains a gate ID, slice number, or ticket-ish slug
- Scripts named `scripts/verify-<ticket-id>.sh`,
  `scripts/test-<gate-slug>.sh`, `tools/<cycle>-smoke.sh`
- Test files like `tests/tickets/test_T732_*.py`,
  `tests/<cycle>/test_*.py` (note: a `tests/tickets/` directory is
  itself an AP-24 marker — tests should live by their *type*, not
  their *ticket*)
- Doc filenames `docs/PRD-<cycle>.md`, `docs/<gate>-cutover.md` kept
  in the long-lived `docs/` tree instead of `.plan/` or `.tickets/`
- e2e configs that hardcode `PROOF_DIR = "../proof/<gate-slug>/..."`
  in playwright/jest/cypress configs instead of taking the path from
  env
- Diff stats that show a new top-level directory whose name encodes
  the ticket lifecycle (e.g. `4G-ui-cycle/`, `IG-7G4/`) rather than
  the feature

**Challenge questions:**
- "When this cycle closes and someone reads `proof/4G-ui-cycle/`
  three quarters from now, what does the directory name tell them
  about the *test it contains*? If the answer is 'nothing — they'd
  have to open the spec to know', the name is a planning artifact
  leaking into the long-lived tree."
- "Is this proof / fixture / artifact directory load-bearing for any
  CI step or runtime code path? If yes, name it after the *step*
  (`proof/chat-stack-smoke/`); if no, gitignore it."
- "Why does the playwright config bake the gate slug into
  `PROOF_DIR`? An env-var default with a feature-scoped fallback
  costs three lines and outlives every gate."
- "If we rename this ticket from `4G-ui-cycle` to `chat-stack-rollout`
  next week, how many file paths change? Every `mv` is an AP-24
  data point."

**Historical example:** A frontend cycle named `4G-ui-cycle` shipped
playwright e2e tests that wrote artifacts to `proof/4G-ui-cycle/`.
`react/e2e/chat-stack-smoke.spec.ts` and `react/playwright.config.ts`
both hardcoded `PROOF_DIR = "../proof/4G-ui-cycle"`. `scripts/
smoke-chat-stack.sh` defaulted `PROOF_ROOT` to the same path. After
the cycle closed, three review rounds asked "what's `4G-ui-cycle`?"
and the answer was always "an old gate name". The fix was a
trivial rename to `proof/chat-stack-smoke/` and an env-var override
hook (`PROOF_DIR=$ROOT bash smoke.sh`) — but only after the slug had
been load-bearing for an entire merge cycle.

**Prevention:**
- **Name by scope, not by cycle.** Any committed path under `proof/`,
  `evidence/`, `tests/`, `scripts/`, or `tools/` must be named for
  what it tests / does, not what cycle created it. The PRD should
  reject task instructions that direct authors to create
  `proof/<gate>/...` paths in the committed tree.
- **Env-overridable artifact roots.** Test configs that need a
  writeable artifact path read it from `os.environ.get(...)` /
  `process.env.PROOF_DIR ?? <stable-default>`. The stable default
  is the feature-scoped name; CI / orchestration can override per
  cycle.
- **`tests/tickets/` is gitignored.** Tests live by *type*
  (`tests/unit/`, `tests/infra/`, `tests/docs/`). A ticket-named
  test file is a planning artifact that belongs in `.tickets/` or
  inline in the ticket spec, not committed to source.
- **No verify-script-per-ticket.** If a ticket genuinely needs a
  one-off verify script, the spec captures the commands inline; the
  script itself stays in `.tickets/<ticket>/verify.sh` (gitignored)
  or in the ticket body, not in committed `scripts/`.

## AP-25: Vendor Coupling in Agnostic Identifier

**Definition:** A named entity — config filename, environment
variable, identifier, route, error code, log field, doc title —
contains a specific vendor / runtime / product token (`-dmr`,
`-ollama`, `DockerModelRunner`, `bedrock_`, `s3_`) when the design
explicitly says the choice of vendor is configurable or pluggable.
The name asserts a coupling the architecture denies. Every future
contributor who tries to swap the vendor either edits the name
everywhere or learns to live with a lie.

AP-25 is the long-lived-tree cousin of AP-1 (Speculative
Architecture). AP-1 builds infrastructure for a vendor the user
doesn't have; AP-25 names its infrastructure after a vendor the
user is supposed to be able to swap out.

**Detection signals:**
- Config files named `*-<vendor>.<ext>` (`agent.local-dmr.yaml`,
  `provider-ollama.json`) when the spec says provider/runtime is
  selected by env var or CLI flag
- Class / function / module names containing a vendor token when
  the same code paths handle multiple vendors (`OllamaClient` in a
  module that also handles vLLM, ChatGPT, and Bedrock)
- Env vars / config keys with vendor prefixes (`OLLAMA_BASE_URL`,
  `DMR_MODEL`) when the spec defines a runtime-agnostic surface
  (the project's own naming convention should be
  `LLM_BASE_URL` / `LLM_MODEL`)
- Doc page titles "Local dev with Docker Model Runner" when the
  doc actually describes a runtime-agnostic startup flow whose only
  DMR-specific content is the default `base_url`
- Mermaid diagram nodes labeled `Docker Model Runner` /
  `host.docker.internal:11434` in an architecture doc that's
  supposed to read at the abstraction level
- Test data tags hardpinning the vendor's source ref
  (`EMBEDDING_PULL_TAG = "hf.co/unsloth/..."`) in a doc-test that's
  supposed to assert the *alias* is documented

**Challenge questions:**
- "Name the alternate vendor / runtime / provider this code is
  supposed to support next. Now read the filename / class name /
  env-var name out loud as if that alternate were the active
  choice. Does it still make sense, or does it lie?"
- "If your design supports DMR *and* Ollama *and* a cloud OpenAI-
  compatible endpoint, which one of the three does the
  *filename* / *class name* / *env-var name* describe? If it
  describes one, the name picks a winner."
- "What is the cost of swapping vendors today? Count the files
  that would need to be renamed if `LLM_RUNTIME=dmr` became
  `LLM_RUNTIME=ollama` as the default."
- "Show me the docstring or doc page that calls this an
  abstraction. Now show me the filename. Do they agree?"

**Historical example:** A chat-BFF cycle landed
`packages/c3-chat/config/agent.local-dmr.yaml`. The `-dmr` suffix
came from the author's local dev environment (Docker Model Runner).
The same file is loaded for every local dev run regardless of
whether the operator's `LLM_RUNTIME` was `dmr` or `ollama`; the
operator just edits `provider.base_url` and `provider.model`. The
filename asserted DMR; the code denied it. Seven referrers
(Makefile, Dockerfile, scripts, docs, tests) had to be updated
when the file was finally renamed to `agent.local.yaml`. The same
PR's Mermaid diagrams labeled the LLM node `Docker Model Runner`
in a doc whose body claimed the stack was runtime-agnostic — a
direct AP-25 self-contradiction.

**Prevention:**
- **Name the abstraction, not today's instantiation.** If the spec
  promises agnosticism, every committed identifier reflects that.
  The vendor's name appears only in: (a) runtime-specific code
  paths that exist *to implement that vendor* (`provision_dmr()`),
  (b) `LLM_RUNTIME=<vendor>` values, (c) runtime-tagged fixtures
  inside `tests/`.
- **Project-prefixed env vars over vendor-prefixed env vars.**
  `LLM_BASE_URL` not `OLLAMA_BASE_URL`. `LLM_MODEL` not `DMR_MODEL`.
  If the same surface needs to accept both, normalize to the
  project prefix and route via a single override seam.
- **Doc-page titles describe the role, not the runtime.** "Local
  dev" rather than "Local dev with Docker Model Runner". The
  body's runtime-specific notes go in a side table or per-runtime
  subsection.
- **Catalog files for vendor-specific data.** When a runtime needs
  per-vendor source refs (Hugging Face tags, Ollama model names),
  extract them to a `config/<thing>-catalog.{json,yaml}` keyed by
  alias × runtime. The code path that consumes the catalog stays
  vendor-agnostic; the catalog itself names vendors because that's
  its job.


## AP-26: Operator Entry Point Not Smoke-Tested

**Definition:** A ticket introduces a user-facing command — a Makefile
target, wrapper script, docker compose invocation, or CLI entry point
that the operator is supposed to type to bring a system up — but no
acceptance criterion in any ticket runs the *literal* command from a
fresh-clone state and asserts it exits 0. Every individual piece may
have been verified (the docker build succeeds, the ASGI route returns
200, the unit tests pass), but the wrapper invocation that ties them
together has never been exercised end-to-end. The wrapper ships
broken in a way that's invisible to every gate.

AP-26 is the wrapper-and-compose cousin of AP-23 (Publish ≠ Deploy).
AP-23 catches "image pushed but never started." AP-26 catches "wrapper
written but never invoked." Both come from gating on the constituent
artifact (image, target body) rather than the operator action that
consumes it.

**Detection signals:**
- DAG introduces a user-facing command but no AC in any ticket runs
  the literal command from a fresh-clone state and asserts exit 0
- Per-ticket ACs verify infrastructure pieces (docker build, ASGI
  request, unit tests) but no AC executes the wrapper invocation an
  operator would actually type (`make compose-up`, `./deploy.sh`,
  `make demo`)
- Compose / Makefile / wrapper-script ticket references "profiles",
  "services", or "env_file" but no AC asserts that the operator
  invocation produces *only* the intended services / env / state
  (positive AND negative — intended up, unintended NOT up)
- Subagent verification path for an operator-target ticket uses an
  explicit-service or sidestep invocation (`docker compose up svc1
  svc2`) instead of the wrapper target the operator will type (`make
  compose-patent`) — the sidestep masks bugs in the wrapper
- Compose stack adds new profile-tagged services to a root compose
  that has default-profile services; no AC scopes the `up` invocation
  to the new profile's services explicitly AND no AC verifies the
  default services do NOT get auto-up'd by `--profile X`
- Ticket DAG defers operator validation to a downstream integration
  gate that is itself skip-prone (Docker not running, DB unreachable,
  Ollama unavailable) — when the gate skips, the operator command is
  never end-to-end-validated

**Challenge questions:**
- "Type out, character-for-character, the first command an operator
  runs to bring this up from a fresh clone. Now find the AC that
  executes that exact string. If you can't, AP-26 is live."
- "Did the build subagent for this ticket run the wrapper target, or
  did it run an explicit invocation that sidesteps the wrapper? If
  sidestep, the wrapper is unverified."
- "When the downstream integration gate skips because Docker / DB /
  Ollama isn't available, what code path verifies the wrapper? If
  the answer is 'the operator', AP-26 is live."
- "If a maintainer adds a new default-profile service to the root
  compose tomorrow, does this wrapper still work? If your AC scopes
  with `--profile X` only and not an explicit service list, the
  answer is no."

**Historical example:** A local-LLM migration consolidated the
patent-search app's docker-compose into a root compose under
`profiles: ["patent"]`. The new `make compose-patent` Makefile target
ran `docker compose --profile patent up -d --build` without an
explicit service list. The integration-gate tickets (T09, T12) used
explicit-service invocations during their own verification. The
operator's first invocation of `make compose-patent` failed
immediately because the root compose also had services without
profiles (a pre-existing toolkit reference stack) whose Dockerfile
had a separate pnpm install failure. The wrapper was unverified by
every AC in the DAG; the operator was the first to type the literal
string, and the bug surfaced on contact.

**Prevention:**
- **Every wrapper ticket has a wrapper-invocation AC.** If the ticket
  introduces `make X`, an AC must read: "Given a fresh-clone state
  (no caches assumed), when `make X` is run from the project root,
  then exit 0 AND only the intended state is produced."
- **Negative ACs for profile-scoped wrappers.** When the wrapper
  selects services by profile, the AC must verify that
  non-profile-tagged or other-profile services are *not* started.
  `docker compose --profile X ps` should show only the intended set.
- **Subagent briefs name the wrapper, not the sidestep.** When the
  build subagent verifies its own work, the verification command
  must be the operator's wrapper, not the explicit form. If a
  sidestep is necessary for the subagent's environment, that's a
  signal the wrapper itself can't be verified here — escalate to a
  named gate that *can* verify it.
- **Skip-prone gates have wrapper-invocation fallbacks.** If the
  integration gate that exercises the wrapper depends on optional
  infrastructure, the skip path must be loud (logged at WARNING)
  AND a hermetic alternative must exercise as much of the wrapper as
  possible (e.g., the wrapper's first phase that doesn't require the
  optional dep).


## AP-27: Brownfield Surface Lacks Runtime Contracts

**Definition:** The brownfield context document enumerates files at
their paths — surface table columns are "path", "role", "transitive
dependencies" — but doesn't capture the *runtime invariants* for each
surface: Pydantic schema constraints (min_length, max_length, regex),
enum value lists, base-image package availability, env-var
requirements, profile membership, default-vs-config behavior. The
document is a paths map; the spec-writer and downstream subagents
inherit the paths but have no contract for what those paths actually
*do* at runtime. Bugs surface mid-build when the subagent collides
with a contract the brownfield doc never captured.

AP-27 is the upstream cousin of every "subagent caught a deviation
mid-build" report. The deviation isn't an agent failure — it's a
brownfield failure. If the contract had been captured at Phase 0,
the spec would have prescribed the right approach the first time.

**Detection signals:**
- brownfield-context.md enumerates files at paths but doesn't capture
  the runtime invariants for each — Pydantic schema constraints,
  enum value lists, base-image package availability, env-var
  requirements, profile membership
- Brownfield doc lists a path like `app/X/Y.py` — verifier (Read or
  ls) was not run to confirm the path exists on disk; spec-writer
  inherits an incorrect path and downstream subagents must correct
  mid-build
- Brownfield doc references model / enum / Literal types by name but
  doesn't enumerate the actual values or field count — downstream
  tickets reason about "the 6 fields" when the schema has 9, or
  assume enum values that aren't there
- Brownfield doc captures a fact like "no profile" or "no Dockerfile"
  or "uses pnpm 8" as a path attribute but doesn't draw the
  implication — services without profile auto-up under any
  `--profile X`; absent Dockerfile = wrapper command will fail; pnpm
  version mismatch = lockfile install will fail
- Brownfield doc lists base images without inventorying which CLI
  binaries are present (curl, wget, jq, python, nc) — downstream
  healthcheck or startup commands prescribed in tickets reference
  binaries not in the image
- Brownfield doc was authored from prose / memory / a different
  repo's mental model rather than from `grep` + `Read` against the
  actual target repo; paths and types drift

**Challenge questions:**
- "For every path in the brownfield surface table, did you Read /
  ls / grep against the actual repo? If any were authored from
  memory or assumption, AP-27 is live."
- "For every model / schema / enum named in the brownfield doc, do
  you have the actual field count, value list, or constraint set
  enumerated? If the doc says 'PatentEnrichment', does it list the
  9 fields?"
- "For every fact like 'no profile' / 'no Dockerfile' / 'uses
  pnpm@8', does the doc draw the implication? 'No profile' means
  auto-up; 'no Dockerfile' means wrapper-target gap; 'pnpm@8' means
  lockfile compatibility risk."
- "For every base image you'll inherit (`python:3.13-slim`,
  `nginx:alpine`, `node:20-alpine`), do you know which CLI binaries
  are present? If a ticket prescribes `curl http://X/health`, is
  curl in the image?"

**Historical example:** A brownfield-context.md for a local-LLM
migration listed `app/ingestion/silver_storage.py` as the location
of the `get_pending_gold` query. The actual file was at
`app/storage/silver_storage.py`. The spec-writer copied the wrong
path forward into T04. The build subagent discovered the correct
path at build time and patched silently in its final report. The
same brownfield doc named `PatentEnrichment` as the Gold schema
but didn't enumerate its 9 fields; the ticket prose said "all 6
fields" and the build subagent had to fill in 9. The doc captured
the root compose's "no profile" toolkit services as a fact but
didn't draw the implication ("operator wrapper must scope services
explicitly") — the operator hit the gotcha on first invocation.

**Prevention:**
- **Brownfield Phase 0 = grep + Read, not prose.** Every path in the
  brownfield surface table must be backed by an actual file-read or
  glob during Phase 0. The authoring agent's transcript must show
  the verifier ran.
- **Runtime invariants are columns in the surface table.** For every
  surface, capture: schema constraints (`min_length=4`), enum values
  (`{pending, complete, failed}`), profile membership (`no profile`
  + implication: "auto-up gotcha"), base-image binaries available
  (`nginx:alpine has wget, no curl`), env-var requirements
  (`requires DATABASE_URL or fails fast at lifespan`).
- **Implications, not facts.** For every captured fact, the doc must
  also state the consequence. "No profile" alone is not enough;
  "No profile — services auto-up under `--profile X`; operator
  wrapper must use explicit service list" is the right capture.
- **Schema enumeration is mandatory for any type a ticket will
  construct.** If T04 will build a `PatentEnrichment` fallback
  instance, the brownfield doc must list the 9 fields and their
  types, not just name the schema.
- **Path verification gate.** Before brownfield-context.md is
  accepted, a verifier (script or subagent) must `ls` every path in
  the surface table and report mismatches. validate.py can be
  extended to check this.
