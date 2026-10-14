#!/usr/bin/env bash
# Shared stdin parser for skill hooks. Source it, then call: hook_field command|file_path
# Harnesses nest fields differently (Claude: tool_input.*, Cursor: top level), so try all.

HOOK_INPUT=$(cat)
HOOK_PY=$(command -v python3 || command -v python)

hook_field() {
  [ -z "$HOOK_PY" ] && return 0
  printf '%s' "$HOOK_INPUT" | "$HOOK_PY" -c '
import sys, json
want = sys.argv[1]
keys = {"command": ["command", "cmd"], "file_path": ["file_path", "path", "filePath"]}[want]
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
for scope in (d.get("tool_input"), d.get("toolInput"), d.get("input"), d):
    if isinstance(scope, dict):
        for k in keys:
            v = scope.get(k)
            if isinstance(v, str) and v:
                print(v)
                sys.exit(0)
' "$1" 2>/dev/null
}

# Per-project kill switch, independent of which harness runs the hook.
hooks_disabled() {
  local root="${CLAUDE_PROJECT_DIR:-${CURSOR_PROJECT_DIR:-$PWD}}"
  [ -f "$root/.claude/hooks-disabled" ] || [ -f "$root/.hooks-disabled" ]
}

hook_project_root() {
  printf '%s' "${CLAUDE_PROJECT_DIR:-${CURSOR_PROJECT_DIR:-$PWD}}"
}
