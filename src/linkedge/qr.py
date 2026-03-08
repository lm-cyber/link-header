"""QR code generation for linkedge."""

from __future__ import annotations

from PIL import Image
from PIL.Image import Resampling
from qrcode.constants import ERROR_CORRECT_H  # type: ignore[import-untyped]
from qrcode.image.styledpil import StyledPilImage  # type: ignore[import-untyped]
from qrcode.image.styles.moduledrawers.pil import (  # type: ignore[import-untyped]
    RoundedModuleDrawer,
)
from qrcode.main import QRCode  # type: ignore[import-untyped]

from linkedge.exceptions import QRGenerationError


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
