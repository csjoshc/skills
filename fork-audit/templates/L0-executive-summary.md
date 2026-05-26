# L0 — Executive Summary

**Repo:** `<owner/repo>` (`<fork-identity>`)
**Forked from:** `<upstream owner/repo>` (`<upstream-identity>`)
**Snapshot:** `<branch> @ <sha>` (`<date>`)
**Audience:** product, exec, programme owners — read this first

---

## What this repo is

<One paragraph identity. Lead with what the fork is (the shipping app / specific use case), then how it relates to the upstream platform. Name the user and the primary surface. End with the structural fact that justifies the rest of the doc — usually "fork is additive on the app layer".>

| | Upstream (`<base>`) | Fork (`<head>`) |
|---|---|---|
| Purpose | <one phrase> | <one phrase> |
| User | <who> | <who> |
| Primary surface | <how they interact> | <how they interact> |
| Data | <data posture> | <data posture> |
| Default state | <apps/packages baseline> | <what's added/changed> |

---

## Problem · Constraints · Solution

| Problem | Constraints | Solution |
|---|---|---|
| <what need pushed this> | <what limited the design> | <what was actually built> |

---

## What changed vs the upstream

<N> PRs / commits land on top of `<base>`:

| PR/SHA | Title | Files | Net LOC | What it does |
|---|---|---|---|---|
| **#<n>** / `<sha>` | <title> | <count> | +<adds> / −<dels> | <one-line summary> |
| **#<n>** / `<sha>` | <title> | <count> | +<adds> / −<dels> | <one-line summary> |

The commits and their merge SHAs: <list shas with their PR numbers>.

---

## How it relates to the canonical architecture

<2–3 sentences describing the upstream architecture pattern (chat platform / agent runtime / RAG / whatever).>

The fork reuses that pattern but specialises in <X>:

- **<Surface 1>** — <how the fork uses it>
- **<Surface 2>** — <how the fork uses it>
- **<Surface 3>** — <where the fork replaces or extends the pattern>

Same architecture vocabulary, different <data / tool / deployment> topology.

---

## Health snapshot

- **Tests:** <counts from CI / PR descriptions>
- **Lint:** <state>
- **Operational quirks:** <pg version bumps, checked-in artifacts, rate-limit posture, etc.>

---

## Where to go from here

| To understand… | Read |
|---|---|
| The technical shape of the diff (architecture, components, integration points) | [L1 — Technical Overview](./L1-technical-overview.md) |
| File-by-file walkthrough of the divergent commits | [L2 — Deep Dive](./L2-deep-dive.md) |
| The novel architectural pattern | [topics/<novel-pattern>.md](./topics/<novel-pattern>.md) |
| The distinctive feature added on top | [topics/<distinctive-feature>.md](./topics/<distinctive-feature>.md) |
| What changed inside the shared platform packages | [topics/<package-diff>.md](./topics/<package-diff>.md) |
| The shipping app — full developer guide | `<in-repo path>` |
