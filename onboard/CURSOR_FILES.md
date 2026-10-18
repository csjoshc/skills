# Cursor Files

## Contents

- core-agent-behavior.mdc
- .cursorignore

## core-agent-behavior.mdc

Create **`.cursor/rules/core-agent-behavior.mdc`** with exactly this content:

```markdown
---
description: Core agent behavior — concise replies and minimal code surface
alwaysApply: true
---

# CORE DIRECTIVES

- **Read and follow \`AGENTS.md\`** in the project root for all project conventions, context exclusions, and operational rules.
- Be extremely concise.
- Do not explain code unless explicitly asked.
- NO pleasantries (e.g., 'Sure!', 'I can help').
- Provide only the code or the direct answer.
- For small changes, provide snippets, not the whole file.
```

If `.cursor/rules/` does not exist, create it.

---

## `.cursorignore` — use only the blocks for detected stacks

Cursor reads **`.cursorignore`** at the project root for indexing and `@` context. It is **not** `.gitignore`; duplicate patterns when needed. Most other tools only respect `.gitignore`, which is why `AGENTS.md` embeds the exclusion list directly.

**Always include** the **Universal** block. **Add npm block** if npm/Node detected. **Add Python block** if Python detected.

When merging into an existing `.cursorignore`: keep user lines; append missing patterns; deduplicate exact lines; preserve section comments.

Verbatim Universal / npm / Python blocks live in [cursorignore-blocks.md](cursorignore-blocks.md). Copy what applies to the detected stack.
