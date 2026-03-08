"""Custom exceptions for linkedin-banner."""


class LinkedinBannerError(Exception):
    """Base exception for linkedin-banner."""


class InvalidColorError(LinkedinBannerError):
    """Raised when a color value is invalid."""


class FontLoadError(LinkedinBannerError):
    """Raised when a font cannot be loaded."""


class QRGenerationError(LinkedinBannerError):
    """Raised when QR code generation fails."""


class BannerGenerationError(LinkedinBannerError):
    """Raised when banner generation fails."""


class FaviconFetchError(LinkedinBannerError):
    """Raised when a favicon cannot be fetched."""
