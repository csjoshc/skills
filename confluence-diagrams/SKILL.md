---
name: confluence-diagrams
description: >-
  Render text-based diagrams (Mermaid, PlantUML) to SVG and embed them in
  Confluence pages. Use when uploading diagrams to Confluence, embedding
  images in wiki pages, or converting mermaid/markdown diagrams for Confluence.
---

# Confluence Diagram Workflow

## TL;DR (Quick Start)

Convert text-based diagrams (Mermaid/PlantUML) to SVG for Confluence Cloud. Requires `mmdc` CLI, Confluence REST API credentials, and mcp-cli for page updates.

**When to use:** Uploading diagrams to Confluence wiki pages, embedding Mermaid diagrams that Confluence doesn't natively render.

**Invocation:** 1) Create .mmd file → 2) Render to SVG with `mmdc` → 3) Upload via REST API → 4) Embed with `<ac:image>` in storage format.

## Decision Tree

Use this skill when you need to:

1. **What type of diagram?**
   - Mermaid → Use `mmdc` CLI to render
   - PlantUML → Convert to Mermaid first or use PlantUML CLI

2. **What is the diagram width?**
   - Wide (4+ participants) → `ac:width="900"`
   - Medium (3 participants) → `ac:width="750"`
   - Narrow/flowchart → `ac:width="600"`

3. **How to embed in Confluence?**
   - Storage format → Use `<ac:image>` with `<ri:attachment>`
   - Markdown format → Will lose image sizing, avoid

## Prerequisites

`@mermaid-js/mermaid-cli` must be installed globally:

```bash
npm install -g @mermaid-js/mermaid-cli
```

Verify with `mmdc --version`. If missing, install before proceeding.

## Workflow

### 1. Create `.mmd` file

Write the Mermaid diagram to a `.mmd` file. Avoid curly braces `{}` and
HTML entities in message labels — these break the parser. Use `Note`
blocks for detailed text instead.

### 2. Render to SVG

```bash
mmdc -i diagram.mmd -o diagram.svg -b transparent
```

### 3. Upload as attachment via REST API

The `mcp-atlassian` MCP server has **no** attachment upload tool (it was
added then removed due to security/usability issues). Use the Confluence
REST API directly via curl.

Credentials live in `~/.config/mcp/mcp_servers.json` under
`mcpServers.atlassian.env` (`CONFLUENCE_URL`, `CONFLUENCE_USERNAME`,
`CONFLUENCE_API_TOKEN`). Extract them with:

```bash
CONFLUENCE_URL=$(python3 -c "import json; print(json.load(open('$HOME/.config/mcp/mcp_servers.json'))['mcpServers']['atlassian']['env']['CONFLUENCE_URL'])")
CONFLUENCE_USERNAME=$(python3 -c "import json; print(json.load(open('$HOME/.config/mcp/mcp_servers.json'))['mcpServers']['atlassian']['env']['CONFLUENCE_USERNAME'])")
CONFLUENCE_API_TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/.config/mcp/mcp_servers.json'))['mcpServers']['atlassian']['env']['CONFLUENCE_API_TOKEN'])")
```

Upload each SVG (re-uploading the same filename auto-creates a new version):

```bash
curl -s -u "$CONFLUENCE_USERNAME:$CONFLUENCE_API_TOKEN" \
  -X PUT \
  -H "X-Atlassian-Token: nocheck" \
  -F "file=@diagram.svg" \
  -F "comment=Auto-uploaded diagram" \
  "$CONFLUENCE_URL/rest/api/content/<page_id>/child/attachment"
```

Verify each curl returns HTTP 200 with attachment metadata JSON.

### 4. Embed inline with explicit width

**Before updating,** fetch the current page in storage format to use as a
base. Via `mcp-cli`:

```bash
mcp-cli call atlassian confluence_get_page \
  '{"page_id": "<page_id>", "include_metadata": false, "convert_to_markdown": false}'
```

This returns the raw storage-format XHTML. Edit it to insert or replace
`<ac:image>` tags, then update the page.

Update the page using `content_format: "storage"` and insert:

```xml
<ac:image ac:align="center" ac:layout="center" ac:width="WIDTH">
  <ri:attachment ri:filename="diagram.svg" ri:version-at-save="1" />
</ac:image>
```

**Width guidelines** (based on content viewBox):

