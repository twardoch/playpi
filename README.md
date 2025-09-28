# PlayPi

Automate AI chat workflows through browser automation.

PlayPi provides simple, high-level functions for automating browser-based AI chat workflows, starting with Google Gemini Deep Research. The package delegates all browser lifecycle management to the [`playwrightauthor`](https://pypi.org/project/playwrightauthor/) library, so Chrome for Testing installation and profile handling happen automatically.

## Installation

```bash
pip install playpi
```

Or for development:

```bash
git clone https://github.com/twardoch/playpi
cd playpi
uv sync
```

## Quick Start

### Google Deep Research

```python
import asyncio
from playpi import google_gemini_deep_research

async def main():
    # Perform deep research on a topic
    result = await google_gemini_deep_research(
        "Analyze the impact of quantum computing on cryptography",
        headless=True,  # Retained for compatibility; playwrightauthor runs headed
        timeout=600,    # 10 minute timeout
        verbose=True    # Enable detailed logging
    )

    print(result)  # Markdown-formatted research results

asyncio.run(main())
```

### Command Line Interface

```bash
# Standard Gemini prompt with optional file prompt + Deep Think toggle
playpi gemi --file_prompt prompt.md --prompt "Add a concise summary" --deep --output_file response.md

# Single or multi Deep Research via JSON piped on stdin
printf '{"prompt": "What are the latest developments in renewable energy?"}' | playpi gemi_dr
cat jobs.json | playpi gemi_dr

# Test browser session
playpi test
```

Headless flags are currently ignored because playwrightauthor always operates Chrome in headed mode.

## Prerequisites

### Authentication

Before using Google Deep Research, you need to:

1. **Login to Google**: Open https://gemini.google.com in your browser and sign in
2. **Browser profiles**: PlayPi relies on playwrightauthor-managed profiles, so you only need to login once in the selected profile

### System Requirements

- Python 3.12+
- Chrome for Testing (downloaded automatically by playwrightauthor)
- 2GB+ RAM for browser automation
- Internet connection

## Features

- ✅ **Google Gemini Deep Research** - Automated research with source compilation
- ✅ **Session Management** - Persistent authentication across multiple queries
- ✅ **Cross-Platform** - Works on Windows, macOS, and Linux
- ✅ **Concurrent Processing** - Run up to 3 research tasks simultaneously
- ✅ **Rich Output** - Clean Markdown formatting with links and structure
- ✅ **Error Handling** - Graceful handling of timeouts and UI changes

## API Reference

### `google_gemini_deep_research(prompt, **options)`

Perform Google Gemini Deep Research on a given prompt.

**Parameters:**
- `prompt` (str): Research query or question
- `headless` (bool): Retained for compatibility; playwrightauthor currently launches Chrome in headed mode (default: True)
- `timeout` (int): Maximum wait time in seconds (default: 600)
- `verbose` (bool): Enable detailed logging (default: False)
- `profile` (str): Browser profile name managed by playwrightauthor (default: `"default"`)

**Returns:**
- `str`: Research results formatted as Markdown

**Raises:**
- `AuthenticationError`: Not logged in to Google/Gemini
- `PlayPiTimeoutError`: Research exceeded timeout limit
- `ProviderError`: UI elements not found or changed

## Development

### Running Tests

```bash
# Run all tests without hitting live Gemini login
PLAYPI_FORCE_AUTH_FAILURE=1 uvx hatch run test:python -m pytest

# Run with coverage (same auth guard applies)
PLAYPI_FORCE_AUTH_FAILURE=1 uvx hatch run test:python -m pytest --cov=src/playpi --cov-report=html

# Run specific test categories
PLAYPI_FORCE_AUTH_FAILURE=1 uvx hatch run test:python -m pytest tests/test_session.py -v
```

`PLAYPI_FORCE_AUTH_FAILURE=1` short-circuits the authentication check during testing so suites do not wait for manual Google sign-in.

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run mypy src/playpi
```

## License

MIT License. See [LICENSE](LICENSE) for details.
