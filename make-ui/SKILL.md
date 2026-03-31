---
name: make-ui
description: Use when building or redesigning frontend UI, choosing design direction, or when the user says "make ui vibe", "make ui consult", "UI polish", "design system", or "help me design"
---

# Make UI

## TL;DR (Quick Start)

Architect and implement high-variance frontend designs. Avoids "AI slop" and generic templates by matching aesthetic direction to product verticals.

**When to use:** "make ui vibe", "ui polish", "design system", "help me design".

**Invocation:**
- **Vibe Mode:** Proceed directly to coding (for small tasks).
- **Consultation Mode:** Mandatory approval gate before coding (for redesigns).

## When to Use
- Building new UI components or pages from scratch.
- Redesigning existing interfaces for premium "vibe".
- Establishing or extending a design system/theme.
- **NOT for:** E2E testing (use `test-ui`) or basic bug fixing (use standard tools).

## Decision Tree

1. **Is the task a full redesign or large component?**
   - YES → Use **Consultation Mode** (approval gate required).
   - NO (small polish/fix) → Use **Vibe Mode**.

2. **Does an existing design system exist?**
   - YES → Extend and match existing tokens/components.
   - NO → Establish foundational tokens via `technical-standards.md`.

3. **Is the user unsure of the direction?**
   - YES → Provide 2-3 product anchors (e.g., "Linear-style", "Vercel-clean") and trade-offs.

## Workflow

### 1. Pre-flight (Audit)
Read `AGENTS.md`, `README`, and scan `package.json`/CSS. Existing stack takes precedence.

### 2. Mode Selection (Vibe vs. Consult)
- **Vibe:** Match aesthetic directly and execute.
- **Consult:** Walk through binary decision gates with the user before any code.

### 3. Execution
Implement with production-grade code using foundational tokens (colors, typography, spacing).

## Assumptions & Escalation

- **Tier 1 (reversible):** Color/spacing tweaks — proceed, explain rationale, flag for feedback.
- **Tier 2 (conflict):** Requested UI contradicts project style — check previous commits, block if still ambiguous.
- **Tier 3 (UX):** Requested UI pattern violates core accessibility or usability — **STOP**, block and propose safer alternative.

## Examples (Few-Shot)

**Example 1: Polishing a component**
Input: "Make the login button pop more"
Output: Implementation using gradients, subtle shadows, and hover transitions.

**Example 2: Designing a dashboard**
Input: "Consult me on a new dark mode dashboard"
Output: Audit of current state, presentation of 3 aesthetic directions, and token-level spec after approval.

## Related Skills
| Skill | When to use instead |
|-------|---------------------|
| test-ui | For verifying visual behavior via E2E |
| chrome-devtools | For manual CSS inspection and live testing |
