# Plain vernacular technical explainers

Genre framing for explaining scoped technical work to readers who do not know the codebase. Apply stop-slop Core Rules for voice; use this file for audience, structure, and evidence honesty.

## Audience

- Default reader: smart, busy, unfamiliar with this repo.
- Use plain English and concrete names (files, jobs, checks, PRs).
- Lead with the failure and the fix. Leave internal ticket IDs and planning jargon out of the prose.

## Structure (what / why / evidence)

For each scoped change or claim:

1. **What:** Name the edit in plain language. What broke or was risky before? What does the reader see now?
2. **Why:** Explain the consequence and the design choice. Mention another option only when the reader needs to understand why you rejected it.
3. **Evidence:** Explain how you know it works. Separate what tests proved from what a live PR or CI run proved.

Use the actual failure mode, such as "merge would have passed with a required review still open," instead of an abstract claim like "improved reliability."

## Evidence honesty

- Separate unit and integration coverage from live workflow proof.
- When both kinds of evidence matter, a small table can make the distinction clear:

| Claim | Proved by tests | Proved by live PR / CI |
| --- | --- | --- |
| … | yes / no / partial: cite | yes / no / partial: cite run or PR |

- State when evidence is missing. A local test does not prove a live gate, and a live run does not replace a missing test.
- Limit claims to the edit under discussion. Avoid claims about overall system quality or personal track record unless the evidence supports them.

## Vernacular rules (complement stop-slop)

- Prefer specific names and active voice when the actor matters. Follow the writer's punctuation; check repeated dashes and formulaic structures in `structures.md`.
- Explain implications in operator terms: what a reviewer, merger, or on-call person would hit.
- Cut meta ("this section will cover"). State the change, then the proof.
- Keep each distinct item. End when the claim and its evidence are clear.
