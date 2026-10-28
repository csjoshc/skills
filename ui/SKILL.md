---
name: ui
description: "Routes frontend design, implementation, audit, and testing through one UI workflow. Use when creating or changing a web interface, defining a reusable DESIGN.md, or reviewing UI behavior or appearance."
---

# ui

Handle frontend design and implementation from one entry. Infer the requested outcome from the user’s request and the project’s current state; do not present a mode menu when the task is clear.

## Route by outcome

1. **Create or revise a reusable design system** → read [design-spec.md](references/design-spec.md). Do this only when requested or when the feature needs durable cross-page design decisions; ordinary UI work does not require a `DESIGN.md`.
2. **Build or restyle UI** → read the project’s `AGENTS.md`, existing UI patterns, and root `DESIGN.md` if present. With a spec, follow [apply-mode.md](references/apply-mode.md). Without one, follow [vibe-mode.md](references/vibe-mode.md) and infer a direction from the product, content, and existing interface.
3. **Audit appearance** → read [audit-mode.md](references/audit-mode.md). Use `DESIGN.md` when present; otherwise audit against the user's criteria, existing product patterns, and relevant accessibility and responsive expectations.
4. **Test UI behavior or document a defect** → read [testing.md](references/testing.md), then only the relevant [setup](references/SETUP.md), [selector](references/SELECTORS.md), [coverage](references/CHECKLIST.md), or [bug report](references/BUG_REPORT.md) reference.

When a request combines implementation and review, implement first and verify the changed surface. Keep each pass within the requested scope.

## Working rules

- Match the project’s stack and established patterns. Treat its `DESIGN.md` as the source of truth when present.
- For a new direction, inspect the product and its content, then make a concrete choice and proceed. Use the [decision matrix](references/decision-matrix.md) as inspiration when the direction is unclear. Ask one focused question only when a consequential decision cannot be inferred from the project or request.
- Prefer existing assets and design tokens. Use external reference images only when they materially improve the requested UI; respect their licenses and attribution requirements.
- Preserve the requested feature and avoid unrelated redesign. If a ticket or acceptance criteria were supplied, treat them as the scope and use the caller’s TDD/test sequence.
- Apply the [change-quality pass](../shared/QUALITY_RUBRIC.md#change-quality-pass) before editing, when the requested surface first works, and on the final diff; reuse a current pass from the caller.
- Run relevant existing UI tests before adding custom browser automation. Read [technical-standards.md](references/technical-standards.md) when implementation needs design, accessibility, responsive, or motion guidance; adapt those defaults to the project.
- When the app can run and browser tools are available, inspect the changed UI at representative desktop and mobile widths. Fix defects introduced by this change or required by the request; report unrelated visual defects separately. Capture the changed surface again and report any remaining issue. Call the Skill tool with `browser` for live browser work.
- If rendered-browser evidence cannot be collected, state the concrete blocker and use available automated checks. Do not imply visual verification succeeded.
- For a new or revised `DESIGN.md`, follow the Stitch structure in [stitch-format.md](references/stitch-format.md), generate the preview artifacts, and call the Skill tool with `stop-slop` on generated prose. Infer choices and emit without section-by-section approvals; pause only for a consequential unresolved choice.

## Completion

Finish when the requested UI outcome is implemented or audited, relevant checks have run, and browser evidence has been captured when available. Report what changed, checks run, screenshots or findings, and any verification gap.

## References

- [design-spec.md](references/design-spec.md): reusable `DESIGN.md` authoring workflow.
- [apply-mode.md](references/apply-mode.md): implementation against an existing spec.
- [vibe-mode.md](references/vibe-mode.md): implementation when no spec exists.
- [audit-mode.md](references/audit-mode.md): evidence-based conformance audit.
- [testing.md](references/testing.md): existing E2E tests, custom Playwright, and defect reports.
- [technical-standards.md](references/technical-standards.md): conditional implementation guidance.
