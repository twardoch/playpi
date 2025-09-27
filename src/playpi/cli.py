# this_file: src/playpi/cli.py
"""Command-line interface for PlayPi package."""

import asyncio
import sys
from pathlib import Path

import fire
from rich.console import Console

from playpi.config import PlayPiConfig
from playpi.exceptions import PlayPiError
from playpi.providers.google import google_deep_research
from playpi.session import create_session

console = Console()


def google_research(
    prompt: str,
    *,
    output: str | None = None,
    headless: bool = True,
    timeout: int = 600,
    verbose: bool = False,
) -> None:
    """Perform Google Gemini Deep Research.

    Args:
        prompt: Research query
        output: Output file path (prints to console if not specified)
        headless: Run browser in headless mode
        timeout: Maximum wait time in seconds
        verbose: Enable verbose logging
    """
    try:
        result = asyncio.run(
            google_deep_research(
                prompt,
                headless=headless,
                timeout=timeout,
                verbose=verbose,
            )
        )

        if output:
            output_path = Path(output)
            output_path.write_text(result, encoding="utf-8")
            console.print(f"✅ Research saved to: {output_path}")
        else:
            console.print("\n📄 Research Results:")
            console.print(result)

    except PlayPiError as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n⚠️  Research interrupted by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
        sys.exit(1)


def test_session() -> None:
    """Test basic browser session functionality."""
    try:

        async def _test():
            config = PlayPiConfig(verbose=True)
            async with create_session(config) as session:
                page = await session.get_page()
                await page.goto("https://httpbin.org/json")
                title = await page.title()
                console.print(f"✅ Browser session test passed! Page title: {title}")

        asyncio.run(_test())

    except Exception as e:
        console.print(f"❌ Session test failed: {e}", style="red")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    fire.Fire(
        {
            "google": google_research,
            "test": test_session,
        }
    )


if __name__ == "__main__":
    main()
