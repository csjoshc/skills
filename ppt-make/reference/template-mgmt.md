# Template Management

## Contents

- Template location
- Available layouts
- Regenerating the template
- Connectors and arrows

---

## Template Location

`templates/c3-template.pptx` — clean slide-stripped PPTX with 0 slides
and 15 layouts carrying the C3 slide master.

---

## Available Layouts

| Index | Name                 | Use for                |
|-------|----------------------|------------------------|
| 0     | Title Slide Option   | Opening / title slide  |
| 13    | Blank                | All custom content     |
| 14    | Closing logo slide   | Q&A / closing          |

---

## Regenerating the Template

Use the zipfile stripping recipe — **NOT** `_sldIdLst.remove()`:

```python
import zipfile, re
from lxml import etree

SRC = "source-deck.pptx"
CLEAN = "templates/c3-template.pptx"
NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
skip = [
    re.compile(r'^ppt/slides/slide\d+\.xml$'),
    re.compile(r'^ppt/slides/_rels/slide\d+\.xml\.rels$'),
    re.compile(r'^ppt/notesSlides/notesSlide\d+\.xml$'),
    re.compile(r'^ppt/notesSlides/_rels/notesSlide\d+\.xml\.rels$'),
]
with zipfile.ZipFile(SRC, 'r') as zin, \
     zipfile.ZipFile(CLEAN, 'w', zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if any(p.match(item.filename) for p in skip):
            continue
        if item.filename == 'ppt/presentation.xml':
            root = etree.fromstring(data)
            lst = root.find('.//p:sldIdLst', NS)
            if lst is not None:
                for child in list(lst): lst.remove(child)
            data = etree.tostring(root, xml_declaration=True,
                                  encoding='UTF-8', standalone=True)
        elif item.filename == 'ppt/_rels/presentation.xml.rels':
            root = etree.fromstring(data)
            for rel in list(root):
                if re.match(r'slides/slide\d+\.xml', rel.get('Target', '')):
                    root.remove(rel)
            data = etree.tostring(root, xml_declaration=True,
                                  encoding='UTF-8', standalone=True)
        elif item.filename == '[Content_Types].xml':
            root = etree.fromstring(data)
            for o in list(root):
                pn = o.get('PartName', '')
                if re.match(r'/ppt/(slides|notesSlides)/\w+\d+\.xml', pn):
                    root.remove(o)
            data = etree.tostring(root, xml_declaration=True,
                                  encoding='UTF-8', standalone=True)
        zout.writestr(item, data)
```

---

## Connectors and Arrows

- Use `MSO_CONNECTOR_TYPE.STRAIGHT` — never text-based arrows
- **Always directional:** `a:tailEnd` type="triangle", w="med", len="med"
- Branch labels (YES/NO) in separate textboxes with `wrap=False`
- Label textboxes >= 0.50" wide to prevent word-wrap
