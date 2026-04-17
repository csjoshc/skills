#!/usr/bin/env bash
# SessionStart — log fire; reminder to use /caveman when context is high
# Mode: setup-only (no block)
LOG=/Users/joshc/.skills/hooks/hook.log
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] caveman-budget-auto fired  cwd=$(pwd)" >> "$LOG"

[ -f ".claude/hooks-disabled" ] && exit 0

echo "CAVEMAN: If context window exceeds 50%, invoke /caveman to compress output."
exit 0
