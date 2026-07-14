# TDD Workflow Details

## 1. Planning

Before writing any code:

- [ ] Confirm with user what interface changes are needed
- [ ] Confirm with user which behaviors to test (prioritize)
- [ ] Identify opportunities for deep modules (small interface, deep implementation)
- [ ] Design interfaces for testability
- [ ] List the behaviors to test (not implementation steps)
- [ ] Identify async/await requirements (pytest-asyncio, httpx for streaming)
- [ ] Get user approval on the plan

Ask: "What should the public interface look like? Which behaviors are most important to test?"

**You can't test everything.** Confirm with the user exactly which behaviors matter most. Focus testing effort on critical paths and complex logic, not every possible edge case.

### One source file per cycle (support set included)

Treat each TDD cycle as **one source file** plus its support set — not a second unrelated source file "for a small tweak."

Dependency order inside the cycle (skip steps the node does not need):

1. Contract / types (interface)
2. Type-guard tests → guards (when used)
3. Interaction expectations (see [INTERFACE_DESIGN.md](./INTERFACE_DESIGN.md) — interaction spec)
4. Canonical mocks / factories for this unit
5. RED behavioral tests
6. Implementation
7. Public surface (`provides` / exports) if the module uses an explicit barrel
8. Integration test only when a producer → subject → consumer boundary is reached

Rules:

- Types/interfaces/guards are **not** their own cycles — attach them to the first source file that consumes the change.
- Do not orphan an interface edit in a separate task from its consumer.
- Build producers before consumers; keep the tree buildable after each cycle.
- Prefer relational identifiers (path + symbol) over numbered steps that break on insert/reorder.

### Discovery halt (multi-file scope)

If completing the current cycle requires editing a **second source file** (or an undeclared support file outside this cycle):

1. Stop editing.
2. Report discovery: dependent files, why, minimal next cycles.
3. Propose the added cycles (one source file each).
4. Wait for explicit approval — do not improvise the multi-file change.

## 2. Tracer Bullet

Write ONE test that confirms ONE thing about the system:

```
RED:   Write test for first behavior → test fails
GREEN: Write minimal code to pass → test passes
```

This is your tracer bullet - proves the path works end-to-end.

## 3. Incremental Loop

For each remaining behavior:

```
RED:   Write next test → fails
GREEN: Minimal code to pass → passes
```

Rules:
- One test at a time
- Only enough code to pass current test
- Don't anticipate future tests
- Keep tests focused on observable behavior

## 4. Refactor

After all tests pass, look for refactor candidates:

- [ ] Extract duplication
- [ ] Deepen modules (move complexity behind simple interfaces)
- [ ] Apply SOLID principles where natural
- [ ] Consider what new code reveals about existing code
- [ ] Run tests after each refactor step

**Never refactor while RED.** Get to GREEN first.

## Applying to Bug Fixes

When fixing a bug, TDD still applies:

1. **Write a failing test first** that reproduces the bug
2. **Fix the bug** to make the test pass
3. **Refactor** if needed

This ensures:
- The bug is actually reproduced (not just symptoms)
- The fix actually works
- The bug doesn't regress

```
RED:   Write test that fails due to bug → test fails
GREEN: Fix bug → test passes
REFACTOR: Clean up if needed
```
