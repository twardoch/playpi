#!/usr/bin/env python
# this_file: examples/google_deep_research.py
"""Concurrent Google Deep Research example.

This example demonstrates how to run two PlayPi Google Deep Research queries
concurrently and save their Markdown results into separate files.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from playpi import PlayPiError, google_gemini_deep_research_multi
from playpi.example_prompts import PROMPT_EN, PROMPT_PL

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_EN_FILE = OUTPUT_DIR / "google_deep_research_en.md"
OUTPUT_PL_FILE = OUTPUT_DIR / "google_deep_research_pl.md"


async def main() -> None:
    """Run the two deep-research tasks concurrently and save their outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    config = [
        {"prompt": PROMPT_EN, "output_path": OUTPUT_EN_FILE},
        {"prompt": PROMPT_PL, "output_path": OUTPUT_PL_FILE},
    ]

    try:
        results = await google_gemini_deep_research_multi(config, headless=True, timeout=900, verbose=False)
        for _result in results:
            pass
    except PlayPiError as exc:  # Re-raise with context for quick troubleshooting.
        error_msg = "Google Deep Research example failed"
        raise PlayPiError(error_msg) from exc


if __name__ == "__main__":  # pragma: no cover - illustrative script
    asyncio.run(main())
