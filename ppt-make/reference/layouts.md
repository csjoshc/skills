# Layout Reference — Full YAML Schema

## Contents

- Layout: title
- Layout: panels
- Layout: flow
- Layout: diagram
- Layout: pipeline
- Layout: table
- Layout: comparison
- Layout: mixed
- Layout: bullets
- Layout: text
- Layout: closing
- Slide extras (all layouts)

---

## Layout: `title`

Opening slide. Uses template placeholders (index 0).

```yaml
- title: "Deck Title"
  layout: title
```

No additional fields — uses top-level `title` and `subtitle`.

---

## Layout: `panels`

2-4 column layout with colored header bars.

```yaml
- title: "Context & Constraints"
  layout: panels
  panels:
    - header: "Problem"
      color: orange
      content: |
        - Standard C3 packages bundle UI and API
        - No c3auth for non-browser consumers
    - header: "Constraints"
      color: dark
      content: "..."
    - header: "Quality Attributes"
      color: green
      content: "..."
```

Panel widths auto-size: 2 panels = 6.14" each, 3 = 4.05", 4 = 3.01".

---

## Layout: `flow`

Linear sequence of boxes with directional connector arrows.
Supports multi-row flows, branching (YES/NO), and output paths.

```yaml
- title: "Cloud Runtime Flow"
  layout: flow
  subtitle: "Browser -> UI -> Proxy -> Token -> API"
  rows:
    - items:
        - text: "Browser\nGET /flights"
          fill: gray
        - text: "UI App\nc3auth"
          fill: dark
        - text: "Proxy\n.handle()"
          fill: orange
        - text: "API Service"
          fill: green
      direction: right
    - items:
        - text: "JSON response"
          fill: gray
        - text: "Forward"
          fill: dark
      direction: left
      branch:
        from_index: 3
        label: "YES"
        direction: down
        color: orange
        no:
          text: "COMPLETED"
          fill: green
  output_path:
    label: "Output path:"
    items:
      - text: "Output Guardrails"
        fill: blue
      - text: "Response -> User"
        fill: gray
  legend:
    - color: gray
      label: "External"
    - color: orange
      label: "CDAO-Owned"
```

**Auto-layout:** Box sizes, gaps, and font sizes auto-scale based on
item count. Override with explicit `w`, `y` on items/rows.

---

## Layout: `diagram`

Architecture diagram with layer labels, positioned boxes, and edges.

```yaml
- title: "Architecture — Chat UI Path"
  layout: diagram
  subtitle: "Agent-based flow"
  layers:
    - label: "Consumer Layer"
      color: gray
    - label: "Agent Layer"
      color: orange
  elements:
    - id: chat-ui
      text: "Chat UI\n(React SPA)"
      fill: gray
      layer: 0
    - id: agent
      text: "Agent\n(FastAPI BFF)"
      fill: orange
      layer: 1
      left: 1.60        # optional position override
      w: 5.00            # optional width override
  edges:
    - from: chat-ui
      to: agent
      label: "HTTP / SSE"
      color: orange
      direction: down    # auto, down, up, left, right
  legend:
    - color: gray
      label: "Consumer / External"
```

Elements auto-distribute within each layer row.

---

## Layout: `pipeline`

Horizontal box strip at top, then detail sections (tables/text) below.

```yaml
- title: "Request Forwarding"
  layout: pipeline
  pipeline:
    boxes:
      - text: "Inbound"
        fill: gray
      - text: "Strip Prefix"
        fill: dark
      - text: "Inject Bearer"
        fill: orange
  sections:
    - header: "Forwarded"
      color: green
      table:
        headers: ["Element"]
        rows:
          - ["HTTP method"]
          - ["URL path"]
    - header: "Dropped"
      color: white
      table:
        headers: ["Element"]
        rows:
          - ["c3auth cookie"]
```

Sections auto-divide the slide width equally.

---

## Layout: `table`

Structured data with auto column widths and font scaling.

```yaml
- title: "Failure Modes"
  layout: table
  subtitle: "Common errors and fixes"
  table:
    headers: ["Symptom", "Cause", "Fix"]
    rows:
      - ["302 from /oauth/token", "Missing Basic header", "Add header"]
    col_widths: [3.50, 4.00, 4.90]  # optional; auto if omitted
  footnote: "Optional footnote text"
```

Auto font sizing: <6 rows = 11pt, 6-8 = 10pt, >8 = 9pt.

---

## Layout: `comparison`

Side-by-side diagrams (e.g., Local Dev vs Cloud).

```yaml
- title: "Local Dev vs Cloud"
  layout: comparison
  sides:
    - header: "Local Development"
      elements:
        - type: box
          text: "Browser\n(localhost)"
          fill: gray
          h: 0.70
        - type: arrow
          label: "Vite proxy"
          color: orange
          h: 0.50
        - type: box
          text: "dev-proxy"
          fill: orange
          h: 0.75
        - type: label
          text: "Creds from .env"
    - header: "Cloud"
      elements:
        - type: box
          text: "Browser"
          fill: gray
          h: 0.70
  bridge:
    text: "Same API"
    fill: dark
    y: 3.60
  table:
    headers: ["Aspect", "Local", "Cloud"]
    rows: [...]
    top: 5.30
```

---

## Layout: `mixed`

Compose multiple element types on one slide.

```yaml
- title: "Token Cache & Refresh"
  layout: mixed
  elements:
    - type: boxes
      items:
        - text: "Start"
          fill: dark
        - text: "POST /token"
          fill: orange
    - type: table
      headers: ["Param", "Value"]
      rows: [...]
      w: 12.40
      h: 2.80
    - type: callout
      label: "Takeaway"
      detail: "Cache tokens, send both auth methods"
      fill: dark
    - type: text
      text: "Additional context..."
      fsz: 11
```

Elements compose top-to-bottom with auto spacing.

---

## Layout: `bullets`

Enhanced bullet list with optional per-item styling.

```yaml
- title: "Key Takeaways"
  layout: bullets
  subtitle: "Auto font sizing based on content density"
  items:
    - "First key point — brief and impactful"
    - "Second point with more detail"
    - text: "Bold orange point"
      bold: true
      color: orange
```

---

## Layout: `text`

Generic text fallback.

```yaml
- title: "Notes"
  layout: text
  content: "Free-form text content here."
```

---

## Layout: `closing`

Q&A / thank you slide. Uses template closing layout (index 14).

```yaml
- title: "Questions?"
  layout: closing
  content: "Contact: team@example.com | Slack: #project-channel"
```

---

## Slide Extras (all layouts)

Every slide supports these optional fields:

```yaml
notes: "Speaker notes text"
subtitle: "Italic light-gray line under title"
links:
  - text: "Link text"
    url: "https://..."
    left: 0.30
    top: 6.88
footnote: "Small italic text below main content"
```
