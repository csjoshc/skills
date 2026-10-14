# Context Hygiene Reference

Sources: `https://jdforsythe.github.io/10-principles/principles/context-hygiene/`, and Matt Pocock's `writing-for-agents` (MIT, `https://github.com/mattpocock/skills`).
The enforceable rules live in [../../shared/SKILL_CONVENTIONS.md](../../shared/SKILL_CONVENTIONS.md); this file explains why they hold and how to apply them.

## Contents

- The two loads
- Information hierarchy
- Pruning
- Migration checks

## The two loads

Every document and pointer spends one of two budgets.

- **Context load** is the cost on the agent's window of anything always loaded: a skill description, an `AGENTS.md` line.
  It spends tokens and attention every turn, whether or not it fires.
- **Cognitive load** is the cost on the human, who has to remember which documents exist and when to reach for each.
  Spend it where human judgement matters, and remove it where it does not.

Material reached only through a pointer pays context load for the pointer's line alone.
Material with no pointer rides entirely on cognitive load.
The pointer's wording, not its target, decides when the agent reaches the material.
When a must-have target is reached unreliably, sharpen the pointer first, and inline the material only if that fails.

## Information hierarchy

A document holds **steps** (ordered actions) and **reference** (rules and facts consulted on demand).
Each piece sits on a ladder ranked by how immediately the agent needs it:

1. **In-file step**: what the agent does, in order.
2. **In-file reference**: consulted on demand. A flat set of peer rules on one rung is fine.
3. **Disclosed reference**: a separate file behind a pointer, loaded only when the pointer fires.

Push too little down and the top bloats; push too much and you hide material the agent needs.
The branching test settles it: inline what every branch needs, and put behind a pointer what only some branches reach.
Reference left inline above the steps buries them, and the agent attends to them less reliably.

**Co-location**: keep a concept's definition, rules and caveats under one heading, so reading one part brings its neighbours.

**Sprawl** is a document too long even when every line is live.
Attention thins across the excess.
Cure it with the ladder: disclose reference, and split by branch or sequence so each path carries only what it needs.

## Pruning

- **Single source of truth**: each meaning lives in one place, so changing behaviour is a one-place edit.
  Duplication costs tokens and inflates a meaning's prominence past its real rank.
- **Cache**: a document that restates the environment (`package.json` scripts, config, directory layout, `--help`) is a copy of a lookup that will go stale.
  Record what the agent cannot find by looking: the unwritten convention, the reason behind a choice, the gotcha no config confesses.
- **Sediment**: stale layers that settle because adding feels safe and removing feels risky.
  Check every line for relevance to what the document does today, and delete what has gone stale or never bore on the task.
- **No-ops**: an instruction the model already obeys by default pays load to say nothing.
  Test each sentence: does it change behaviour versus the default?
  When it fails, delete the whole sentence.
  A leading word too weak to beat the default (_be thorough_) is a no-op too; replace it with a stronger word (_relentless_).
- **Negation**: a prohibition puts the banned behaviour into context and makes it more available.
  State the target behaviour instead. Keep a prohibition only as a hard guardrail, paired with its positive.

## Migration checks

Remediating an existing skill is done when every check holds:

- SKILL.md carries only steps, decision logic and what every branch needs; branch-only material sits in companions.
- Long templates and examples live in companion files linked directly from SKILL.md.
- No line contradicts current standards in `shared/SKILL_CONVENTIONS.md`, and no superseded rule remains.
- No line restates what the agent can find in one lookup in the repo.
- Hard constraints appear on the first screen of SKILL.md.
