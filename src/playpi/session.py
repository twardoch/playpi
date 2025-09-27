# this_file: src/playpi/session.py
"""Browser session management for PlayPi package."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from loguru import logger
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from playpi.config import PlayPiConfig
from playpi.exceptions import BrowserError, SessionError


class PlayPiSession:
    """Manages browser lifecycle and authentication state.

    This class handles browser instances, contexts, and pages for automated
    AI chat workflows. It provides session persistence and proper cleanup.
    """

    def __init__(self, config: PlayPiConfig | None = None) -> None:
        """Initialize session with configuration.

        Args:
            config: Configuration object, uses defaults if None
        """
        self.config = config or PlayPiConfig()
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def __aenter__(self) -> "PlayPiSession":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit with cleanup."""
        await self.close()

    async def start(self) -> None:
        """Start the browser session."""
        if self._playwright is not None:
            logger.warning("Session already started")
            return

        try:
            logger.debug("Starting Playwright")
            self._playwright = await async_playwright().start()

            logger.debug("Launching browser")
            self._browser = await self._playwright.chromium.launch(**self.config.get_browser_launch_options())

            logger.debug("Creating browser context")
            self._context = await self._browser.new_context()

            logger.debug("Creating new page")
            self._page = await self._context.new_page()

            logger.info("Browser session started successfully")

        except Exception as e:
            await self.close()
            msg = f"Failed to start browser session: {e}"
            raise BrowserError(msg) from e

    async def get_page(self) -> Page:
        """Get the current page.

        Returns:
            The current Playwright page instance

        Raises:
            SessionError: If session is not started
        """
        if self._page is None:
            msg = "Session not started. Call start() first."
            raise SessionError(msg)
        return self._page

    async def get_authenticated_page(self, provider: str) -> Page:
        """Get authenticated page for a provider.

        Args:
            provider: Provider name (e.g., 'google')

        Returns:
            Authenticated page for the provider

        Raises:
            SessionError: If session is not started
        """
        page = await self.get_page()

        # Load persistent context/profile for this provider if it exists
        profile_dir = self.config.profiles_dir / provider
        if profile_dir.exists():
            logger.debug(f"Loading profile for {provider} from {profile_dir}")
            # Note: For now, we'll use the default context
            # In a full implementation, we'd create provider-specific contexts

        return page

    async def close(self) -> None:
        """Clean up browser resources."""
        logger.debug("Closing browser session")

        try:
            if self._page:
                logger.debug("Closing page")
                await self._page.close()
                self._page = None

            if self._context:
                logger.debug("Closing context")
                await self._context.close()
                self._context = None

            if self._browser:
                logger.debug("Closing browser")
                await self._browser.close()
                self._browser = None

            if self._playwright:
                logger.debug("Stopping Playwright")
                await self._playwright.stop()
                self._playwright = None

            logger.info("Browser session closed successfully")

        except Exception as e:
            logger.error(f"Error closing browser session: {e}")
            # Don't raise exception during cleanup


@asynccontextmanager
async def create_session(
    config: PlayPiConfig | None = None,
) -> AsyncGenerator[PlayPiSession, None]:
    """Create a PlayPi session with automatic cleanup.

    Args:
        config: Configuration object, uses defaults if None

    Yields:
        PlayPiSession instance

    Example:
        async with create_session() as session:
            page = await session.get_page()
            await page.goto("https://example.com")
    """
    session = PlayPiSession(config)
    try:
        await session.start()
        yield session
    finally:
        await session.close()
