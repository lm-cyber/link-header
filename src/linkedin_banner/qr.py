"""QR code generation for linkedin-banner."""

from __future__ import annotations

from PIL import Image
from PIL.Image import Resampling
from qrcode.constants import ERROR_CORRECT_H  # type: ignore[import-untyped]
from qrcode.image.styledpil import StyledPilImage  # type: ignore[import-untyped]
from qrcode.image.styles.moduledrawers.pil import (  # type: ignore[import-untyped]
    RoundedModuleDrawer,
)
from qrcode.main import QRCode  # type: ignore[import-untyped]

from linkedin_banner.exceptions import QRGenerationError


def _recolor(
    img: Image.Image,
    front_color: tuple[int, int, int],
    back_color: tuple[int, int, int],
) -> Image.Image:
    """Recolor a black-on-white QR image to use custom colors."""
    rgba = img.convert("RGBA")
    pixels = rgba.load()
    if pixels is None:
        return rgba
    for y in range(rgba.height):
        for x in range(rgba.width):
            pixel = pixels[x, y]
            r: int = pixel[0]  # type: ignore[index]
            a: int = pixel[3]  # type: ignore[index]
            if r < 128:
                pixels[x, y] = (*front_color, a)
            else:
                pixels[x, y] = (*back_color, a)
    return rgba


def overlay_favicon(
    qr_img: Image.Image,
    favicon: Image.Image,
    bg_color: tuple[int, int, int],
    favicon_ratio: float = 0.22,
) -> Image.Image:
    """Overlay a favicon on the center of a QR code image.

    The favicon is sized to ~22% of the QR width (within ERROR_CORRECT_H's 30% tolerance).
    A background-colored padding rectangle is drawn behind it for readability.
    """
    qr_size = qr_img.width
    icon_size = int(qr_size * favicon_ratio)
    padding = icon_size // 6

    favicon_resized = favicon.resize((icon_size, icon_size), Resampling.LANCZOS)

    # Create a background pad behind the favicon
    pad_size = icon_size + padding * 2
    pad = Image.new("RGBA", (pad_size, pad_size), (*bg_color, 255))

    # Center positions
    pad_x = (qr_size - pad_size) // 2
    pad_y = (qr_size - pad_size) // 2
    icon_x = (qr_size - icon_size) // 2
    icon_y = (qr_size - icon_size) // 2

    result = qr_img.copy()
    result.paste(pad, (pad_x, pad_y), pad)
    result.paste(favicon_resized, (icon_x, icon_y), favicon_resized)
    return result


def generate_qr(
    url: str,
    size: int,
    front_color: tuple[int, int, int],
    back_color: tuple[int, int, int],
) -> Image.Image:
    """Generate a styled QR code image.

    Returns an RGBA PIL Image resized to `size` x `size`.
    """
    try:
        qr = QRCode(error_correction=ERROR_CORRECT_H, border=2)
        qr.add_data(url)
        qr.make(fit=True)

        # Generate styled QR (black on white), then recolor
        # SolidFillColorMask is broken in qrcode 8.x with StyledPilImage
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
        )

        pil_img = img.get_image()
        pil_img = _recolor(pil_img, front_color, back_color)
        pil_img = pil_img.resize((size, size), Resampling.LANCZOS)
        return pil_img
    except Exception as e:
        raise QRGenerationError(f"Failed to generate QR code: {e}") from e
