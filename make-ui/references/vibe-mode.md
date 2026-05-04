# Vibe Mode — Speed Path

No DESIGN.md, no consultation, no approval gates. Quick aesthetic pick, then build with production-grade code.

## When to use

- Single-component addition to an existing project
- Prototype or proof-of-concept
- One-off polish pass on a small surface
- User explicitly says "vibe", "just build it", "no consult"

## When NOT to use

- Multi-page or full-app design — use `/make-design-md` first to capture decisions, then Apply Mode.
- Project already has DESIGN.md — use Apply Mode (faster and consistent).
- User wants a portable design spec — redirect to `/make-design-md`.

## Process

### 1. Pre-flight (5 min, mandatory)

- Read `AGENTS.md` / `README.md`
- Inspect `package.json`: framework, CSS approach, component library
- Scan existing CSS / tokens / `tailwind.config.*` / `globals.css`
- Look for an existing `ui/` or shared primitives directory

**Existing stack takes precedence over any default.** If the project uses CSS modules, do not introduce Tailwind. If it uses MUI, do not introduce shadcn.

### 2. Pick aesthetic (1 decision)

Use [vibe-quick-pick.md](vibe-quick-pick.md) — vertical → aesthetic in one table. If existing components hint at a direction, follow them. Don't ask the user unless the project is truly ambiguous.

### 3. Pick density (1 decision)

Compact / Balanced / Airy. Default to Balanced unless the project signals otherwise (Linear-tight = Compact, Apple-style = Airy).

### 4. Build

Apply [technical-standards.md](technical-standards.md) defaults. Output:

- Component(s) requested, with all states (default / hover / focus / disabled / loading / error)
- Any new shared primitives extracted (if you find yourself copy-pasting class strings)
- Token additions to existing tokens file (if needed for the new component)
- `prefers-reduced-motion` paths if motion is added

### 5. Hand-off note (always)

Append a short note (3–5 lines) to your final response:

> "If you want this captured as a portable design spec for future agents to read, run `/make-design-md` — it will audit what was built and emit a `DESIGN.md` + `preview-ui/` artifacts."

## Quality bar

Apply [technical-standards.md](technical-standards.md) operational directives:
- Deep reasoning chain before code: `Audit → Gap analysis → Aesthetic → Approach → Design`
- Production-grade: real imports, responsive classes, a11y attrs, semantic tokens
- No placeholder styling; no AI-template tells

## Common mistakes

| Mistake | Fix |
|---|---|
| Introducing a new UI library because "the existing one is limited" | Stay on existing stack unless user approves change |
| Inventing tokens scattered through the new component | Add to the project's tokens file once; reuse |
| Skipping pre-flight | Half the work in vibe is reading what's already there |
| Single-state buttons | Always all 5+ states |
| Generic SaaS gradient bg | Use a deliberate page bg; see prohibited patterns in [vibe-quick-pick.md](vibe-quick-pick.md) |
