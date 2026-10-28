#!/bin/sh
# Codex registration entry point for the merge gate (see ~/.codex/hooks.json).
#
# Codex fails open: a hook that cannot start, exits non-zero or prints garbage lets the tool
# run. So this wrapper finds a working interpreter, and answers deny itself when there is
# none. The adapter prints deny JSON and always exits 0; an empty answer means allow.
set -u
here=$(CDPATH= cd -- "${0%/*}" && pwd)  # builtins only: a broken PATH must not hide the adapter

deny() {
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"BLOCKED [merge-gate]: the hook adapter could not start. It needs python3; set MERGE_GATE_PYTHON if it is not on PATH."}}'
}

for python in "${MERGE_GATE_PYTHON:-}" python3 /usr/bin/python3; do
  [ -n "$python" ] || continue
  command -v "$python" >/dev/null 2>&1 || continue
  if out=$("$python" "$here/merge-gate.py"); then
    [ -n "$out" ] && printf '%s\n' "$out"
    exit 0
  fi
done
deny
