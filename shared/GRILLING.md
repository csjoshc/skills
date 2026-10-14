# Grilling: Shared Question-Round Rules

Used by planning skills (antiplan, make-prd) that interview the user to reach a shared understanding.
This is a reference file, not a skill.
Each skill keeps its own ledger, gates and question content; this file sets how a round is built and asked.

Adapted from Matt Pocock's `grilling` skill (MIT).

## The design tree

Map the plan as a design tree: every decision branches into the decisions that hang off it.
The **frontier** is every open decision whose prerequisites are already settled.
Those are the questions you can ask now without guessing at answers you haven't heard yet.

A question whose answer depends on another question still open in this round belongs to a later round.

## Rounds

1. Compute the frontier.
2. Ask the whole frontier in one round, up to 5 questions. If the frontier holds more, ask the 5 with the highest impact and carry the rest to the next round.
3. Number each question and give your recommended answer.
4. Word each question so "yes" accepts your recommendation.
5. Wait for the user's answers, then recompute the frontier. Settled decisions push it outward and unblock what depended on them.

When a decision is genuinely open (no clearly better option), still recommend one, and list the 2-3 concrete options with their trade-offs in the question body.

Format a round like so:

```
**Q1 - <question title>**: <question body, may include options and trade-offs>

Recommended: <your answer>

---

**Q2 - <question title>**: <question body>

Recommended: <your answer>
```

## Facts are your job, decisions are the user's

When a frontier question needs a fact from the environment (code, config, docs, tools, runtime), look it up yourself.
Ask the user only for what you can't look up.
A lookup can run in a subagent when that pays off (see `~/.skills/shared/SUBAGENTS.md`); inline is fine otherwise.

A pending lookup is an unsettled prerequisite.
Only the questions downstream of it wait; ask the rest of the frontier now.

Decisions belong to the user: put each one to them and wait for the answer.

## Done

The interview is done when the frontier is empty: every branch visited, nothing silently assumed.
If the user defers a decision, record the assumption you'll use and move on (the calling skill says where).
Act on the result only after the user confirms you've reached a shared understanding, or the calling skill's gate passes.
