---
name: redundancy-watcher
description: >-
  Blocks duplicate implementations and speculative code at write time, before
  they land. Searches for existing symbols, file names, and docstrings that
  already cover the use case before any new file or export is created. Flags
  unused exports and dead branches. Use before creating any new module, utility,
  helper, or constant.
---

# redundancy-watcher

Stops duplication before it lands. Cleanup-time dedup always loses to
write-time refusal — once a second implementation exists, tests depend on
it and the duplicate becomes permanent.

## Contents

- When to invoke
- Phase 1 — Symbol-level search
- Phase 2 — File-level similarity
- Phase 3 — Decision table
- Phase 4 — Hand off to cleanup
- "Just in case" heuristics
- Hard rules
- Output contract

---

## When to Invoke

Invoke before:

- Creating any new file (`Write` of a non-existent path)
- Adding a new exported symbol to an existing file
- Copying code from an existing file
- Introducing a new constant, config flag, or feature toggle
- Writing a new "utility" or "helper" module

Skip only for:

- Test files (test-file duplication is inherent to test isolation)
- Generated files (codegen output, migrations)
- One-off scripts in `scripts/` or `tools/`

---

## Phase 1 — Symbol-Level Search

For each proposed new symbol (function, class, const):

```bash
# Exact name match
grep -rEn "(def|function|const|class|export)\s+${SYMBOL}\b" \
  --include='*.ts' --include='*.tsx' --include='*.py' --include='*.js' \
  --exclude-dir=node_modules --exclude-dir=.git .

# Fuzzy name match (edit distance 2)
python3 -c "import difflib,sys; print(difflib.get_close_matches('${SYMBOL}', sys.stdin.read().split(), n=10, cutoff=0.75))" < <(cat all_symbols.txt)
```

Query `codebase-memory-mcp` if available:
mcp**codebase-memory-mcp**search_code: "${SYMBOL}"
mcp**codebase-memory-mcp**search_graph: semantic match on purpose

---

## Phase 2 — File-Level Similarity

```bash
# Path similarity
find . -type f -name "*$(basename ${NEW_FILE} .${EXT})*" -not -path '*/node_modules/*'

# Top-of-file docstring match (first 20 lines vs proposed purpose)
for f in $(find . -type f -name "*.py" -o -name "*.ts"); do
  head -20 "$f" | grep -iE "$(echo ${PROPOSED_PURPOSE} | tr ' ' '|')" && echo "^ $f"
done
```

---

## Phase 3 — Decision Table

| Finding                                          | Action                                     |
| ------------------------------------------------ | ------------------------------------------ |
| Exact symbol match in same layer                 | **BLOCK** — extend existing                |
| Fuzzy match (edit dist ≤ 2) in same layer        | **BLOCK** unless purpose clearly different |
| Same purpose in different file (docstring match) | **BLOCK** — consolidate                    |
| Similar symbol in lower layer                    | **ASK** — consider moving to lower layer   |
| Similar symbol in higher layer                   | **PROCEED** — lower layer is correct home  |
| No match                                         | **PROCEED**                                |

On **BLOCK**, emit:

```markdown
## REDUNDANCY BLOCK

Proposed: `<new symbol / file>`
Existing: `<path>:<line> — <existing symbol>`
Similarity: <exact | fuzzy | purpose>

Recommended action:

1. Extend `<existing symbol>` instead of creating new
2. If truly different: rename to disambiguate and justify in 1 sentence
3. Override: user types "override" with justification

Do not proceed until resolved.
```

---

## Phase 4 — Hand Off to Cleanup

Do **not** re-run the dead-code tool matrix here. After any write/edit,
note changed files and surface them to `cleanup`'s Phase 0, which owns
the canonical tool run (`ruff F401`, `ts-prune`, `knip`, `vulture`, comment
greps). Running both produces duplicate findings.

---

## "Just in Case" Heuristics

Reject these patterns unless the PR description cites a concrete, imminent
(within 1 sprint) consumer:

- New `optional` parameters with no caller passing them
- Feature flags with a single code path (always-on or always-off)
- `if DEBUG` blocks referencing unpublished features
- Abstract base classes with a single concrete subclass
- Config keys with no reader
- Public exports from an internal module

For each: _who calls this within the next two weeks?_ If "nobody yet" — delete it.

---

## Hard Rules

- A BLOCK may only be overridden by explicit user text, not agent reasoning alone.
- Never dedup across layers by pulling lower-layer code upward — push the
  shared piece to a lower layer both callers can use.
- Dead-code findings are advisory, not auto-delete.

---

## Output Contract

Exactly one of:

1. `REDUNDANCY OK: N proposals, 0 blocks.`
2. `REDUNDANCY BLOCK: <proposal> vs <existing>. Awaiting resolution.`
