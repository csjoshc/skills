#!/usr/bin/env bash
# Render a .mmd source to both light and dark SVGs.
#
# Usage:
#   render.sh <input.mmd> [output-basename]
#
# Produces:
#   <basename>.light.svg
#   <basename>.dark.svg
#
# If output-basename is omitted, uses the input path without the .mmd suffix.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIGHT_CFG="$SKILL_DIR/palettes/light.json"
DARK_CFG="$SKILL_DIR/palettes/dark.json"

if [[ $# -lt 1 ]]; then
  echo "usage: $(basename "$0") <input.mmd> [output-basename]" >&2
  exit 2
fi

INPUT="$1"
BASE="${2:-${INPUT%.mmd}}"

if ! command -v mmdc >/dev/null 2>&1; then
  echo "error: mmdc not found. Install with: npm i -g @mermaid-js/mermaid-cli" >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "error: input not found: $INPUT" >&2
  exit 1
fi

echo "→ rendering $INPUT"
mmdc -i "$INPUT" -o "${BASE}.light.svg" -c "$LIGHT_CFG" -b transparent
mmdc -i "$INPUT" -o "${BASE}.dark.svg"  -c "$DARK_CFG"  -b transparent

echo "✓ ${BASE}.light.svg"
echo "✓ ${BASE}.dark.svg"
