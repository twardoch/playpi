#!/usr/bin/env python3
import logging
import ssl

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configure SSL context
ssl._create_default_https_context = ssl._create_unverified_context


def main():
    logger.info("Starting the undetected-chromedriver example")

    # Set up Chrome options
    logger.debug("Setting up Chrome options")
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--verbose")
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=0")

    # Initialize the undetected-chromedriver
    logger.debug("Initializing undetected-chromedriver")
    driver = uc.Chrome(options=options)

    try:
        # Navigate to a website (e.g., Google)
        logger.info("Navigating to Google")
        driver.get("https://www.google.com")

        # Wait for the search input to be present
        logger.debug("Waiting for search input to be present")
        search_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        logger.info("Search input found")

        # Perform a search
        logger.debug("Performing search")
        search_input.send_keys("undetected-chromedriver")
        search_input.submit()

        # Wait for search results
        logger.debug("Waiting for search results")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search")))
        logger.info("Search results loaded")

        # Print the title of the page
        page_title = driver.title
        logger.info(f"Page title: {page_title}")

        # You can add more interactions or assertions here

    except Exception as e:
        logger.error(f"An error occurred: {e!s}", exc_info=True)

    finally:
        # Close the browser
        logger.info("Closing the browser")
        driver.quit()


if __name__ == "__main__":
    main()
