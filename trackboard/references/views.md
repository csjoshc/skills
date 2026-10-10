# Views

The board has eight views in two groups. The first three are the brief: what we are building, what defines done, and what proves each stage. The other five are tracking: where work stands and how it moved. The Cursor canvas, the artifact and the HTML page put each group behind a Brief | Tracking switch; the markdown summary prints the brief first.

The brief reads `.plan/board/brief.md` first and falls back per section to `.plan/PRD.md` and the tickets. A view with no data stays hidden, so a project with neither file shows no overview and a board with no cycles shows no burn chart. `views.order` in `config.json` sets the order and can drop views.

| View id | Group | Question it answers | Fields used |
|---|---|---|---|
| `overview` | brief | What are we building, and what is out of scope? | `brief.overview`: `title`, `goal[]`, `non_goals[]`, `constraints[]`, `source` |
| `spec` | brief | What defines done for each ticket? | `tickets[].intent`, `intent_tags`, `acceptance[]`, `stage` |
| `proof` | brief | What must be true to leave each stage, and has each gate met its bar? | `brief.stage_rules`, `stage_rule_tags`, `stage_rules_source`, `gates[]`, `proof_notes[]` |
| `now` | tracking | Which tickets are in flight or stuck right now? | `tickets[].stage` in BUILD, REVIEW, BLOCKED; `owner`, `note` |
| `timeline` | tracking | What changed, when, and in which cycle? | `events[]`: `ts`, `cycle`, `ticket`, `from`, `to`, `evidence`; `cycles[].name` |
| `dag` | tracking | What blocks what, and where does each ticket sit? | `tickets[].deps`, `stage`, `is_gate` |
| `gates` | tracking | Which gates are open, which tickets feed them, and what proves they passed? | `tickets[].is_gate`, `gate`, `deps`, `stage`, `evidence[]` |
| `burn` | tracking | How many tickets started and finished in each cycle, and how many stayed open? | `burn[]`: `started`, `completed`, `open_at_end`; `cycles[]` |

When `brief.authored` is set, all four renderers show one quiet line under the title: "Brief written <date> by <author>.", or, when `brief.stale` is true, "Brief written <date>; N tickets changed since (ids)." Source tags render as small muted labels after each claim.

All four renderers also show a stage count strip, a drift notice when `drift[]` has entries, and a full ticket table.

## Notes per view

- `overview`: Building, Not building and Constraints, each with its tags, and the source paths used. Trackboard never edits the PRD or the brief.
- `spec`: lists tickets that have an intent or acceptance criteria, grouped by stage. Each ticket shows its first three criteria; a "more" control reveals the rest. Checked items render muted with a check.
- `proof`: a table of stage exit rules, with a note when the generic defaults are in use, any proof notes that name no stage or gate, then one card per gate with its question, brief note, criteria, evidence links and a met or not-met marker.
- `now`: BLOCKED tickets carry the danger tone in the Cursor canvas.
- `timeline`: groups events by cycle, newest first. Events dated outside the configured cycles sit under "Outside any cycle". Lines where `from` equals `to` show as "evidence".
- `dag`: the Cursor canvas lays out nodes with `computeDAGLayout` from `cursor/canvas`; the HTML and artifact renderers rank nodes by longest dependency path. The outline color shows the stage, and a thicker outline marks a gate.
- `gates`: "Feeds" lists tickets whose `gate` names this gate, or the gate's own `deps` when no ticket names it.
- `burn`: `started` counts tickets that moved to BUILD during the cycle, including a ticket first seen at BUILD; `completed` counts moves to COMPLETE; `open_at_end` counts tickets whose latest stage on the cycle's end date was not COMPLETE.
