<!-- imported from addyosmani/agent-skills source-driven-development -->

# Source-Driven Development

Every framework-specific code decision must be backed by official documentation. Don't implement from memory — verify, cite, let the user check.

Training data goes stale. APIs deprecate. This guards against shipping outdated patterns.

## Contents

- When to Use
- Process
- Common Rationalizations
- Red Flags
- Verification

## When to Use

| Trigger | Note |
|---|---|
| User wants current best practices | Always |
| Building boilerplate / patterns to be copied | Always |
| User asks for "documented" / "verified" code | Always |
| Framework-recommended approach matters | forms, routing, data fetching, state, auth |
| About to write framework-specific code from memory | Stop, verify |

**Don't use when:** correctness doesn't depend on a specific version (renames, typos, file moves); pure logic; user explicitly wants speed over verification.

## Process

```
DETECT → FETCH → IMPLEMENT → CITE
```

### Step 1 — Detect Stack and Versions

| File | Tells you |
|---|---|
| package.json | Node/React/Vue/Angular/Svelte |
| composer.json | PHP/Symfony/Laravel |
| requirements.txt / pyproject.toml | Python/Django/Flask |
| go.mod | Go |
| Cargo.toml | Rust |
| Gemfile | Ruby/Rails |

State explicitly:

```
STACK DETECTED:
- React 19.1.0
- Vite 6.2.0
- Tailwind CSS 4.0.3
→ Fetching official docs.
```

If versions ambiguous, ask. Don't guess.

### Step 2 — Fetch Official Docs

Fetch the specific page, not the homepage.

| Priority | Source | Examples |
|---|---|---|
| 1 | Official docs | react.dev, docs.djangoproject.com, symfony.com/doc |
| 2 | Official blog / changelog | react.dev/blog, nextjs.org/blog |
| 3 | Web standards | MDN, web.dev, html.spec.whatwg.org |
| 4 | Compatibility | caniuse.com, node.green |

**Not authoritative — never cite as primary:**

- Stack Overflow
- Blog posts / tutorials
- AI-generated docs
- Your own training data

```
BAD:  Fetch React homepage
GOOD: Fetch react.dev/reference/react/useActionState

BAD:  Search "django authentication best practices"
GOOD: Fetch docs.djangoproject.com/en/6.0/topics/auth/
```

When official sources conflict (migration guide vs API ref), surface the discrepancy and verify which actually works against the detected version.

### Step 3 — Implement Per Docs

- Use API signatures from docs, not memory
- Use the new way if docs show one
- Don't use deprecated patterns
- If docs don't cover something, flag as unverified

**Conflict with existing code:**

```
CONFLICT DETECTED:
Existing codebase uses useState for form loading state.
React 19 docs recommend useActionState.
(Source: react.dev/reference/react/useActionState)

Options:
A) Modern pattern (useActionState) — current docs
B) Match existing code (useState) — codebase consistency
→ Which approach?
```

Surface, don't pick silently.

### Step 4 — Cite

In code:

```typescript
// React 19 form handling with useActionState
// Source: https://react.dev/reference/react/useActionState#usage
const [state, formAction, isPending] = useActionState(submitOrder, initialState);
```

In conversation:

```
Using useActionState instead of manual useState. React 19 replaced
manual isPending/setIsPending with this hook.

Source: https://react.dev/blog/2024/12/05/react-19#actions
"useTransition now supports async functions [...] to handle pending
states automatically"
```

Citation rules:

- Full URLs (no shorteners)
- Prefer deep links with anchors (`/useActionState#usage`)
- Quote the relevant passage for non-obvious decisions
- Include browser/runtime support data when recommending platform features
- If you can't find docs:

```
UNVERIFIED: Could not find official docs for this pattern.
Based on training data, may be outdated. Verify before production.
```

Honesty about unverified beats false confidence.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'm confident about this API" | Confidence ≠ evidence. Training data has outdated patterns. |
| "Fetching docs wastes tokens" | Hallucinating wastes more. One fetch prevents hours of rework. |
| "Docs won't have what I need" | If they don't, the pattern may not be officially recommended. |
| "I'll mention it might be outdated" | Hedging is the worst option. Verify or flag as unverified. |
| "Simple task, no need to check" | Simple tasks become templates copied 10x. |

## Red Flags

- Framework-specific code without checking docs for that version
- "I believe" / "I think" instead of citation
- Implementing without knowing the version
- Citing Stack Overflow / blog posts as primary
- Using deprecated APIs because they're in training data
- Not reading `package.json` first
- Delivering without source citations
- Fetching whole docs sites when one page is relevant

## Verification

- [ ] Versions identified from dependency file
- [ ] Official docs fetched
- [ ] Sources are official (not blogs/training)
- [ ] Code matches current-version patterns
- [ ] Non-trivial decisions have full-URL citations
- [ ] No deprecated APIs (checked against migration guides)
- [ ] Conflicts surfaced
- [ ] Anything unverified is flagged
