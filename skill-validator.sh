#!/bin/bash
# skill-validator.sh — Validates skill structure compliance
# Usage: ./skill-validator.sh [--fix] [<skill-dir>]

set -e

FIX_MODE=false
SKILL_DIR="${1:-.}"

if [[ "$1" == "--fix" ]]; then
  FIX_MODE=true
  SKILL_DIR="${2:-.}"
fi

ERRORS=0
WARNINGS=0

echo "=== Skill Structure Validator ==="
echo "Checking: $SKILL_DIR"
echo ""

# ── STRUCTURAL CHECKS ──────────────────────────────────────────────────────

# Check for line count issues (flag >500 without subsections)
echo "--- Line Count Check ---"
find "$SKILL_DIR" -name "SKILL.md" -type f | while read -r file; do
  lines=$(wc -l < "$file")
  dir=$(dirname "$file")
  
  if [[ $lines -gt 500 ]]; then
    subsections=$(grep -c "^## " "$file" || true)
    if [[ $subsections -lt 3 ]]; then
      echo "FAIL: $(basename "$dir") has $lines lines but only $subsections subsections"
      ERRORS=$((ERRORS + 1))
    else
      echo "OK: $(basename "$dir") has $lines lines with $subsections subsections"
    fi
  else
    echo "OK: $(basename "$dir") has $lines lines"
  fi
done

echo ""

# Check for TL;DR (Quick Start) line count
echo "--- TL;DR Line Count Check ---"
find "$SKILL_DIR" -name "SKILL.md" -type f | while read -r file; do
  dir=$(dirname "$file")
  tldr_lines=$(sed -n '/## TL;DR/,/##/p' "$file" | grep -v "##" | sed '/^$/d' | wc -l || true)
  if [[ $tldr_lines -gt 10 ]]; then
    echo "WARN: $(basename "$dir") TL;DR is too long ($tldr_lines lines, should be <= 10)"
    WARNINGS=$((WARNINGS + 1))
  else
    echo "OK: $(basename "$dir") TL;DR is $tldr_lines lines"
  fi
done

echo ""

# Check for assumption flagging in planning skills
echo "--- Assumption Flagging Check ---"
planning_skills=("spec-writer" "handoff" "write-prd" "ticket-critic")
for skill in "${planning_skills[@]}"; do
  file="$SKILL_DIR/$skill/SKILL.md"
  if [[ -f "$file" ]]; then
    count=$(grep -c "\[ASSUMPTION:" "$file" || true)
    if [[ $count -lt 1 ]]; then
      echo "WARN: $skill has no [ASSUMPTION:] flags"
      WARNINGS=$((WARNINGS + 1))
    else
      echo "OK: $skill has $count assumption flags"
    fi
  fi
done

echo ""

# Check for few-shot examples
echo "--- Few-Shot Examples Check ---"
find "$SKILL_DIR" -name "SKILL.md" -type f -exec sh -c '
  file="$1"
  count=$(grep -c "Example\|Input:\|Output:" "$file" 2>/dev/null || echo 0)
  dir=$(dirname "$file")
  if [[ $count -lt 2 ]]; then
    echo "FAIL: $(basename "$dir") has only $count example references (need 2+)"
    exit 1
  else
    echo "OK: $(basename "$dir") has $count example references"
  fi
' _ {} \;


echo ""

# Check for decision trees
echo "--- Decision Tree Check ---"
find "$SKILL_DIR" -name "SKILL.md" -type f -exec sh -c '
  file="$1"
  if grep -q "Decision\|when to use\|if.*then" "$file" 2>/dev/null; then
    echo "OK: $(basename "$(dirname "$file")") has decision guidance"
  else
    echo "WARN: $(basename "$(dirname "$file")") missing decision tree"
  fi
' _ {} \;


echo ""

# Check for escalation guidance
echo "--- Escalation/When to Block Check ---"
find "$SKILL_DIR" -name "SKILL.md" -type f -exec sh -c '
  file="$1"
  if grep -q "## Assumptions & Escalation\|## When to Block" "$file" 2>/dev/null; then
    echo "OK: $(basename "$(dirname "$file")") has escalation section"
  else
    echo "WARN: $(basename "$(dirname "$file")") missing escalation guidance"
  fi
' _ {} \;

echo ""

# Check for Windows backslashes in paths
echo "--- Path Format Check ---"
backslash_count=$(grep -r '\\\\' "$SKILL_DIR" --include="SKILL.md" 2>/dev/null | wc -l || true)
if [[ $backslash_count -gt 0 ]]; then
  echo "FAIL: Found $backslash_count Windows backslashes in paths"
  ERRORS=$((ERRORS + 1))
  grep -r '\\\\' "$SKILL_DIR" --include="SKILL.md" 2>/dev/null | head -5
else
  echo "OK: No Windows backslashes found"
fi

echo ""

# Check for magic numbers (unjustified constants)
echo "--- Magic Number Check ---"
magic_count=$(grep -rE '[A-Z_]+ = [0-9]+' "$SKILL_DIR" --include="SKILL.md" 2>/dev/null | grep -v "// " | grep -v "# " | wc -l || true)
if [[ $magic_count -gt 0 ]]; then
  echo "WARN: Found $magic_count potential magic numbers"
  WARNINGS=$((WARNINGS + 1))
