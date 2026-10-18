# ADR Format

Adapted from Matt Pocock's `domain-modeling` skill (MIT).
Loaded from [domain-model.md](domain-model.md), which holds the three-condition test for when to offer one.

ADRs live in `docs/adr/` with sequential numbering: `0001-slug.md`, `0002-slug.md`, and so on.
Create `docs/adr/` lazily, when the first ADR is needed.
To number a new one, scan `docs/adr/` for the highest number and add one.

## Template

```md
# {Short title of the decision}

{1-3 sentences: the context, what we decided, and why.}
```

An ADR can be a single paragraph.
The value is in recording that a decision was made and why, not in filling out sections.

## Optional sections

Add these only when they carry real information:

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`): when decisions get revisited.
- **Considered Options**: when the rejected alternatives are worth remembering.
- **Consequences**: when non-obvious downstream effects need calling out.

## What qualifies

- **Architectural shape.** "We're using a monorepo." "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target. Only the ones that would take a quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no's are as valuable as the yes's.
- **Deliberate deviations from the obvious path.** "We're using manual SQL instead of an ORM because X." These stop the next engineer from "fixing" something deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of compliance requirements." "Responses must be under 200ms because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** If you picked REST over GraphQL for subtle reasons, record it, or someone will suggest GraphQL again in six months.
