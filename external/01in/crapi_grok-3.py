#!/usr/bin/env python3

"""
Grok CLI: A tool for interacting with Grok on X (Twitter) to retrieve answers and citations.

This module provides functionality to automate questions to Grok and extract
the responses and related citations, with both file-based and direct question options.
"""

from __future__ import annotations

import asyncio
import html
import locale
import logging
import re
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Callable, Coroutine
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import urlparse, urlunparse

import nodriver as nd
from bs4 import BeautifulSoup, NavigableString, Tag
from html2text import HTML2Text
from pydantic import BaseModel
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress

# Configure logging
console = Console()
logging.basicConfig(
    level=logging.WARNING,
    format="\n> %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)],
)
logger = logging.getLogger("grok")


def verbose_logger(verbose: bool = False):
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)


# Type aliases
QuestionCallback = Callable[[str, "GrokResponse"], None]
AsyncQuestionCallback = Callable[[str, "GrokResponse"], Coroutine]


# Helper functions
async def wait_for_selector(tab: nd.Tab, selector: str, timeout: int = 10000) -> nd.Element:
    """Wait for an element to be present on the page."""
    try:
        return await tab.select(selector, timeout=timeout)
    except TimeoutError:
        msg = f"Timeout waiting for selector: {selector}"
        raise TimeoutError(msg) from None


def html_to_markdown(html_content: str) -> str:
    """Convert HTML content to Markdown or plain text."""
    h = HTML2Text()
    h.body_width = 0
    h.bypass_tables = False
    h.close_quote = """
    h.default_image_alt = "image"
    h.emphasis_mark = "_"
    h.escape_snob = False
    h.google_doc = False
    h.google_list_indent = 0
    h.hide_strikethrough = False
    h.ignore_emphasis = False
    h.ignore_images = False
    h.ignore_links = False
    h.ignore_mailto_links = False
    h.ignore_tables = False
    h.images_as_html = False
    h.images_to_alt = False
    h.images_with_size = False
    h.inline_links = True
    h.links_each_paragraph = False
    h.mark_code = True
    h.open_quote = """
    h.pad_tables = True
    h.protect_links = True
    h.single_line_break = False
    h.skip_internal_links = False
    h.strong_mark = "**"
    h.tag_callback = None
    h.ul_item_mark = "-"
    h.unicode_snob = True
    h.use_automatic_links = True
    h.wrap_links = False
    h.wrap_list_items = False
    h.wrap_tables = False
    return h.handle(html_content)


def from_html(html_content: str) -> str:
    return html_to_markdown(html_content).strip()


class GrokResponse(BaseModel):
    """Represents a response from Grok."""

    question: str
    html: str = ""
    x_html: str | None = None
    text: str = ""
    x_text: str | None = None
    x_links: list[str] | None = None

    def __init__(self, **data):
        super().__init__(**data)
        self._process_response()
        self._process_x_links()

    def _process_response(self) -> None:
        """Process the HTML response and convert it to text."""
        if self.html:
            self.text = from_html(self.html)

    def _process_x_links(self) -> None:
        """Process X (Twitter) links from the HTML response."""
        if self.x_html:
            soup = BeautifulSoup(self.x_html, "html.parser")
            self.x_text = from_html(self.x_html)

            unique_links = OrderedDict()
            for a in soup.find_all("a", href=True):
                url = a["href"]
                if url.startswith("/"):
                    url = f"https://x.com{url}"

                parsed_url = urlparse(url)
                clean_path = re.sub(r"/photo/\d+/?$", "/", parsed_url.path)
                clean_url = urlunparse(
                    (
                        parsed_url.scheme,
                        parsed_url.netloc,
                        clean_path,
                        parsed_url.params,
                        parsed_url.query,
                        parsed_url.fragment,
                    )
                )

                unique_links[clean_url] = None

            self.x_links = list(unique_links.keys())


class BrowserInterface(ABC):
    """Abstract base class for browser interactions."""

    @abstractmethod
    async def setup(self) -> nd.Browser:
        """Set up and return a Browser instance."""

    @abstractmethod
    async def login(self, browser: nd.Browser) -> None:
        """Log in to the X platform."""

    @abstractmethod
    async def interact(self, browser: nd.Browser, question: str) -> GrokResponse:
        """Interact with Grok and return the response."""


