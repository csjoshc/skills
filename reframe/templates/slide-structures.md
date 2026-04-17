# Slide Structures

## Contents

- [Exec Deck Structure](#exec-deck-structure)
- [Architect Deck Structure](#architect-deck-structure)
- [Engineer Deck Structure](#engineer-deck-structure)
- [Adapting Slide Count](#adapting-slide-count)

---

## Exec Deck Structure

Target: 5-8 slides. Every slide answers "so what?" for a non-technical stakeholder.

### Slide 1: Title
- Project/initiative name
- One-line value proposition (not a description — a benefit)
- Date and presenter name

### Slide 2: Punchline
- "We recommend [X]. Here is why."
- Single recommendation as the headline
- 2-3 supporting bullets maximum
- This slide must work standalone if the exec leaves after 2 minutes

### Slide 3: Value / Impact
- Quantified benefits: cost savings, efficiency gains, revenue impact, time-to-market
- Use metrics from the source material only
- If no metrics exist, write **"METRICS NEEDED: [describe what to measure]"**
- Format: 3-4 large numbers or KPIs with brief labels

### Slide 4: Risk
- Top 3 risks in a table:

| Risk | Likelihood | Impact | Mitigation | Status |
|------|-----------|--------|------------|--------|
| ... | High/Med/Low | High/Med/Low | ... | Mitigated / In progress / Open |

- Keep descriptions to one line each

### Slide 5: Timeline
- Milestones with dates in a horizontal timeline or simple table
- Highlight the critical path and key decision points
- Mark dependencies that require exec action

### Slide 6: The Ask
- Explicit and actionable: "We need approval to [X] by [date]"
- What the exec needs to decide, approve, or fund
- Next steps with owners and dates
- Never end a deck without a clear ask

### Slide 7: Appendix (optional)
- Supporting data, competitive context, detailed breakdown
- Exists for Q&A deep-dives, not for presentation

---

## Architect Deck Structure

Target: 8-15 slides. Every claim has a tradeoff or constraint attached.

### Slide 1: Title
- System/feature name and architectural scope
- "Architecture Review" or "Design Proposal" subtitle

### Slide 2: Context
- Problem space and business driver (one paragraph max)
- Key constraints: regulatory, timeline, budget, team, existing systems
- Quality attributes that matter most (rank top 3)

### Slide 3: Current State (if migration/evolution)
- Current architecture diagram (simplified)
- Pain points annotated on the diagram
- Skip this slide for greenfield projects

### Slide 4: Options / Tradeoff Matrix
- Table comparing 2-3 approaches across quality attributes:

| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| Latency | p99 < 50ms | p99 < 100ms | p99 < 200ms |
| Availability | 99.99% | 99.9% | 99.95% |
| Complexity | High | Medium | Low |
| Cost (annual) | $X | $Y | $Z |
| Migration risk | Low | Medium | High |

- Highlight the recommended option

### Slide 5: Recommended Architecture
- Component diagram (embedded Mermaid SVG)
- Subgraphs for bounded contexts or deployment zones
- Show synchronous vs asynchronous communication
- Annotate latency-sensitive paths

### Slide 6: System Boundaries
- What is ours vs external/third-party
- Trust boundaries and security perimeters
- Data ownership and flow direction across boundaries

### Slide 7: Integration Points
- APIs, events, shared state — each with:
  - Protocol (REST, gRPC, async event)
  - SLA/SLO targets
  - Versioning strategy
  - Compatibility concerns with existing consumers

### Slide 8: Quality Attributes
- Specific targets with measurement approach:
  - Latency: p50, p99, p99.9
  - Availability: target %, measurement window
  - Throughput: requests/sec, messages/sec
  - Consistency model: strong, eventual, causal

### Slide 9: Migration / Rollout
- Current → target state transition plan
- Phases with rollback criteria
- Coexistence strategy for legacy systems
- Feature flag or canary approach

### Slide 10: Risks and Open Questions
- Architectural risks with mitigation plans
- Unresolved decisions that need input
- Dependencies on other teams or systems

### Slides 11+: Deep-Dives (optional)
- One slide per complex subsystem
- Used for Q&A or follow-up sessions

---

## Engineer Deck Structure

Target: 10-20 slides. Prioritize "what do I need to know to build/operate this."

### Slide 1: Title
- Component/feature name
- "Implementation Guide" or "Technical Deep Dive" subtitle

### Slide 2: What It Does
- 3-5 bullet functional summary
- User-visible behavior, not internal mechanism (save that for next slide)
- Scope: what is and is not covered

### Slide 3: How It Works
- Sequence diagram or data flow (embedded Mermaid SVG)
- Show the primary happy-path flow end-to-end
- Label concrete endpoint names, message types, and data stores

### Slide 4: Components
- Table:

| Component | Responsibility | Owner | Repo/Path |
|-----------|---------------|-------|-----------|
| ... | ... | ... | ... |

- Map to actual repo structure so engineers can find code

### Slide 5: Interfaces / Contracts
- API endpoints with method, path, key request/response fields
- Event schemas with type, payload structure
- Config format with key fields and defaults
- Code snippets where helpful (focused, not walls of code)

### Slide 6: Data Model
- Key entities and relationships
- Storage technology and access patterns
- Caching strategy and invalidation
- Data flow diagram showing transformations

### Slide 7: Failure Modes
- Table:

| Failure | Detection | Impact | Recovery | Blast Radius |
|---------|-----------|--------|----------|-------------|
| ... | ... | ... | ... | ... |

- Include: retries, backoff, idempotency, circuit breakers
- Show error paths on diagrams with dashed lines

### Slide 8: Operational Concerns
- Monitoring: key metrics, dashboards, alerts
- Scaling: horizontal/vertical, autoscaling triggers
- Deployment: strategy, rollback procedure, feature flags
- On-call: what to check first, common failure scenarios

### Slide 9: Implementation Notes
- Prerequisites and setup
- Gotchas and known limitations
- Dependencies and version constraints
- Testing strategy: unit, integration, contract, performance

### Slide 10: Getting Started
- How to run locally (commands, env setup)
- How to deploy (pipeline, manual steps)
- Key configuration knobs
- Where to find more detail (links to docs, runbooks)

### Slides 11+: Code Walkthrough (optional)
- Key code paths with annotations
- One slide per critical flow
- Focused snippets, not full files

---

## Adapting Slide Count

The targets above are guidelines. Adapt based on:

- **Time budget**: If told "5-minute presentation," cut to minimum slides (exec: 4, architect: 5, engineer: 6).
- **Source depth**: Thin source material produces fewer slides. Do not pad.
- **Complexity**: A simple feature needs fewer slides than a platform migration.
- **Format switch**: For engineer content exceeding 15 slides, suggest switching to a document format with the same section structure.
