# Stop Slop

A skill for removing formulaic AI patterns from prose without inventing facts or flattening the writer's voice.

## Skill Structure

```
stop-slop/
├── SKILL.md                              # Modes, safeguards, register, editing process
├── references/
│   ├── patterns.md                       # Patterns to inspect, with tests and fixes
│   ├── examples.md                       # Before/after transformations
│   ├── plain-vernacular-explainers.md    # Explaining technical work to outsiders
│   └── user-voice.md                     # Prose the user presents as their own
├── evals/                                # evals.json and fixture files
└── README.md
```

## What it catches

**Missing substance** - hollow drafts, importance claimed without mechanism, specific-looking vagueness, vague attribution. Gaps get a `[TK: question]`, never an invented detail.

**Formula** - binary contrasts, negative listing, colon reveals, forced triads, decorative `-ing` tails, abstract actors, structural regularity, recap endings.

**Surface residue** - stock words, throat-clearing, meta narration, chat wrappers, empty adverbs, jargon, formatting by habit.

Every pattern is a prompt to read the passage in context, not a ban. See `references/patterns.md`.

## Credits

Original skill by [Hardik Pandya](https://hvpandya.com).
Safeguards, register table, diagnosis order, and several pattern tests adapted from https://github.com/addyosmani/clarity @ e27ceef.

## License

MIT. Use freely, share widely.
