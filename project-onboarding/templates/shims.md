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

Create symlinks for `CLAUDE.md` and `GEMINI.md` pointing to `AGENTS.md`. Use OS-specific commands:

### Windows (cmd.exe)

```batch
mklink CLAUDE.md AGENTS.md
mklink GEMINI.md AGENTS.md
```

### Windows (PowerShell)

```powershell
New-Item -ItemType SymbolicLink -Path "CLAUDE.md" -Target "AGENTS.md"
New-Item -ItemType SymbolicLink -Path "GEMINI.md" -Target "AGENTS.md"
```

### macOS/Linux

```bash
ln -s AGENTS.md CLAUDE.md
ln -s AGENTS.md GEMINI.md
```

### Python (cross-platform)

```python
import os
os.symlink('AGENTS.md', 'CLAUDE.md')
os.symlink('AGENTS.md', 'GEMINI.md')
```

**Note:** Only create these symlinks if they don't already exist. Add `CLAUDE.md` and `GEMINI.md` to `.gitignore` to avoid committing symlinks.

### Other tools

| Tool | How it picks up `AGENTS.md` |
|------|----------------------------|
| **OpenCode** | Reads `AGENTS.md` natively — no shim needed. |
| **GitHub Copilot** | Reads `AGENTS.md` natively. Optionally reference from `.github/copilot-instructions.md`. |
| **Windsurf** | Create `.windsurfrules` with same shim text as CLAUDE.md. |
| **Aider** | Add `read: AGENTS.md` to `.aider.conf.yml`. |
| **Cline** | Create `.clinerules` with same shim text as CLAUDE.md. |
