# this_file: src/playpi/providers/google/cli_helpers.py
"""Helper utilities backing the PlayPi CLI commands."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from loguru import logger

from playpi.config import PlayPiConfig
from playpi.providers.google.gemini import (
    google_gemini_ask,
    google_gemini_ask_deep_think,
    google_gemini_deep_research,
    google_gemini_deep_research_multi,
)
from playpi.session import create_session

_stdin = sys.stdin


async def google_research_command(
    prompt: str,
    *,
    output: str | None = None,
    headless: bool = True,
    timeout: int = 600,
    verbose: bool = False,
) -> str | Path:
    """Run Deep Research and optionally persist the result."""
    result = await google_gemini_deep_research(
        prompt,
        headless=headless,
        timeout=timeout,
        verbose=verbose,
    )

    if output:
        output_path = Path(output)
        output_path.write_text(result, encoding="utf-8")
        return output_path
    return result


async def gemi_command(
    *,
    file_prompt: str | None = None,
    prompt: str | None = None,
    deep: bool = False,
    output_file: str | None = None,
    verbose: bool = False,
) -> str | Path:
    """Execute a Gemini prompt, optionally in Deep Think mode."""
    parts: list[str] = []
    if file_prompt:
        parts.append(Path(file_prompt).read_text(encoding="utf-8").rstrip())
    if prompt:
        parts.append(prompt)

    if not parts:
        msg = "Provide --prompt, --file_prompt, or both."
        raise ValueError(msg)

    full_prompt = "\n".join(part for part in parts if part)
    provider = google_gemini_ask_deep_think if deep else google_gemini_ask
    result = await provider(full_prompt, verbose=verbose)

    if output_file:
        output_path = Path(output_file)
        output_path.write_text(result, encoding="utf-8")
        return output_path
    return result


async def gemi_dr_command() -> Any:
    """Run multiple Deep Research tasks using JSON read from stdin."""
    raw = _stdin.read()
    if not raw.strip():
        msg = "No JSON payload supplied on stdin."
        raise ValueError(msg)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = "stdin does not contain valid JSON"
        raise ValueError(msg) from exc

    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        msg = "Deep Research config must be a list of jobs."
        raise ValueError(msg)

    return await google_gemini_deep_research_multi(payload)


async def test_session_command(*, verbose: bool = True) -> str:
    """Verify that a browser session can be created and navigate to httpbin."""
    config = PlayPiConfig(verbose=verbose)
    async with create_session(config) as session:
        page = await session.get_page()
        await page.goto("https://httpbin.org/json")
        title = await page.title()
        logger.debug(f"Session test navigated to {title}")
        return f"Browser session available (title: {title})"
