# Skill Evals

Small, per-skill test sets that show whether a skill earns its place. Build them from real failures or from outputs the skill promises, not from imagined cases.

## Contents

- Layout
- evals.json format
- Case design rules
- Running
- Gotchas

## Layout

```
<skill>/evals/
  evals.json        # the cases
  files/            # small fictional fixtures the cases reference
  runs/             # outputs from run_evals.py (gitignored)
```

## evals.json format

```json
{
  "skill": "stop-slop",
  "cases": [
    {
      "id": "detect-quotes-no-rewrite",
      "type": "behavior",
      "prompt": "Run stop-slop in detect mode on sample.md.",
      "files": ["files/sample.md"],
      "expected_behavior": [
        "Quotes at least two offending lines verbatim",
        "Names the pattern for each quoted line",
        "Does not provide a rewritten version of the text"
      ],
      "check": { "cmd": "! grep -q '—' output.txt", "expect_exit": 0 }
    },
    {
      "id": "trigger-yes-edit-draft",
      "type": "trigger",
      "prompt": "Tighten this blog draft so it sounds less like AI: ...",
      "should_trigger": true
    }
  ]
}
```

Fields:

- `id`: kebab-case, unique within the skill.
- `type`: `behavior` (judge the output) or `trigger` (did the skill load?).
- `prompt`: what the user types. Realistic, not a restatement of the skill's own text.
- `files`: fixtures copied into the run directory, paths relative to the `evals/` folder.
- `expected_behavior`: 2 to 4 observable, checkable statements. No vague quality words.
- `check` (optional): shell command run in the run directory after the model finishes. The model's final text is saved as `output.txt`. Exit code equal to `expect_exit` passes. Use it whenever a rule can be checked mechanically.
- `should_trigger`: trigger cases only.

## Case design rules

- At least 3 behavior cases and 2 trigger cases (one should-trigger, one should-not).
- Cover the skill's riskiest promises first: required output structure, hard "never" rules, scope boundaries.
- The should-not trigger prompt must be a near miss from a neighbouring skill, not an unrelated request.
- Fixtures are small (under 60 lines) and fictional. No real project, company, or personal data.
- A case that passes without the skill is not testing the skill. Rewrite it.

## Running

```
python3 ~/.skills/skillsmith/scripts/run_evals.py <skill> [--model <model>] [--case <id>] [--no-baseline]
```

Each behavior case runs twice in a throwaway directory: once with the skill installed as a project skill, once without. Trigger cases run once with the skill installed and check whether the Skill tool loaded it. Results print as a table; raw outputs go to `<skill>/evals/runs/`. Runs cost tokens and are manual only.

## Gotchas

- Judge only what `expected_behavior` states. Extra good behavior is not a pass criterion.
- Models vary: note the model used when recording results.
