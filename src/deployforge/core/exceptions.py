"""Custom exceptions for DeployForge."""


class DeployForgeError(Exception):
    """Base exception for all DeployForge errors."""

    pass


class ImageNotFoundError(DeployForgeError):
    """Raised when an image file cannot be found."""

    pass


class UnsupportedFormatError(DeployForgeError):
    """Raised when an unsupported image format is encountered."""

    pass


class MountError(DeployForgeError):
    """Raised when there's an error mounting or unmounting an image."""

    pass


class ValidationError(DeployForgeError):
    """Raised when validation of input or configuration fails."""

    pass


class OperationError(DeployForgeError):
    """Raised when a file operation fails."""

    pass


class DISMError(DeployForgeError):
    """Raised when a DISM operation fails."""

    pass