else
  echo "OK: No unjustified magic numbers"
fi

echo ""

# Check for first-person descriptions
echo "--- Description Style Check ---"
first_person=$(grep -rE '\bI (can|will|help)\b' "$SKILL_DIR" --include="SKILL.md" 2>/dev/null | wc -l || true)
if [[ $first_person -gt 0 ]]; then
  echo "WARN: Found $first_person first-person descriptions (should be third-person)"
  WARNINGS=$((WARNINGS + 1))
else
  echo "OK: No first-person descriptions"
fi

echo ""

# ── SEMANTIC CHECKS ────────────────────────────────────────────────────────

# Check for shared file references (planning skills must reference ASSUMPTION_TIERS.md)
echo "--- Shared File Reference Check ---"
shared_tiers="shared/ASSUMPTION_TIERS.md"
shared_arch="shared/ARCHITECTURE_DECISIONS.md"
planning_skills=("spec-writer" "ticket-critic" "cleanup" "handoff" "write-prd" "tdd" "orchestrate")
for skill in "${planning_skills[@]}"; do
  file="$SKILL_DIR/$skill/SKILL.md"
  if [[ -f "$file" ]]; then
    if grep -q "$shared_tiers" "$file" 2>/dev/null; then
      echo "OK: $skill references ASSUMPTION_TIERS.md"
    else
      echo "WARN: $skill does not reference shared/ASSUMPTION_TIERS.md"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done

# Check that spec-writer references ARCHITECTURE_DECISIONS.md (not embedded)
spec_writer="$SKILL_DIR/spec-writer/SKILL.md"
if [[ -f "$spec_writer" ]]; then
  if grep -q "$shared_arch" "$spec_writer" 2>/dev/null; then
    echo "OK: spec-writer references ARCHITECTURE_DECISIONS.md"
  else
    echo "WARN: spec-writer does not reference shared/ARCHITECTURE_DECISIONS.md (may have embedded content)"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

echo ""

# Check for embedded Architecture Decisions in spec-writer
echo "--- Embedded Content Check ---"
if [[ -f "$spec_writer" ]]; then
  # Flag if spec-writer has >150 lines of embedded API/auth/data/testing patterns
  embedded=$(grep -c "### API Pattern\|### Authentication & Authorization\|### Data Layer\|### Testing Strategy\|### Code Organization" "$spec_writer" || true)
  if [[ $embedded -gt 2 ]]; then
    echo "FAIL: spec-writer has embedded Architecture Decisions ($embedded sections) — should reference shared/ARCHITECTURE_DECISIONS.md"
    ERRORS=$((ERRORS + 1))
  else
    echo "OK: spec-writer does not embed Architecture Decisions"
  fi
fi

echo ""

# Check for redundant companion files across skills
echo "--- Cross-Skill Redundancy Check ---"
# Check that GLOBAL_SYMLINKS.md and PROJECT_SYMLINKS.md don't exist in individual skills
for skill_dir in "$SKILL_DIR"/*/; do
  skill_name=$(basename "$skill_dir")
  for dup_file in "GLOBAL_SYMLINKS.md" "PROJECT_SYMLINKS.md"; do
    if [[ -f "$skill_dir/$dup_file" ]]; then
      echo "FAIL: $skill_name/$dup_file should be in shared/ — delete and reference shared/SYMLINK_MAP.md"
      ERRORS=$((ERRORS + 1))
    fi
  done
done
echo "OK: No redundant symlink maps found in individual skills"

echo ""

# Check token budget (SKILL.md > 200 lines should reference companions)
echo "--- Token Budget Check ---"
find "$SKILL_DIR" -name "SKILL.md" -type f | while read -r file; do
  lines=$(wc -l < "$file")
  dir=$(dirname "$file")
  skill_name=$(basename "$dir")
  
  if [[ $lines -gt 200 ]]; then
    # Check if it references companion files
    has_companions=$(grep -c "\[.*\.md\]\|See \[" "$file" || true)
    if [[ $has_companions -lt 1 ]]; then
      echo "WARN: $skill_name has $lines lines but no companion file references"
      WARNINGS=$((WARNINGS + 1))
    else
      echo "OK: $skill_name has $lines lines with $has_companions companion references"
    fi
  fi
done

echo ""

# Check stage enum consistency (skills referencing stages should point to orchestrate)
echo "--- Stage Enum Consistency Check ---"
stage_skills=("ticket-critic" "spec-writer")
for skill in "${stage_skills[@]}"; do
  file="$SKILL_DIR/$skill/SKILL.md"
  if [[ -f "$file" ]]; then
    if grep -q "orchestrate" "$file" 2>/dev/null; then
      echo "OK: $skill references orchestrate for stage enum"
    else
      echo "WARN: $skill may re-define stage enum instead of referencing orchestrate"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done

echo ""

# ── SUMMARY ────────────────────────────────────────────────────────────────

echo "=== Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [[ $ERRORS -gt 0 ]]; then
  echo "STATUS: FAILED"
  exit 1
elif [[ $WARNINGS -gt 0 ]]; then
  echo "STATUS: PASSED with warnings"
  exit 0
else
  echo "STATUS: PASSED"
  exit 0
fi
