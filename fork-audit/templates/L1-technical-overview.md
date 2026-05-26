---
title: "<Fork-identity> on <Upstream-identity>"
subtitle: "Architecture Review of <head>@<sha> vs <base>@<sha>"
audience: architect
author: "Generated from diff analysis"
date: "<Month Year>"
sources:
  - label: "<head> @ <sha>"
    url: "https://github.com/<owner>/<repo>/tree/<sha>"
  - label: "<base> @ <sha> (upstream)"
    url: "https://github.com/<owner>/<repo>/tree/<sha>"
  - label: "PR #<n> — <title>"
    url: "https://github.com/<owner>/<repo>/pull/<n>"
diagrams:
  - path: "./diagrams/l1-system-context.mmd"
    slide: "Component Boundaries"
  - path: "./diagrams/l1-data-flow.mmd"
    slide: "Novel Pattern — Data Flow"
  - path: "./diagrams/l1-request-flow.mmd"
    slide: "Primary Request Flow"
---

## Slide: Thesis

<One paragraph stating the architectural shape of the fork. Where does the fork add structurally? Where does it reuse upstream? What is the *one* novel pattern that justifies a topic breakout?>

## Slide: The Core Tension

| Tension | What pushed it | How the fork resolved it |
|---|---|---|
| <vs> | <forcing function> | <design choice> |

## Slide: Context

| | Upstream | Fork |
|---|---|---|
| Identity | … | … |
| Default branch HEAD | `<sha>` (`<date>`) | `<sha>` (`<date>`) |
| Divergent commits | — | <list of shas/PR-numbers> |
| `apps/` | … | … |
| `packages/` | … | … |
| `helm/` | … | … |
| `containers/` | … | … |
| `.github/workflows/` | … | … |

## Slide: Component Boundaries

![Component Boundaries](./diagrams/l1-system-context.svg)

Source: [./diagrams/l1-system-context.mmd](./diagrams/l1-system-context.mmd)

- **Reused as-is**: <list specific symbols / modules>
- **Not used here**: <list upstream surfaces the fork bypasses>
- **Newly added**: <list new modules / surfaces>

## Slide: Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Backend HTTP | … | … |
| ORM / DB | … | … |
| Frontend | … | … |
| AI provider | … | … |
| … | … | … |

## Slide: Novel Pattern — <name>

![<name>](./diagrams/l1-data-flow.svg)

Source: [./diagrams/l1-data-flow.mmd](./diagrams/l1-data-flow.mmd)

| Stage | Files | Table / Surface | Role |
|---|---|---|---|
| … | … | … | … |

## Slide: Primary Request Flow

![Primary Request Flow](./diagrams/l1-request-flow.svg)

Source: [./diagrams/l1-request-flow.mmd](./diagrams/l1-request-flow.mmd)

<Numbered walkthrough of one canonical end-to-end request — what crosses each boundary and why.>

## Slide: Toolkit / Platform Reuse Map

| Upstream primitive | Used by fork | How |
|---|---|---|
| `<module.X>` | Yes / No / Vestigial | <one phrase> |
| … | … | … |

## Slide: CI/CD Posture

| Workflow | Status | Triggers | Scope |
|---|---|---|---|
| `<workflow>.yml` | Added / Removed / Modified | <triggers> | <scope> |

## Slide: NFRs and Operational Notes

- **Throughput** — <numbers if known, "METRICS NEEDED" otherwise>
- **Concurrency** — <coordination posture>
- **Storage caps** — <limits>
- **Recoverability** — <idempotency / cascade rules>
- **Audit / logging** — <where it lands>

## Slide: Architectural Risks

| Risk | Severity | Mitigation in place | Suggested follow-up |
|---|---|---|---|
| … | Low/Med/High | … | … |

## Slide: Migration Considerations

- **Likely conflict surfaces** when merging from upstream: …
- **No-conflict surfaces**: …
- **Pulling vs rebasing** — given the merge style on this repo, … is safer because …

## Slide: Parking Lot

- **<topic>** — covered in [L2 — Deep Dive](./L2-deep-dive.md) instead (engineer audience).
- **<topic>** — covered in [topics/<name>.md](./topics/<name>.md).
- **<topic>** — exec-audience material; lives in [L0 — Executive Summary](./L0-executive-summary.md).
