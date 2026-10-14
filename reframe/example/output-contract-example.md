# Output Contract Example

A complete exec-audience reframe output that satisfies the contract in SKILL.md.

```markdown
---
title: "Platform Migration"
subtitle: "Q3 Recommendation"
audience: exec
author: "Jane Doe"
date: "April 2026"
sources:
  - label: "Architecture RFC"
    url: "./docs/rfc-042.md"
diagrams:
  - path: "./platform-migration-exec-timeline.mmd"
    slide: "Timeline"
---

## Slide: Recommendation

- Migrate to managed Kubernetes by Q4
- Projected 30% infrastructure cost reduction
- Risk: 2-week service disruption during cutover

## Slide: Business Value

- $1.2M annual savings from consolidated compute
- 40% faster deployment cycles
- Improved compliance posture (FedRAMP inheritance)

## Slide: Timeline

- **Q3**: Proof of concept + team training
- **Q4**: Production migration (3 phases)
- **Q1 next year**: Decommission legacy

## Slide: Parking Lot

- **Detailed migration runbook**: Cut because exec audience; available in engineer reframe
- **Kubernetes operator comparison**: Cut because implementation detail
```
