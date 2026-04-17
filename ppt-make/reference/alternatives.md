# Alternative Approaches

## Contents

- Gramener PPTXHandler (template-based rules)
- PptxGenJS (JavaScript generation)
- pptx-builder-from-yaml
- When to use which

---

## Gramener PPTXHandler (template-based rules)

- **Concept:** Design slides in PowerPoint, name shapes, then use YAML
  rules to modify shape properties (text, fill, position, visibility).
- **Strengths:** Pixel-perfect branding (designers own the template),
  data-driven reports (loop over rows, clone shapes), chart support
  (bar, line, pie, scatter via `chart:` rules), copy-slide for repeating
  sections.
- **Best for:** Recurring data reports where layout is fixed but data
  changes (quarterly reviews, dashboards, status reports).
- **Not ideal for:** One-off architecture decks where slide structure
  varies per topic.
- **Reference:** https://gramener.com/gramex/guide/pptxhandler/

---

## PptxGenJS (JavaScript generation)

- **Concept:** Programmatic PPTX generation in JavaScript/TypeScript.
- **Strengths:** Rich chart API (BAR, LINE, PIE, DOUGHNUT, AREA, SCATTER,
  BUBBLE), shadow effects, slide masters, runs in Node or browser.
- **Best for:** Web apps that generate presentations client-side, or when
  chart-heavy decks are needed.
- **Pitfalls:** No native YAML schema; requires JS wrapper. Shadow/glow
  effects can look inconsistent across PowerPoint versions.
- **Reference:** https://gitbrent.github.io/PptxGenJS/

---

## pptx-builder-from-yaml

- **Concept:** Simple YAML-to-PPTX with basic slide types.
- **Strengths:** Minimal, easy to understand.
- **Limitations:** No diagrams, no flow layouts, no auto-sizing. Too basic
  for technical architecture decks.

---

## When to Use Which

| Scenario                                  | Recommended approach         |
|-------------------------------------------|------------------------------|
| Technical architecture deck from docs     | **ppt-make YAML adapter**    |
| Recurring data report with fixed layout   | **Gramener PPTXHandler**     |
| Chart-heavy presentation                  | **PptxGenJS** or python-pptx |
| Quick bullet-point deck                   | **ppt-make** (bullets layout)|
| Designer-owned branded template           | **Gramener PPTXHandler**     |
