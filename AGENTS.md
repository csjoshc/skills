# AI Agent Guidelines

**Location:** `~/.skills/AGENTS.md`

**Purpose:** Provide AI agents with context about this skills repository and how to work within it.

---

## Project Overview

This is a **skills repository** containing AI agent skills for various development tasks. Each skill is a self-contained module that can be invoked by AI agents to perform specialized tasks.

**Stack:**
- **Shell scripts:** Bash/PowerShell skill wrappers
- **Python:** Core skill logic (`sync.py`, skill implementations)
- **Markdown:** Documentation, standards, ticket specs

**Key Directories:**
- `chrome-devtools/` — Browser testing and debugging
- `cleanup/` — Code cleanup utilities
- `cmd-cli/` — CLI tool wrappers (git, docker, npm)
- `make-ui/` — UI design and implementation
- `project-onboarding/` — Project setup and AI configuration
- `spec-writer/` — Technical specification generation
- `tdd/` — Test-driven development workflows
- `ticket-critic/` — Ticket review and analysis
- `templates/` — Reusable templates for skills
- `.tickets/` — Ticket specifications
- `.handoff/` — Handoff documentation
- `.orchestra/` — Orchestration configuration

---

## How to Work in This Repository

### 1. Before Making Changes

1. **Read STANDARDS.md** — Contains architectural decisions and resolved questions
2. **Check existing skills** — Avoid duplicating functionality
3. **Review ticket specs** — Located in `.tickets/` directory

### 2. Creating New Skills

**Structure:**
```
skill-name/
├── skill-name.sh          # Entry point (Bash wrapper)
├── skill-name.py          # Core logic (if Python)
├── README.md              # Usage documentation
└── templates/             # Skill-specific templates (optional)
```

**Naming:**
- Use kebab-case: `my-skill/`, not `my_skill/` or `MySkill/`
- Entry point: `skill-name.sh` or `skill-name.ps1` (Windows)

**Documentation:**
- Include TL;DR section
- Decision tree for skill logic
- Usage examples
- When to use / when NOT to use

### 3. Editing Existing Skills

1. **Read the entire skill file** before editing (capture indentation/whitespace)
2. **Use shortest unique snippets** for replacements
3. **Preserve existing patterns** — match style, structure, conventions
4. **Update README** if changing behavior

### 4. Testing Changes

- Run skill manually to verify behavior
- Check logs in `.orchestra_logs/` if applicable
- Update `skill-discovery-index.md` if adding new skill

---

## Common Tasks

### Adding a New Skill

1. Create skill directory with entry point script
2. Add README.md with usage docs
3. Register in `skill-discovery-index.md`
4. Test invocation via agent tool

### Updating STANDARDS.md

1. Add new resolved questions under "Resolved Questions"
2. Document architectural decisions
3. Update security checklist if needed
4. Append project-specific section if major changes

### Working with Tickets

1. Check `.tickets/` for ticket specifications
2. Use `ticket-critic` skill to review tickets
3. Follow blocker detection checklist in STANDARDS.md
4. Update ticket status as you work

---

## Windows-Specific Notes

**Shell Scripts:**
- Use `.ps1` (PowerShell) wrappers for Windows
- Avoid Unix-specific paths (`/usr/bin`, etc.)
- Use forward slashes in paths when possible (Git-compatible)

**Python:**
- Use `pathlib` for cross-platform path handling
- Avoid hardcoded path separators
- Test on Windows before committing

**Git:**
- Configure `core.autocrlf` appropriately
- Use `.gitattributes` to control line endings

---

## Security Considerations

**This repository contains AI agent skills that may:**
- Execute shell commands
- Access external services
- Modify project files

**Before implementing new skills:**

1. **Validate user input** — Never pass directly to subprocess
2. **Limit permissions** — Skills should only access necessary resources
3. **Audit logging** — Log sensitive operations
4. **Document risks** — Add security notes to skill README

---

## Quick Reference

| Task | Command / Skill |
|------|-----------------|
| Onboard new project | `npx project-onboarding` |
| Review ticket | `/ticket-critic` |
| Write spec | `/spec-writer` |
| Create PR | `/create-pr` |
| Sync skills | `python sync.py` |
| Check standards | Read `STANDARDS.md` |

---

## Getting Help

- **Skill documentation:** Check skill's `README.md`
- **Architecture questions:** See `STANDARDS.md`
- **Ticket specs:** `.tickets/` directory
- **Logs:** `.orchestra_logs/` directory
