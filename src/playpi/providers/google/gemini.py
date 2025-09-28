"""Google Gemini provider for PlayPi package."""

import asyncio
import os
import pathlib
import shutil
import sys

from loguru import logger
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from playpi.config import PlayPiConfig
from playpi.exceptions import PlayPiTimeoutError, ProviderError
from playpi.html import extract_research_content, html_to_markdown
from playpi.providers.google.auth import ensure_authenticated
from playpi.session import create_session

RESEARCH_CONTENT_MIN_LENGTH = 50_000


async def google_gemini_deep_research(
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
            page = await session.get_page()
            return await _google_gemini_deep_research_on_page(page, prompt, timeout=timeout)

    except PlaywrightTimeoutError as e:
        msg = f"Research timed out after {timeout} seconds"
        raise PlayPiTimeoutError(msg) from e
    except Exception as e:
        logger.error(f"Google Deep Research failed: {e}")
        msg = f"Deep Research failed: {e}"
        raise ProviderError(msg) from e


async def google_gemini_deep_research_full(
    prompt: str | None = None,
    prompt_path: str | pathlib.Path | None = None,
    output_path: str | pathlib.Path | None = None,
    **kwargs,
) -> str | pathlib.Path:
    """Perform Google Gemini Deep Research with full options."""
    if prompt_path:
        with open(prompt_path) as f:
            prompt_from_file = f.read()
        full_prompt = f"{prompt_from_file}\n{prompt}" if prompt else prompt_from_file
    elif prompt:
        full_prompt = prompt
    else:
        msg = "Either 'prompt' or 'prompt_path' must be provided."
        raise ValueError(msg)

    result = await google_gemini_deep_research(full_prompt, **kwargs)

    if output_path:
        with open(output_path, "w") as f:
            f.write(result)
        return pathlib.Path(output_path)
    return result


async def google_gemini_deep_research_multi(config: list[dict], **kwargs):
    """Perform multiple Google Gemini Deep Research tasks concurrently."""
    semaphore = asyncio.Semaphore(3)

    async def run_task(session, task_config):
        async with semaphore:
            page = await session.new_page()
            prompt = task_config.get("prompt")
            prompt_path = task_config.get("prompt_path")
            output_path = task_config.get("output_path")

            if prompt_path:
                with open(prompt_path) as f:
                    prompt_from_file = f.read()
                full_prompt = f"{prompt_from_file}\n{prompt}" if prompt else prompt_from_file
            elif prompt:
                full_prompt = prompt
            else:
                msg = "Either 'prompt' or 'prompt_path' must be provided."
                raise ValueError(msg)

            result = await _google_gemini_deep_research_on_page(page, full_prompt, **kwargs)

            if output_path:
                with open(output_path, "w") as f:
                    f.write(result)
                return pathlib.Path(output_path)
            return result

    async with create_session(PlayPiConfig(**kwargs)) as session:
        tasks = [run_task(session, task_config) for task_config in config]
        return await asyncio.gather(*tasks)


async def _google_gemini_deep_research_on_page(page: Page, prompt: str, **kwargs) -> str:
    """Helper function to run deep research on a specific page."""
    timeout = kwargs.get("timeout", 600)
    # Navigate to Gemini
    logger.info("🌐 Navigating to Gemini...")
    await page.goto("https://gemini.google.com/u/0/app", timeout=30000)

    # Ensure the user is authenticated before interacting with UI
    logger.info("🔐 Checking authentication...")
    await ensure_authenticated(page, timeout)

    # Enter the prompt
    logger.info("✏️ Entering research prompt...")
    await _enter_prompt(page, prompt)

    # Activate Deep Research
    logger.info("🔧 Activating Deep Research mode...")
    await _activate_deep_research(page)

    # Click send button
    logger.info("📤 Submitting research request...")
    await _click_send_button(page)

    # Handle confirmation dialog
    logger.info("✅ Confirming Deep Research parameters...")
    await _handle_confirmation_dialog(page, timeout)

    # Wait for research to complete
    logger.info("🔍 Deep Research in progress - this may take several minutes...")
    await _wait_for_completion(page, timeout)

    # Extract results
    logger.info("📄 Extracting research results...")
    html_content = await extract_research_content(page)
    markdown_result = html_to_markdown(html_content)

    logger.info("✅ Google Deep Research completed successfully!")
    return markdown_result


async def google_gemini_generate_image(prompt: str, **kwargs):
    """Generate an image using Google Gemini."""
    if kwargs.get("verbose", False):
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")

    logger.info(f"Starting Google Gemini Image Generation for: {prompt[:50]}...")

    config = PlayPiConfig(
        headless=kwargs.get("headless", True),
        timeout=kwargs.get("timeout", 600) * 1000,  # Convert to milliseconds for provider waits
        verbose=kwargs.get("verbose", False),
        profile=kwargs.get("profile", "default"),
    )

    try:
        async with create_session(config) as session:
            page = await session.get_authenticated_page("google")

            # Navigate to Gemini
            logger.info("🌐 Navigating to Gemini...")
            await page.goto("https://gemini.google.com/u/0/app", timeout=30000)

            # Ensure the user is authenticated before interacting with UI
            logger.info("🔐 Checking authentication...")
            await ensure_authenticated(page, config.timeout)

            # Activate Image Generation
            logger.info("🎨 Activating Image Generation mode...")
            await _activate_image_generation(page)

            # Enter the prompt
            logger.info("✏️ Entering image prompt...")
            await _enter_prompt(page, prompt)

            # Click send button
            logger.info("📤 Submitting image request...")
            await _click_send_button(page)

            # Wait for image to be generated
            logger.info("🖼️ Image generation in progress...")
            await _wait_for_image_generation(page, config.timeout)

            # Download the image
            logger.info("⬇️ Downloading generated image...")
            download_path = kwargs.get("download_path", ".")
            downloaded_image_path = await _download_generated_image(page, download_path)

            logger.info(
                f"✅ Google Gemini Image Generation completed successfully! Image saved to: {downloaded_image_path}"
            )
            return downloaded_image_path

    except PlaywrightTimeoutError as e:
        msg = f"Image generation timed out after {config.timeout / 1000} seconds"
        raise PlayPiTimeoutError(msg) from e
    except Exception as e:
        logger.error(f"Google Gemini Image Generation failed: {e}")
        msg = f"Image Generation failed: {e}"
        raise ProviderError(msg) from e


async def _activate_image_generation(page: Page) -> None:
    """Activate the Image Generation tool."""
    try:
        logger.debug("Clicking Tools button to open toolbox")
        tools_button = page.get_by_role("button", name="Tools")
        await tools_button.wait_for(state="visible", timeout=10000)
        await tools_button.click()

        await asyncio.sleep(2)

        logger.debug("Looking for Image Generation button in dropdown")
        image_gen_button = page.locator("button:has-text('Create images')").first
        await image_gen_button.wait_for(state="visible", timeout=10000)
        await image_gen_button.click()
        logger.debug("Image Generation button clicked")

        await asyncio.sleep(2)

    except Exception as e:
        msg = f"Failed to activate Image Generation: {e}"
        raise ProviderError(msg) from e


async def _wait_for_image_generation(page: Page, timeout: int) -> None:
    """Wait for the image to be generated."""
    try:
        download_button = page.locator('[data-test-id="download-generated-image-button"]')
        await download_button.wait_for(state="visible", timeout=timeout)
    except Exception as e:
        msg = f"Failed to wait for image generation: {e}"
        raise ProviderError(msg) from e


async def _download_generated_image(page: Page, download_path: str) -> str:
    """Download the generated image."""
    downloads_dir = str(pathlib.Path.home() / "Downloads")
    # Get list of files before download
    files_before = os.listdir(downloads_dir)

    download_button = page.locator('[data-test-id="download-generated-image-button"]').first
    await download_button.click()

    # Wait for a short period to allow the download to complete
    await asyncio.sleep(5)

    # Get list of files after download
    files_after = os.listdir(downloads_dir)

    # Find the new file
    new_files = [f for f in files_after if f not in files_before]
    if not new_files:
        msg = "Could not find downloaded image."
        raise ProviderError(msg)

    newest_file = max([os.path.join(downloads_dir, f) for f in new_files], key=os.path.getctime)

    # Move the file to the destination
    destination_path = os.path.join(download_path, os.path.basename(newest_file))
    shutil.move(newest_file, destination_path)

    return destination_path


async def google_gemini_ask_deep_think(prompt: str, **kwargs):
    """Perform a deep think using Google Gemini."""
    if kwargs.get("verbose", False):
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")

    logger.info(f"Starting Google Gemini Deep Think for: {prompt[:50]}...")

    config = PlayPiConfig(
        headless=kwargs.get("headless", True),
        timeout=kwargs.get("timeout", 600) * 1000,  # Convert to milliseconds for provider waits
        verbose=kwargs.get("verbose", False),
        profile=kwargs.get("profile", "default"),
    )

    try:
        async with create_session(config) as session:
            page = await session.get_authenticated_page("google")

            # Navigate to Gemini
            logger.info("🌐 Navigating to Gemini...")
            await page.goto("https://gemini.google.com/u/0/app", timeout=30000)

            # Ensure the user is authenticated before interacting with UI
            logger.info("🔐 Checking authentication...")
            await ensure_authenticated(page, config.timeout)

            # Activate Deep Think
            logger.info("🤔 Activating Deep Think mode...")
            await _activate_deep_think(page)

            # Enter the prompt
            logger.info("✏️ Entering deep think prompt...")
            await _enter_prompt(page, prompt)

            # Click send button
            logger.info("📤 Submitting deep think request...")
            await _click_send_button(page)

            # Wait for completion
            logger.info("🤔 Deep Think in progress...")
            await _wait_for_completion(page, config.timeout)

            # Extract results
            logger.info("📄 Extracting deep think results...")
            html_content = await extract_research_content(page)
            markdown_result = html_to_markdown(html_content)

            logger.info("✅ Google Gemini Deep Think completed successfully!")
            return markdown_result

    except PlaywrightTimeoutError as e:
        msg = f"Deep think timed out after {config.timeout / 1000} seconds"
        raise PlayPiTimeoutError(msg) from e
    except Exception as e:
        logger.error(f"Google Gemini Deep Think failed: {e}")
        msg = f"Deep Think failed: {e}"
        raise ProviderError(msg) from e


async def _activate_deep_think(page: Page) -> None:
    """Activate the Deep Think tool."""
    try:
        logger.debug("Clicking Tools button to open toolbox")
        tools_button = page.get_by_role("button", name="Tools")
        await tools_button.wait_for(state="visible", timeout=10000)
        await tools_button.click()

        await asyncio.sleep(2)

        logger.debug("Looking for Deep Think button in dropdown")
        deep_think_button = page.locator("button:has-text('Deep Think')").first
        await deep_think_button.wait_for(state="visible", timeout=10000)
        await deep_think_button.click()
        logger.debug("Deep Think button clicked")

        await asyncio.sleep(2)

    except Exception as e:
        msg = f"Failed to activate Deep Think: {e}"
        raise ProviderError(msg) from e


async def google_gemini_ask(prompt: str, **kwargs):
    """Ask a simple question to Google Gemini."""
    if kwargs.get("verbose", False):
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")

    logger.info(f"Asking Gemini: {prompt[:50]}...")

    config = PlayPiConfig(
        headless=kwargs.get("headless", True),
        timeout=kwargs.get("timeout", 600) * 1000,  # Convert to milliseconds for provider waits
        verbose=kwargs.get("verbose", False),
        profile=kwargs.get("profile", "default"),
    )

    try:
        async with create_session(config) as session:
            page = await session.get_authenticated_page("google")

            # Navigate to Gemini
            logger.info("🌐 Navigating to Gemini...")
            await page.goto("https://gemini.google.com/app", timeout=30000)

            # Ensure the user is authenticated before interacting with UI
            logger.info("🔐 Checking authentication...")
            await ensure_authenticated(page, config.timeout)

            # Enter the prompt
            logger.info("✏️ Entering prompt...")
            await _enter_prompt(page, prompt)

            # Click send button
            logger.info("📤 Submitting prompt...")
            await _click_send_button(page)

            # Wait for completion
            logger.info("🤔 Waiting for response...")
            await _wait_for_completion(page, config.timeout)

            # Extract results
            logger.info("📄 Extracting response...")
            markdown_result = await _extract_simple_response(page)

            logger.info("✅ Gemini responded successfully!")
            return markdown_result

    except PlaywrightTimeoutError as e:
        msg = f"Gemini timed out after {config.timeout / 1000} seconds"
        raise PlayPiTimeoutError(msg) from e
    except Exception as e:
        logger.error(f"Gemini request failed: {e}")
        msg = f"Gemini request failed: {e}"
        raise ProviderError(msg) from e


async def _extract_simple_response(page: Page) -> str:
    """Extract the simple response from the page."""
    try:
        response_elements = page.locator("response-element")
        await response_elements.last.wait_for(state="visible", timeout=10000)
        html_content = await response_elements.last.inner_html()
        return html_to_markdown(html_content)
    except Exception as e:
        msg = f"Failed to extract simple response: {e}"
        raise ProviderError(msg) from e


async def _enter_prompt(page: Page, prompt: str) -> None:
    """Enter the research prompt in the text area."""
    try:
        logger.debug("Looking for prompt input field")

        # Try multiple selectors for the text input to be more robust
        text_input = None
        selectors = [
            'role=textbox[name="Enter a prompt here"]',
            '[role="textbox"]',
            ".text-input-field_textarea .ql-editor",
            "rich-textarea .ql-editor",
        ]

        for selector in selectors:
            try:
                text_input = page.locator(selector).first
                await text_input.wait_for(state="visible", timeout=5000)
                logger.debug(f"Found text input using selector: {selector}")
                break
            except PlaywrightTimeoutError:
                continue

        if text_input is None:
            # Fallback to role-based selector with longer timeout
            text_input = page.get_by_role("textbox", name="Enter a prompt here")
            await text_input.wait_for(state="visible", timeout=10000)
            logger.debug("Found text input using role-based selector")

        # Click and fill immediately
        logger.debug("Clicking text input and entering prompt")
        await text_input.click()
        await text_input.fill(prompt)

        logger.debug(f"Prompt entered successfully: {prompt[:100]}...")

    except Exception as e:
        msg = f"Failed to enter prompt: {e}"
        raise ProviderError(msg) from e


async def _activate_deep_research(page: Page) -> None:
    """Activate the Deep Research tool."""
    try:
        logger.debug("Clicking Tools button to open toolbox")
        # Click the Tools button
        tools_button = page.get_by_role("button", name="Tools")
        await tools_button.wait_for(state="visible", timeout=10000)
        await tools_button.click()

        # Wait for the dropdown to appear
        await asyncio.sleep(2)

        logger.debug("Looking for Deep Research button in dropdown")
        # First try the specific CSS selector you provided
        deep_research_button = page.locator(
            "#cdk-overlay-0 > mat-card > mat-action-list > toolbox-drawer-item:nth-child(1) > button"
        )

        # Check if this is actually the Deep Research button
        try:
            await deep_research_button.wait_for(state="visible", timeout=5000)
            button_text = await deep_research_button.text_content()
            logger.debug(f"First button text: '{button_text}'")

            if not button_text or "Deep Research" not in button_text:
                logger.debug("First button is not Deep Research, searching within overlay")
                # Find Deep Research button within the overlay
                overlay = page.locator("#cdk-overlay-0 > mat-card")
                deep_research_button = overlay.locator("toolbox-drawer-item button:has-text('Deep Research')").first

        except Exception:
            logger.debug("Direct selector failed, using overlay search")
            # Fallback: find Deep Research button within the overlay
            overlay = page.locator("#cdk-overlay-0 > mat-card")
            deep_research_button = overlay.locator("toolbox-drawer-item button:has-text('Deep Research')").first

        # Wait for it to be visible and clickable
        await deep_research_button.wait_for(state="visible", timeout=10000)
        logger.debug("Deep Research button found and visible")

        # Click the Deep Research button
        await deep_research_button.click()
        logger.debug("Deep Research button clicked")

        # Wait a moment for the selection to take effect
        await asyncio.sleep(2)

        # Check if Deep Research is now selected by looking for the deselect button
        try:
            deselect_button = page.locator('button[aria-label*="Deselect Deep Research"]')
            if await deselect_button.count() > 0:
                logger.debug("Deep Research successfully activated (deselect button found)")
            else:
                # Alternative check - look for the toolbox showing Deep Research as selected
                selected_indicator = page.locator("toolbox-drawer").locator(':has-text("Deep Research")')
                if await selected_indicator.count() > 0:
                    logger.debug("Deep Research appears to be selected")
                else:
                    logger.warning("Could not confirm Deep Research activation, but continuing")
        except Exception as e:
            logger.debug(f"Could not verify Deep Research activation: {e}, continuing anyway")

        logger.debug("Deep Research activation completed")

    except Exception as e:
        msg = f"Failed to activate Deep Research: {e}"
        raise ProviderError(msg) from e


async def _click_send_button(page: Page) -> None:
    """Click the send button to submit the research query."""
    try:
        logger.debug("Looking for send button")
        # Look for send button inside .send-button-container or use the role-based selector
        send_button = page.locator('.send-button-container button[data-test-id="send-button"]')

        if await send_button.count() == 0:
            # Fallback to role-based selector
            send_button = page.get_by_role("button", name="Send message")

        await send_button.wait_for(state="visible", timeout=10000)
        logger.debug("Clicking send button")
        await send_button.click()
        logger.debug("Send button clicked successfully")

    except Exception as e:
        msg = f"Failed to click send button: {e}"
        raise ProviderError(msg) from e


async def _handle_confirmation_dialog(page: Page, timeout: int) -> None:
    """Handle the Deep Research confirmation dialog (works with localized text)."""
    try:
        logger.debug("Waiting for deep-research-confirmation-widget to appear")
        # Wait for confirmation widget to appear - be more generous with timeout
        confirmation_widget = page.locator("deep-research-confirmation-widget")
        await confirmation_widget.wait_for(state="visible", timeout=20000)  # Increased timeout

        logger.debug("Confirmation widget found, looking for confirm button")
        # Click the confirmation button using data-test-id (language-independent)
        confirm_button = confirmation_widget.locator('[data-test-id="confirm-button"]')
        await confirm_button.wait_for(state="visible", timeout=10000)

        # Get button text for logging (helps with debugging localization)
        button_text = await confirm_button.text_content()
        logger.debug(f"Found confirmation button with text: '{button_text}'")

        logger.debug("Clicking confirmation button")
        await confirm_button.click(force=True)  # Use force click to ensure it works
        logger.debug("Deep Research confirmation clicked successfully")

        # Wait a moment to ensure the click was processed
        await asyncio.sleep(1)

    except PlaywrightTimeoutError:
        logger.debug("No confirmation dialog appeared within timeout, continuing")
    except Exception as e:
        logger.warning(f"Error handling confirmation dialog: {e}, continuing anyway")
        # Don't raise error here as the confirmation dialog might not always appear


async def _wait_for_completion(page: Page, timeout: int) -> None:
    """Wait for Deep Research to complete and final Markdown response to be ready."""
    try:
        # Wait for the export button or similar completion indicator
        completion_indicators = [
            '[data-test-id="export-menu-button"]',
            'button:has-text("Export")',
            'button:has-text("Copy")',
            '[data-test-id="scroll-container"]',
        ]

        logger.info(f"⏱️ Monitoring Deep Research progress (timeout: {timeout}s)...")
        completion_found = False
        start_time = asyncio.get_running_loop().time()
        last_progress_time = start_time

        # Progress monitoring loop
        while not completion_found and (asyncio.get_running_loop().time() - start_time) < timeout:
            current_time = asyncio.get_running_loop().time()
            elapsed = current_time - start_time

            # Report progress every 30 seconds
            if current_time - last_progress_time >= 30:
                logger.info(f"📊 Deep Research still in progress... ({elapsed:.0f}s elapsed)")
                last_progress_time = current_time

                # Check for research steps or progress indicators
                try:
                    # Look for research step indicators
                    steps = page.locator('[data-test-id="research-steps"] .research-step')
                    step_count = await steps.count()
                    if step_count > 0:
                        logger.info(f"📝 Research plan has {step_count} steps")

                    # Check for any progress messages
                    progress_msgs = page.locator(':has-text("Klaar over"), :has-text("Ready in"), :has-text("Done in")')
                    if await progress_msgs.count() > 0:
                        msg_text = await progress_msgs.first.text_content()
                        logger.info(f"⏰ Status: {msg_text}")

                except Exception:
                    pass  # Progress checking is best effort

            # Check for completion indicators
            for indicator in completion_indicators:
                try:
                    if await page.locator(indicator).is_visible():
                        logger.info(f"🎯 Research completion detected: {indicator}")
                        completion_found = True
                        break
                except Exception:
                    continue

            if not completion_found:
                await asyncio.sleep(5)  # Check every 5 seconds

        if not completion_found:
            logger.info("⏳ No completion indicators found, checking content-based completion...")
            # Check if there's substantial content on the page
            content_length = len(await page.content())
            logger.info(f"📏 Page content length: {content_length} characters")

            if content_length > RESEARCH_CONTENT_MIN_LENGTH:
                logger.info("✅ Research appears complete based on content length")
                completion_found = True

        # Give additional time for the final response to fully render
        if completion_found:
            logger.info("🔄 Waiting for final response to render...")
            await asyncio.sleep(5)  # Allow time for final response to render
        else:
            msg = f"Deep Research did not complete within {timeout} seconds"
            raise PlayPiTimeoutError(msg)

        logger.info("✅ Deep Research completion wait finished")

    except Exception as e:
        if isinstance(e, PlayPiTimeoutError):
            raise
        msg = f"Error waiting for research completion: {e}"
        raise ProviderError(msg) from e
