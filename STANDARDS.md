# Project Standards (index)

Resolve architecture questions here before blocking on a human.
This file is an index. Read only the topic file you need.

## How to use

**Agents:** before blocking on an assumption or open question:

1. Find the topic below and read that file.
2. If it answers the question, apply it and proceed.
3. If not, block for human clarification, then propose an addition.

**Humans:** when an agent blocks on a question you already decided, add the decision to the topic file (or to Project-Specific Additions below) and tell the agent to re-check.

## Authority map

Standards live in one place and are cited, not restated, so the surfaces below
cannot drift. If two files disagree, the home file wins; fix the other to match.

| Surface | Role | Home for |
|---|---|---|
| `STANDARDS.md` + `standards/*.md` | Decisions and patterns agents read before building or blocking | API, auth, data, testing strategy, layers, modularity, docstrings, security, performance |
| `pr-review/reference/review-standards.md` | Citable coded catalog (FN/DA/RT/TS/DC… codes) enforced at review time | The review-time wording of the above; keep each code consistent with its home topic file |
| `shared/QUALITY_RUBRIC.md` | Scoring rubric (M-codes, tiers, AI anti-patterns) | Mechanical/subjective altitude; cross-links to `reviews/` |
| `reviews/arch-violations/` | Diff-time architectural violation catalog (ARCH-* codes) | Layer/dependency/modularity drift |

New or changed rules go in the home topic file first; the reviewer catalog and
rubric reference it rather than copying the prose.

## Topics

| Topic | Read when | File |
|---|---|---|
| Blocker detection, ticket review, template | Reviewing a ticket before marking it READY | [standards/pre-flight.md](standards/pre-flight.md) |
| Block vs. proceed, assumption tiers | Unsure whether to ask or assume | [standards/decisions.md](standards/decisions.md) |
| API, auth, data, testing, structure, file size, errors | Designing or placing code | [standards/architecture.md](standards/architecture.md) |
| Layer ownership (domain, service, application, infra) | Deciding where logic belongs | [standards/layers.md](standards/layers.md) |
| Module depth vocabulary (seam, depth, leverage, locality) | Designing or reviewing module shape | [standards/modularity.md](standards/modularity.md) |
| Security checklist, subprocess rules | Before implementing any feature | [standards/security.md](standards/security.md) |
| Performance budgets, cleanup | Setting or checking targets | [standards/performance.md](standards/performance.md) |
| Docstrings and comment format | Writing or reviewing docs in code | [standards/docstrings.md](standards/docstrings.md) |
| Previously answered questions | Before asking the human | [standards/resolved.md](standards/resolved.md) |

## Project-Specific Additions

Merge project-specific standards below this line. Project wins on conflict; note the override.

### [Project Name] - Added [Date]

- **Stack adjustments:** (deviations from the default stack)
- **Architecture decisions:** (project ADRs)
- **Resolved questions:** (project Q&A)
- **Security requirements:** (extra checklist items)
- **Performance targets:** (project budgets)

## Maintenance

Update the topic file when a human clarifies a blocking question, an architecture decision is made, a reusable security pattern appears, or a performance issue needs prevention.
Review every 3 months or when onboarding to a very different project.
