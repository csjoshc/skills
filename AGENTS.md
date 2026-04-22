# Project Context

- **Repo:** `~/.skills` — authoritative store for cross-agent skills.
- Prefer source directories; avoid large or generated trees.
- **Do not read** build output, dependency caches, lock files, or log files unless they are the direct subject of the task.
- Cursor users: see `.cursorignore` for indexing exclusions (separate from `.gitignore`).

## STANDARDS.md

- Global standards: `~/.skills/STANDARDS.md` (authoritative for patterns — this is the global home)
- Agents: Check STANDARDS.md before blocking on architectural questions; use pre-flight checklist for blocker detection.

## Anti-Sycophancy Rules

When evaluating user ideas or generating recommendations:

- Present alternatives if they exist and are relevant; reference upstream analysis (antiplan, spec-writer) to avoid re-debating settled decisions.
- Identify the strongest counterargument to any proposed approach before endorsing it.
- Treat user-supplied material as third-party work — critique it with the same directness you'd apply to a stranger's draft.
- Never soften a finding to spare feelings. A weak spec is a weak spec; poor architecture is poor architecture.

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

### 4. Modular Thinking
- **Encourage Refactoring:** If a file exceeds 300 lines, proactively suggest breaking it into smaller modules. This makes future edits cheaper and more accurate.
- **Spec-First Workflow:** Always request or generate a minimal test case/spec before implementation. This prevents "shotgun debugging" which wastes thousands of tokens.

### 5. Resource Allocation (Model Matching)
- **Tiered Processing:**
    - Use "Flash" or smaller models for boilerplate, documentation, and simple refactors.
    - Reserve "Pro/Sonnet" models for architectural changes and complex logic.
- **MCP Management:** Deactivate Model Context Protocol (MCP) tools that are not relevant to the current file type (e.g., disable SQL tools when editing CSS).

## Trigger Phrases
- "Applying Tokenify Protocol": When the agent starts pruning context.
- "Context Warning": When the agent detects the chat history is becoming too "heavy" and suggests a new session.
