# PlayPi

Automate AI chat workflows through browser automation.

PlayPi provides simple, high-level functions for automating browser-based AI chat workflows, starting with Google Gemini Deep Research.

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
from playpi import google_deep_research

async def main():
    # Perform deep research on a topic
    result = await google_deep_research(
        "Analyze the impact of quantum computing on cryptography",
        headless=True,  # Run browser in background
        timeout=600,    # 10 minute timeout
        verbose=True    # Enable detailed logging
    )

    print(result)  # Markdown-formatted research results

asyncio.run(main())
```

### Command Line Interface

```bash
# Perform research and save to file
playpi google "What are the latest developments in renewable energy?" --output research.md

# Interactive mode (visible browser)
playpi google "Climate change mitigation strategies" --headless=false --verbose

# Test browser session
playpi test
```

## Prerequisites

### Authentication

Before using Google Deep Research, you need to:

1. **Install Playwright browsers**: `playwright install chromium`
2. **Login to Google**: Open https://gemini.google.com in your browser and sign in
3. **Browser profiles**: PlayPi reuses browser sessions, so you only need to login once

### System Requirements

- Python 3.11+
- Chromium browser (installed automatically)
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

### `google_deep_research(prompt, **options)`

Perform Google Gemini Deep Research on a given prompt.

**Parameters:**
- `prompt` (str): Research query or question
- `headless` (bool): Run browser in headless mode (default: True)
- `timeout` (int): Maximum wait time in seconds (default: 600)
- `verbose` (bool): Enable detailed logging (default: False)
- `profile` (str): Browser profile name (reserved for future use)

**Returns:**
- `str`: Research results formatted as Markdown

**Raises:**
- `AuthenticationError`: Not logged in to Google/Gemini
- `PlayPiTimeoutError`: Research exceeded timeout limit
- `ProviderError`: UI elements not found or changed

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/playpi --cov-report=html

# Run specific test categories
uv run pytest tests/test_session.py -v
```

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