# Skill Conventions

The enforceable baseline for skills in `~/.skills`.
`skillsmith/scripts/skill_audit.py` checks the mechanical parts.

Sources:
- Claude skill authoring best practices: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`
- Context hygiene and specialized review: `https://jdforsythe.github.io/10-principles/`
- Matt Pocock, `writing-for-agents` and `.agents/invocation.md` (MIT): `https://github.com/mattpocock/skills`

## Frontmatter

- `name`: max 64 chars, lowercase letters, numbers and hyphens, matches the folder name, no `anthropic` or `claude`.
- `description`: non-empty, max 1024 chars, third person.

## Invocation

Every skill is one of two kinds:

- **Model-invoked** (the default): the agent or the user can fire it, and other skills can call it.
  Its description is model-facing and always loaded, so it carries the trigger branches ("Use when ...").
- **User-invoked**: add `disable-model-invocation: true`.
  Only a human typing its name can fire it, and no other skill can call it.
  Its description is one human-facing line with no trigger list. The audit skips the "use when" and minimum-length checks for these.

Pick model-invoked only when the agent must reach the skill on its own, or another skill must call it.
Before flipping a skill to user-invoked, grep for skills that call it.
Harnesses that ignore the flag (Codex, some others) still auto-invoke it, so the short description is what pays off everywhere.

## Descriptions are context pointers

The description sits in every session's context, so every word costs on every turn.

- Front-load the leading word: the term the user actually types.
- One trigger per distinct branch. Synonyms for one branch are one trigger.
- Cut identity the body already carries.
- "Not for X (use Y)" routing earns its place only when mis-triggering is observed.

## Calling other skills

- To run another skill, write "Call the Skill tool with `<name>`", one call per skill.
- Material two or more skills need lives in `shared/` (or `standards/`, `reviews/`), not inside one skill's folder.
- A user-invoked skill can only be suggested to the human ("tell the user to run `/todo`"), never called.

## Structure

- SKILL.md body under 500 lines. It holds steps and decision logic.
- Inline what every branch needs; put what only some branches reach in a companion file linked directly from SKILL.md.
- References one level deep: no SKILL.md -> A -> B chains for required instructions.
- Companion files over 100 lines start with `## Contents`.

## Writing

- Every step ends on a completion criterion the agent can check.
- State the target behaviour, not the prohibition. Use a "don't" only for a hard guardrail, paired with the positive.
- Delete no-ops: sentences the model already obeys by default.
- Leave one-command lookups to the environment (`package.json`, config, `--help`). Record what the agent can't look up: conventions, reasons, gotchas.
- One meaning, one place. Prune stale lines; they cost more than missing ones.

## Review skills

A skill that reviews, audits or critiques:

1. Uses specialist lenses, not "review everything".
2. Runs deterministic checks (build, lint, test) before judgement.
3. Requires evidence per finding (file, line, trace).
4. Keeps review separate from code generation.

## Evals

Public skills should carry `evals/evals.json` (3+ behavior cases, 2+ trigger cases). Format and runner: `skillsmith/reference/evals.md`.

## Validate before commit

```bash
python3 ~/.skills/skillsmith/scripts/skill_audit.py ~/.skills
```