class ChromeInterface(BrowserInterface):
    """Implements browser interactions using Chrome."""

    def __init__(self, cookie_path: Path, verbose: bool = False):
        self.cookie_path = cookie_path
        self.verbose = verbose
        verbose_logger(self.verbose)

    async def setup(self) -> nd.Browser:
        """Set up and return a Chrome Browser instance."""
        logger.debug("Setting up Chrome Browser")
        try:
            browser = await nd.start(headless=False, no_sandbox=True)
        except Exception as e:
            logger.error(f"Failed to start browser: {e!s}")
            logger.info("Attempting to start browser with additional options...")
            try:
                browser = await nd.start(
                    headless=False,
                    no_sandbox=True,
                    disable_gpu=True,
                    disable_dev_shm_usage=True,
                )
            except Exception as e:
                logger.error(f"Failed to start browser with additional options: {e!s}")
                raise

        await self.load_cookies(browser)
        return browser

    async def load_cookies(self, browser: nd.Browser) -> None:
        """Load cookies for the Browser."""
        await browser.get("https://x.com/home")
        if self.cookie_path.exists():
            await browser.cookies.load(self.cookie_path)

    async def save_cookies(self, browser: nd.Browser) -> None:
        """Save cookies from the Browser."""
        await browser.cookies.save(self.cookie_path)

    async def login(self, browser: nd.Browser) -> None:
        """Log in to X platform using Chrome."""
        logger.debug("Logging in to X platform")
        await browser.get("https://x.com/i/grok")
        await browser.main_tab.select("body", timeout=10)

        # Check if we are on the login page
        if "flow/login" in browser.main_tab.url:
            console.print("Please log in manually. Waiting for redirection...")

            # Wait for the URL to change after login
            current_url = browser.main_tab.url
            while browser.main_tab.url == current_url:
                await asyncio.sleep(1)

            console.print("Login successful!")
            await self.save_cookies(browser)
            await browser.get("https://x.com/i/grok")

    async def interact(self, browser: nd.Browser, question: str) -> GrokResponse:
        """Interact with Grok using Chrome and return the response."""
        try:
            logger.debug("New Grok tab")
            tab = await browser.get("https://x.com/i/grok", new_tab=True)

            input_box = await wait_for_selector(tab, "textarea[placeholder='Ask anything']")

            logger.debug(f"Asking Grok:\n{question}")
            await input_box.send_keys(question)
            await input_box.send_keys(nd.Keys.ENTER)

            response_element = await wait_for_selector(
                tab,
                "(//span[contains(text(), 'Answer')]/parent::div/parent::div/following-sibling::div)[1]",
            )

            await wait_for_selector(
                tab,
                "//button[@aria-label='Copy text' and @role='button']",
            )

            response_html = await response_element.get_attribute("innerHTML")
            logger.debug("Got answer")

            try:
                citation_element = await tab.select("main nav[role='navigation']", timeout=5000)
                citation_html = await citation_element.get_attribute("outerHTML")
            except TimeoutError:
                citation_html = None

            logger.debug("Got citations")
            await tab.close()

            return GrokResponse(
                question=question,
                html=response_html,
                x_html=citation_html,
            )

        except Exception as e:
            logger.error(f"Error processing question '{question}': {e!s}")
            raise


class GrokInterface:
    """Manages interactions with Grok on X."""

    def __init__(self, browser_interface: BrowserInterface, verbose: bool = False):
        self.browser_interface = browser_interface
        self.browser: nd.Browser | None = None
        self.verbose = verbose
        verbose_logger(self.verbose)

    async def setup(self) -> None:
        """Set up the Browser and log in."""
        logger.debug("Setting up GrokInterface")
        self.browser = await self.browser_interface.setup()
        await self.browser_interface.login(self.browser)

    async def ask(self, question: str) -> GrokResponse:
        """Ask Grok a single question and return the response."""
        if not self.browser:
            msg = "Browser not set up. Call setup() first."
            raise RuntimeError(msg)

        logger.debug(f"Asking Grok: {question}")

        try:
            return await self.browser_interface.interact(self.browser, question)
        except Exception as e:
            logger.error(f"Error processing question '{question}': {e!s}")
            raise

    async def ask_list(self, questions: list[str], callback: AsyncQuestionCallback | None = None) -> list[GrokResponse]:
        """Ask Grok a list of questions and return the responses."""
        if not self.browser:
            msg = "Browser not set up. Call setup() first."
            raise RuntimeError(msg)

        results = []
        with Progress() as progress:
            if len(questions) > 1:
                task = progress.add_task("[green]Grok", total=len(questions))
            for question in questions:
                try:
                    result = await self.browser_interface.interact(self.browser, question)
                    results.append(result)
                    if callback:
                        await callback(question, result)
                    if len(questions) > 1:
                        progress.update(task, advance=1)
                        await asyncio.sleep(3)  # Add a delay between questions to avoid rate limiting
                except Exception as e:
                    logger.error(f"Error processing question '{question}': {e!s}")

        return results

    async def close(self) -> None:
        """Close the Browser."""
        if self.browser:
            logger.debug("Closing Browser")
            await self.browser.stop()


