# AGENTS.md Verbatim Blocks

## Contents

- Tokenify block
- Engineering principles block
- graphify (if present)
- MCP Tools (optional)

Copy-verbatim blocks appended to `AGENTS.md` after the stack preamble. Extracted from `SKILL.md` for the 500-line budget.

### Tokenify block (append after Engineering principles block — copy verbatim)

```markdown
# Tokenify — Context & Token Optimization

## Goal
Minimize token consumption and prevent context window pollution while maintaining high accuracy in code generation and task execution.

## Operational Rules

### 1. Context Minimization (Surgical Mentions)
- **Do not read entire directories** unless specifically instructed.
- **Selective Reading:** Before reading a file, check if a summary or the file structure (tree) is sufficient.
- **Exclude Noise:** Automatically ignore lock files (`package-lock.json`, `pnpm-lock.yaml`), build artifacts, and large static assets unless they are the direct subject of the task.

### 2. Information Density
- **Log Pruning:** When analyzing errors, do not ingest entire terminal outputs. Extract only the stack trace and the specific error message.
- **Concise Responses:** Avoid conversational filler ("Certainly!", "I have updated the file..."). Provide the direct solution or the diff.
- **Diffs over Rewrites:** Whenever possible, output only the modified lines (diff format) rather than rewriting a 500-line file to change two variables.

### 3. Task Segmentation
- **Sub-tasking:** If a request is complex (e.g., "Build the API and the UI"), decompose it. Propose to handle the API first, then "Reset" or start a new context for the UI.
- **The "Clean Slate" Protocol:** If a bug remains unresolved after 3 attempts, signal the user to "Hard Reset" the chat to purge the accumulated "hallucination debt" in the current context.

### 4. Resource Allocation (Model Matching)
- **Tiered Processing:**
    - Use "Flash" or smaller models for boilerplate, documentation, and simple refactors.
    - Reserve "Pro/Sonnet" models for architectural changes and complex logic.
- **MCP Management:** Deactivate Model Context Protocol (MCP) tools that are not relevant to the current file type (e.g., disable SQL tools when editing CSS).

## Trigger Phrases
- "Applying Tokenify Protocol": When the agent starts pruning context.
- "Context Warning": When the agent detects the chat history is becoming too "heavy" and suggests a new session.
```


### Engineering principles block (always add; place right after the Code comments block — copy verbatim)

```markdown
# Engineering principles

Before writing code, in order:
1. Reuse: check the repo, stdlib and platform first. Don't reinvent.
2. YAGNI: build only what was asked. No abstraction for a single use.
3. DRY: dedupe repeated *knowledge* at the 2nd-3rd real use, not look-alike code.
4. SOLID: reshape only when a second real consumer or change pressure exists.
YAGNI wins over DRY/SOLID until then. Prefer the shortest solution that is still correct.

Never trade away validation, error handling or auth checks at trust boundaries for brevity.
Touch only what the task needs; match existing style.
If requirements are ambiguous or conflict, state your assumption and ask. Don't pick silently.
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
