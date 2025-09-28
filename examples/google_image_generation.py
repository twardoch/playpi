#!/usr/bin/env python
# this_file: examples/google_image_generation.py
"""Google Gemini Image Generation example."""

import asyncio
import contextlib
from pathlib import Path

from playpi import google_gemini_generate_image

OUTPUT_DIR = Path(__file__).parent / "output"


async def main() -> None:
    """Run the image generation task and save the output."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    prompt = "A futuristic cityscape with flying cars and neon lights."
    with contextlib.suppress(Exception):
        await google_gemini_generate_image(
            prompt, headless=True, timeout=900, verbose=False, download_path=str(OUTPUT_DIR)
        )


if __name__ == "__main__":
    asyncio.run(main())
