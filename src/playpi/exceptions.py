# this_file: src/playpi/exceptions.py
"""Custom exceptions for PlayPi package."""


class PlayPiError(Exception):
    """Base exception for all PlayPi errors."""


class BrowserError(PlayPiError):
    """Raised when browser automation fails."""


class AuthenticationError(PlayPiError):
    """Raised when authentication with a provider fails."""


class ProviderError(PlayPiError):
    """Raised when a provider-specific operation fails."""


class SessionError(PlayPiError):
    """Raised when session management fails."""


class PlayPiTimeoutError(PlayPiError):
    """Raised when an operation exceeds the specified timeout."""
