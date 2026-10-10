# Board data contract

`scripts/board_refresh.py` writes `.plan/board/board.json` and appends to `.plan/board/history.jsonl`. The renderers in `templates/` read only the fields below. Bump `schema_version` when you rename or remove a field.

## Contents

- Files under `.plan/board/`
- board.json fields
- Brief fields
- history.jsonl lines
- config.json
- Stage vocabulary
- Sources and the fields each one supplies
- Brief sources
- brief.md format
- Drift entries
- Sample

## Files under `.plan/board/`

| File | Writer | Notes |
|---|---|---|
| `config.json` | `init` creates it; the user edits it | Title, cycles, view order, stage exit rules |
| `stages.yaml` or `stages.json` | The user, by hand | Optional manual stage per ticket |
| `brief.md` | The agent, via `/trackboard brief` | Optional explanation of decisions, with source tags; see brief.md format |
| `history.jsonl` | `refresh` appends | One JSON object per line; refresh never rewrites a line |
| `board.json` | `refresh` rewrites | Rebuilt from the sources and history on each run |

## board.json fields

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | int | `1` in this version |
| `title` | string | From `config.json`, else the project folder name |
| `generated_at` | string | UTC timestamp of the last run that changed content. A run with no change leaves the file untouched |
| `sources[]` | `{kind, path, count}` | Sources read: `tickets`, `task-sequence`, `stages` |
| `cycles[]` | `{id, name, start, end}` | Copied from `config.json`; dates are `YYYY-MM-DD`, inclusive |
| `views` | `{order: string[]}` | View ids in display order: `overview`, `spec`, `proof`, `now`, `timeline`, `dag`, `gates`, `burn` |
| `brief` | object | Overview, stage exit rules and gate proof; see Brief fields |
| `tickets[]` | object | See the ticket fields below |
| `events[]` | object | Every line of `history.jsonl`, oldest first |
| `burn[]` | `{cycle, started, completed, open_at_end}` | Per-cycle counts derived from `events` |
| `drift[]` | `{ticket, kind, values}` | Source disagreements, see Drift entries |

Ticket fields:

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Ticket id, for example `T-001` or `GATE-1` |
| `title` | string | Ticket title |
| `stage` | string | One value from the stage vocabulary |
| `deps` | string[] | Ids this ticket depends on |
| `gate` | string or null | Id of the gate this ticket feeds |
| `is_gate` | bool | True when frontmatter says `gate: true` or another ticket names this id as its gate |
| `owner` | string or null | `owner:` or `assignee:` |
| `note` | string or null | `note:` from frontmatter |
| `evidence[]` | `{label, url}` | Frontmatter evidence plus every evidence link in history for this ticket |
| `intent` | string or null | The ticket's line in `brief.md` `## Spec`, else the first paragraph of the ticket body, up to 200 characters |
| `intent_tags` | string[] | Source tags on the `brief.md` spec line; empty otherwise |
| `acceptance[]` | `{text, checked?}` | Acceptance criteria; `checked` is present only for checkbox items |

## Brief fields

| Field | Type | Meaning |
|---|---|---|
| `brief.overview` | object or null | `{title, goal[], non_goals[], constraints[], source}`. `goal`, `non_goals` and `constraints` hold claims, `{text, tags[]}`. `null` when neither `brief.md` nor `.plan/PRD.md` supplies an overview section |
| `brief.stage_rules` | object | Stage id to exit rule, one sentence each |
| `brief.stage_rule_tags` | object | Stage id to source tags, for rules taken from `brief.md` |
| `brief.stage_rules_source` | `brief`, `config` or `default` | `brief` when `brief.md` sets any rule; else `default` when the rules equal the generic defaults below |
| `brief.proof_notes[]` | claim | `## Proof` lines that name no stage and no gate |
| `brief.authored` | object or null | `{path, written_at, written_by, covers}` from `brief.md` frontmatter; `null` without the file |
| `brief.stale` | bool | True when `covers` differs from the hash of the current tickets |
| `brief.changed[]` | string | Ids whose stage or criteria changed since the brief was written |
| `brief.covered` | object | Ticket id to a 12-character digest, saved while the brief was current; used to fill `changed` |
| `brief.untagged[]` | string | Claim lines in Building, Not building or Proof with no source tag. `refresh` prints them as `brief_untagged`; they are warnings, not drift |
| `brief.gates[]` | object | `{id, question, stage, acceptance[], evidence[], met, note}` per gate ticket. `question` is the gate's intent, else its title. `met` is true when the gate is COMPLETE and has at least one evidence link. `note` is the gate's `brief.md` proof line as a claim, or `null` |

Default stage exit rules, written into `config.json` by `init` and used when `stage_rules` is absent:

| Stage | Exit rule |
|---|---|
| NEW | Ticket has a goal and acceptance criteria. |
| BUILD | Tests written and failing. |
| REVIEW | Tests pass, PR open, CI green. |
| BLOCKED | Blocker named, with who or what clears it. |
| COMPLETE | PR merged and evidence linked. |

