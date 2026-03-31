# Shim Templates

## `.cursorrules` (Cursor-specific)

`.cursorrules` no longer holds full instructions. It references `AGENTS.md` and adds Cursor-specific notes.

Pick the stack variant matching detection. If appending to an existing `.cursorrules`, append to the bottom.

### npm only

```markdown
# Project context (npm / Node)

- Full project conventions, context exclusions, and Tokenify rules: see `AGENTS.md`.
- Indexing exclusions: `.cursorignore` (separate from `.gitignore`).
```

### Python only

```markdown
# Project context (Python)

- Full project conventions, context exclusions, and Tokenify rules: see `AGENTS.md`.
- Indexing exclusions: `.cursorignore` (separate from `.gitignore`).
```

### npm + Python

```markdown
# Project context (npm / Node + Python)

- Full project conventions, context exclusions, and Tokenify rules: see `AGENTS.md`.
- Indexing exclusions: `.cursorignore` (separate from `.gitignore`).
```

### Neither

```markdown
# Project context

- Full project conventions, context exclusions, and Tokenify rules: see `AGENTS.md`.
- Indexing exclusions: `.cursorignore` (separate from `.gitignore`).
```

## Cross-tool shims

### `CLAUDE.md` (Claude Code)

```markdown
Read and follow AGENTS.md in this directory for project conventions,
context exclusions, and operational rules.
```

### `GEMINI.md` (Gemini CLI)

```markdown
Read and follow AGENTS.md in this directory for project conventions,
context exclusions, and operational rules.
```

### Other tools

| Tool | How it picks up `AGENTS.md` |
|------|----------------------------|
| **OpenCode** | Reads `AGENTS.md` natively — no shim needed. |
| **GitHub Copilot** | Reads `AGENTS.md` natively. Optionally reference from `.github/copilot-instructions.md`. |
| **Windsurf** | Create `.windsurfrules` with same shim text as CLAUDE.md. |
| **Aider** | Add `read: AGENTS.md` to `.aider.conf.yml`. |
| **Cline** | Create `.clinerules` with same shim text as CLAUDE.md. |
