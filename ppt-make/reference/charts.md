# Chart Support

## Contents

- Adding charts to adapter-generated decks
- Supported python-pptx chart types
- Dark theme chart styling

---

## Adding Charts to Adapter-Generated Decks

The adapter does not yet include a dedicated `chart` layout, but charts
can be added using python-pptx's native chart API alongside adapter-generated
slides.

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

# Generate the deck first
prs = build_deck("deck.yaml")

# Add a chart slide manually
slide = prs.slides[5]  # or add a new blank slide
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('Revenue', (120, 145, 160, 190))

chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(1.0), Inches(2.0),
    Inches(11.0), Inches(4.5),
    chart_data
).chart

# Style for dark background
plot = chart.plots[0]
plot.has_data_labels = True
chart.has_legend = True
```

---

## Supported python-pptx Chart Types

- COLUMN_CLUSTERED, COLUMN_STACKED
- BAR_CLUSTERED, BAR_STACKED
- LINE, LINE_MARKERS
- PIE, DOUGHNUT
- AREA, AREA_STACKED
- XY_SCATTER, XY_SCATTER_LINES
- BUBBLE

---

## Dark Theme Chart Styling

Import colors from `palette.py` for consistency:

```python
from palette import WHITE, WARM_GRAY, NEAR_BLACK, ORANGE, GREEN, C3_BLUE
```

- Chart background: transparent or `NEAR_BLACK` (#1A1A1A)
- Axis labels / data labels: `WHITE` (#FFFFFF)
- Series fills: use accent colors (`ORANGE`, `GREEN`, `C3_BLUE`)
- Gridlines: `WARM_GRAY` (#CBC8C7) at 0.5pt
- Legend text: white, positioned outside plot area
