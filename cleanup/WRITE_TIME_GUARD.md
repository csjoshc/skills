---
name: redundancy-watcher
description: >-
  Blocks duplicate implementations and "just in case" code at write time, not
  cleanup time. Before any new file or new export is added, searches the
  codebase for existing symbols, file names, and docstrings that already
  cover the use case. Flags unused exports, dead branches, commented-out
  blocks, and feature flags with no consumer. Use before creating any new
  module, utility, helper, or constant.
---

# redundancy-watcher

Stops duplication before it lands. Cleanup-time dedup always loses to
write-time refusal — once the second implementation exists, someone's tests
depend on it and the dup becomes permanent. This skill enforces the
"never reinvent" rule from `antiplan` at the moment of creation.

## When to invoke

Invoke before:

- Creating any new file (`Write` of a non-existent path)
- Adding a new exported symbol to an existing file
- Copying code from an existing file (pattern duplication)
- Introducing a new constant, config flag, or feature toggle
- Writing a new "utility" or "helper" module

Skip only for:

- Test files (test-file duplication is inherent to test isolation)
- Generated files (codegen output, migrations)
- One-off scripts in `scripts/` or `tools/`

## Workflow

### Phase 1: Symbol-level search

For each proposed new symbol (function, class, const):

```bash
# Exact name match
grep -rEn "(def|function|const|class|export)\s+${SYMBOL}\b" \
  --include='*.ts' --include='*.tsx' --include='*.py' --include='*.js' \
  --exclude-dir=node_modules --exclude-dir=.git .

# Fuzzy name match (edit distance 2)
python3 -c "import difflib,sys; print(difflib.get_close_matches('${SYMBOL}', sys.stdin.read().split(), n=10, cutoff=0.75))" < <(cat all_symbols.txt)
```

Also query codebase-memory-mcp if available:

```
mcp__codebase-memory-mcp__search_code: "${SYMBOL}"
mcp__codebase-memory-mcp__search_graph: semantic match on purpose
```

### Phase 2: File-level similarity

For each proposed new file path:

```bash
# Path similarity
find . -type f -name "*$(basename ${NEW_FILE} .${EXT})*" -not -path '*/node_modules/*'

# Top-of-file docstring match (first 20 lines vs proposed purpose)
for f in $(find . -type f -name "*.py" -o -name "*.ts"); do
  head -20 "$f" | grep -iE "$(echo ${PROPOSED_PURPOSE} | tr ' ' '|')" && echo "^ $f"
done
```

### Phase 3: Decision

| Finding | Action |
|---|---|
| Exact symbol match in same layer | **BLOCK** — extend existing |
| Fuzzy match (edit dist ≤ 2) in same layer | **BLOCK** unless purpose clearly different |
| Same purpose in different file (docstring match) | **BLOCK** — consolidate |
| Similar symbol in lower layer | **ASK** — consider moving to lower layer |
| Similar symbol in higher layer | **PROCEED** — lower layer is correct home |
| No match | **PROCEED** |

On **BLOCK**, emit:

```markdown
## REDUNDANCY BLOCK

Proposed: `<new symbol / file>`
Existing: `<path>:<line> — <existing symbol>`
Similarity: <exact | fuzzy | purpose>

Recommended action:
1. Extend `<existing symbol>` instead of creating new
2. If truly different: rename proposal to disambiguate and justify in 1 sentence
3. Override: user types "override" with justification

Do not proceed until resolved.
```

## Phase 4: Dead-code scan on changed files

After any write/edit, scan the changed files only:

```bash
# Python
ruff check --select F401,F841 ${CHANGED_FILES}
vulture ${CHANGED_FILES} --min-confidence 80

# TypeScript
npx ts-prune --project tsconfig.json | grep -E "$(echo ${CHANGED_FILES} | tr ' ' '|')"
npx knip --include files,exports

# Comments / TODOs
grep -En '^\s*(//|#).*(TODO|FIXME|HACK|XXX|someday|maybe)' ${CHANGED_FILES}
grep -En '^\s*(//|#).*\b(DEBUG|if\s+false|if\s+0)\b' ${CHANGED_FILES}
```

Flag each finding. Do not auto-delete — the user may have a reason. Report:

```markdown
## DEAD-CODE FINDINGS (advisory)

| File | Line | Kind | Note |
|---|---|---|---|
| src/utils.ts | 42 | unused export | `parseLegacy` has 0 importers |
| src/api.py | 17 | orphan TODO | "someday make this async" — 3 years old |
```

## "Just in case" heuristics

Reject these patterns unless the PR description cites a concrete, imminent
(within 1 sprint) consumer:

- New `optional` parameters with no caller passing them
- Feature flags with a single code path (always-on or always-off)
- `if DEBUG` blocks that reference unpublished features
- Abstract base classes with a single concrete subclass
- Config keys with no reader
- Public exports from an internal module

For each, ask: *who calls this within the next two weeks?* If the answer is
"nobody yet, but maybe later" — delete it.

## Interaction with other skills

- `cleanup` mechanical-pass: runs the same dead-code scans after landing;
  this skill is the write-time version.
- `antiplan` AP-1 through AP-14: this is the runtime enforcer for AP-4
  (never reinvent) and AP-9 (YAGNI).
- `layer-boundary-critic`: when redundancy sits across layers, boundary
  critic decides the correct home.
- `workflow-guard`: invokes redundancy-watcher before any `Write` of a
  new file path.

## Hard rules

- A BLOCK may only be overridden by explicit user text, not by agent
  reasoning alone. "I think these are different enough" is not an override.
- Never dedup across layers by pulling lower-layer code upward — dedup
  means pushing the shared piece to a lower layer both callers can use.
- Dead-code findings are advisory, not auto-delete. The agent reports; the
  user decides.

## Output contract

Exactly one of:

1. `REDUNDANCY OK: N proposals, 0 blocks, K dead-code advisories.`
2. `REDUNDANCY BLOCK: <proposal> vs <existing>. Awaiting resolution.`
