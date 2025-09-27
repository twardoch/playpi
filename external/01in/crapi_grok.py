#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from crapi_core import (
    AIInterface,
    AIResponse,
    AskAI,
    ChromeInterface,
    config_logger,
    console,
    logger,
    wait_for_element,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class GrokResponse(AIResponse):
    """Represents a response from Grok."""

    x_html: str | None = None
    x_text: str | None = None
    x_links: list[str] | None = None

    def _process_x_links(self) -> None:
        """Process X (Twitter) links from the HTML response."""
        if self.x_html:
            soup = BeautifulSoup(self.x_html, "html.parser")
            self.x_text = self.from_html(self.x_html)

            unique_links: dict[str, None] = {}
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


class GrokChromeInterface(ChromeInterface):
    def login(self, driver: WebDriver) -> None:
        """Log in to X platform using Chrome."""
        logger.debug(">> Logging in to X platform")
        driver.get("https://x.com/i/grok")
        wait_for_element(driver, (By.TAG_NAME, "body"))
        if "flow/login" in driver.current_url:
            console.print("Please log in manually. Waiting for redirection...")
            WebDriverWait(driver, 900).until(EC.url_to_be("https://x.com/home"))
            console.print("Login successful!")
            self.save_cookies(driver)
            driver.get("https://x.com/i/grok")

    def interact(self, driver: WebDriver, question: str) -> GrokResponse:
        """Interact with Grok using Chrome and return the response."""
        try:
            logger.debug("New Grok tab")
            driver.switch_to.new_window("tab")
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get("https://x.com/i/grok")
            letswait = WebDriverWait(driver, 10)

            letswait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            input_box = wait_for_element(driver, (By.CSS_SELECTOR, "textarea[placeholder='Ask anything']"))

            logger.debug(f"Asking Grok:\n{question}")
            input_box.send_keys(question)
            input_box.send_keys(Keys.RETURN)

            response_element = wait_for_element(
                driver,
                (
                    By.XPATH,
                    "(//span[contains(text(), 'Answer')]/parent::div/parent::div/following-sibling::div)[1]",
                ),
            )

            wait_for_element(
                driver,
                (
                    By.XPATH,
                    "//button[@aria-label='Copy text' and @role='button']",
                ),
            )

            response_html = response_element.get_attribute("innerHTML")
            logger.debug(">> Got answer")

            try:
                citation_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "main nav[role='navigation']"))
                )
                citation_html = citation_element.get_attribute("outerHTML")
            except TimeoutException:
                citation_html = None

            response = GrokResponse(
                question=question,
                html=response_html,
                x_html=citation_html,
            )

            if citation_html:
                logger.debug(f">> Got {len(response.x_links)} citations")
            else:
                logger.debug(">> Got 0 citations")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            return response

        except Exception as e:
            logger.error(f"Error processing question '{question}': {e!s}")
            raise


class AskGrokOnX(AskAI):
    """Main class for interacting with Grok on X."""

    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        try:
            cookie_path = Path(__file__).parent / f"{Path(__file__).stem}_cookies.pkl"
            chrome_interface = GrokChromeInterface(cookie_path, verbose=verbose)
            self.interface = AIInterface(chrome_interface, verbose=verbose)
            self.interface.setup()
        except Exception as e:
            logger.error(f"Failed to initialize AskGrokOnX: {e!s}")
            raise


def format_grok_response(grok: GrokResponse) -> str:
    formatted = format_response(grok)
    if grok.x_links:
        lines = formatted.splitlines()
        reference_index = lines.index("### References:")
        lines[reference_index] = "### X References:"
        formatted = "\n".join(lines)
    return formatted


def ask_grok(
    questions: str | list[str],
    full: bool = False,
    verbose: bool = False,
    callback: QuestionCallback | None = None,
    api: AskGrokOnX | None = None,
) -> list[GrokResponse] | list[str]:
    """Ask questions to Grok and return responses."""
    config_logger(verbose)
    if api is None:
        api = AskGrokOnX(verbose=verbose)
    grok_list = ask(questions, full=True, verbose=verbose, callback=callback, api=api)
    if not full:
        return [format_grok_response(grok) for grok in grok_list]
    return grok_list


def ask_grok_topics(
    topics: str | list[str],
    full: bool = False,
    date: str | None = None,
    template: str | None = None,
    verbose: bool = False,
    callback: QuestionCallback | None = None,
    api: AskGrokOnX | None = None,
) -> list[GrokResponse] | list[str]:
    """Ask Grok about specific topics and return responses."""
    config_logger(verbose)
    if api is None:
        api = AskGrokOnX(verbose=verbose)
    grok_list = ask_topics(
        topics,
        full=True,
        date=date,
        template=template,
        verbose=verbose,
        callback=callback,
        api=api,
    )
    if not full:
        return [format_grok_response(grok) for grok in grok_list]
    return grok_list


if __name__ == "__main__":
    import fire

    fire.Fire(
        {
            "ask": ask_grok,
            "topics": ask_grok_topics,
        }
    )
