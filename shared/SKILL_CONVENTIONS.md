# Skill Conventions

This file defines the enforceable baseline for skills in `~/.skills`.

## Source Baseline

These conventions are grounded in:

- Context Hygiene Principle: `https://jdforsythe.github.io/10-principles/principles/context-hygiene/`
- Specialized Review Principle: `https://jdforsythe.github.io/10-principles/principles/specialized-review/`
- Claude skill authoring best practices: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`

## Core Rule

Keep always-loaded context lean and high-signal. Push details into companion files and load only when needed.

## Required Structure (All SKILL.md Files)

1. Include YAML frontmatter with:
- `name`
- `description`

2. Frontmatter validation:
- `name` must be lowercase letters, numbers, hyphens only.
- `name` must not contain reserved words like `anthropic` or `claude`.
- `description` must be third-person (avoid `I`, `you`, `we`).
- `description` must state what the skill does and when to use it.

3. Size limit:
- Keep SKILL.md body under 500 lines.
- If near the limit, split into companion files.

4. Progressive disclosure:
- Keep SKILL.md as overview, decision logic, and routing.
- Move large templates, examples, references, and checklists to companion files.
- SKILL.md must link to those companions directly.

5. Reference depth:
- Keep references one level deep from SKILL.md.
- Avoid SKILL.md -> file A -> file B dependency chains for required instructions.

6. Companion navigation:
- Any companion/reference file longer than 100 lines should include `## Contents` near the top.

## Context Hygiene Rules

1. Store durable state in files, not chat history.
2. Remove stale instructions quickly (context poisoning is worse than context bloat).
3. Put high-priority identity and hard constraints near the beginning of SKILL.md.
4. Put execution checklists and retrieval anchors near the end of SKILL.md.
5. Do not include discoverable repo facts the agent can read directly.

## Specialized Review Rules (Review Skills)

If a skill performs review/audit/critique, it must:

1. Prefer specialist lenses over generic "review everything" instructions.
2. Run deterministic checks before LLM judgment when applicable (build/lint/test/static checks).
3. Require evidence for each finding (file/line/trace, not bare claims).
4. Keep reviewer responsibility separate from code-generation responsibility.
5. Use domain vocabulary and named anti-patterns for each review lens.

## Shared vs Local Content

Move content to `shared/` when it is reused by 2+ skills.

Keep in skill-local companions when content is:
- Domain-specific
- Workflow-specific
- Not broadly reused across skills

## Maintenance

- Review and prune skill instructions on a regular cadence.
- Update this file only when rules are changed for all skills.
- Validate before commit:

```bash
python3 /Users/joshchiu/.skills/skillsmith/scripts/skill_audit.py /Users/joshchiu/.skills
```

