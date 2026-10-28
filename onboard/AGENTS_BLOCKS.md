# AGENTS.md Verbatim Blocks

## Contents

- Tokenify block
- Engineering principles block
- graphify (if present)
- MCP Tools (optional)

Copy-verbatim blocks appended to `AGENTS.md` after the stack preamble. Extracted from `SKILL.md` for the 500-line budget.

### Tokenify block (optional, on request; append after Engineering principles block - copy verbatim)

```markdown
# Tokenify
- Read only what the task needs: skip lock files, build output and large assets; from long logs take the error and stack trace.
- After 3 failed attempts at one bug, stop and suggest a fresh session with a handoff.
```

### Engineering principles block (always add; place right after the Code comments block - copy verbatim)

```markdown
# Engineering principles

Before writing code, in order:
1. Reuse: use what the repo, stdlib and platform already provide.
2. YAGNI: build only what was asked. Add an abstraction once it has a second real use.
3. DRY: dedupe repeated *knowledge* at the 2nd-3rd real use, not look-alike code.
4. SOLID: reshape only when a second real consumer or change pressure exists.
YAGNI wins over DRY/SOLID until then.
Prefer the smallest coherent change that is correct, readable, and complete.

Keep validation, error handling and auth checks at trust boundaries, even when they cost lines.
Touch only what the task needs; match existing style.
If requirements are ambiguous or conflict, state your assumption and ask before choosing.
```

### graphify (if present)

If `graphify-out/` exists, add this block to `AGENTS.md`:

```markdown
## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current
```

### MCP Tools (optional)

Add any Model Context Protocol tools available in your workflow:

```markdown
## Available MCP Tools

- **[your-mcp-name-1]** - [brief description of what it does]
- **[your-mcp-name-2]** - [brief description]
```


---
