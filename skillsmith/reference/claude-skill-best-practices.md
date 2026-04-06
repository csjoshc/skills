# Claude Skill Best Practices Reference

Source: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`

## Contents

- Mandatory metadata requirements
- Structural requirements
- Progressive disclosure requirements
- Quality checklist used for enforcement

## Mandatory Metadata Requirements

1. `SKILL.md` must include frontmatter with `name` and `description`.
2. `name` rules:
- Max 64 chars
- Lowercase letters, numbers, hyphens only
- No reserved words like `anthropic` or `claude`

3. `description` rules:
- Non-empty
- Max 1024 chars
- Third-person voice
- Must say what the skill does and when to use it
- Should include concrete trigger terms for discovery

## Structural Requirements

1. Keep SKILL.md body under 500 lines.
2. Split additional detail into companion files.
3. Keep references one level deep from SKILL.md.
4. Keep terminology consistent across SKILL and companions.
5. Keep examples concrete and operational.

## Progressive Disclosure Requirements

1. SKILL.md should act as overview and navigation.
2. Companion files should hold deep references, examples, and large workflows.
3. Long companion files (>100 lines) should include `## Contents` near top.
4. Avoid deep nested reference chains to prevent partial-read failures.

## Quality Checklist Used for Enforcement

- Description is specific and discoverable.
- Description includes what + when.
- SKILL.md remains under line budget.
- Companion files are used when needed.
- References are one level deep.
- Workflows are sequential and checkable.
- Required dependencies and tools are explicit.

