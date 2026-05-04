<!-- imported from addyosmani/agent-skills incremental-implementation -->

# Incremental Slicing

Build in thin vertical slices. Implement → test → verify → commit → next. Each slice leaves the system working.

## Contents

- When to Use
- The Increment Cycle
- Slicing Strategies
- Implementation Rules
- Working with Agents
- Increment Checklist
- Common Rationalizations
- Red Flags
- Final Verification

## When to Use

| Trigger | Note |
|---|---|
| Multi-file change | Always |
| Building from a task breakdown | Always |
| Refactor | Especially |
| About to write >100 lines without testing | Stop |

Skip for single-file, single-function changes already minimal in scope.

## The Increment Cycle

```
Implement → Test → Verify → Commit → Next slice
```

For each slice:

1. Implement the smallest complete piece
2. Test (run suite or write a test)
3. Verify (tests pass, build clean, manual check)
4. Commit with descriptive message
5. Next slice — carry forward, don't restart

## Slicing Strategies

### Vertical (preferred)

One complete path through the stack:

```
Slice 1: Create task (DB + API + basic UI)
Slice 2: List tasks (query + API + UI)
Slice 3: Edit task
Slice 4: Delete task
```

### Contract-First

Backend + frontend in parallel:

```
Slice 0: Define API contract
Slice 1a: Backend against contract + tests
Slice 1b: Frontend against mock matching contract
Slice 2: Integrate end-to-end
```

### Risk-First

Tackle the riskiest piece first:

```
Slice 1: Prove WebSocket connection works
Slice 2: Build real-time updates on proven connection
Slice 3: Offline + reconnection
```

If Slice 1 fails, you discover it before investing in 2 and 3.

## Implementation Rules

### Rule 0 — Simplicity First

Before code: "what is the simplest thing that could work?"
After code: can this be fewer lines? Are abstractions earning their complexity? Building for hypothetical futures?

| Don't | Do |
|---|---|
| Generic EventBus with middleware for one notification | Simple function call |
| Abstract factory for two similar components | Two straightforward components |
| Config-driven form builder for three forms | Three forms |

Three similar lines beat a premature abstraction.

### Rule 0.5 — Scope Discipline

Touch only what the task requires. Don't:

- Clean up adjacent code
- Refactor imports in unmodified files
- Remove comments you don't fully understand
- Add features not in the spec
- Modernize syntax in files you're only reading

If you notice something worth fixing, note it; don't fix it:

```
NOTICED BUT NOT TOUCHING:
- src/utils/format.ts has unused import (unrelated)
- auth middleware error messages could improve (separate task)
→ Want me to create tasks for these?
```

### Rule 1 — One Thing at a Time

Each increment changes one logical thing. Don't mix concerns.

### Rule 2 — Keep It Compilable

After each increment: project builds, existing tests pass.

### Rule 3 — Feature Flags for WIP

```typescript
const ENABLE_TASK_SHARING = process.env.FEATURE_TASK_SHARING === 'true';
if (ENABLE_TASK_SHARING) { /* new sharing UI */ }
```

### Rule 4 — Safe Defaults

```typescript
export function createTask(data: TaskInput, options?: { notify?: boolean }) {
  const shouldNotify = options?.notify ?? false;
  // ...
}
```

### Rule 5 — Rollback-Friendly

| Pattern | Why |
|---|---|
| Additive (new files/functions) | Easy to revert |
| Minimal modification of existing | Focused diff |
| DB migrations have rollback migrations | Reversible |
| Don't delete + replace in same commit | Separate them |

## Working with Agents

Be explicit about scope IN and OUT per increment:

```
Implement Task 3. Start with DB schema + API endpoint only.
Don't touch UI yet — next increment.
After implementing, run `npm test` and `npm run build`.
```

## Increment Checklist

- [ ] Does one thing completely
- [ ] All existing tests pass
- [ ] Build succeeds
- [ ] Type check passes
- [ ] Lint passes
- [ ] New functionality works
- [ ] Committed with descriptive message

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll test it all at the end" | Bugs compound. Slice 1 bug makes 2-5 wrong. |
| "Faster to do it all at once" | Until something breaks across 500 lines. |
| "Too small to commit separately" | Small commits are free. Large commits hide bugs. |
| "I'll add the feature flag later" | Add it now if not complete. |
| "This refactor is small enough to include" | Mixed refactor + feature is harder to review. |

## Red Flags

- >100 lines without running tests
- Multiple unrelated changes in one increment
- "Quickly add this too" scope expansion
- Skipping test/verify
- Build/tests broken between increments
- Large uncommitted changes
- Building abstractions before third use case
- Touching files outside scope "while I'm here"
- New utility files for one-time operations

## Final Verification

- [ ] Each increment individually tested + committed
- [ ] Full test suite passes
- [ ] Build clean
- [ ] Feature works end-to-end
- [ ] No uncommitted changes
