#!/usr/bin/env bash
# PostToolUse: Edit — advisory if a .tickets/*.md file now contains "Stage: BUILD"
# Mode: advisory (exit 0)
INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null || echo "")

case "$FILE" in
  *".tickets/"*".md"|*"/tickets/"*".md") ;;
  *) exit 0 ;;
esac

[ -f ".claude/hooks-disabled" ] && exit 0

if grep -q "Stage: BUILD" "$FILE" 2>/dev/null; then
  echo "ADVISORY [ticket-critic-build-gate]: $FILE promoted to Stage: BUILD — run /ticket-critic for AC→Test traceability check."
fi
exit 0
