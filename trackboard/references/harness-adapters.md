# Harness adapters

One `board.json` feeds four renderers. Each export copies the data into a template at the token `__TRACKBOARD_DATA__`, so no renderer reads files or the network at runtime.

## Contents

- Detection order
- Cursor
- Claude.ai artifacts
- ChatGPT canvas and Codex
- Terminal agents
- What remains unverified

## Detection order

Pick the first match:

1. A Cursor workspace: `~/.cursor/projects/<workspace>/canvases/` exists, or the session lists a canvas skill. Export `cursor`, then also `html` for the tracked copy.
2. A chat surface that renders React artifacts (Claude.ai, ChatGPT canvas). Export `artifact` and paste the file content as the artifact body.
3. Anything else with a file system (Claude Code, Codex CLI, Gemini CLI, other terminal agents). Export `html` and `md`.
4. Chat only, no file system: print the `md` export.

When unsure, export `html` plus `md`. Both work in any browser or chat window.

## Cursor

```bash
python3 ~/.skills/trackboard/scripts/board_refresh.py export --target cursor \
  --out ~/.cursor/projects/<workspace>/canvases/<project>-board.canvas.tsx
```

- Cursor only picks up canvases saved in that `canvases/` folder itself; it ignores subfolders.
- The template imports only from `cursor/canvas` and takes colors from `useHostTheme()`.
- Canvases cannot `fetch` or read files, so re-run the export after each `refresh`.
- The canvas write result reports a `Canvas TypeScript check`; treat any error there as a template bug.

## Claude.ai artifacts

Export `artifact` and paste `artifact.tsx` into a React artifact. The component imports only `react` (`useState`), uses inline styles, and has one default export. Claude.ai documents React artifacts with default exports and React hooks; the template avoids Tailwind and third-party packages so it does not depend on which extra libraries the sandbox preloads.

## ChatGPT canvas and Codex

ChatGPT canvas can preview React code. Paste the same `artifact.tsx`. Codex (cloud or CLI) has no confirmed live React preview, so treat it as a terminal agent and export `html`.

## Terminal agents

Claude Code, Codex CLI, Gemini CLI, and similar agents:

```bash
S=~/.skills/trackboard/scripts/board_refresh.py
python3 $S export --target html --out .plan/board/board.html
python3 $S export --target md --out .plan/board/board.md
open .plan/board/board.html        # macOS; xdg-open on Linux, start on Windows
```

- `board.html` is one file with no build step and no network requests. Its Content-Security-Policy blocks external loads.
- The data sits in `<script type="application/json" id="board-data">`. The export escapes `<`, `>` and `&` as `\u003c`, `\u003e`, `\u0026`, so a ticket note containing `</script>` cannot close the tag.
- Light and dark follow `prefers-color-scheme`.
- Commit `board.html` as the tracked copy of the board. `board.json` and `history.jsonl` hold the record; commit them if the team wants history in git.
- `board.md` suits PR descriptions and chat replies.

## What remains unverified

- ChatGPT canvas React preview: this skill's author did not run `artifact.tsx` in it. OpenAI may change which imports the preview allows.
- Claude.ai artifacts: not run in the live product; `artifact.tsx` passes `tsc --strict` against `@types/react@18`.
- Gemini CLI and Codex CLI: no inline renderer known, so they use the HTML path.
- Cursor canvas detection by folder presence is a heuristic. A workspace folder may exist while the session runs elsewhere.