| Diagram type | Recommended `ac:width` |
|---|---|
| Wide sequence diagram (4+ participants) | `900` |
| Medium sequence diagram (3 participants) | `750` |
| Narrow / flowchart | `600` |

### 5. Why explicit width is required

Mermaid CLI generates SVGs with `width="100%"` and a `viewBox` attribute.
Confluence ignores `viewBox` and needs a concrete pixel width, otherwise
the image renders as a tiny thumbnail. Always set `ac:width`.

## Key gotchas

- **Use storage format** when embedding images. If you update via
  `content_format: "markdown"`, Confluence converts `<ac:image>` to
  `<img>` tags and loses the `ac:width` attribute.
- **Don't use `<img>` tags.** Only `<ac:image>` with `<ri:attachment>`
  renders attached files inline with size control.
- **SVG MIME type:** Confluence may store SVGs as `application/octet-stream`.
  This is fine — they still render correctly via `<ac:image>`.
- **Re-uploading** an attachment with the same filename creates a new
  version automatically. Update `ri:version-at-save` if referencing a
  specific version, or omit it to use the latest.

## Example: full sequence

```bash
# 1. Render
mmdc -i architecture.mmd -o architecture.svg -b transparent

# 2. Upload (via REST API — no MCP tool exists for this)
curl -s -u "$CONFLUENCE_USERNAME:$CONFLUENCE_API_TOKEN" \
  -X PUT -H "X-Atlassian-Token: nocheck" \
  -F "file=@architecture.svg" -F "comment=Architecture diagram" \
  "$CONFLUENCE_URL/rest/api/content/$PAGE_ID/child/attachment"

# 3. Embed (via mcp-cli update_page with content_format="storage")
#    Insert into the page storage-format HTML:
#    <ac:image ac:align="center" ac:layout="center" ac:width="900">
#      <ri:attachment ri:filename="architecture.svg" />
#    </ac:image>
```

## Verification

**Do not use browser-based visual verification.** The browser MCP tool
has no stored Atlassian session and Confluence login requires separate
authentication from the API token used by the MCP server. Attempting to
navigate to the page will hit a login wall.

Instead, verify via the REST API:

```bash
curl -s -u "$CONFLUENCE_USERNAME:$CONFLUENCE_API_TOKEN" \
  "$CONFLUENCE_URL/rest/api/content/$PAGE_ID?expand=body.storage" \
  | python3 -c "
import sys, json, re
data = json.loads(sys.stdin.read())
storage = data['body']['storage']['value']
images = re.findall(r'<ac:image[^>]*>.*?</ac:image>', storage)
print(f'ac:image tags: {len(images)}')
for i, img in enumerate(images):
    print(f'  {i+1}. {img}')

`@mermaid-js/mermaid-cli` must be installed globally:

```bash
npm install -g @mermaid-js/mermaid-cli
```

Verify with `mmdc --version`. If missing, install before proceeding.

## Workflow

### 1. Create `.mmd` file

Write the Mermaid diagram to a `.mmd` file. Avoid curly braces `{}` and
HTML entities in message labels — these break the parser. Use `Note`
blocks for detailed text instead.

### 2. Render to SVG

```bash
mmdc -i diagram.mmd -o diagram.svg -b transparent
```

### 3. Upload as attachment via REST API

The `mcp-atlassian` MCP server has **no** attachment upload tool (it was
added then removed due to security/usability issues). Use the Confluence
REST API directly via curl.

Credentials live in `~/.config/mcp/mcp_servers.json` under
`mcpServers.atlassian.env` (`CONFLUENCE_URL`, `CONFLUENCE_USERNAME`,
`CONFLUENCE_API_TOKEN`). Extract them with:

```bash
CONFLUENCE_URL=$(python3 -c "import json; print(json.load(open('$HOME/.config/mcp/mcp_servers.json'))['mcpServers']['atlassian']['env']['CONFLUENCE_URL'])")
CONFLUENCE_USERNAME=$(python3 -c "import json; print(json.load(open('$HOME/.config/mcp/mcp_servers.json'))['mcpServers']['atlassian']['env']['CONFLUENCE_USERNAME'])")
CONFLUENCE_API_TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/.config/mcp/mcp_servers.json'))['mcpServers']['atlassian']['env']['CONFLUENCE_API_TOKEN'])")
```

Upload each SVG (re-uploading the same filename auto-creates a new version):

```bash
curl -s -u "$CONFLUENCE_USERNAME:$CONFLUENCE_API_TOKEN" \
  -X PUT \
  -H "X-Atlassian-Token: nocheck" \
  -F "file=@diagram.svg" \
  -F "comment=Auto-uploaded diagram" \
  "$CONFLUENCE_URL/rest/api/content/<page_id>/child/attachment"
