# this_file: src/playpi/html.py
"""HTML processing utilities for PlayPi package."""

import html2text
from loguru import logger
from playwright.async_api import Page


def html_to_markdown(html_content: str) -> str:
    """Convert HTML content to clean Markdown.

    Args:
        html_content: Raw HTML content

    Returns:
        Clean Markdown text
    """
    # Configure html2text for clean output
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0  # Don't wrap lines
    h.unicode_snob = True
    h.skip_internal_links = True

    # Convert to markdown
    markdown = h.handle(html_content)

    # Clean up the markdown
    lines = markdown.split("\n")
    cleaned_lines = []

    for raw_line in lines:
        # Remove excessive whitespace
        line = raw_line.strip()
        # Skip empty lines in sequences
        if line or (cleaned_lines and cleaned_lines[-1]):
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


async def extract_research_content(page: Page) -> str:
    """Extract research content from Google Gemini Deep Research page.

    Args:
        page: Playwright page instance

    Returns:
        Extracted HTML content
    """
    try:
        # Wait for research results to be available
        logger.debug("Waiting for research content to load")

        # Try to find the main content container
        # This selector may need updating based on current Gemini UI
        content_selectors = [
            '[data-test-id="scroll-container"]',
            ".research-content",
            ".response-container",
            'main [role="main"]',
            "article",
        ]

        content_html = ""
        for selector in content_selectors:
            try:
                logger.debug(f"Trying selector: {selector}")
                element = page.locator(selector).first
                if await element.count() > 0:
                    content_html = await element.inner_html()
                    logger.debug(f"Found content with selector: {selector}")
                    break
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue

        if not content_html:
            # Fallback: get all text content from body
            logger.warning("No specific content container found, using body fallback")
            content_html = await page.locator("body").inner_html()

        return content_html

    except Exception as e:
        logger.error(f"Error extracting research content: {e}")
        raise
