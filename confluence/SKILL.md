---
name: confluence
description: "Uploads and embeds rendered Mermaid or PlantUML SVGs in Confluence pages with size control. Use when diagrams must be attached to Confluence."
---

# Confluence Diagram Workflow

Confluence Cloud does not natively render Mermaid or PlantUML. This skill uploads diagram SVGs as attachments and embeds them inline with explicit width control.

**For diagram authoring conventions, palettes, and light/dark rendering** — use the `diagram` skill instead. This skill focuses solely on Confluence upload and embedding.

## Prerequisites

Rendering comes from the `diagram` skill (Pele, no browser). Set it up once:

```bash
cd ~/.skills/diagram && npm install
```

## Workflow: Upload & Embed

### 1. Render diagram to SVG

Confluence embeds SVG, so render the light and dark variants with the `diagram` skill and pick one:

```bash
node ~/.skills/diagram/scripts/render.mjs diagram.mmd --for confluence
# produces: diagram.light.svg + diagram.dark.svg
```

### 2. Upload as attachment via REST API

Launch each approved operation with only `CONFLUENCE_API_TOKEN`, `CONFLUENCE_URL` (Cloud, ends in `/wiki`) and `CONFLUENCE_USERNAME` from its owning credential store.
The example uses the work store; substitute the explicitly approved store for another account.
If a required value is missing, run `./bootstrap.sh --secrets` in `~/bootstrap` and fill in that store.
`credential_exec.py` fails before launching Bash when a value is missing and keeps unrelated credentials out of the child environment.
The sourced REST helper passes authentication to curl through a pipe, not process arguments.

```bash
python3 -I ~/.skills/shared/credential_exec.py \
  --file ~/.config/secrets/work.env \
  --var CONFLUENCE_URL --var CONFLUENCE_USERNAME --var CONFLUENCE_API_TOKEN -- \
  bash --noprofile --norc <<'BASH'
. ~/.skills/confluence/scripts/confluence_env.sh || exit 1

confluence_curl -X PUT \
  -H "X-Atlassian-Token: nocheck" \
  -F "file=@diagram.svg" \
  -F "comment=Diagram" \
  "$CONFLUENCE_URL/rest/api/content/<page_id>/child/attachment"
BASH
```

### 3. Embed inline

Fetch the page in storage format, edit the body, then PUT it back with the version bumped by one.
For each fetch or approved publish, reuse the scoped launch above and replace its upload command with the relevant command below.
Keep `. confluence_env.sh` inside that child shell; the parent shell never loads the store.

```bash
confluence_curl "$CONFLUENCE_URL/rest/api/content/<page_id>?expand=body.storage,version" > page.json
# Edit the storage body into body.html, adding:
# <ac:image ac:align="center" ac:layout="center" ac:width="750">
#   <ri:attachment ri:filename="diagram.svg" />
# </ac:image>
confluence_put_storage <page_id> body.html   # keeps the title, sets version = current + 1
```

## Width Guidelines

| Diagram type | Recommended width |
|---|---|
| Wide sequence (4+ participants) | 900 |
| Medium sequence (3 participants) | 750 |
| Narrow / flowchart | 600 |

**Why?** Mermaid SVGs have `width="100%"` but Confluence ignores `viewBox`. Explicit `ac:width` prevents thumbnail shrinking.

## Key Gotchas

- **Use storage format** when embedding. Markdown format converts `<ac:image>` to `<img>`, loses width control, and wipes other macros and browser edits on a live page. Follow [../shared/CONFLUENCE_EDITING.md](../shared/CONFLUENCE_EDITING.md) for the fetch, edit, publish and read-back steps.
- **Only `<ac:image>` with `<ri:attachment>`** renders attached SVGs inline.
- **SVG MIME type** may be `application/octet-stream` — this is fine.
- **Re-uploading** the same filename auto-creates a new version.

Test the helper: `bash ~/.skills/confluence/scripts/test_confluence_env.sh`.
