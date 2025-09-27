# Specification: `playpi` Python Package

## 1. Overview

The `playpi` package will provide a high-level, function-based API for automating browser-based tasks. It will use `playwrightauthor` as its core engine to handle browser interactions, including authentication, while exposing simple, task-oriented functions to the end-user.

The primary goal is to abstract the complexities of web automation and provide robust, reusable functions for common workflows.

## 2. Architecture and Design

- **Core Engine:** The package will be built on top of `playwright` and `playwrightauthor`. `playwrightauthor` will be used to manage browser contexts, including persistent authentication, to avoid the need for repeated manual logins.
- **Modularity:** The package will be organized into modules. A core module will handle browser initialization and management, while other modules will contain the high-level task functions.
- **Simplicity:** Functions will accept simple data types (like strings) and return processed results, hiding the underlying browser navigation, element selection, and interaction logic.
- **Error Handling:** The package will implement custom exceptions to provide clear feedback on failures, such as login errors, navigation issues, or changes in the target website's UI.

## 3. Proposed Module Structure

```
playpi/
├── __init__.py         # Exposes the public API
├── core.py             # Manages playwrightauthor, browser instances, and contexts
└── functions/
    ├── __init__.py
    └── google.py       # Contains functions related to Google services, e.g., google_deep_research
```

## 4. Function Specification

### 4.1. `google_deep_research`

This function will automate the process of performing a "Deep Research" query in Google Gemini.

- **Location:** `playpi.functions.google`
- **Signature:**
  ```python
  def google_deep_research(
      input_prompt: str,
      headless: bool = True,
      timeout: int = 600
  ) -> str:
  ```
- **Description:**
  Initiates a "Deep Research" task on Google Gemini using the provided prompt. It waits for the research to complete, copies the result, converts it to Markdown, and returns it.

- **Parameters:**
  - `input_prompt` (str): The text prompt to be used for the research.
  - `headless` (bool, optional): If `True`, the browser will run in the background. If `False`, the browser window will be visible. Defaults to `True`.
  - `timeout` (int, optional): The maximum time in seconds to wait for the research to complete. Defaults to 600 (10 minutes).

- **Returns:**
  - `str`: The research result formatted as a Markdown string.

- **Raises:**
  - `playpi.exceptions.LoginError`: If authentication with `playwrightauthor` fails.
  - `playpi.exceptions.NavigationError`: If the Gemini web application cannot be loaded.
  - `playpi.exceptions.ElementNotFoundError`: If a critical UI element cannot be found, suggesting a change in the website's layout.
  - `playpi.exceptions.TimeoutError`: If the research does not complete within the specified `timeout`.

- **High-Level Implementation Steps:**
  1.  Use the `core` module to get an authenticated `playwright` page instance for Google.
  2.  Navigate to `https://gemini.google.com/`.
  3.  Locate the prompt text area and enter the `input_prompt`.
  4.  Click the "Tools" button to open the tools menu.
  5.  Select the "Deep Research" option.
  6.  Click the "Send message" button to submit the prompt.
  7.  Wait for the "Deep Research confirmation" widget to appear and click the confirm button.
  8.  Wait until the research is complete. This will be determined by the appearance of an "export" or "copy" button in the results panel. This wait must be subject to the `timeout` parameter.
  9.  Once the results are ready, click the "Export" or "Copy" button to copy the content to the clipboard. The content is expected to be in HTML format.
  10. Retrieve the HTML content from the clipboard.
  11. Use a library like `html2text` to convert the HTML content into clean Markdown.
  12. Return the resulting Markdown string.
  13. Ensure the browser context is properly closed.

## 5. Dependencies

- `playwright`
- `playwright-author`
- `html2text`

## 6. Example Usage

```python
import playpi

# The prompt for the deep research
my_prompt = "Provide a detailed analysis of the impact of quantum computing on modern cryptography."

try:
    # Call the function to perform the research
    print("Starting deep research...")
    result_markdown = playpi.google_deep_research(my_prompt, headless=True)

    # Save the result to a file
    with open("research_result.md", "w", encoding="utf-8") as f:
        f.write(result_markdown)

    print("Research complete. Result saved to research_result.md")

except Exception as e:
    print(f"An error occurred: {e}")

```
