# this_file: src/playpi/providers/google.py
"""Google Gemini provider for PlayPi package."""

import asyncio
import sys

from loguru import logger
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from playpi.config import PlayPiConfig
from playpi.exceptions import AuthenticationError, PlayPiTimeoutError, ProviderError
from playpi.html import extract_research_content, html_to_markdown
from playpi.session import create_session

RESEARCH_CONTENT_MIN_LENGTH = 50_000


async def google_deep_research(
    prompt: str,
    *,
    headless: bool = True,
    timeout: int = 600,
    profile: str | None = None,
    verbose: bool = False,
) -> str:
    """Perform Google Gemini Deep Research.

    Args:
        prompt: Research query
        headless: Retained for compatibility. playwrightauthor currently operates
            Chrome in headed mode, so this flag is ignored.
        timeout: Maximum wait time in seconds
        profile: Browser profile name for authentication (unused for now)
        verbose: Enable verbose logging

    Returns:
        Research result as Markdown string

    Raises:
        AuthenticationError: If Google authentication fails
        PlayPiTimeoutError: If research exceeds timeout
        ProviderError: If UI elements not found
    """
    if verbose:
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")

    logger.info(f"Starting Google Deep Research for: {prompt[:50]}...")

    if headless:
        logger.debug("playwrightauthor runs in headed mode; ignoring headless=True request")

    config = PlayPiConfig(
        headless=headless,
        timeout=timeout * 1000,  # Convert to milliseconds for provider waits
        verbose=verbose,
        profile=profile or "default",
    )

    try:
        async with create_session(config) as session:
            page = await session.get_authenticated_page("google")

            # Navigate to Gemini
            logger.debug("Navigating to Gemini")
            await page.goto("https://gemini.google.com/u/0/app", timeout=30000)

            # Ensure the user is authenticated before interacting with UI
            await _ensure_authenticated(page, timeout)

            # Enter the prompt
            logger.debug("Entering prompt")
            await _enter_prompt(page, prompt)

            # Activate Deep Research
            logger.debug("Activating Deep Research")
            await _activate_deep_research(page)

            # Submit the research
            logger.debug("Submitting research")
            await _submit_research(page, timeout)

            # Wait for research to complete
            logger.debug("Waiting for research completion")
            await _wait_for_completion(page, timeout)

            # Extract results
            logger.debug("Extracting results")
            html_content = await extract_research_content(page)
            markdown_result = html_to_markdown(html_content)

            logger.info("Google Deep Research completed successfully")
            return markdown_result

    except PlaywrightTimeoutError as e:
        msg = f"Research timed out after {timeout} seconds"
        raise PlayPiTimeoutError(msg) from e
    except Exception as e:
        logger.error(f"Google Deep Research failed: {e}")
        msg = f"Deep Research failed: {e}"
        raise ProviderError(msg) from e


async def _ensure_authenticated(page: Page, timeout: int) -> None:
    """Prompt the user to authenticate with Gemini if required.

    Args:
        page: Active Playwright page.
        timeout: Overall research timeout (seconds). Login wait is capped.
    """

    login_deadline = asyncio.get_running_loop().time() + min(timeout, 60)
    prompt_displayed = False

    while True:
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except PlaywrightTimeoutError:
            logger.debug("Waiting for Gemini load state timed out; retrying")
            # Continue probing authentication state

        if await _has_chat_interface(page):
            return

        current_url = page.url
        if not prompt_displayed:
            logger.warning(
                "Gemini chat interface not available. Please complete the login "
                "flow in the open Chrome window. Once the chat input appears, "
                "the automation will continue automatically."
            )
            prompt_displayed = True

        if "accounts.google.com" in current_url or "signin" in current_url:
            logger.info("Gemini redirected to Google sign-in page; waiting for login...")

        if asyncio.get_running_loop().time() > login_deadline:
            msg = "Gemini chat interface not found after waiting for login."
            raise AuthenticationError(msg)

        await asyncio.sleep(2)


async def _has_chat_interface(page: Page) -> bool:
    """Return True if the Gemini chat textbox is present."""

    try:
        chat_input = page.locator('[role="textbox"]').first
        return await chat_input.count() > 0
    except Exception as exc:  # pragma: no cover - locator lookup is best-effort
        logger.debug(f"Chat interface probe failed: {exc}")
        return False


