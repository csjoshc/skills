# PPTX Generation

## Contents

- [Prerequisites](#prerequisites)
- [Generation Strategy](#generation-strategy)
- [Slide Layout Mapping](#slide-layout-mapping)
- [Typography](#typography)
- [Color Schemes by Audience](#color-schemes-by-audience)
- [Embedding Diagrams](#embedding-diagrams)
- [Building Tables](#building-tables)
- [Error Handling](#error-handling)
- [Output](#output)

---

Instructions for generating PowerPoint slide decks using python-pptx.
Only loaded when `--slides` is requested.

## Prerequisites

Check availability:
```bash
python3 -c "import pptx; print('python-pptx available')"
```

If not installed:
```bash
pip3 install python-pptx
# or if uv is available:
uv pip install python-pptx
```

If installation fails (sandboxed environment, no pip), produce markdown output
with a note: "PPTX generation unavailable — use the markdown outline to build
slides manually or install python-pptx."

## Generation Strategy

Write a temporary Python script that builds the deck, then execute it.
Use `Presentation()` with the default template (no external template dependency).

Key python-pptx patterns:
```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.333)   # widescreen 16:9
prs.slide_height = Inches(7.5)
```

## Slide Layout Mapping

| Layout index | Name | Use for |
|-------------|------|---------|
| 0 | Title Slide | Cover slide |
| 1 | Title and Content | Most body slides |
| 5 | Blank | Diagram-only slides |
| 6 | Title Only | Section dividers |

For blank layouts (diagrams), add the title as a text box manually:
```python
slide = prs.slides.add_slide(prs.slide_layouts[5])
txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.8))
txBox.text_frame.paragraphs[0].text = "Slide Title"
txBox.text_frame.paragraphs[0].font.size = Pt(28)
```

## Typography

| Element | Font | Size | Color |
|---------|------|------|-------|
| Title | Calibri | 28pt | Audience header color |
| Subtitle | Calibri | 18pt | #666666 |
| Body | Calibri | 16pt | #333333 |
| Caption | Calibri | 12pt | #999999 |
| Code | Consolas | 14pt | #1A1A2E |

## Color Schemes by Audience

### Exec
- Header: Navy `#1B2A4A`
- Background: White `#FFFFFF`
- Accent: Gold `#C7923E`
- Text: Dark gray `#333333`

### Architect
- Header: Dark slate `#2D3436`
- Background: Light gray `#F5F6FA`
- Accent: Blue `#4285F4`
- Text: Dark gray `#333333`

### Engineer
- Header: Near-black `#1A1A2E`
- Background: White `#FFFFFF`
- Accent: Green `#34A853`
- Text: Dark gray `#333333`

## Embedding Diagrams

Render Mermaid to PNG first (python-pptx handles PNG natively, not SVG):
```bash
mmdc -i diagram.mmd -o diagram.png -b white -w 1200
```

Embed in a blank slide:
```python
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.add_picture(
    "diagram.png",
    left=Inches(1),
    top=Inches(1.2),
    width=Inches(11),
)
```

Center the image horizontally. Place below the title text box.

## Building Tables

For tradeoff matrices and risk tables:
```python
from pptx.util import Inches, Pt

rows, cols = 4, 5
table_shape = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(1.5), Inches(12), Inches(4))
table = table_shape.table

# Style header row
for i, header in enumerate(["Criterion", "Option A", "Option B", "Option C", "Recommended"]):
    cell = table.cell(0, i)
    cell.text = header
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0x1B, 0x2A, 0x4A)  # navy
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        paragraph.font.size = Pt(14)
```

## Error Handling

- **python-pptx not available**: Produce markdown only. Note in output.
- **Diagram embedding fails**: Insert a text box with the Mermaid source code
  and a note: "Diagram render failed — Mermaid source included for manual rendering."
- **Layout index out of range**: Fall back to layout 1 (Title and Content).
- **File write fails**: Report the error and the markdown path as fallback.

## Output

Save to: `<source-stem>-<audience>.pptx`
Report the full path to the user after generation.
