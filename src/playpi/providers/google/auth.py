"""Google authentication for PlayPi."""

import asyncio

from loguru import logger
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from playpi.exceptions import AuthenticationError


async def ensure_authenticated(page: Page, timeout: int) -> None:
    """Prompt the user to authenticate with Gemini if required.

    Args:
        page: Active Playwright page.
        timeout: Overall research timeout (seconds). Login wait is capped.
    """

    login_deadline = asyncio.get_running_loop().time() + min(timeout, 60)
    prompt_displayed = False

    while True:
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)  # Reduced timeout
        except PlaywrightTimeoutError:
            logger.debug("Waiting for Gemini load state timed out; checking for chat interface")
            # Continue probing authentication state

        if await has_chat_interface(page):
            logger.info("✅ Authentication verified - chat interface available")
            return

        current_url = page.url
        if not prompt_displayed:
            logger.info(
                "🔐 Please complete login in the browser window. "
                "Automation will continue once the chat interface appears..."
            )
            prompt_displayed = True

        if "accounts.google.com" in current_url or "signin" in current_url:
            logger.info("🔑 Google sign-in page detected - waiting for authentication...")

        if asyncio.get_running_loop().time() > login_deadline:
            msg = "Gemini chat interface not found after waiting for login."
            raise AuthenticationError(msg)

        await asyncio.sleep(1)  # Reduced sleep time for faster checks


async def has_chat_interface(page: Page) -> bool:
    """Return True if the Gemini chat textbox is present."""

    try:
        chat_input = page.locator('[role="textbox"]').first
        return await chat_input.count() > 0
    except Exception as exc:  # pragma: no cover - locator lookup is best-effort
        logger.debug(f"Chat interface probe failed: {exc}")
        return False
