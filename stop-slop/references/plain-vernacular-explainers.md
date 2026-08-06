# Plain vernacular technical explainers

Genre framing for explaining scoped technical work to readers who do not know the codebase. Apply stop-slop Core Rules for voice; use this file for audience, structure, and evidence honesty.

## Audience

- Default reader: smart, busy, unfamiliar with this repo.
- Prefer plain English and concrete names (files, jobs, checks, PRs) over ticket IDs and planning jargon.
- Ticket / F-ids optional; lead with the failure mode and the fix, not the tracker label.

## Structure (what / why / evidence)

For each scoped change or claim:

1. **What** — Name the edit in vernacular. What broke or was risky before? What does the reader see now?
2. **Why** — Relevance, justification, and the design choice you made (and what you rejected if it matters).
3. **Evidence** — How you know it works. Separate what tests proved from what a live PR / CI run proved.

Put the reader in the room: concrete failure modes ("merge would have passed while X was still open"), not abstract "improved reliability."

## Evidence honesty

- Do not blur unit/integration coverage with live workflow proof.
- Prefer a small table when both exist:

| Claim | Proved by tests | Proved by live PR / CI |
| --- | --- | --- |
| … | yes / no / partial — cite | yes / no / partial — cite run or PR |

- If evidence is missing, say so. Do not imply a live gate from a local test, or the reverse.
- Scope claims to the edit under discussion. No portfolio language.

## Vernacular rules (complement stop-slop)

- Active voice; specific names; no em dashes; no filler; no formulaic AI structures (see Core Rules and `structures.md`).
- Explain implications in operator terms: what a reviewer, merger, or on-call person would hit.
- Cut meta ("this section will cover"). State the change, then the proof.
- Two items beat three. End when the claim and its evidence are clear.
