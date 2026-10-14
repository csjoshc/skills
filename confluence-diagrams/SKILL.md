---
name: confluence-diagrams
description: "Uploads and embeds rendered Mermaid or PlantUML SVGs in Confluence pages with size control. Use when diagrams must be attached to Confluence."
---

# Confluence Diagram Workflow

Confluence Cloud does not natively render Mermaid or PlantUML. This skill uploads diagram SVGs as attachments and embeds them inline with explicit width control.

**For diagram authoring conventions, palettes, and light/dark rendering** — use the `make-mmd` skill instead. This skill focuses solely on Confluence upload and embedding.

## Prerequisites

`@mermaid-js/mermaid-cli` must be installed globally:

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc --version   # verify
```

## Workflow: Upload & Embed

### 1. Render diagram to SVG

Use `make-mmd` skill's `render.sh` for light/dark variants, or render directly:

```bash
mmdc -i diagram.mmd -o diagram.svg -b transparent
```

### 2. Upload as attachment via REST API

The token, URL and username come from the environment only: `CONFLUENCE_API_TOKEN`, `CONFLUENCE_URL` (Cloud, ends in `/wiki`) and `CONFLUENCE_USERNAME` in `~/.config/secrets/work.env` (loaded by every new shell).
If one is missing, run `./bootstrap.sh --secrets` in `~/bootstrap` and fill in the file.
The helper below checks all three, stops with a clear message if one is missing, and defines `confluence_curl`, which passes the credentials to curl on a pipe so the token never shows in `ps`.

```bash
. ~/.skills/confluence-diagrams/scripts/confluence_env.sh || exit 1

confluence_curl -X PUT \
  -H "X-Atlassian-Token: nocheck" \
  -F "file=@diagram.svg" \
  -F "comment=Diagram" \
  "$CONFLUENCE_URL/rest/api/content/<page_id>/child/attachment"
```

### 3. Embed inline

Fetch the page in storage format, edit the body, then PUT it back with the version bumped by one:

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

- **Use storage format** when embedding. Markdown format converts `<ac:image>` to `<img>` and loses width control.
- **Only `<ac:image>` with `<ri:attachment>`** renders attached SVGs inline.
- **SVG MIME type** may be `application/octet-stream` — this is fine.
- **Re-uploading** the same filename auto-creates a new version.

Test the helper: `bash ~/.skills/confluence-diagrams/scripts/test_confluence_env.sh`.
