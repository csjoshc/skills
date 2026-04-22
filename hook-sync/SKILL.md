---
name: hook-sync
description: >-
  Syncs agent hooks (PreToolUse, PostToolUse, SessionStart, etc.) across
  Claude Code, Cursor, Codex CLI, and Gemini CLI from a single authoritative
  master store at ~/.hooks/. Models on skill-sync and mcp-sync. Applies
  per-target transforms (JSON vs YAML, embedded vs file-per-hook). Use when
  adding, editing, or removing a hook definition.
---

# hook-sync

One hook definition, propagated to every platform that supports hooks.
Same design pattern as `skill-sync` and `mcp-sync`: master store + target
transforms + surgical writes. Different targets store hooks differently
(Claude Code embeds them in `settings.json`; Cursor uses a directory; Codex
uses YAML), so symlinks can't do the job alone.

## Master store

```
~/.hooks/
├── verify-claim-gate.json
├── pr-review-self-check.json
├── workflow-gates-session.json
├── ticket-critic-build-gate.json
├── caveman-budget-auto.json
└── _schema.json        # JSON Schema for validation
```

Before adding a new hook, consult `shared/HOOK_PRINCIPLES.md` and verify
all five hook criteria are satisfied. Most enforcement belongs in skills
invoked on demand, not hooks. Over-hooking trains agents to ignore the
very checks you wrote.

## Hook definition shape

Target-agnostic. Each file describes one hook:

```json
{
  "$schema": "./_schema.json",
  "name": "verify-claim-gate",
  "description": "Block PR creation and git commit unless verify-claim passes",
  "events": [
    { "event": "PreToolUse", "tool": "Bash", "matcher": "git commit" },
    { "event": "PreToolUse", "tool": "Bash", "matcher": "gh pr create" }
  ],
  "action": {
    "type": "skill",
    "skill": "verify-claim"
  },
  "on_block": "halt",
  "timeout_ms": 10000,
  "platforms": ["claude-code", "cursor", "codex", "gemini"]
}
```

Alternate action types:

```json
{ "type": "command", "command": "ruff check --select F401 ${TOOL_INPUT_FILES}" }
{ "type": "prompt", "prompt_file": "~/.hooks/prompts/caveman-on.md" }
```

## Target matrix

| Target | Location | Format | Method |
|---|---|---|---|
| Claude Code (user) | `~/.claude/settings.json` → `hooks` | Embedded JSON | Surgical `jq` write |
| Claude Code (project) | `.claude/settings.json` → `hooks` | Embedded JSON | Surgical `jq` write |
| Cursor | `~/.cursor/hooks/*.json` | File per hook | Symlink where possible, else copy |
| Codex CLI | `~/.codex/hooks.yaml` | YAML | `yq` write |
| Gemini CLI | `~/.gemini/hooks.json` | JSON | Full-file rewrite (agent owns it) |
| Antigravity | `~/.gemini/antigravity/hooks.json` | JSON | Full-file rewrite |

Surgical writes for `settings.json` are required — those files carry
other user settings that must not be clobbered (same discipline as
`mcp-sync` with `~/.claude.json`).

## Transforms

### Claude Code (JSON embed)

```jq
.hooks += [
  {
    "event": "PreToolUse",
    "matcher": "Bash(git commit*)",
    "hooks": [
      { "type": "command", "command": "claude-skill verify-claim" }
    ]
  }
]
```

### Codex (YAML)

```yaml
hooks:
  - event: PreToolUse
    tool: Bash
    matcher: "git commit"
    action: { type: skill, skill: verify-claim }
```

### Cursor (file per hook)

One file per master hook; keep the name identical.

## Workflow

### Phase 1: Validate master

```bash
for f in ~/.hooks/*.json; do
  # Validate against _schema.json
  jq -e 'has("name") and has("events") and has("action")' "$f" > /dev/null \
    || { echo "INVALID: $f"; exit 1; }
done
```

### Phase 2: Apply transforms per target

```bash
# Claude Code user scope
for f in ~/.hooks/*.json; do
  # Read, transform, merge into ~/.claude/settings.json
  jq --slurpfile new <(transform_cc "$f") \
    '.hooks = ((.hooks // []) | map(select(.name != ($new[0].name))) + [$new[0]])' \
    ~/.claude/settings.json > /tmp/cc.json && mv /tmp/cc.json ~/.claude/settings.json
done
```

Repeat per target. Never replace the whole file — merge by `name`.

### Phase 3: Report

```markdown
## Hook Sync Status

| Hook | Claude Code | Cursor | Codex | Gemini |
|---|---|---|---|---|
| verify-claim-gate | OK | OK | OK | OK |
| redundancy-watcher-prewrite | OK | OK | SKIP (no tool support) | OK |
| caveman-compression | OK | OK | OK | OK |

Total: N hooks across M targets. K skipped (platform unsupported).
```

## Platform capability map

Not every platform supports every event. Honor capability:

| Event | Claude Code | Cursor | Codex | Gemini |
|---|---|---|---|---|
| SessionStart | yes | yes | yes | yes |
| PreToolUse | yes | yes | partial | yes |
| PostToolUse | yes | yes | partial | yes |
| UserPromptSubmit | yes | no | no | no |
| Stop | yes | yes | yes | yes |

If a master hook targets an event the platform doesn't support, mark
`SKIP (unsupported)` in the report — do not fail.

## SYMLINK_MAP integration

`hook-sync` extends `shared/SYMLINK_MAP.md` with a "Global Hook Paths"
section (see the companion edit). Hooks that can be symlinked (directory
targets, e.g., Cursor) use `ln -s`; embedded hooks (Claude Code
`settings.json`) use surgical write.

## Version bumps

- On master change: re-run `hook-sync`.
- On target tool upgrade that changes the schema: bump the schema
  version in `_schema.json`; re-apply.

## Hard rules

- Never clobber settings.json. Always merge by `name`.
- Never leave stale hooks in a target. Every sync does a full reconcile:
  targets' hooks minus master = delete; master minus target = add.
- Never sync a hook with no `name`. Unnamed hooks can't be reconciled.
- Never sync across an unknown schema version without running the
  migration (`~/.hooks/migrations/`).

## Output contract

```
HOOK SYNC: M hooks × N targets = MN operations
SUCCESS: X · SKIP: Y · ERROR: Z
```
