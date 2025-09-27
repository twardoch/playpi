#!/usr/bin/env python
# this_file: examples/google_deep_research.py
"""Concurrent Google Deep Research example.

This example demonstrates how to run two PlayPi Google Deep Research queries
concurrently and save their Markdown results into separate files. The
underlying browser automation is powered by the `playwrightauthor` package,
which launches Chrome for Testing in headed mode using the configured profile.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from playpi import PlayPiError, google_deep_research
from playpi.example_prompts import PROMPT_EN, PROMPT_PL

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_EN_FILE = OUTPUT_DIR / "google_deep_research_en.md"
OUTPUT_PL_FILE = OUTPUT_DIR / "google_deep_research_pl.md"


async def _run_single(prompt: str, destination: Path) -> None:
    """Execute a single research query and persist the Markdown output."""
    result = await google_deep_research(prompt, headless=True, timeout=900, verbose=False)
    destination.write_text(result, encoding="utf-8")


async def main() -> None:
    """Run the two deep-research tasks concurrently and save their outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tasks = (
        asyncio.create_task(_run_single(PROMPT_EN, OUTPUT_EN_FILE)),
        asyncio.create_task(_run_single(PROMPT_PL, OUTPUT_PL_FILE)),
    )

    try:
        await asyncio.gather(*tasks)
    except PlayPiError as exc:  # Re-raise with context for quick troubleshooting.
        error_msg = "Google Deep Research example failed"
        raise PlayPiError(error_msg) from exc

    print(f"English results saved to: {OUTPUT_EN_FILE}")  # noqa: T201
    print(f"Polish results saved to: {OUTPUT_PL_FILE}")  # noqa: T201


if __name__ == "__main__":  # pragma: no cover - illustrative script
    asyncio.run(main())
