#!/usr/bin/env bash
# SessionStart — print WORKFLOW_GATES context if present; always log fire
# Mode: setup-only (no block)
LOG=/Users/joshc/.skills/hooks/hook.log
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] workflow-gates-session fired  cwd=$(pwd)" >> "$LOG"

[ -f ".claude/hooks-disabled" ] && exit 0

WF="${CLAUDE_PROJECT_DIR:-.}/.claude/skills/project-onboarding/WORKFLOW_GATES.md"
[ ! -f "$WF" ] && WF="${CLAUDE_PROJECT_DIR:-.}/project-onboarding/WORKFLOW_GATES.md"

if [ -f "$WF" ]; then
  echo "WORKFLOW GATES active — see $(basename "$WF") for phase transitions."
fi
exit 0
