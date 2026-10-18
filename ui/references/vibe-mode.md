# Vibe Mode — Speed Path

No DESIGN.md. Infer an appropriate visual direction from project evidence, then build and verify the requested UI.

## When to use

- Single-component addition to an existing project
- Prototype or proof-of-concept
- One-off polish pass on a small surface
- User explicitly says "vibe", "just build it", "no consult"

## When NOT to use

- Multi-page or full-app design with durable shared decisions — use the design-spec route first, then implement against the emitted spec.
- Project already has DESIGN.md — use Apply Mode (faster and consistent).
- User wants a portable design spec — use the design-spec route.

## Process

### 1. Pre-flight (5 min, mandatory)

- Read `AGENTS.md` / `README.md`
- Inspect `package.json`: framework, CSS approach, component library
- Scan existing CSS / tokens / `tailwind.config.*` / `globals.css`
- Look for an existing `ui/` or shared primitives directory

**Existing stack takes precedence over any default.** If the project uses CSS modules, do not introduce Tailwind. If it uses MUI, do not introduce shadcn.

### 2. Infer visual direction

Use `vibe-quick-pick.md` as inspiration when the project gives no clear signal. Follow existing components and product context when they establish a direction. Ask only if a consequential choice remains unclear.

### 3. Infer density

Infer compact / balanced / airy density from the existing interface and content. Use balanced when there is no signal.

### 4. Build

Apply `technical-standards.md` defaults. Output:

- Component(s) requested, with all states (default / hover / focus / disabled / loading / error)
- Any new shared primitives extracted (if you find yourself copy-pasting class strings)
- Token additions to existing tokens file (if needed for the new component)
- `prefers-reduced-motion` paths if motion is added

## Quality bar

Apply `technical-standards.md` operational directives:
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
| Generic SaaS gradient bg | Use a deliberate page bg; see prohibited patterns in `vibe-quick-pick.md` |
