---
name: confluence-diagrams
description: "Upload and embed Mermaid or PlantUML diagrams in Confluence pages with size control. Use when SVG diagrams are ready and must be attached to Confluence."
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

Credentials live in `~/.config/mcp/mcp_servers.json`:

```bash
CONFLUENCE_URL=$(python3 -c "import json; print(json.load(open('$HOME/.config/mcp/mcp_servers.json'))['mcpServers']['atlassian']['env']['CONFLUENCE_URL'])")
CONFLUENCE_USERNAME=$(python3 -c "import json; print(json.load(open('$HOME/.config/mcp/mcp_servers.json'))['mcpServers']['atlassian']['env']['CONFLUENCE_USERNAME'])")
CONFLUENCE_API_TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/.config/mcp/mcp_servers.json'))['mcpServers']['atlassian']['env']['CONFLUENCE_API_TOKEN'])")

curl -s -u "$CONFLUENCE_USERNAME:$CONFLUENCE_API_TOKEN" \
  -X PUT \
  -H "X-Atlassian-Token: nocheck" \
  -F "file=@diagram.svg" \
  -F "comment=Diagram" \
  "$CONFLUENCE_URL/rest/api/content/<page_id>/child/attachment"
```

### 3. Embed inline

Fetch the page in storage format, then update with explicit width:

```bash
# Fetch current page
mcp-cli call atlassian confluence_get_page \
  '{"page_id": "<page_id>", "include_metadata": false, "convert_to_markdown": false}'

# Then update via mcp-cli with content_format: "storage":
# <ac:image ac:align="center" ac:layout="center" ac:width="750">
#   <ri:attachment ri:filename="diagram.svg" />
# </ac:image>
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
