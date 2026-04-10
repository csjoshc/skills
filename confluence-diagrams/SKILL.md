---
name: confluence-diagrams
description: >-
  Render text-based diagrams (Mermaid, PlantUML) to SVG and embed them in
  Confluence pages. Use when uploading diagrams to Confluence, embedding
  images in wiki pages, or converting mermaid/markdown diagrams for Confluence.
---

# Confluence Diagram Workflow

Confluence Cloud does not natively render Mermaid or PlantUML. This skill
converts text-based diagrams to SVG, uploads them as attachments, and
embeds them inline at a readable size.

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

## Visual Conventions

When authoring diagrams, apply consistent color and line-style conventions
based on C4, UML, and ArchiMate standards. A companion example is at
`confluence-diagrams/example-conventions.mmd`.

### Node colors (classDef)

| classDef | Hex | Entity type |
|----------|-----|-------------|
| `person` | `#E8EAED` (light grey) | User, browser, actor |
| `service` | `#4285F4` (blue) | Application, API, deployed service |
| `library` | `#4FC3F7` (light blue) | In-process library or module |
| `guard` | `#F9AB00` (gold/amber) | Security boundary, guardrail, policy |
| `external` | `#9AA0A6` (grey) | External system outside your control |
| `state` | `#A142F4` (purple) | State, data store, configuration |
| `errBlock` | `#EA4335` (red) | Error state, blocked path |
| `passNode` | `#34A853` (green) | Success outcome, data-in-motion |
| `auditNode` | `#9AA0A6` (grey) | Audit, logging (side-effect) |

### Edge styles

| Style | Mermaid syntax | Meaning |
|-------|---------------|---------|
| Solid + filled arrow | `A --> B` | Synchronous call |
| Solid + label | `A -->\|"label"\| B` | HTTP call (use blue labels for HTTP) |
| Dashed + filled arrow | `A -.-> B` | Async, streaming, or exceptional path |
| Dotted + open arrow | `A -.-\|"label"\| B` | Dependency, side-effect, optional |

### Legend block

Include a legend subgraph at the bottom of complex diagrams:

```
subgraph Legend ["LEGEND"]
  direction LR
  L_svc["Service / API"]:::service
  L_lib["Library / Module"]:::library
  L_guard["Security / Guardrail"]:::guard
  L_ext["External System"]:::external
  L_state["State / Data"]:::state
  L_err["Error / Block"]:::errBlock
end
```

### Mermaid-specific notes

- Use `<br/>` for line breaks in node labels (not `\n`).
- `classDef` only works in `flowchart` diagrams — `sequenceDiagram` and
  `stateDiagram-v2` ignore it.
- Edge styling via `linkStyle N` is index-based and fragile. Prefer
  solid vs dashed arrows and descriptive labels over edge colors.
- Avoid `{}` and HTML entities in labels — they break the Mermaid parser.

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
