# Evidence-Based UI Audit

Audit only. Do not edit the implementation while reviewing it.

## Choose the review rubric

1. Read project instructions and identify the relevant routes and UI source roots.
2. If a root `DESIGN.md` exists, use it as the visual source of truth. Otherwise use the user's stated criteria, brand materials, and established product patterns. If none define the visual direction, review hierarchy, responsive behavior, interaction states, semantics, and accessibility without prescribing a redesign.
3. Skip generated and dependency directories such as `node_modules/`, `dist/`, `build/`, `.next/`, and `.cache/`.

## Gather evidence

- Run the relevant existing lint, accessibility, or UI checks before subjective review. Prefer project scripts; do not create broad new checks just for the audit.
- When the app can run and browser tools are available, inspect relevant desktop and mobile states with `chrome-devtools`. Capture screenshots and inspect console errors that affect the reviewed surface.
- If the app cannot run, continue with source and existing test evidence. State that rendered behavior was not verified and why.

## Report

Write `ui-audit.md` at the repo root when the user requests a persistent report; otherwise summarize findings in the response.

Order findings by impact. Every finding needs evidence: a file and line for a source issue, a failing check with output, or a screenshot and viewport for a rendered defect. Separate functional failures, spec drift, and visual polish. Give a concise fix direction. Keep verified strengths and speculative suggestions out of the findings list.

If a design spec seems wrong, report the evidence and do not change the spec during the audit. End when each finding is evidence-backed and the verification gap is explicit.
