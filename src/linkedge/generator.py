"""Banner image generation for linkedge."""

from __future__ import annotations

import platform
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from linkedge.exceptions import BannerGenerationError
from linkedge.models import BannerConfig, OutputFormat, PatternStyle, QRPosition
from linkedge.palette import choose_text_color, hex_to_rgb, lighten, resolve_color
from linkedge.qr import generate_qr

# Font candidates per platform
_FONT_CANDIDATES: dict[str, list[str]] = {
    "Darwin": [
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ],
    "Linux": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ],
    "Windows": [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ],
}


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a system font at the given size, with fallback to Pillow default."""
    system = platform.system()
    candidates = _FONT_CANDIDATES.get(system, [])

    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue

    # Pillow 10.1+ default font with size
    return ImageFont.load_default(size=size)


def _draw_text_fitted(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    max_width: int,
    initial_size: int,
    color: tuple[int, int, int],
    min_size: int = 16,
) -> int:
    """Draw text, reducing font size if it exceeds max_width. Returns actual font size used."""
    size = initial_size
    while size >= min_size:
        font = _load_font(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            draw.text(xy, text, fill=color, font=font)
            return size
        size -= 2

    # At minimum size, draw anyway
    font = _load_font(min_size)
    draw.text(xy, text, fill=color, font=font)
    return min_size


def _draw_pattern(
    size: tuple[int, int],
    style: PatternStyle,
    pattern_color: tuple[int, int, int],
    opacity: int = 40,
) -> Image.Image:
    """Create a pattern overlay on a transparent RGBA layer."""
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    fill = (*pattern_color, opacity)

    if style == PatternStyle.GRID:
        spacing = 48
        for x in range(0, w, spacing):
            draw.line([(x, 0), (x, h)], fill=fill, width=1)
        for y in range(0, h, spacing):
            draw.line([(0, y), (w, y)], fill=fill, width=1)

    elif style == PatternStyle.DOTS:
        spacing = 36
        radius = 3
        for x in range(spacing, w, spacing):
            for y in range(spacing, h, spacing):
                draw.ellipse(
                    [x - radius, y - radius, x + radius, y + radius],
                    fill=fill,
                )

    elif style == PatternStyle.LINES:
        spacing = 24
        # Diagonal lines from top-left to bottom-right
        for offset in range(-h, w + h, spacing):
            draw.line([(offset, 0), (offset + h, h)], fill=fill, width=1)

    return layer


def generate_banner(config: BannerConfig) -> Image.Image:
    """Generate a LinkedIn banner image from config."""
    try:
        hex_color = resolve_color(config.color)
        bg_rgb = hex_to_rgb(hex_color)
        text_rgb = choose_text_color(bg_rgb)

        # Create base image with solid fill
        banner = Image.new("RGBA", (config.width, config.height), (*bg_rgb, 255))

        # Pattern overlay
        if config.pattern != PatternStyle.NONE:
            pattern_color = lighten(bg_rgb, 0.3)
            pattern_layer = _draw_pattern(
                (config.width, config.height), config.pattern, pattern_color
            )
            banner = Image.alpha_composite(banner, pattern_layer)

        # Generate QR code
        is_corner = config.qr_position in (QRPosition.CORNER_BR, QRPosition.CORNER_BL)
        qr_size = 220 if is_corner else 300
        qr_img = generate_qr(config.url, qr_size, text_rgb, bg_rgb)

        # Calculate layout
        draw = ImageDraw.Draw(banner)
        margin_x = 80
        qr_margin = 60

        # Font sizes
        name_size = 52
        title_size = 32
        tagline_size = 24

        if config.qr_position == QRPosition.RIGHT:
            # QR on right, text on left
            qr_x = config.width - qr_size - qr_margin
            qr_y = (config.height - qr_size) // 2
            text_x = margin_x
            text_max_w = qr_x - margin_x - 40

        elif config.qr_position == QRPosition.LEFT:
            # QR on left, text after
            qr_x = qr_margin
            qr_y = (config.height - qr_size) // 2
            text_x = qr_x + qr_size + 40
            text_max_w = config.width - text_x - margin_x

        elif config.qr_position == QRPosition.CORNER_BR:
            qr_x = config.width - qr_size - 30
            qr_y = config.height - qr_size - 20
            text_x = margin_x
            text_max_w = qr_x - margin_x - 40

        else:  # CORNER_BL
            qr_x = 30
            qr_y = config.height - qr_size - 20
            text_x = qr_x + qr_size + 40
            text_max_w = config.width - text_x - margin_x

        # Calculate text block height for vertical centering
        line_heights = [name_size, title_size]
        line_gaps = [14, 10]
        if config.tagline:
            line_heights.append(tagline_size)
            line_gaps.append(0)

        total_text_h = sum(line_heights) + sum(line_gaps[: len(line_heights) - 1])
        text_y = (config.height - total_text_h) // 2

        # Draw text lines
        current_y = text_y
        _draw_text_fitted(draw, config.name, (text_x, current_y), text_max_w, name_size, text_rgb)
        current_y += name_size + line_gaps[0]

        _draw_text_fitted(
            draw, config.title, (text_x, current_y), text_max_w, title_size, text_rgb
        )
        current_y += title_size + line_gaps[1]

        if config.tagline:
            _draw_text_fitted(
                draw, config.tagline, (text_x, current_y), text_max_w, tagline_size, text_rgb
            )

        # Paste QR with alpha mask
        banner.paste(qr_img, (qr_x, qr_y), qr_img)

        return banner
    except BannerGenerationError:
        raise
    except Exception as e:
        raise BannerGenerationError(f"Failed to generate banner: {e}") from e


def save_banner(image: Image.Image, path: str, fmt: OutputFormat) -> Path:
    """Save banner image to disk."""
    output_path = Path(path)
    if fmt == OutputFormat.JPG:
        rgb_image = image.convert("RGB")
        rgb_image.save(output_path, "JPEG", quality=95)
    else:
        image.save(output_path, "PNG")
    return output_path
