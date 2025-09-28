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
from playpi.providers import (
    google_gemini_ask,
    google_gemini_ask_deep_think,
    google_gemini_deep_research,
    google_gemini_deep_research_full,
    google_gemini_deep_research_multi,
    google_gemini_generate_image,
)

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
    "google_gemini_ask",
    "google_gemini_ask_deep_think",
    "google_gemini_deep_research",
    "google_gemini_deep_research_full",
    "google_gemini_deep_research_multi",
    "google_gemini_generate_image",
]
