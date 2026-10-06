# Diagram conventions and quality checklist

## Contents

- Diagram conventions
- Quality checklist

## Diagram conventions

Three Mermaid diagrams target the architect layer (L1):

1. **System context / component boundaries** (flowchart LR) — boxes for consumers, services, libraries, state, external systems; classDef colors per role; subgraphs for trust boundaries
2. **Novel-pattern data flow** (flowchart TB) — stages in the data pipeline / orchestration / state machine
3. **Primary request flow** (sequenceDiagram) — one canonical user→system→external→system→user round trip

**classDef color convention** (consistent with `/make-mmd` and `confluence-diagrams`):

```
classDef consumer fill:#bfbfbf,stroke:#444,color:#000;
classDef service  fill:#a8c5ff,stroke:#2855a8,color:#000;
classDef library  fill:#c9e3ff,stroke:#3970b8,color:#000;
classDef state    fill:#d6c4f0,stroke:#6a4ea8,color:#000;
classDef external fill:#d3d3d3,stroke:#666,color:#000;
classDef compute  fill:#a8c5ff,stroke:#2855a8,color:#000;
classDef output   fill:#c4eac4,stroke:#3a7a3a,color:#000;
classDef removed  fill:#f8d6d6,stroke:#a83838,color:#000,stroke-dasharray: 5 5;
```

Render each `.mmd` to `.svg` with `mmdc -i X.mmd -o X.svg -b transparent`.

## Quality checklist

Before reporting done:

- [ ] Output folder is gitignored and `git status` is clean
- [ ] L0 fits on one screen and leads with the identity paragraph
- [ ] L1 has YAML frontmatter, `## Slide:` sections, a parking-lot appendix, and at least one diagram
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
