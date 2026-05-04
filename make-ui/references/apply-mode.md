# Apply Mode — Conform a Codebase to DESIGN.md

Generic version of `/c3-ui`. Runs phased application of any DESIGN.md spec.

## Pre-flight

1. Confirm `<repo-root>/DESIGN.md` exists. If not → redirect to `/make-design-md`.
2. Read DESIGN.md cover-to-cover before any edits. Keep §2/§3/§5/§6/§8 open during the work.
3. Read `AGENTS.md` / `README.md` and inspect `package.json` + existing CSS to understand the stack.
4. If the stack contradicts DESIGN.md (e.g. spec says Tailwind v4, project uses CSS modules) — pause and ask the user how to proceed (port the spec or change the stack).

## Phases

Work in order. Each phase is independently verifiable.

### Phase 1 — Token Infrastructure

Goal: get the design tokens from DESIGN.md §2/§3/§5/§6 into the project as runnable CSS.

```
- [ ] 1.1 Create src/tokens/tokens.css (or equivalent) with :root { --bg-page, --bg-surface, ... } from §2
- [ ] 1.2 Add .dark { ... } block with dark counterparts from §2
- [ ] 1.3 Add typography stack (font imports, --font-heading, --font-body, --font-mono) from §3
- [ ] 1.4 Add spacing variables --space-00..08 from §5
- [ ] 1.5 Add shadow variables --shadow-card, --shadow-menu, --shadow-modal from §6
- [ ] 1.6 Add motion variables --duration-fast/normal/slow + --ease-* from §6
- [ ] 1.7 Wire tokens into framework (Tailwind v4 @theme block, or CSS custom prop usage)
- [ ] 1.8 Verify: app loads, no CSS errors, tokens visible in DevTools
```

### Phase 2 — Dark Mode

```
- [ ] 2.1 Add `.dark` class toggle mechanism (useTheme hook or framework equivalent)
- [ ] 2.2 Persist preference in localStorage; default per spec (light unless §1 says otherwise)
- [ ] 2.3 Add `:root { color-scheme: light; } .dark { color-scheme: dark; }` for native controls
- [ ] 2.4 Test: toggle light↔dark, all surfaces follow, no hardcoded colors leak through
```

### Phase 3 — Layout Shell

Goal: implement §5 layout primitive.

```
- [ ] 3.1 App root: full-viewport layout per §5 (sidebar+content, topnav+content, etc.)
- [ ] 3.2 Implement breakpoint behavior from §5 table (sm/md/lg/xl)
- [ ] 3.3 Touch-target rule: ≥44×44px on touch breakpoints
- [ ] 3.4 Verify: resize window, layout adapts, scroll containers correct
```

### Phase 4 — Component Restyle

Read §4 for exact class strings. Build or restyle each:

```
- [ ] 4.1 Buttons (primary / secondary / danger) with all states from §4 button table
- [ ] 4.2 Inputs / form fields with focus + error + disabled states
- [ ] 4.3 Cards using §4 card recipe
- [ ] 4.4 Dropdowns — never native <select>; use custom listbox or Radix per §4
- [ ] 4.5 Modals
- [ ] 4.6 State catalog implementations: Empty / Loading / Error / Success / Skeleton
- [ ] 4.7 Verify: every variant × state renders correctly in light + dark
```

### Phase 5 — Token Migration (brownfield)

If existing UI has drift, find-and-replace anti-patterns from §8:

```
- [ ] 5.1 Hardcoded hex → semantic token
- [ ] 5.2 rounded-xl/rounded-lg on cards/buttons → spec radius
- [ ] 5.3 shadow-sm/md on cards → shadow-card
- [ ] 5.4 font-semibold on buttons (if §3 says default weight) → remove
- [ ] 5.5 Native <select> → custom dropdown
- [ ] 5.6 Generic gradients → spec page background
- [ ] 5.7 Grep for old token names; confirm zero matches
```

For greenfield projects, skip Phase 5.

### Phase 6 — Final Audit

Compose with Audit Mode:
```
- [ ] 6.1 Run /make-ui Audit Mode against the changed code
- [ ] 6.2 Address every ❌ violation; document any deferred ⚠️ drift
- [ ] 6.3 Compare rendered output against preview-ui/preview.html and preview-dark.html
- [ ] 6.4 Test prefers-reduced-motion + reduced-color-contrast paths
```

## Conditional Steps

- **No existing UI (greenfield):** skip Phase 5.
- **Spec has no dark mode:** skip Phase 2 (rare; modern specs always pair).
- **Stack mismatch:** stop and resolve with user before Phase 1.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Adding tokens not in DESIGN.md "for polish" | Stop. If spec is missing tokens, fix the spec via `/make-design-md`. |
| Per-component style overrides | Use semantic tokens; if a token is missing, add it to the spec, not the component. |
| Skipping Phase 1 verification | Token errors compound; each phase depends on the prior. |
| Native `<select>` in dark mode | OS popup ignores the theme — always use custom dropdowns. |
| Dark mode = inverted light values | Pick deliberate dark hex per §2; don't compute. |
