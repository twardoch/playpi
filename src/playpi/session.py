# this_file: src/playpi/session.py
"""Browser session management built on top of playwrightauthor."""

from __future__ import annotations

import typing
from contextlib import AsyncExitStack, asynccontextmanager
from typing import TYPE_CHECKING, Self

from loguru import logger
from playwrightauthor import AsyncBrowser
from playwrightauthor.exceptions import PlaywrightAuthorError

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, Page

from playpi.config import PlayPiConfig
from playpi.exceptions import BrowserError, SessionError


class PlayPiSession:
    """Manage a single PlayPi browser session via playwrightauthor."""

    def __init__(self, config: PlayPiConfig | None = None) -> None:
        self.config = config or PlayPiConfig()
        self._exit_stack: AsyncExitStack | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._context_owned = False
        self._pages: list[Page] = []

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def start(self) -> None:
        """Launch browser resources using playwrightauthor."""
        if self._exit_stack is not None:
            logger.warning("Session already started")
            return

        self._exit_stack = AsyncExitStack()
        try:
            logger.debug("Starting playwrightauthor AsyncBrowser")
            async_browser = AsyncBrowser(**self.config.playwrightauthor_kwargs())
            browser = await self._exit_stack.enter_async_context(async_browser)
            self._browser = browser

            logger.debug("Creating playwright context")
            contexts = browser.contexts
            logger.debug(f"Existing browser contexts detected: {len(contexts)}")
            if contexts:
                context = contexts[0]
                self._context_owned = False
            else:
                context = await browser.new_context()
                self._exit_stack.push_async_callback(context.close)
                self._context_owned = True
            self._context = context

            await self.new_page()

            logger.info("PlayPi session started")
        except PlaywrightAuthorError as exc:  # pragma: no cover - bubble up descriptive message
            await self.close()
            msg = f"Failed to start playwrightauthor session: {exc}"
            raise BrowserError(msg) from exc
        except Exception as exc:  # pragma: no cover - safeguard for unexpected errors
            await self.close()
            msg = f"Failed to start browser session: {exc}"
            raise BrowserError(msg) from exc

    async def new_page(self) -> Page:
        """Create and return a new page."""
        if self._context is None or self._exit_stack is None:
            message = "Session not started. Call start() first."
            raise SessionError(message)

        logger.debug("Opening new page")
        page = await self._context.new_page()
        await page.bring_to_front()
        self._exit_stack.push_async_callback(page.close)
        self._pages.append(page)
        return page

    async def get_page(self) -> Page:
        """Return the active Playwright page."""
        if not self._pages:
            message = "Session not started or no pages available. Call start() or new_page() first."
            raise SessionError(message)
        return self._pages[-1]

    async def get_authenticated_page(self, _provider: str) -> Page:
        """Return an authenticated page for the requested provider.

        playwrightauthor manages profiles internally; an explicit provider value is
        currently unused but retained for compatibility with the public API.
        """
        return await self.get_page()

    async def close(self) -> None:
        """Tear down all managed resources."""
        try:
            if self._exit_stack is not None:
                await self._exit_stack.aclose()
        finally:
            self._exit_stack = None
            self._browser = None
            self._context = None
            self._context_owned = False
            self._pages = []
            logger.info("PlayPi session closed")


@asynccontextmanager
async def create_session(
    config: PlayPiConfig | None = None,
) -> typing.AsyncGenerator[PlayPiSession]:
    """Convenience async context manager for PlayPi sessions."""
    session = PlayPiSession(config)
    try:
        await session.start()
        yield session
    finally:
        await session.close()
