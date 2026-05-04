---
name: make-ui
description: Builds, applies, or audits frontend UI against a design spec. Three modes — Vibe (build now from a quick aesthetic pick), Apply (conform a repo to an existing DESIGN.md), Audit (diff a repo against DESIGN.md and emit a drift report). Use when implementing UI, restyling components, polishing visuals, or checking conformance. For authoring a DESIGN.md, redirect to /make-design-md.
---

# Make UI — Apply, Audit, or Vibe-Build a Frontend

**Anti-AI Slop.** If the result reads like a bootstrapped template, it failed. Every project must feel deliberate.

## Mode Dispatcher

Decide the mode before doing anything else.

```
1. User wants to *create* a DESIGN.md          → redirect to /make-design-md
2. DESIGN.md exists at repo root + build/restyle → APPLY MODE
3. DESIGN.md exists + check conformance         → AUDIT MODE
4. No DESIGN.md + user wants to build now       → VIBE MODE
```

Detection rule for #2/#3: check `<repo-root>/DESIGN.md`. If present, default to Apply or Audit. If absent and the user explicitly asks for a spec, redirect to `/make-design-md`. If absent and the user wants speed, Vibe Mode.

## Modes

### Apply Mode → [apply-mode.md](references/apply-mode.md)

Read a DESIGN.md, install token infrastructure, build the layout shell, restyle components, migrate anti-patterns. Phased like `/c3-ui`. Use this when a spec exists and the codebase needs to conform.

### Audit Mode → [audit-mode.md](references/audit-mode.md)

Diff the codebase against DESIGN.md. Emit `ui-audit.md` with per-section findings categorized ✅ conforms / ⚠️ drift / ❌ violation, with file:line citations and suggested fixes. Use before merging UI changes or before an Apply pass to scope the work.

### Vibe Mode → [vibe-mode.md](references/vibe-mode.md)

No DESIGN.md, no time. Quick-pick aesthetic from [vibe-quick-pick.md](references/vibe-quick-pick.md), build directly with production-grade code. Use for prototypes, single-component additions, or one-off polish.

## Companion Files

- [apply-mode.md](references/apply-mode.md) — phased application workflow
- [audit-mode.md](references/audit-mode.md) — drift-report workflow
- [vibe-mode.md](references/vibe-mode.md) — speed path
- [vibe-quick-pick.md](references/vibe-quick-pick.md) — slim aesthetic matrix
- [technical-standards.md](references/technical-standards.md) — implementer defaults (CSS, motion, a11y, responsive)

## Hard Constraints

- Existing project patterns take precedence over any default. Extend, don't replace.
- Apply Mode and Audit Mode read DESIGN.md as source of truth — do not propose token changes inside these modes; redirect to `/make-design-md` if the spec needs revision.
- Vibe Mode never produces a DESIGN.md. If the user wants a portable spec from the result, redirect to `/make-design-md` after the build.
- For C3-aligned React + Tailwind v4 projects, `/c3-ui` is the C3-specific instance of Apply Mode — use it directly when the target spec is `c3-design-system.md`.