async def _enter_prompt(page: Page, prompt: str) -> None:
    """Enter the research prompt in the text area."""
    try:
        # Wait for and click on the text input area
        text_input = page.get_by_role("textbox", name="Enter a prompt here")
        await text_input.wait_for(state="visible", timeout=15000)
        await text_input.click()

        # Clear any existing text and enter the prompt
        await text_input.fill(prompt)

        logger.debug(f"Entered prompt: {prompt[:100]}...")

    except Exception as e:
        msg = f"Failed to enter prompt: {e}"
        raise ProviderError(msg) from e


async def _activate_deep_research(page: Page) -> None:
    """Activate the Deep Research tool."""
    try:
        # Click the Tools button
        tools_button = page.get_by_role("button", name="Tools")
        await tools_button.wait_for(state="visible", timeout=10000)
        await tools_button.click()

        # Wait a moment for the menu to appear
        await asyncio.sleep(1)

        # Wait for the drawer overlay to appear so we scope our selector correctly
        # and avoid matching historical "Deep Research" messages.
        drawer_overlay = page.locator("mat-card:has(toolbox-drawer)")
        await drawer_overlay.wait_for(state="visible", timeout=10000)

        toolbox_drawer = drawer_overlay.locator("toolbox-drawer")
        deep_research_button = toolbox_drawer.locator(
            "toolbox-drawer-item button[mat-list-item]:has-text('Deep Research')"
        )

        if await deep_research_button.count() == 0:
            deep_research_button = toolbox_drawer.locator(
                "toolbox-drawer-item button:has(.label:has-text('Deep Research'))"
            )

        button = deep_research_button.first
        await button.wait_for(state="visible", timeout=10000)
        await button.click()

        # Some localizations toggle aria-pressed after a short delay. Waiting keeps
        # us from submitting before Deep Research mode is active.
        try:
            await page.wait_for_function(
                "el => el.getAttribute('aria-pressed') === 'true'",
                arg=button,
                timeout=2000,
            )
        except PlaywrightTimeoutError:
            logger.debug("Deep Research button did not toggle aria-pressed in time")

        logger.debug("Deep Research activated")

    except Exception as e:
        msg = f"Failed to activate Deep Research: {e}"
        raise ProviderError(msg) from e


async def _submit_research(page: Page, timeout: int) -> None:
    """Submit the research query."""
    try:
        # Click the send button
        send_button = page.get_by_role("button", name="Send message")
        await send_button.wait_for(state="visible", timeout=10000)
        await send_button.click()

        # Wait for and click the confirmation button if it appears
        try:
            confirmation_widget = page.locator("deep-research-confirmation-widget")
            await confirmation_widget.wait_for(state="visible", timeout=timeout * 1000)

            confirm_button = confirmation_widget.locator('[data-test-id="confirm-button"]')
            await confirm_button.wait_for(state="visible", timeout=timeout * 1000)
            await confirm_button.click()
            logger.debug("Clicked research confirmation")
        except Exception:
            logger.debug("No confirmation dialog found, continuing")

    except Exception as e:
        msg = f"Failed to submit research: {e}"
        raise ProviderError(msg) from e


async def _wait_for_completion(page: Page, timeout: int) -> None:
    """Wait for research to complete."""
    try:
        # Wait for the export button or similar completion indicator
        completion_indicators = [
            '[data-test-id="export-menu-button"]',
            'button:has-text("Export")',
            'button:has-text("Copy")',
            '[data-test-id="scroll-container"]',
        ]

        logger.debug(f"Waiting up to {timeout} seconds for research completion")

        for indicator in completion_indicators:
            try:
                await page.locator(indicator).wait_for(state="visible", timeout=timeout * 1000)
                logger.debug(f"Research completed - found indicator: {indicator}")
                return
            except TimeoutError:
                continue

        # If no specific indicator found, wait for a reasonable time
        # and check if content has loaded
        await asyncio.sleep(min(30, timeout // 2))

        # Check if there's substantial content on the page
        content_length = len(await page.content())
        if content_length > RESEARCH_CONTENT_MIN_LENGTH:
            logger.debug("Research appears complete based on content length")
            return

        msg = f"Research did not complete within {timeout} seconds"
        raise PlayPiTimeoutError(msg)

    except Exception as e:
        if isinstance(e, PlayPiTimeoutError):
            raise
        msg = f"Error waiting for research completion: {e}"
        raise ProviderError(msg) from e