A `stage_rules` object in `config.json` replaces the default for each stage it names; stages it omits keep the default. A `- STAGE: rule` line in `brief.md` `## Proof` replaces both for that stage.

## history.jsonl lines

```json
{"ts": "2030-01-09", "cycle": "C2", "ticket": "T-002", "from": "NEW", "to": "BUILD", "evidence": []}
```

- `ts`: the run date (`--today` or the local date).
- `cycle`: id of the cycle whose `start..end` contains `ts`, or `null`.
- `from`: the stage in the previous `board.json`; `null` the first time a ticket appears.
- `to`: the new stage. When `from` equals `to`, the line records evidence only (`refresh --evidence`).

## config.json

```json
{
  "schema_version": 1,
  "title": "Checkout rewrite",
  "cycles": [
    {"id": "C1", "name": "Cycle 1", "start": "2030-01-01", "end": "2030-01-14"},
    {"id": "C2", "name": "Cycle 2", "start": "2030-01-15", "end": "2030-01-28"}
  ],
  "views": {"order": ["overview", "spec", "proof", "now", "timeline", "dag", "gates", "burn"]},
  "stage_rules": {
    "NEW": "Ticket has a goal and acceptance criteria.",
    "BUILD": "Tests written and failing.",
    "REVIEW": "Tests pass, PR open, CI green.",
    "BLOCKED": "Blocker named, with who or what clears it.",
    "COMPLETE": "PR merged and evidence linked."
  }
}
```

## Stage vocabulary

`NEW`, `BUILD`, `REVIEW`, `BLOCKED`, `COMPLETE`, matching `/todo`. The script maps common aliases:

| Read as | Aliases |
|---|---|
| NEW | TODO, OPEN, BACKLOG, SPEC, SPEC_SPLIT, PLAN, PLANNED, READY |
| BUILD | IN_PROGRESS, DOING, WIP, ACTIVE, STARTED |
| REVIEW | IN_REVIEW, VERIFY, QA |
| BLOCKED | FAILED, ON_HOLD |
| COMPLETE | COMPLETED, DONE, MERGED, CLOSED, PASSED |

Matching ignores case, spaces and hyphens. Any other value lands in `drift[]` as `unknown-stage`.

## Sources and the fields each one supplies

1. `.tickets/*.md` frontmatter. Keys, case-insensitive: `id`, `title`, `Stage` (or `Status`), `Depends-On` (or `deps`, `depends`, `dependencies`, `blocked_by`), `Gate` (an id, or `true` for a gate ticket), `owner`, `note`, `evidence`. Lists may be inline (`[T-001, T-002]`) or block (`- T-001`). Write evidence items as `label | url`.
2. `.plan/task-sequence.md`. The script reads the first markdown table whose header row has an id column. Header names it accepts: `ID`/`Ticket`/`Key`, `Title`/`Name`/`Summary`, `Depends on`/`Depends-On`/`Deps`/`Blocked by`, `Stage`/`Status`, `Gate`, `Owner`/`Assignee`. It ignores other columns, strips backticks, bold and link markup, and treats `-`, an em dash, and `none` as empty. Rows missing from `.tickets/` still appear; for rows present in both, ticket frontmatter supplies title, deps and gate.
3. `.plan/board/stages.yaml`. A flat `ID: STAGE` list, one per line, `#` comments allowed. The script parses this subset itself so it needs no YAML library. `stages.json` (a flat `{"T-001": "BUILD"}` object) takes precedence when both exist.

## Brief sources

`.plan/board/brief.md` comes first. Each overview section, spec line and proof rule it supplies overrides the extracted value; anything it lacks falls back to the sources below, which other skills own. Trackboard never writes back to them.

1. Overview, from `.plan/PRD.md`. `title` is the first `# ` heading. `goal` is the first paragraph under a heading matching `goal`, `problem`, `summary` or `overview` (case-insensitive, `non-goals` excluded), else the first paragraph in the file; it keeps at most three sentences and 300 characters. `non_goals` and `constraints` take up to five bullets from the first heading matching `non-goals` or `out of scope`, and `constraints` or `principles`. Link and bold markup are stripped; each bullet is cut at 160 characters.
2. Acceptance criteria, per ticket. First choice: the bullets under a heading in the ticket body matching `acceptance`, `AC` or `done when`. A whole-line bold label such as `**Acceptance:**` counts as a heading. `- [x]` and `- [ ]` items keep their checked state. Fallback when the ticket body has none: `- AC: ...` lines in `.plan/task-sequence.md` under a heading that contains the ticket id as a whole word.
3. Intent: the first plain paragraph of the ticket body. Headings, bullets, tables, quotes and code fences are skipped.
4. Stage rules: `stage_rules` in `config.json`, merged over the defaults.

## brief.md format