```

Verify each curl returns HTTP 200 with attachment metadata JSON.

### 4. Embed inline with explicit width

**Before updating,** fetch the current page in storage format to use as a
base. Via `mcp-cli`:

```bash
mcp-cli call atlassian confluence_get_page \
  '{"page_id": "<page_id>", "include_metadata": false, "convert_to_markdown": false}'
```

This returns the raw storage-format XHTML. Edit it to insert or replace
`<ac:image>` tags, then update the page.

Update the page using `content_format: "storage"` and insert:

```xml
<ac:image ac:align="center" ac:layout="center" ac:width="WIDTH">
  <ri:attachment ri:filename="diagram.svg" ri:version-at-save="1" />
</ac:image>
```

**Width guidelines** (based on content viewBox):

| Diagram type | Recommended `ac:width` |
|---|---|
| Wide sequence diagram (4+ participants) | `900` |
| Medium sequence diagram (3 participants) | `750` |
| Narrow / flowchart | `600` |

### 5. Why explicit width is required

Mermaid CLI generates SVGs with `width="100%"` and a `viewBox` attribute.
Confluence ignores `viewBox` and needs a concrete pixel width, otherwise
the image renders as a tiny thumbnail. Always set `ac:width`.

## Key gotchas

- **Use storage format** when embedding images. If you update via
  `content_format: "markdown"`, Confluence converts `<ac:image>` to
  `<img>` tags and loses the `ac:width` attribute.
- **Don't use `<img>` tags.** Only `<ac:image>` with `<ri:attachment>`
  renders attached files inline with size control.
- **SVG MIME type:** Confluence may store SVGs as `application/octet-stream`.
  This is fine — they still render correctly via `<ac:image>`.
- **Re-uploading** an attachment with the same filename creates a new
  version automatically. Update `ri:version-at-save` if referencing a
  specific version, or omit it to use the latest.

## Example: full sequence

```bash
# 1. Render
mmdc -i architecture.mmd -o architecture.svg -b transparent

# 2. Upload (via REST API — no MCP tool exists for this)
curl -s -u "$CONFLUENCE_USERNAME:$CONFLUENCE_API_TOKEN" \
  -X PUT -H "X-Atlassian-Token: nocheck" \
  -F "file=@architecture.svg" -F "comment=Architecture diagram" \
  "$CONFLUENCE_URL/rest/api/content/$PAGE_ID/child/attachment"

# 3. Embed (via mcp-cli update_page with content_format="storage")
#    Insert into the page storage-format HTML:
#    <ac:image ac:align="center" ac:layout="center" ac:width="900">
#      <ri:attachment ri:filename="architecture.svg" />
#    </ac:image>
```

## Verification

**Do not use browser-based visual verification.** The browser MCP tool
has no stored Atlassian session and Confluence login requires separate
authentication from the API token used by the MCP server. Attempting to
navigate to the page will hit a login wall.

Instead, verify via the REST API:

```bash
curl -s -u "$CONFLUENCE_USERNAME:$CONFLUENCE_API_TOKEN" \
  "$CONFLUENCE_URL/rest/api/content/$PAGE_ID?expand=body.storage" \
  | python3 -c "
import sys, json, re
data = json.loads(sys.stdin.read())
storage = data['body']['storage']['value']
images = re.findall(r'<ac:image[^>]*>.*?</ac:image>', storage)
print(f'ac:image tags: {len(images)}')
for i, img in enumerate(images):
    print(f'  {i+1}. {img}')
"
```

Confirm:
- Expected number of `<ac:image>` tags are present
- Each has the correct `ri:filename` and `ac:width`
- No stale `<img>` tags or ASCII code blocks remain for diagrams

## Assumptions & Escalation

- **Tier 1 (reversible):** Diagram styling (colors, fonts) — proceed, flag for review.
- **Tier 2 (logic):** Sequence/Flowchart logic errors — verify against requirement, block if ambiguous.
- **Tier 3 (security):** Sensitive data in diagram text (keys, PII) — always block.

---

**Editing this skill?** Use [`~/.skills/skillsmith`](~/.skills/skillsmith) for skill creation guidelines.
