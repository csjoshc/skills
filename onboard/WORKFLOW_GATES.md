# Workflow routing

This is a reference linked from project `AGENTS.md`, not a callable skill or an installed hook.
Use it when choosing the next phase; it does not require a new pipeline for small tasks.
Call the Skill tool for the named skill only when its trigger fits.
Read linked companions as documents, not as skills.

## Phase map

| Phase trigger (user or agent intent) | Required skill(s) | Gate |
|---|---|---|
| "Create ticket / spec / plan for X" | `spec`; `challenge` when contested or risky | Coherent behavior per ticket, declared files, AC→test table |
| Small source change | [Change-quality pass](../shared/QUALITY_RUBRIC.md#change-quality-pass); implement directly, `tdd` for test-first work | Scope stated before editing, checked at first working slice |
| Bug fix / tests / integration | `tdd` | Reproduction or behavioral test fails first, then passes; required consumers updated |
| Build or change frontend UI | `ui`, preserving a caller's TDD sequence | Requested surface works without unrelated redesign |
| New interface or boundary mock | `tdd`; read [interface design](../tdd/INTERFACE_DESIGN.md) or [mock contract](../tdd/MOCK_CONTRACT.md) when relevant | Contracts and behavior checked at the boundary |
| Review a completed ticket | Read [evidence reviewer](../shared/EVIDENCE_REVIEWER.md) | Starting-state comparison includes uncommitted work |
| Review a branch or PR | `pr-review --local` or `pr-review` | Scope and findings backed by the actual diff |
| "I'm done / complete / fixed X" | `verify` | Evidence and final source scope checked, unresolved gaps reported |
| "Open / create PR" | `pr-create` | Aggregate scope/size preflight, then one substantive review |
| "Fix review comments" | `pr-fix` | Staleness check green |
| Audit repo/package health | `cleanup` | Mechanical checks then evidence-backed findings; no automatic remediation |
| Implement an agreed refactor | Shared change-quality pass; `tdd` for behavior protection | Necessary refactor stays within agreed scope |

## Boundaries

- `/todo` remains a user-invoked entry for planned multi-ticket work; do not call it automatically for a small edit.
- Reuse the shared pass at each checkpoint for its specific purpose: initial scope, first-slice expansion, final diff.
  Do not run a full cleanup audit or PR review at every checkpoint.
- Cleanup's [redundancy](../cleanup/redundancy-watcher.md) and [layer](../cleanup/layer-boundary-critic.md) companions are detailed audit references.
  Routine implementation uses the shared pass's reuse and scope checks, not mandatory standalone watcher calls.
- Escalate unexpected subsystem or contract changes before editing them.
  A second declared implementation/support file is not itself a blocker.
- Skills do not grant permission to commit, push, merge, or rewrite history.
  Preserve the user's authorization boundaries.

Installed hook behavior is documented in [Hook principles](../shared/HOOK_PRINCIPLES.md).
Routing instructions alone do not prove a check ran; report actual verification and any gaps.
