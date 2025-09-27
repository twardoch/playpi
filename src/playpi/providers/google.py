# this_file: src/playpi/providers/google.py
"""Google Gemini provider for PlayPi package."""

import asyncio
from typing import Optional

from loguru import logger
from playwright.async_api import Page, TimeoutError

from playpi.config import PlayPiConfig
from playpi.exceptions import AuthenticationError, PlayPiTimeoutError, ProviderError
from playpi.html import extract_research_content, html_to_markdown
from playpi.session import create_session


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
        headless: Run browser in headless mode
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
        logger.add(lambda msg: print(msg, end=""), level="DEBUG")

    logger.info(f"Starting Google Deep Research for: {prompt[:50]}...")

    config = PlayPiConfig(
        headless=headless,
        timeout=timeout * 1000,  # Convert to milliseconds
        verbose=verbose,
    )

    try:
        async with create_session(config) as session:
            page = await session.get_authenticated_page("google")

            # Navigate to Gemini
            logger.debug("Navigating to Gemini")
            await page.goto("https://gemini.google.com/u/0/app", timeout=30000)

            # Check if we need authentication
            await _check_authentication(page)

            # Enter the prompt
            logger.debug("Entering prompt")
            await _enter_prompt(page, prompt)

            # Activate Deep Research
            logger.debug("Activating Deep Research")
            await _activate_deep_research(page)

            # Submit the research
            logger.debug("Submitting research")
            await _submit_research(page)

            # Wait for research to complete
            logger.debug("Waiting for research completion")
            await _wait_for_completion(page, timeout)

            # Extract results
            logger.debug("Extracting results")
            html_content = await extract_research_content(page)
            markdown_result = html_to_markdown(html_content)

            logger.info("Google Deep Research completed successfully")
            return markdown_result

    except TimeoutError as e:
        msg = f"Research timed out after {timeout} seconds"
        raise PlayPiTimeoutError(msg) from e
    except Exception as e:
        logger.error(f"Google Deep Research failed: {e}")
        msg = f"Deep Research failed: {e}"
        raise ProviderError(msg) from e


async def _check_authentication(page: Page) -> None:
    """Check if user is authenticated with Google."""
    try:
        # Wait a moment for page to load
        await page.wait_for_load_state("networkidle", timeout=10000)

        # Check for login indicators
        current_url = page.url
        if "accounts.google.com" in current_url or "signin" in current_url:
            msg = "Not authenticated with Google. Please log in to Google/Gemini first."
            raise AuthenticationError(msg)

        # Check for the main chat interface
        chat_input = page.locator('[role="textbox"]').first
        if await chat_input.count() == 0:
            msg = "Gemini chat interface not found. Please ensure you're logged in."
            raise AuthenticationError(msg)

    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        msg = f"Failed to check authentication: {e}"
        raise ProviderError(msg) from e


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

        # Click Deep Research option
        deep_research_button = page.get_by_role("button", name="Deep Research")
        await deep_research_button.wait_for(state="visible", timeout=10000)
        await deep_research_button.click()

        logger.debug("Deep Research activated")

    except Exception as e:
        msg = f"Failed to activate Deep Research: {e}"
        raise ProviderError(msg) from e


async def _submit_research(page: Page) -> None:
    """Submit the research query."""
    try:
        # Click the send button
        send_button = page.get_by_role("button", name="Send message")
        await send_button.wait_for(state="visible", timeout=10000)
        await send_button.click()

        # Wait for and click the confirmation button if it appears
        try:
            confirm_button = page.locator('[data-test-id="confirm-button"]')
            await confirm_button.wait_for(state="visible", timeout=15000)
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
        if content_length > 50000:  # Arbitrary threshold for "substantial content"
            logger.debug("Research appears complete based on content length")
            return

        msg = f"Research did not complete within {timeout} seconds"
        raise PlayPiTimeoutError(msg)

    except Exception as e:
        if isinstance(e, PlayPiTimeoutError):
            raise
        msg = f"Error waiting for research completion: {e}"
        raise ProviderError(msg) from e