class AskGrokOnX:
    """Main class for interacting with Grok on X."""

    def __init__(self, verbose: bool = False):
        self.interface = None
        self.verbose = verbose
        verbose_logger(self.verbose)
        cookie_path = Path(__file__).parent / f"{Path(__file__).stem}_cookies.pkl"
        chrome_interface = ChromeInterface(cookie_path, verbose=verbose)
        self.interface = GrokInterface(chrome_interface, verbose=verbose)

    async def setup(self):
        try:
            await self.interface.setup()
        except Exception as e:
            logger.error(f"Failed to initialize AskGrokOnX: {e!s}")
            logger.info("Please make sure you have the latest version of Chrome installed.")
            logger.info(
                "If the problem persists, try running the script with sudo (not recommended) or as a non-root user."
            )
            raise

    async def ask(self, question: str) -> GrokResponse:
        """Ask a single question to Grok."""
        return await self.interface.ask(question)

    async def ask_list(self, questions: list[str], callback: AsyncQuestionCallback | None = None) -> list[GrokResponse]:
        """Ask a list of questions to Grok."""
        return await self.interface.ask_list(questions, callback)

    async def close(self):
        if self.interface:
            await self.interface.close()


async def ask(
    questions: str | list[str],
    full: bool = False,
    verbose: bool = False,
    callback: AsyncQuestionCallback | None = None,
    api: AskGrokOnX | None = None,
) -> list[GrokResponse] | list[str]:
    """Ask questions to Grok and return responses."""
    verbose_logger(verbose)
    if api is None:
        api = AskGrokOnX(verbose=verbose)
        await api.setup()
    if isinstance(questions, str):
        questions = questions.split(";")
    grok_list = await api.ask_list(questions, callback)
    await api.close()
    if not full:
        return [grok.html for grok in grok_list]
    return grok_list


async def ask_topics(
    topics: str | list[str],
    full: bool = False,
    date: str | None = None,
    template: str | None = None,
    verbose: bool = False,
    callback: AsyncQuestionCallback | None = None,
    api: AskGrokOnX | None = None,
) -> list[GrokResponse] | list[str]:
    """Ask Grok about specific topics and return responses."""
    verbose_logger(verbose)
    if api is None:
        api = AskGrokOnX(verbose=verbose)
        await api.setup()
    if isinstance(topics, str):
        topics = topics.split(";")

    if not date:
        current_locale = locale.getlocale()
        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
        date = datetime.now().strftime("%B %Y")
        locale.setlocale(locale.LC_TIME, current_locale)

    if not template:
        template = """I'm interested in current news, events and trends about {topic}. Print the heading "{topic} in {date}. Then give me a citation-grounded TLDR bullet list that distills the important news & trends about {topic} in {date}. Each bullet item should have a concise title, immediately followed by a concise description. Important: Don't give me old news! Ignore news older than {date}. Ignore items published or updated before {date}. If there are no specific X posts related to {topic} in {date}, just say so and don't search for older X posts!"""

    questions = [template.format(topic=topic, date=date) for topic in topics]

    result = await ask(questions, full=full, verbose=verbose, callback=callback, api=api)
    await api.close()
    return result


def cli():
    """Main entry point for the CLI."""
    import fire

    async def async_ask(*args, **kwargs):
        return await ask(*args, **kwargs)

    async def async_ask_topics(*args, **kwargs):
        return await ask_topics(*args, **kwargs)

    def sync_ask(*args, **kwargs):
        return asyncio.run(async_ask(*args, **kwargs))

    def sync_ask_topics(*args, **kwargs):
        return asyncio.run(async_ask_topics(*args, **kwargs))

    fire.Fire(
        {
            "ask": sync_ask,
            "topics": sync_ask_topics,
        }
    )


if __name__ == "__main__":
    cli()
