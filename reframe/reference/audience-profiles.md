# Audience Profiles

## Contents

- [Exec Profile](#exec-profile)
- [Architect Profile](#architect-profile)
- [Engineer Profile](#engineer-profile)
- [Audience Selection Heuristics](#audience-selection-heuristics)

---

## Exec Profile

**Persona:** VP+, C-suite, budget owner, board member, non-technical stakeholder.
Attention window: 10-15 minutes. Will interrupt if relevance is unclear in the first 2 minutes.

**Primary goal:** Decide, approve, fund, or prioritize something.

**What they care about:**
- Business value delivered (revenue, cost savings, efficiency)
- Risk to the organization (compliance, security, operational, reputational)
- Timeline to impact (milestones, dependencies, critical path)
- What they need to decide or approve — the explicit "ask"
- Competitive or strategic positioning

**Language rules:**
- Business outcomes only: "market share", "risk exposure", "OPEX reduction", "time-to-market"
- No component names, no acronyms without expansion, no architecture terms
- "System" not "microservice". "Data platform" not "Kafka cluster"
- Dollar signs, percentages, and time units are the native vocabulary

**Story arc:** Punchline-first
1. Recommendation (what to do and why, in one sentence)
2. Evidence (3-5 key benefits, quantified where possible)
3. Risks (top 3, with mitigation status: mitigated / in progress / open)
4. Timeline (milestones with dates)
5. The Ask (decision, budget, team allocation — explicit and actionable)

**Anti-patterns (never do these):**
- Burying the ask after 10 slides of background
- Leading with project history or technical journey
- Showing architecture or sequence diagrams
- Using engineering jargon without business translation
- Presenting without a clear decision point

**Slide count target:** 5-8 slides max. Every slide must answer "so what?" for a non-technical stakeholder.

**Visual style:** Simple charts, timelines, RAG status tables. Very high-level architecture
only if explicitly requested (3-7 boxes maximum). One big idea per slide.

---

## Architect Profile

**Persona:** Staff+ engineer, principal engineer, solution architect, platform lead, technical program manager.
Evaluating fit, risk, integration cost, and long-term maintainability.

**Primary goal:** Validate architecture, assess patterns and tradeoffs, evaluate feasibility and risk.

**What they care about:**
- Architectural patterns used and why (CQRS, event sourcing, hexagonal, etc.)
- System boundaries and bounded contexts
- Quality attributes: latency, availability, consistency, scalability, security
- Integration points: APIs, events, shared state, protocol choices
- What could go wrong at scale — single points of failure, bottlenecks
- Migration paths and coexistence strategies with legacy systems
- Governance and operational constraints

**Language rules:**
- Architecture vocabulary is native: "bounded context", "bulkhead", "circuit breaker",
  "eventual consistency", "anti-corruption layer"
- No business ROI or revenue language (that is exec territory)
- No raw code or config (that is engineer territory)
- Diagram-first communication — text explains what diagrams show

**Story arc:** Tradeoff-first
1. Context and constraints (problem space, quality attributes, existing landscape)
2. Options with tradeoff matrix (compare across NFRs: latency, availability, cost, complexity)
3. Recommended approach with rationale
4. System boundaries and integration implications
5. Non-functional requirements with specific targets (p99 < Xms, availability > Y%)
6. Migration plan (current → target state, phased rollout)
7. Risks and open architectural questions

**Anti-patterns (never do these):**
- Jumping straight to code or implementation detail
- Ignoring non-functional requirements
- Presenting a single option without alternatives or tradeoffs
- Hand-wavy diagrams without quality attributes or constraints
- Missing integration points or external system dependencies

**Slide count target:** 8-15 slides. Every claim must have a tradeoff or constraint attached.

**Visual style:** Architecture diagrams (component, deployment, data-flow), tradeoff matrices,
current-vs-target-state comparisons, risk/constraint tables. Layered views that can zoom
from enterprise landscape → system → component level.

---

## Engineer Profile

**Persona:** IC engineer, SRE, backend/frontend developer, implementer, on-call engineer.
Needs to build, test, debug, and operate this day-to-day.

**Primary goal:** Understand how it works in detail and how to build, test, and operate it.

**What they care about:**
- Mechanism of action: step-by-step flows, request/response traces, state transitions
- Components and their responsibilities, mapped to repo structure
- Interfaces and contracts: API endpoints, event schemas, config formats
- Data flow and transformations through the system
- Failure modes: what breaks, how to detect, how to recover
- Operational concerns: monitoring, alerting, scaling, deployment
- Edge cases: race conditions, idempotency, backpressure, ordering guarantees
- Implementation gotchas and known limitations

**Language rules:**
- Full technical vocabulary: "idempotent", "backpressure", "circuit breaker timeout",
  "consumer group rebalance"
- Code snippets and config examples welcome (focused, not walls of code)
- Exact paths, commands, and endpoint names
- Concrete over abstract: "POST /v1/events with payload {type, data, timestamp}"
  not "events are published to the bus"

**Story arc:** Mechanism-first
1. What it does (3-5 bullet functional summary)
2. How it works (sequence diagram or data flow — the core mechanism)
3. Components (table: component, responsibility, owner, repo path)
4. Interfaces and contracts (API specs, event schemas, config)
5. Data flow (transformations, storage, caching)
6. Failure modes (what breaks, detection, recovery, blast radius)
7. Operational concerns (monitoring, alerting, scaling, deployment)
8. Implementation notes (prerequisites, gotchas, known limitations)

**Anti-patterns (never do these):**
- Leading with business justification or ROI
- Abstracting away the mechanism ("it just works")
- Vague diagrams without concrete names or paths
- Skipping failure modes and operational requirements
- Hiding edge cases behind "happy path only" descriptions

**Slide count target:** 10-20 slides, or switch to document format for very deep content.

**Visual style:** Sequence diagrams, state machines, data flow diagrams, component maps
with concrete labels. Code snippets on slides (small, focused). Error paths shown
with dashed lines. Operational dashboards or metric examples where relevant.

---

## Audience Selection Heuristics

When audience is `auto`, use these signals to classify:

**Signal words → audience:**

| User says | Audience |
|-----------|----------|
| "summarize for leadership", "board deck", "business case", "executive summary" | exec |
| "explain the value", "ROI", "budget request", "decision brief" | exec |
| "architecture review", "design doc", "tradeoff analysis", "system design" | architect |
| "integration assessment", "feasibility review", "platform evaluation" | architect |
| "implementation guide", "how does this work", "runbook", "onboarding doc" | engineer |
| "deep dive", "code walkthrough", "debugging guide", "operational playbook" | engineer |

**Recipient role → audience:**

| Recipient | Audience |
|-----------|----------|
| CEO, CTO, VP, Director, PM, non-technical stakeholder | exec |
| Staff engineer, principal, solution architect, platform lead | architect |
| IC engineer, SRE, developer, on-call, new team member | engineer |

When signals conflict (e.g., "architecture review for leadership"), ask the user
to choose — do not guess.
