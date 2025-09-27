# this_file: src/playpi/__init__.py
"""PlayPi: Automate AI chat workflows through browser automation.

This package provides simple, high-level functions for automating browser-based
AI chat workflows, starting with Google Gemini Deep Research.
"""

from importlib.metadata import version

from playpi.exceptions import (
    AuthenticationError,
    BrowserError,
    PlayPiError,
    PlayPiTimeoutError,
    ProviderError,
    SessionError,
)
from playpi.providers.google import google_deep_research

try:
    __version__ = version("playpi")
except Exception:
    __version__ = "unknown"

__all__ = [
    "AuthenticationError",
    "BrowserError",
    "PlayPiError",
    "PlayPiTimeoutError",
    "ProviderError",
    "SessionError",
    "__version__",
    "google_deep_research",
]
