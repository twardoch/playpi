#!/usr/bin/env python3

from __future__ import annotations

import html
import locale
import logging
import multiprocessing
import pickle
import ssl
import time
from abc import abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

import undetected_chromedriver as uc
from bs4 import BeautifulSoup, NavigableString, Tag
from html2text import HTML2Text
from pydantic import BaseModel
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if TYPE_CHECKING:
    from pathlib import Path

    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

# Configure SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Configure logging
console = Console()
logger = logging.getLogger("crapi")


def config_logger(verbose: bool = False):
    if not logger.handlers:
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.WARNING,
            format="\n> %(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console)],
        )
    else:
        logger.setLevel(logging.DEBUG if verbose else logging.WARNING)


DEFAULT_CHROME_OPTIONS = [
    "disable-search-engine-choice-screen",
    "start-maximized",
]

# Type aliases
QuestionCallback = Callable[[str, "AIResponse"], None]


# Helper functions
def wait_for_element(driver: WebDriver, locator: tuple, timeout: int = 240) -> WebElement:
    """Wait for an element to be present on the page."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


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


def prune_html(soup):
    elements_to_remove = ["svg", "button", "input", "textarea", "select", "option"]
    for element in soup.find_all(elements_to_remove):
        element.decompose()
    return soup


def recursive_unescape(element):
    if isinstance(element, NavigableString):
        return html.unescape(str(element))
    if isinstance(element, Tag):
        if element.name in ["code", "pre"]:
            return html.unescape("".join(str(child) for child in element.contents))
        unescaped_children = "".join(recursive_unescape(child) for child in element.contents)
        if element.name == "[document]":
            return unescaped_children
        attrs = " ".join(f'{k}="{v}"' for k, v in element.attrs.items())
        return f"<{element.name}{' ' + attrs if attrs else ''}>{unescaped_children}</{element.name}>"
    return ""


def from_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    pruned_soup = prune_html(soup)
    unescaped_html = recursive_unescape(pruned_soup)
    final_markdown = html_to_markdown(unescaped_html)
    final_markdown = final_markdown.replace("`\n\n", "\n\n").replace("\n\n`", "\n\n")
    return final_markdown.strip()


class AIResponse(BaseModel):
    """Represents a response from an AI service."""

    question: str
    html: str = ""
    text: str = ""
    links: list[str] | None = None

    def __init__(self, **data):
        super().__init__(**data)
        self._process_response()
        self._process_links()

    def _process_response(self) -> None:
        """Process the HTML response and convert it to text."""
        if self.html:
            self.text = from_html(self.html)

    def _process_links(self) -> None:
        """Process links from the HTML response."""
        if self.html:
            soup = BeautifulSoup(self.html, "html.parser")
            self.links = [a["href"] for a in soup.find_all("a", href=True)]


class ChromeInterface:
    """Implements browser interactions using Chrome."""

    def __init__(self, cookie_path: Path, verbose: bool = False):
        self.cookie_path = cookie_path
        self.verbose = verbose
        config_logger(self.verbose)

    def setup(self) -> WebDriver:
        """Set up and return a Chrome WebDriver instance."""
        options = uc.ChromeOptions()
        global DEFAULT_CHROME_OPTIONS
        logger.debug(">> Setting up Chrome WebDriver")
        if self.verbose:
            DEFAULT_CHROME_OPTIONS += [
                "verbose",
                "enable-logging",
                "log-level=0",
                "webview-verbose-logging",
                "v=3",
            ]
        else:
            DEFAULT_CHROME_OPTIONS += ["log-level=3"]
        for option in DEFAULT_CHROME_OPTIONS:
            options.add_argument(f"--{option}")
        options.add_argument("--log-level=0")
        driver = uc.Chrome(use_subprocess=False, options=options)
        self.load_cookies(driver)
        return driver

    def load_cookies(self, driver: WebDriver) -> None:
        """Load cookies for the WebDriver."""
        if self.cookie_path.exists():
            cookies = pickle.load(open(self.cookie_path, "rb"))
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Error adding cookie: {e!s}")

    def save_cookies(self, driver: WebDriver) -> None:
        """Save cookies from the WebDriver."""
        pickle.dump(driver.get_cookies(), open(self.cookie_path, "wb"))

    @abstractmethod
    def login(self, driver: WebDriver) -> None:
        """Log in to the AI service."""

    @abstractmethod
    def interact(self, driver: WebDriver, question: str, **kwargs) -> AIResponse:
        """Interact with the AI service and return the response."""


class AIInterface:
    """Manages interactions with an AI service."""

    def __init__(self, browser_interface: ChromeInterface, verbose: bool = False):
        self.browser_interface = browser_interface
        self.driver: WebDriver | None = None
        self.verbose = verbose
        config_logger(self.verbose)

    def setup(self) -> None:
        """Set up the WebDriver and log in."""
        logger.debug(">> Setting up AIInterface")
        self.driver = self.browser_interface.setup()
        self.browser_interface.login(self.driver)

    def ask(self, question: str, **kwargs) -> AIResponse:
        """Ask the AI service a single question and return the response."""
        if not self.driver:
            msg = "Driver not set up. Call setup() first."
            raise RuntimeError(msg)
        logger.debug(f"Asking AI: {question}")
        try:
            return self.browser_interface.interact(self.driver, question, **kwargs)
        except Exception as e:
            logger.error(f"Error processing question '{question}': {e!s}")
            raise

    def ask_list(self, questions: list[str], callback: QuestionCallback | None = None, **kwargs) -> list[AIResponse]:
        """Ask the AI service a list of questions and return the responses."""
        if not self.driver:
            msg = "Driver not set up. Call setup() first."
            raise RuntimeError(msg)
        results = []
        with Progress() as progress:
            if len(questions) > 1:
                task = progress.add_task("[green]AI", total=len(questions))
            for question in questions:
                try:
                    result = self.browser_interface.interact(self.driver, question, **kwargs)
                    results.append(result)
                    if callback:
                        callback(question, result)
                    if len(questions) > 1:
                        progress.update(task, advance=1)
                        time.sleep(3)  # Add a delay between questions to avoid rate limiting
                except Exception as e:
                    logger.error(f"Error processing question '{question}': {e!s}")
        return results

    def close(self) -> None:
        """Close the WebDriver."""
        if self.driver:
            logger.debug(">> Closing WebDriver")
            self.driver.quit()


class AskAI:
    """Main class for interacting with an AI service."""

    def __init__(self, verbose: bool = False):
        self.interface = None
        self.verbose = verbose
        config_logger(self.verbose)

    def ask(self, question: str, **kwargs) -> AIResponse:
        """Ask a single question to the AI service."""
        return self.interface.ask(question, **kwargs)

    def ask_list(self, questions: list[str], callback: QuestionCallback | None = None, **kwargs) -> list[AIResponse]:
        """Ask a list of questions to the AI service."""
        return self.interface.ask_list(questions, callback, **kwargs)

    def __del__(self):
        if self.interface:
            self.interface.close()


def format_response(ai_response: AIResponse) -> str:
    lines = ai_response.text.strip().splitlines()
    if lines:
        if not lines[0].startswith("#"):
            lines[0] = "## " + lines[0]
    if ai_response.links:
        lines.extend(["", "", "### References:", "", ""])
        lines.extend([f"- {link}" for link in ai_response.links])
        lines.extend(["", ""])
    return "\n".join(lines)


def ask(
    questions: str | list[str],
    full: bool = False,
    verbose: bool = False,
    callback: QuestionCallback | None = None,
    api: AskAI | None = None,
    **kwargs,
) -> list[AIResponse] | list[str]:
    """Ask questions to the AI service and return responses."""
    config_logger(verbose)
    if api is None:
        msg = "API instance must be provided"
        raise ValueError(msg)
    if isinstance(questions, str):
        questions = questions.split(";")
    ai_list = api.ask_list(questions, callback, **kwargs)
    if not full:
        return [format_response(ai) for ai in ai_list]
    return ai_list


def ask_topics(
    topics: str | list[str],
    full: bool = False,
    date: str | None = None,
    template: str | None = None,
    verbose: bool = False,
    callback: QuestionCallback | None = None,
    api: AskAI | None = None,
    **kwargs,
) -> list[AIResponse] | list[str]:
    """Ask the AI service about specific topics and return responses."""
    config_logger(verbose)
    if api is None:
        msg = "API instance must be provided"
        raise ValueError(msg)
    if isinstance(topics, str):
        topics = topics.split(";")

    if not date:
        current_locale = locale.getlocale()
        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
        date = datetime.now().strftime("%B %Y")
        locale.setlocale(locale.LC_TIME, current_locale)

    if not template:
        template = """I'm interested in current news, events and trends about {topic}. Print the heading "{topic} in {date}. Then give me a citation-grounded TLDR bullet list that distills the important news & trends about {topic} in {date}. Each bullet item should have a concise title, immediately followed by a concise description. Important: Don't give me old news! Ignore news older than {date}. Ignore items published or updated before {date}. If there are no specific posts related to {topic} in {date}, just say so and don't search for older posts!"""

    questions = [template.format(topic=topic, date=date) for topic in topics]

    return ask(questions, full=full, verbose=verbose, callback=callback, api=api, **kwargs)


def cli():
    """Main entry point for the CLI."""
    import fire

    fire.Fire(
        {
            "ask": lambda *args, **kwargs: ask(*args, **kwargs),
            "topics": lambda *args, **kwargs: ask_topics(*args, **kwargs),
        }
    )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    cli()
