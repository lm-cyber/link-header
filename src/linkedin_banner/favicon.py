"""Favicon fetching for linkedin-banner."""

from __future__ import annotations

import io
from urllib.parse import urlparse

import httpx
from PIL import Image
from PIL.Image import Resampling


def _extract_domain(url: str) -> str:
    """Extract domain from a URL."""
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path.split("/")[0]
    return domain


def fetch_favicon(url: str, size: int = 128) -> Image.Image | None:
    """Fetch a favicon for the given URL's domain.

    Tries Google's favicon API first, then falls back to /favicon.ico.
    Returns an RGBA PIL Image resized to `size` x `size`, or None on failure.
    """
    domain = _extract_domain(url)

    strategies = [
        f"https://www.google.com/s2/favicons?domain={domain}&sz={size}",
        f"https://{domain}/favicon.ico",
    ]

    for favicon_url in strategies:
        try:
            resp = httpx.get(favicon_url, timeout=5.0, follow_redirects=True)
            resp.raise_for_status()
            raw = Image.open(io.BytesIO(resp.content))
            rgba: Image.Image = raw.convert("RGBA")
            rgba = rgba.resize((size, size), Resampling.LANCZOS)
            return rgba
        except Exception:
            continue

    return None
