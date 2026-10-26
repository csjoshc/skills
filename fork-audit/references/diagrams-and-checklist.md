# Diagram conventions and quality checklist

## Contents

- Diagram conventions
- Quality checklist

## Diagram conventions

Three Mermaid diagrams target the architect layer (L1):

1. **System context / component boundaries** (flowchart LR) — boxes for consumers, services, libraries, state, external systems; classDef colors per role; subgraphs for trust boundaries
2. **Novel-pattern data flow** (flowchart TB) — stages in the data pipeline / orchestration / state machine
3. **Primary request flow** (sequenceDiagram) — one canonical user→system→external→system→user round trip

**classDef color convention** (the `diagram` skill's Semantic colors: hue at 25% alpha, no `color:`):

```
classDef consumer fill:#78716C40,stroke:#78716C,stroke-width:1.5px;
classDef service  fill:#3B82F640,stroke:#3B82F6,stroke-width:1.5px;
classDef library  fill:#0284C740,stroke:#0284C7,stroke-width:1.5px;
classDef state    fill:#A855F740,stroke:#A855F7,stroke-width:1.5px;
classDef external fill:#64748B40,stroke:#64748B,stroke-width:1.5px;
classDef compute  fill:#3B82F640,stroke:#3B82F6,stroke-width:1.5px;
classDef output   fill:#15913F40,stroke:#15913F,stroke-width:1.5px;
classDef removed  fill:#EF444440,stroke:#EF4444,stroke-width:1.5px,stroke-dasharray: 5 5;
```

Render each `.mmd` to `.svg` with the `diagram` skill: `node ~/.skills/diagram/scripts/render.mjs X.mmd --for confluence --theme light --out X.svg`.

## Quality checklist

Before reporting done:

- [ ] Output folder is gitignored and `git status` is clean
- [ ] L0 fits on one screen and leads with the identity paragraph
- [ ] L1 follows the template sections, ends with a parking lot, and has at least one diagram
- [ ] L2 has one section per divergent commit, with app-specific vs platform ride-along sub-sections where applicable
- [ ] At least one topic breakout exists for the novel architectural pattern (the structurally new thing, not just the biggest file group)
- [ ] Each diagram has a `.mmd` source and a rendered `.svg`
- [ ] README lists every file actually produced
- [ ] Cross-references between L0/L1/L2/topics are real (clickable, resolve to existing files)
- [ ] The "where to go from here" / reading-by-audience table is in README and L0
- [ ] `questions.md` + `answers.md` exist; every answer cites code or is flagged as a design gap
- [ ] The Q&A loop ran until a round produced no new gaps
- [ ] The Confluence page is published (or `.docs/FINAL-design.md` exists if no Confluence access), synthesized fresh, and every gap on it traces to `answers.md`
- [ ] If `/stop-slop` is available, the final page and intermediates have been run through it
