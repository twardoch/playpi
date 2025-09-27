# this_file: src/playpi/config.py
"""Lightweight configuration helpers for PlayPi.

The PlayPi package now relies on the `playwrightauthor` project for browser
lifecycle management.  The former configuration surface that mirrored raw
Playwright options has been simplified to expose only the parameters that map to
playwrightauthor's public API while retaining backwards-compatible attributes
where feasible.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PlayPiConfig:
    """User-adjustable settings for PlayPi sessions.

    Attributes:
        headless: Retained for compatibility; playwrightauthor always launches
            Chrome in headed mode so this flag is currently ignored.
        timeout: Default timeout in milliseconds for PlayPi operations (not for
            browser launch).  Individual providers convert from seconds when
            necessary.
        verbose: When ``True`` PlayPi asks playwrightauthor to emit detailed
            diagnostic logs.
        profile: Named profile handled by playwrightauthor; allows multiple
            authenticated browser states.
    """

    headless: bool = True
    timeout: int = 30_000
    verbose: bool = False
    profile: str = "default"

    def playwrightauthor_kwargs(self) -> dict[str, object]:
        """Return keyword arguments accepted by playwrightauthor context managers."""
        return {"verbose": self.verbose, "profile": self.profile}