```markdown
---
written_at: 2030-01-05
written_by: agent name, harness
covers: sha256:<hash from brief-hash>
---

## Building

Buyers pay by card on one screen. [chat 2030-01-04]
Saved cards wait for a later cycle. [D2]

## Not building

- Gift cards [PRD]

## Spec

- T-001: Card form that checks the number as the buyer types. [chat 2030-01-04]

## Proof

- BUILD: Card form tests fail before the form exists. [D3]
- GATE-1: A recorded checkout run closes the gate. [PR #12]
```

- Sections are matched by name, case-insensitive. Missing sections fall back to extraction; other sections are ignored.
- One claim per line. A bullet marker is optional.
- Source tag: one or more `[text]` groups at the end of the line, for example `[T-003]`, `[D2] [T-003]`, `[PR #12]`, `[chat 2030-01-05]`, `[PRD]`. Renderers show tags as small labels. `[x]` at the start of a line is a checkbox, not a tag.
- `## Spec` and `## Proof` lines that start with an uppercase id and a colon (`T-001:`, `BUILD:`, `GATE-1:`) attach to that ticket, stage or gate. Spec lines need no tag; they restate the ticket's intent, never its criteria.
- `covers` is `sha256:` plus the hex SHA-256 of a UTF-8 JSON array, compact separators (`,` and `:`), of `[id, stage, [acceptance texts]]` per ticket, sorted by id. Intent and brief text are not covered, so editing the brief does not make it stale. `brief-hash` prints this value for the current sources.

## Drift entries

When two sources give one ticket different stages, `refresh` records:

```json
{"ticket": "T-001", "kind": "stage-mismatch", "values": {"tickets": "BUILD", "stages": "COMPLETE"}}
```

It keeps the ticket's stage from the previous `board.json` (or the first source on first sight) and writes no history line for that ticket until a person fixes the disagreement in the sources. `refresh --check` exits 2 while any drift exists.

## Sample

```json
{
  "schema_version": 1,
  "title": "Checkout rewrite",
  "generated_at": "2030-01-09T00:00:00Z",
  "sources": [{"kind": "tickets", "path": ".tickets/*.md", "count": 3}],
  "cycles": [{"id": "C1", "name": "Cycle 1", "start": "2030-01-01", "end": "2030-01-14"}],
  "views": {"order": ["overview", "spec", "proof", "now", "timeline", "dag", "gates", "burn"]},
  "brief": {
    "overview": {"title": "Checkout rewrite",
                 "goal": [{"text": "Buyers finish payment on one screen.", "tags": ["PRD"]}],
                 "non_goals": [{"text": "Gift cards", "tags": ["PRD"]}],
                 "constraints": [{"text": "Card data stays with the processor", "tags": ["PRD"]}],
                 "source": ".plan/PRD.md"},
    "stage_rules": {"NEW": "Ticket has a goal and acceptance criteria.", "BUILD": "Tests written and failing.",
                    "REVIEW": "Tests pass, PR open, CI green.", "BLOCKED": "Blocker named, with who or what clears it.",
                    "COMPLETE": "PR merged and evidence linked."},
    "stage_rule_tags": {},
    "stage_rules_source": "default",
    "gates": [{"id": "GATE-1", "question": "Cart works end to end", "stage": "NEW",
               "acceptance": [], "evidence": [], "met": false, "note": null}],
    "proof_notes": [],
    "authored": null, "stale": false, "changed": [], "covered": {}, "untagged": []
  },
  "tickets": [
    {"id": "T-001", "title": "Cart model", "stage": "COMPLETE", "deps": [], "gate": "GATE-1",
     "is_gate": false, "owner": "ana", "note": null,
     "evidence": [{"label": "PR 4", "url": "https://example.test/pr/4"}],
     "intent": "Store cart lines and totals.", "intent_tags": [],
     "acceptance": [{"text": "Total equals the sum of lines", "checked": true}]},
    {"id": "T-002", "title": "Cart API", "stage": "BUILD", "deps": ["T-001"], "gate": "GATE-1",
     "is_gate": false, "owner": "ben", "note": "needs auth stub", "evidence": [],
     "intent": null, "intent_tags": [], "acceptance": []},
    {"id": "GATE-1", "title": "Cart works end to end", "stage": "NEW", "deps": ["T-001", "T-002"],
     "gate": null, "is_gate": true, "owner": null, "note": null, "evidence": [],
     "intent": null, "intent_tags": [], "acceptance": []}
  ],
  "events": [
    {"ts": "2030-01-02", "cycle": "C1", "ticket": "T-001", "from": null, "to": "BUILD", "evidence": []},
    {"ts": "2030-01-06", "cycle": "C1", "ticket": "T-001", "from": "BUILD", "to": "COMPLETE",
     "evidence": [{"label": "PR 4", "url": "https://example.test/pr/4"}]},
    {"ts": "2030-01-09", "cycle": "C1", "ticket": "T-002", "from": null, "to": "BUILD", "evidence": []}
  ],
  "burn": [{"cycle": "C1", "started": 2, "completed": 1, "open_at_end": 1}],
  "drift": []
}
```
