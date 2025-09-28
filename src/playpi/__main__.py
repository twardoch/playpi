# this_file: src/playpi/__main__.py
"""CLI entry point for PlayPi."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import fire
from rich.console import Console

from playpi.exceptions import PlayPiError
from playpi.providers.google import cli_helpers

_console = Console()


def _run_command(coro: Any) -> Any:
    try:
        return asyncio.run(coro)
    except PlayPiError as exc:
        _console.print(f"❌ Error: {exc}", style="red")
        sys.exit(1)
    except KeyboardInterrupt:
        _console.print("⚠️ Operation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - defensive for unexpected issues
        _console.print(f"❌ Unexpected error: {exc}", style="red")
        sys.exit(1)


def _print_result(result: Any, *, success_message: str | None = None) -> None:
    if result is None:
        return
    if isinstance(result, Path):
        message = success_message or f"✅ Saved to: {result}"
        _console.print(message)
        return
    if isinstance(result, list | tuple):
        for item in result:
            _console.print(item)
        return
    _console.print(result)


def gemi(
    *,
    file_prompt: str | None = None,
    prompt: str | None = None,
    deep: bool = False,
    output_file: str | None = None,
    verbose: bool = False,
) -> None:
    """Run a Gemini prompt, optionally with Deep Think."""
    result = _run_command(
        cli_helpers.gemi_command(
            file_prompt=file_prompt,
            prompt=prompt,
            deep=deep,
            output_file=output_file,
            verbose=verbose,
        )
    )
    message = None
    if isinstance(result, Path):
        message = f"✅ Response saved to: {result}"
    _print_result(result, success_message=message)


def gemi_dr() -> None:
    """Execute multiple Deep Research jobs via JSON config from stdin."""
    result = _run_command(cli_helpers.gemi_dr_command())
    _print_result(result)


def test(verbose: bool = True) -> None:
    """Validate that PlayPi can open a browser session."""
    result = _run_command(cli_helpers.test_session_command(verbose=verbose))
    _print_result(result)


def main() -> None:
    """Entrypoint mapping CLI commands."""
    fire.Fire(
        {
            "gemi": gemi,
            "gemi_dr": gemi_dr,
            "test": test,
        }
    )


if __name__ == "__main__":
    main()
