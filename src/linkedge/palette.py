"""Color palette system for linkedge."""

from __future__ import annotations

from linkedge.exceptions import InvalidColorError

PALETTES: dict[str, str] = {
    "midnight": "#1a1a2e",
    "ocean": "#0a3d62",
    "forest": "#1b4332",
    "slate": "#2f3e46",
    "burgundy": "#4a0e0e",
    "charcoal": "#2d2d2d",
    "navy": "#0b1354",
    "plum": "#3c1361",
    "steel": "#37474f",
    "espresso": "#3e2723",
    "olive": "#33691e",
    "graphite": "#424242",
    "teal": "#004d40",
    "rust": "#6e2c00",
    "indigo": "#1a237e",
    "sage": "#4a5d23",
}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """Calculate WCAG 2.0 relative luminance from sRGB."""
    channels = []
    for c in rgb:
        s = c / 255.0
        linear = s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
        channels.append(linear)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def choose_text_color(bg_rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    """Return white or near-black text color based on background luminance."""
    if relative_luminance(bg_rgb) > 0.179:
        return (30, 30, 30)
    return (255, 255, 255)


def lighten(rgb: tuple[int, int, int], factor: float = 0.3) -> tuple[int, int, int]:
    """Blend color toward white by factor (0-1)."""
    return tuple(int(c + (255 - c) * factor) for c in rgb)  # type: ignore[return-value]


def darken(rgb: tuple[int, int, int], factor: float = 0.3) -> tuple[int, int, int]:
    """Blend color toward black by factor (0-1)."""
    return tuple(int(c * (1 - factor)) for c in rgb)  # type: ignore[return-value]


def resolve_color(color: str) -> str:
    """Resolve a palette name or hex code to a hex string."""
    name = color.lower()
    if name in PALETTES:
        return PALETTES[name]
    if color.startswith("#") and len(color) == 7:
        return color
    raise InvalidColorError(f"Unknown color: {color}")
