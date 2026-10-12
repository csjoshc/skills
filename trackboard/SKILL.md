---
name: trackboard
description: >-
  Builds a dated progress board from ticket state that other skills own. In: .tickets/*.md
  frontmatter, .plan/task-sequence.md, or a manual stages file. Process: rebuilds
  .plan/board/board.json, appends stage changes to history.jsonl, reports drift between
  sources. Out: a Cursor canvas, a React artifact, a static HTML page, or a markdown summary.
  Use when the user asks for ticket state over time, a progress board or dashboard, sprint or
  cycle progress, burn by cycle, or gate evidence. Skip for deciding what to work on next
  (/todo) and for planning or ticket breakdown (/antiplan).
---

# Trackboard

Trackboard shows how tickets moved across days and cycles. It reads ticket state, records each stage change once, and renders the same data for whichever harness the user runs.

## Hard constraints

1. **Never edit ticket stage.** Leave `.tickets/*.md`, `.plan/task-sequence.md` and `.plan/PRD.md` untouched. `/todo build`, `/orchestrate` and `/antiplan` own them.
2. **Read sources; write only under `.plan/board/`** plus the export path the user names. The script writes `board.json` and `history.jsonl`; the agent writes `brief.md`.
3. **History is append-only.** `refresh` adds lines to `history.jsonl` and never rewrites or deletes one. To correct a bad line, append a new event.
4. **Report drift; do not resolve it.** When sources disagree on a stage, show the drift entry and name the files. The user fixes the source.
5. **The brief explains decisions already made.** `.plan/board/brief.md` adds no requirements and no acceptance criteria. Criteria stay in tickets and `.plan/task-sequence.md`; the brief cites them.
6. **Keep skill files project-neutral.** Project names, people and IDs belong in the project's `.plan/board/`, not in this skill.

## Use when / Skip when

- **Use when:** "show ticket state", "progress board", "how did this sprint go", "burn by cycle", "which gates have evidence", "export the board for the PR".
- **Skip when:** the user wants the next prompt or ticket to run (`/todo`), wants to plan or split work (`/antiplan`), or wants a claim verified (`/evidence-reviewer`).

## Boundaries

| Skill | Owns | Trackboard's relation |
|---|---|---|
| `/todo` | Pipeline routing, next-step prompts | Reads the same `Stage:` values; never routes |
| `/antiplan` | `.plan/PRD.md`, `.plan/task-sequence.md`, gates | Reads the task-sequence table when no tickets exist |
| `/todo build`, `/orchestrate` | `Stage:` edits in `.tickets/*.md` | Records each edit as one history line on the next refresh |
| `/evidence-reviewer` | VERIFIED or REJECTED verdicts | On VERIFIED, `refresh --evidence` stores the link; the reviewer skill stays unchanged |
| `/handoff` | Session resume prompts | A handoff may link `board.md`; trackboard writes no prompts |
| `trackboard` | `.plan/board/*` and export files | Read-only projection of the above |

## Operations

The script needs Python 3.10+ and only the standard library. Pass `--root <project>` (default: current directory). Pass `--today YYYY-MM-DD` to pin the date in tests or backfills.

```bash
S=~/.skills/trackboard/scripts/board_refresh.py
python3 $S init                       # create .plan/board/config.json, run a first refresh
python3 $S refresh                    # rebuild board.json, append stage changes
python3 $S refresh --evidence "T-002=PR 7|https://example.test/pr/7"
python3 $S refresh --check            # CI: exit 1 if stale, 2 on drift, 0 if clean; writes nothing
python3 $S refresh --check --strict-brief   # also exit 3 when brief.md is out of date
python3 $S brief-hash                # print the covers hash for brief.md frontmatter
python3 $S export --target html --out .plan/board/board.html   # cursor | artifact | html | md
```

### init

1. Run `init`. It creates `config.json` with an empty `cycles` list and generic `stage_rules`, and an empty `history.jsonl`, then runs `refresh`. The first refresh writes one history line per ticket with `from: null`.
2. Ask the user for cycle names and dates, or read them from the plan, and add them to `config.json` (`id`, `name`, `start`, `end`, inclusive `YYYY-MM-DD`).
3. Run `refresh` again so `board.json` carries the cycles.

### refresh

Run after any stage change, merge, or verdict. It reads sources in this order:

1. `.tickets/*.md` frontmatter (`Stage:`, `Gate:`, `Depends-On:`).
2. `.plan/task-sequence.md`, first markdown table with an ID column.
3. `.plan/board/stages.yaml` (flat `ID: STAGE`) or `stages.json`.

For the brief it reads `.plan/board/brief.md` first, then falls back per section to `.plan/PRD.md`, ticket bodies, and `- AC:` lines in `.plan/task-sequence.md`.

It appends a history line only for tickets whose stage differs from the previous `board.json`, tags it with the cycle whose dates contain today, and rewrites `board.json`. A second run with no source change prints `No change.` and leaves both files byte-identical. Field definitions: [references/board-schema.md](references/board-schema.md).

When the output lists drift, quote each entry to the user with the two source paths and stop. Do not edit either source.

### brief

Write `.plan/board/brief.md` after planning, or after a stage change leaves the brief stale. You write the file; the script only hashes and checks it.

1. Read the conversation that produced the plan, plus `.plan/` and `.tickets/` on disk.
2. Write four sections: `## Building` (2 to 4 sentences), `## Not building` (bullets), `## Spec` (`- <ticket id>: <one-line intent>`), `## Proof` (`- <STAGE>: <exit rule>` and optional `- <gate id>: <note>`). Do not restate acceptance criteria.
3. End every claim line in Building, Not building and Proof with a source tag: `[T-003]`, `[D2]`, `[PR #12]`, `[chat 2030-01-05]`, `[PRD]`. A claim with no source does not belong in the brief.
4. Keep it under about 60 lines. Run `/stop-slop` on it.
5. Set frontmatter `written_at` (today), `written_by` (agent and harness), and `covers` (output of `brief-hash`), then run `refresh`.

`refresh` warns `brief_untagged` for claim lines with no tag and `brief_stale` when tickets changed since `covers` was computed. Format: [references/board-schema.md](references/board-schema.md).

### export

`export` copies `board.json` into a template at `__TRACKBOARD_DATA__`. Re-export after each refresh; each renderer holds its own copy of the data.

### --check

Add `refresh --check` to CI or a pre-commit hook to catch a board that lags its sources or carries drift.

## Choosing a harness

| Harness | Target | Output location |
|---|---|---|
| Cursor | `cursor` | `~/.cursor/projects/<workspace>/canvases/<name>.canvas.tsx` |
| Claude.ai, ChatGPT canvas | `artifact` | Paste the file as a React artifact |
| Claude Code, Codex CLI, Gemini CLI, other terminals | `html` and `md` | `.plan/board/board.html`, opened with the OS opener |
| Chat only | `md` | Print the file |

Detection order, escaping, and capabilities not yet verified: [references/harness-adapters.md](references/harness-adapters.md).

## Views

Two groups behind a Brief | Tracking switch. Brief: Overview (from `brief.md`, else `.plan/PRD.md`), Spec (each ticket's intent and acceptance criteria), Proof (stage exit rules from `config.json` `stage_rules`, plus each gate's criteria, evidence, and met or not met). Tracking: Now, Timeline by cycle, Dependency graph, Gates and evidence, Burn by cycle. A view with no source data stays hidden. Brief text renders with its source tags and a written-on caption; a stale brief shows a one-line notice. What each view answers and the fields it reads: [references/views.md](references/views.md).

## Tests

```bash
python3 -m unittest discover -s ~/.skills/trackboard/scripts -p 'test_*.py'
```

## Checklist

- [ ] No source file under `.tickets/` or `.plan/` changed, except `.plan/board/`.
- [ ] `history.jsonl` grew by one line per real stage change and kept every old line.
- [ ] A repeat `refresh` printed `No change.`
- [ ] Drift, if any, went to the user with both source paths.
- [ ] The export matches the harness, and the user has the path or link to open it.
- [ ] `refresh --check` exits 0, or the user knows why it does not.
- [ ] If you wrote `brief.md`: every claim is tagged, it adds no criteria, and `refresh` shows no `brief_untagged` warning.
