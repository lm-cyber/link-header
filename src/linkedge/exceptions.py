"""Custom exceptions for linkedge."""


class LinkedgeError(Exception):
    """Base exception for linkedge."""


class InvalidColorError(LinkedgeError):
    """Raised when a color value is invalid."""


class FontLoadError(LinkedgeError):
    """Raised when a font cannot be loaded."""


class QRGenerationError(LinkedgeError):
    """Raised when QR code generation fails."""


class BannerGenerationError(LinkedgeError):
    """Raised when banner generation fails."""
