"""Banner image generation for linkedin-banner."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from linkedin_banner.exceptions import BannerGenerationError
from linkedin_banner.favicon import fetch_favicon
from linkedin_banner.models import BannerConfig, OutputFormat, PatternStyle
from linkedin_banner.palette import choose_text_color, hex_to_rgb, lighten, resolve_color
from linkedin_banner.qr import generate_qr, overlay_favicon

# Layout constants
_AVATAR_ZONE = 280  # px from left reserved for LinkedIn profile photo
_MARGIN_Y = 30
_MARGIN_RIGHT = 40
_QR_GAP = 30


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
        for offset in range(-h, w + h, spacing):
            draw.line([(offset, 0), (offset + h, h)], fill=fill, width=1)

    return layer


def generate_banner(config: BannerConfig) -> Image.Image:
    """Generate a LinkedIn banner image with multi-QR layout."""
    try:
        hex_color = resolve_color(config.color)
        bg_rgb = hex_to_rgb(hex_color)
        qr_fg = choose_text_color(bg_rgb)

        # Create base image
        banner = Image.new("RGBA", (config.width, config.height), (*bg_rgb, 255))

        # Pattern overlay
        if config.pattern != PatternStyle.NONE:
            pattern_color = lighten(bg_rgb, 0.3)
            pattern_layer = _draw_pattern(
                (config.width, config.height), config.pattern, pattern_color
            )
            banner = Image.alpha_composite(banner, pattern_layer)

        # Calculate QR layout
        n = len(config.urls)
        max_qr_height = config.height - 2 * _MARGIN_Y
        available_width = config.width - _AVATAR_ZONE - _MARGIN_RIGHT
        qr_size = int(min(max_qr_height, (available_width - (n - 1) * _QR_GAP) / n))

        # Center the QR block in the available zone
        total_w = n * qr_size + (n - 1) * _QR_GAP
        start_x = _AVATAR_ZONE + (available_width - total_w) // 2
        qr_y = (config.height - qr_size) // 2

        # Generate and place each QR code
        for i, url in enumerate(config.urls):
            qr_img = generate_qr(url, qr_size, qr_fg, bg_rgb)

            favicon = fetch_favicon(url)
            if favicon is not None:
                qr_img = overlay_favicon(qr_img, favicon, bg_rgb)

            qr_x = start_x + i * (qr_size + _QR_GAP)
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
