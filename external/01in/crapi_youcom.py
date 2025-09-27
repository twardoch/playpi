#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List
from urllib.parse import quote

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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class YouComChromeInterface(ChromeInterface):
    def login(self, driver: WebDriver) -> None:
        """Check if logged in to You.com, prompt for manual login if not."""
        logger.debug(">> Checking login status on You.com")
        driver.get("https://you.com/?chatMode=agent")
        try:
            wait_for_element(
                driver,
                (By.CSS_SELECTOR, "[data-testid='user-profile-button']"),
                timeout=5,
            )
            logger.debug(">> Already logged in")
        except TimeoutException:
            console.print("Please log in manually. Waiting for login...")
            wait_for_element(
                driver,
                (By.CSS_SELECTOR, "[data-testid='user-profile-button']"),
                timeout=300,
            )
            console.print("Login successful!")
            self.save_cookies(driver)

    def interact(self, driver: WebDriver, question: str, mode: str = "default") -> AIResponse:
        """Interact with You.com using Chrome and return the response."""
        try:
            encoded_question = quote(question)
            url = f"https://you.com/search?chatMode={mode}&tbm=youchat&q={encoded_question}"
            driver.get(url)

            # Wait for the stop button to appear and then disappear
            stop_button_locator = (
                By.CSS_SELECTOR,
                "[data-testid='stop-generating-button']",
            )
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(stop_button_locator))
            WebDriverWait(driver, 300).until_not(EC.presence_of_element_located(stop_button_locator))

            # Get the chat history
            chat_history = wait_for_element(driver, (By.ID, "chat-history"))
            response_html = chat_history.get_attribute("innerHTML")

            logger.debug(">> Got answer")

            return AIResponse(
                question=question,
                html=response_html,
            )

        except Exception as e:
            logger.error(f"Error processing question '{question}': {e!s}")
            raise


class AskYouCom(AskAI):
    """Main class for interacting with You.com."""

    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        try:
            cookie_path = Path(__file__).parent / f"{Path(__file__).stem}_cookies.pkl"
            chrome_interface = YouComChromeInterface(cookie_path, verbose=verbose)
            self.interface = AIInterface(chrome_interface, verbose=verbose)
            self.interface.setup()
        except Exception as e:
            logger.error(f"Failed to initialize AskYouCom: {e!s}")
            raise

    def ask(self, question: str, mode: str = "default") -> AIResponse:
        return super().ask(question, mode=mode)

    def ask_list(
        self,
        questions: list[str],
        callback: QuestionCallback | None = None,
        mode: str = "default",
    ) -> list[AIResponse]:
        return super().ask_list(questions, callback, mode=mode)


def ask_youcom(
    questions: str | list[str],
    full: bool = False,
    verbose: bool = False,
    callback: QuestionCallback | None = None,
    api: AskYouCom | None = None,
    mode: str = "default",
) -> list[AIResponse] | list[str]:
    """Ask questions to You.com and return responses."""
    config_logger(verbose)
    if api is None:
        api = AskYouCom(verbose=verbose)
    return ask(questions, full=full, verbose=verbose, callback=callback, api=api, mode=mode)


def ask_youcom_topics(
    topics: str | list[str],
    full: bool = False,
    date: str | None = None,
    template: str | None = None,
    verbose: bool = False,
    callback: QuestionCallback | None = None,
    api: AskYouCom | None = None,
    mode: str = "default",
) -> list[AIResponse] | list[str]:
    """Ask You.com about specific topics and return responses."""
    config_logger(verbose)
    if api is None:
        api = AskYouCom(verbose=verbose)
    return ask_topics(
        topics,
        full=full,
        date=date,
        template=template,
        verbose=verbose,
        callback=callback,
        api=api,
        mode=mode,
    )


if __name__ == "__main__":
    import fire

    fire.Fire(
        {
            "ask": ask_youcom,
            "topics": ask_youcom_topics,
        }
    )
