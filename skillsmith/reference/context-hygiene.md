# Context Hygiene Reference

Source: `https://jdforsythe.github.io/10-principles/principles/context-hygiene/`

## Contents

- Principle summary
- Enforceable requirements for skills
- Practical migration checks
- Anti-patterns to remove

## Principle Summary

Context is a finite attention budget, not durable memory.
Skill authoring should optimize signal density and avoid stale guidance.

## Enforceable Requirements for Skills

1. Keep always-loaded instructions lean.
- SKILL.md should route work and defer heavy detail.
- Large examples and templates should move to companion files.

2. Use progressive disclosure.
- Keep minimal always-needed context in SKILL.md.
- Load references/examples only for relevant tasks.

3. Prevent context poisoning.
- Remove outdated instructions and superseded rules.
- Do not retain contradictory legacy guidance in canonical files.

4. Respect information placement.
- Put identity and hard constraints early.
- Put execution checklists and retrieval anchors near the end.
- Avoid burying critical constraints in the middle of long files.

5. Externalize state.
- Durable process memory belongs in files, not chat-only context.

## Practical Migration Checks

Use these checks when remediating an existing skill:

- Is SKILL.md trying to be the full manual?
- Are there long templates or examples that can move to companion files?
- Are there stale instructions conflicting with current standards?
- Does the skill duplicate information the agent can discover from repo files?
- Are hard constraints discoverable in the first screen of SKILL.md?

## Anti-Patterns to Remove

- "Kitchen sink" skills that load everything up front.
- Never-pruned guidance that references old workflows.
- Deep companion reference chains where critical rules are hard to find.
- Verbose restatements of generic knowledge the model already has.

