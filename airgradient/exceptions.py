"""Exceptions for the AirGradient client library."""


class AirGradientError(Exception):
    """Base exception for all AirGradient errors."""


class AuthenticationError(AirGradientError):
    """Raised when the API token is invalid or missing."""


class NotFoundError(AirGradientError):
    """Raised when a requested resource does not exist."""


class LocalAPIError(AirGradientError):
    """Raised when the local device API returns an error."""


class ConnectionError(AirGradientError):
    """Raised when the device or cloud API cannot be reached."""
