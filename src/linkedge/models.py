"""Data models for linkedge."""

from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, field_validator


class QRPosition(StrEnum):
    RIGHT = "right"
    LEFT = "left"
    CORNER_BR = "corner-br"
    CORNER_BL = "corner-bl"


class PatternStyle(StrEnum):
    NONE = "none"
    GRID = "grid"
    DOTS = "dots"
    LINES = "lines"


class OutputFormat(StrEnum):
    PNG = "png"
    JPG = "jpg"


class BannerConfig(BaseModel):
    name: str
    title: str
    tagline: str | None = None
    url: str
    color: str
    qr_position: QRPosition = QRPosition.RIGHT
    pattern: PatternStyle = PatternStyle.NONE
    output: str = "banner.png"
    format: OutputFormat = OutputFormat.PNG
    preview: bool = False
    width: int = 1584
    height: int = 396

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Normalize and validate hex color or palette name."""
        from linkedge.palette import PALETTES

        # Check if it's a palette name first
        if v.lower() in PALETTES:
            return v.lower()

        # Normalize hex: strip #, validate 6-digit hex
        hex_val = v.lstrip("#").lower()
        if not re.match(r"^[0-9a-f]{6}$", hex_val):
            raise ValueError(
                f"Invalid color '{v}'. Use a 6-digit hex code (e.g. #1a1a2e) or palette name."
            )
        return f"#{hex_val}"
