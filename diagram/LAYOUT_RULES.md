# Layout Rules (complex flowcharts)

## Contents

- Error-bus pattern
- Cascade-local outcomes
- One exit per subgraph
- Consistent anchor direction
- Max one subgraph crossing per arrow
- Audit/side-effect aggregation

These matter when the SVG will be imported into a Confluence whiteboard or
any renderer with a dynamic connector router. Ignore for simple flowcharts.

## 1. Error-bus pattern — never fan-out block arrows

**Bad:** N guardrail nodes each connect individually to a single error node
far away → N diagonal arrows crossing the happy path.

**Good:** Add one local collector per cascade, then one outbound to error.

```
IG1 --> IG2 --> IG3 --> IG4
IG4 --> PassInput

IG1 & IG2 & IG3 & IG4 -.-> InputErr["⛔ Block"]:::errBlock
InputErr -.-> BlockInput
```

## 2. Cascade-local outcomes

Keep pass/block nodes inside or immediately after their subgraph. Rule of
thumb: no arrow should span more than ~800 px horizontally.

## 3. One exit per subgraph

Each subgraph should expose one outbound happy-path connector and one
outbound error connector. Internal fan-out stays inside.

## 4. Consistent anchor direction

For horizontal cascades (LR flow), all connectors use:
- **Source:** right-center `{left: 1, top: 0.5}`
- **Target:** left-center `{left: 0, top: 0.5}`

Never mix (e.g., bottom-center → left-center) — forces steep diagonals the
router cannot clean up.

## 5. Max one subgraph crossing per arrow

If an arrow must cross more than one subgraph boundary, introduce an
intermediary node at the boundary.

## 6. Audit/side-effect aggregation

Instead of 3 separate section→Audit arrows, add one invisible aggregation
node:

```
InputCascade -.-> AuditBus[" "]
OutputCascade -.-> AuditBus
ToolCascade -.-> AuditBus
AuditBus -.-|"all results logged"| Audit
```
