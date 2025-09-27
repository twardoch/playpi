# this_file: src/playpi/exceptions.py
"""Custom exceptions for PlayPi package."""


class PlayPiError(Exception):
    """Base exception for all PlayPi errors."""

    pass


class BrowserError(PlayPiError):
    """Raised when browser automation fails."""

    pass


class AuthenticationError(PlayPiError):
    """Raised when authentication with a provider fails."""

    pass


class ProviderError(PlayPiError):
    """Raised when a provider-specific operation fails."""

    pass


class SessionError(PlayPiError):
    """Raised when session management fails."""

    pass


class PlayPiTimeoutError(PlayPiError):
    """Raised when an operation exceeds the specified timeout."""

    pass
