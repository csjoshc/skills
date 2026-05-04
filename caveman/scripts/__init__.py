"""
Caveman compress helpers — deterministic checks only.

Compression itself is performed by the resident agent (see SKILL.md).
These modules provide file-type detection, safety gating, and post-
compression validation.
"""

__version__ = "2.0.0"

__all__ = ["detect", "safety", "validate"]
