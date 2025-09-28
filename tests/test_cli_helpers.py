# this_file: tests/test_cli_helpers.py
"""Tests for CLI helper functions."""

import io
import json
from typing import Any
from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_gemi_command_when_file_and_prompt_merges_and_writes(tmp_path, monkeypatch):
    """`gemi_command` should merge file and prompt, call ask, and write output."""
    from playpi.providers.google import cli_helpers

    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("FILE", encoding="utf-8")
    output_file = tmp_path / "out.md"

    async_mock = AsyncMock(return_value="RESULT")
    monkeypatch.setattr(cli_helpers, "google_gemini_ask", async_mock)
    monkeypatch.setattr(cli_helpers, "google_gemini_ask_deep_think", AsyncMock())

    await cli_helpers.gemi_command(
        file_prompt=str(prompt_file),
        prompt="MORE",
        deep=False,
        output_file=str(output_file),
    )

    async_mock.assert_awaited_once()
    args, _ = async_mock.call_args
    assert args[0] == "FILE\nMORE"
    assert output_file.read_text(encoding="utf-8") == "RESULT"


@pytest.mark.asyncio
async def test_gemi_command_when_deep_calls_deep_think(monkeypatch):
    """`gemi_command` should route to deep think when `deep=True`."""
    from playpi.providers.google import cli_helpers

    ask_mock = AsyncMock(return_value="STD")
    deep_mock = AsyncMock(return_value="DEEP")
    monkeypatch.setattr(cli_helpers, "google_gemini_ask", ask_mock)
    monkeypatch.setattr(cli_helpers, "google_gemini_ask_deep_think", deep_mock)

    result_path = await cli_helpers.gemi_command(prompt="hello", deep=True)

    ask_mock.assert_not_called()
    deep_mock.assert_awaited_once()
    args, _ = deep_mock.call_args
    assert args[0] == "hello"
    assert result_path == "DEEP"


@pytest.mark.asyncio
async def test_gemi_command_without_prompt_raises(monkeypatch):
    """`gemi_command` should require some prompt content."""
    from playpi.providers.google import cli_helpers

    monkeypatch.setattr(cli_helpers, "google_gemini_ask", AsyncMock())
    monkeypatch.setattr(cli_helpers, "google_gemini_ask_deep_think", AsyncMock())

    with pytest.raises(ValueError):
        await cli_helpers.gemi_command()


def _invoke_gemi_dr(config: Any, monkeypatch):
    from playpi.providers.google import cli_helpers

    mock = AsyncMock(return_value=["ok"])
    monkeypatch.setattr(cli_helpers, "google_gemini_deep_research_multi", mock)

    stdin = io.StringIO(json.dumps(config))
    monkeypatch.setattr(cli_helpers, "_stdin", stdin)

    return cli_helpers, mock


@pytest.mark.asyncio
async def test_gemi_dr_command_reads_stdin_json(monkeypatch):
    """`gemi_dr_command` should parse JSON config and call provider."""
    config = [{"prompt": "one"}, {"prompt": "two"}]
    cli_helpers, mock = _invoke_gemi_dr(config, monkeypatch)

    result = await cli_helpers.gemi_dr_command()

    mock.assert_awaited_once_with(config)
    assert result == ["ok"]


@pytest.mark.asyncio
async def test_gemi_dr_command_invalid_json_raises(monkeypatch):
    """`gemi_dr_command` should raise ValueError on invalid JSON."""
    from playpi.providers.google import cli_helpers

    monkeypatch.setattr(cli_helpers, "google_gemini_deep_research_multi", AsyncMock())
    monkeypatch.setattr(cli_helpers, "_stdin", io.StringIO("not json"))

    with pytest.raises(ValueError):
        await cli_helpers.gemi_dr_command()
