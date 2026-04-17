"""
C3.ai Dark-Mode Color Palette — single source of truth.

Used by adapter.py and reference_build.py. Import from here instead
of redeclaring colors inline.

Usage:
    from palette import COLORS, color, WHITE, ORANGE, GREEN, ...
"""
from __future__ import annotations

from pptx.dml.color import RGBColor


# ── Named palette ──────────────────────────────────────────────
# Keys are the canonical names used in YAML `fill:` / `color:` fields.

COLORS: dict[str, RGBColor] = {
    # Text & backgrounds
    "white":      RGBColor(0xFF, 0xFF, 0xFF),
    "light_gray": RGBColor(0xC8, 0xC8, 0xC8),
    "med_gray":   RGBColor(0x8C, 0x8C, 0x8C),
    "near_black": RGBColor(0x1A, 0x1A, 0x1A),

    # Shape fills
    "dark":       RGBColor(0x50, 0x50, 0x50),
    "gray":       RGBColor(0x8C, 0x8C, 0x8C),
    "panel_dark": RGBColor(0x35, 0x35, 0x35),

    # Accent colors
    "blue":       RGBColor(0x06, 0xA7, 0xE0),
    "orange":     RGBColor(0xF7, 0x94, 0x30),
    "green":      RGBColor(0x9C, 0xCD, 0x6C),

    # Borders & dividers
    "warm_gray":  RGBColor(0xCB, 0xC8, 0xC7),

    # Table alternating rows
    "tbl_hdr":    RGBColor(0x50, 0x50, 0x50),
    "tbl_row_a":  RGBColor(0x3A, 0x3A, 0x3A),
    "tbl_row_b":  RGBColor(0x2D, 0x2D, 0x2D),
}


# ── Convenience constants ──────────────────────────────────────

WHITE      = COLORS["white"]
LIGHT_GRAY = COLORS["light_gray"]
MED_GRAY   = COLORS["med_gray"]
NEAR_BLACK = COLORS["near_black"]
DARK_FILL  = COLORS["dark"]
GRAY_FILL  = COLORS["gray"]
PANEL_DARK = COLORS["panel_dark"]
C3_BLUE    = COLORS["blue"]
ORANGE     = COLORS["orange"]
GREEN      = COLORS["green"]
WARM_GRAY  = COLORS["warm_gray"]
TBL_HDR    = COLORS["tbl_hdr"]
TBL_ROW_A  = COLORS["tbl_row_a"]
TBL_ROW_B  = COLORS["tbl_row_b"]


# ── Resolver ───────────────────────────────────────────────────

def color(name: str | None) -> RGBColor:
    """Resolve a YAML color name to an RGBColor.

    Accepts names like "orange", "light-gray", "panel dark".
    Returns DARK_FILL for unknown/None values.
    """
    if name is None:
        return DARK_FILL
    if isinstance(name, str):
        return COLORS.get(
            name.lower().replace("-", "_").replace(" ", "_"),
            DARK_FILL,
        )
    return DARK_FILL


# ── Role-based color assignments (for diagrams) ───────────────
#
# | Role                    | Fill   | Text  | Border    |
# |-------------------------|--------|-------|-----------|
# | User / external input   | gray   | white | warm_gray |
# | CDAO-owned component    | orange | white | none      |
# | C3 platform component   | green  | white | none      |
# | Guardrail / security    | blue   | white | none      |
# | Decision / branch       | dark   | white | warm_gray |
#
# ── Dark-theme chart styling tips ──────────────────────────────
#
# - Chart background: transparent or near_black (#1A1A1A)
# - Axis labels / data labels: white (#FFFFFF)
# - Series fills: use accent colors (orange, green, blue)
# - Gridlines: warm_gray (#CBC8C7) at 0.5pt
# - Legend text: white, positioned outside plot area
