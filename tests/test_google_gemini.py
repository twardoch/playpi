# this_file: tests/test_google_gemini.py
"""Tests for the Google Gemini provider."""

import asyncio
import pathlib
import unittest
from unittest.mock import patch, AsyncMock

import pytest

from playpi.providers.google.gemini import (
    google_gemini_deep_research,
    google_gemini_deep_research_full,
    google_gemini_deep_research_multi,
    google_gemini_generate_image,
    google_gemini_ask_deep_think,
    google_gemini_ask,
)


@pytest.mark.asyncio
@patch("playpi.providers.google.gemini.create_session")
async def test_google_gemini_deep_research(mock_create_session):
    """Test the main google_gemini_deep_research function."""
    mock_session = AsyncMock()
    mock_page = AsyncMock()
    mock_session.get_page.return_value = mock_page
    mock_create_session.return_value.__aenter__.return_value = mock_session

    with patch("playpi.providers.google.gemini._google_gemini_deep_research_on_page", new_callable=AsyncMock) as mock_research_on_page:
        mock_research_on_page.return_value = "## Test Result"
        result = await google_gemini_deep_research("test prompt")
        assert result == "## Test Result"
        mock_research_on_page.assert_called_once_with(mock_page, "test prompt", timeout=600)


@pytest.mark.asyncio
@patch("playpi.providers.google.gemini.google_gemini_deep_research")
async def test_google_gemini_deep_research_full(mock_google_gemini_deep_research):
    """Test the google_gemini_deep_research_full function."""
    mock_google_gemini_deep_research.return_value = "## Test Result"

    with patch("builtins.open", new_callable=unittest.mock.mock_open) as mock_open:
        # Test with prompt_path and output_path
        mock_open.return_value.read.return_value = "file prompt"
        result = await google_gemini_deep_research_full(prompt="test prompt", prompt_path="/fake/prompt.txt", output_path="/fake/output.txt")
        assert result == pathlib.Path("/fake/output.txt")
        mock_open.assert_any_call("/fake/prompt.txt", "r")
        mock_open.assert_any_call("/fake/output.txt", "w")
        mock_google_gemini_deep_research.assert_called_once_with("file prompt\ntest prompt")

        # Test with only prompt
        mock_google_gemini_deep_research.reset_mock()
        result = await google_gemini_deep_research_full(prompt="test prompt")
        assert result == "## Test Result"
        mock_google_gemini_deep_research.assert_called_once_with("test prompt")

        # Test with only prompt_path
        mock_google_gemini_deep_research.reset_mock()
        mock_open.return_value.read.return_value = "file prompt"
        result = await google_gemini_deep_research_full(prompt_path="/fake/prompt.txt")
        assert result == "## Test Result"
        mock_google_gemini_deep_research.assert_called_once_with("file prompt")

        # Test with no prompt
        with pytest.raises(ValueError):
            await google_gemini_deep_research_full()


@pytest.mark.asyncio
@patch("playpi.providers.google.gemini.create_session")
@patch("playpi.providers.google.gemini._google_gemini_deep_research_on_page")
async def test_google_gemini_deep_research_multi(mock_research_on_page, mock_create_session):
    """Test the google_gemini_deep_research_multi function."""
    mock_session = AsyncMock()
    mock_page = AsyncMock()
    mock_session.new_page.return_value = mock_page
    mock_create_session.return_value.__aenter__.return_value = mock_session
    mock_research_on_page.return_value = "## Test Result"

    config = [
        {"prompt": "prompt1", "output_path": "/fake/output1.txt"},
        {"prompt": "prompt2", "output_path": "/fake/output2.txt"},
    ]

    with patch("builtins.open", new_callable=unittest.mock.mock_open) as mock_open:
        results = await google_gemini_deep_research_multi(config)
        assert len(results) == 2
        assert results[0] == pathlib.Path("/fake/output1.txt")
        assert results[1] == pathlib.Path("/fake/output2.txt")
        assert mock_research_on_page.call_count == 2
        mock_open.assert_any_call("/fake/output1.txt", "w")
        mock_open.assert_any_call("/fake/output2.txt", "w")


@pytest.mark.asyncio
@patch("playpi.providers.google.gemini.create_session")
@patch("playpi.providers.google.gemini._download_generated_image")
async def test_google_gemini_generate_image(mock_download, mock_create_session):
    """Test the google_gemini_generate_image function."""
    mock_session = AsyncMock()
    mock_page = AsyncMock()
    mock_session.get_authenticated_page.return_value = mock_page
    mock_create_session.return_value.__aenter__.return_value = mock_session
    mock_download.return_value = "/fake/image.png"

    with patch("playpi.providers.google.gemini._activate_image_generation", new_callable=AsyncMock) as mock_activate,
         patch("playpi.providers.google.gemini._enter_prompt", new_callable=AsyncMock) as mock_enter_prompt,
         patch("playpi.providers.google.gemini._click_send_button", new_callable=AsyncMock) as mock_click_send,
         patch("playpi.providers.google.gemini._wait_for_image_generation", new_callable=AsyncMock) as mock_wait:
        result = await google_gemini_generate_image("a cat", download_path="/fake")

        assert result == "/fake/image.png"
        mock_activate.assert_called_once_with(mock_page)
        mock_enter_prompt.assert_called_once_with(mock_page, "a cat")
        mock_click_send.assert_called_once_with(mock_page)
        mock_wait.assert_called_once()
        mock_download.assert_called_once_with(mock_page, "/fake")


@pytest.mark.asyncio
@patch("playpi.providers.google.gemini.create_session")
async def test_google_gemini_ask_deep_think(mock_create_session):
    """Test the google_gemini_ask_deep_think function."""
    mock_session = AsyncMock()
    mock_page = AsyncMock()
    mock_session.get_authenticated_page.return_value = mock_page
    mock_create_session.return_value.__aenter__.return_value = mock_session

    with patch("playpi.providers.google.gemini._activate_deep_think", new_callable=AsyncMock) as mock_activate,
         patch("playpi.providers.google.gemini._enter_prompt", new_callable=AsyncMock) as mock_enter_prompt,
         patch("playpi.providers.google.gemini._click_send_button", new_callable=AsyncMock) as mock_click_send,
         patch("playpi.providers.google.gemini._wait_for_completion", new_callable=AsyncMock) as mock_wait,
         patch("playpi.providers.google.gemini.extract_research_content", new_callable=AsyncMock) as mock_extract,
         patch("playpi.providers.google.gemini.html_to_markdown") as mock_markdown:

        mock_extract.return_value = "<h1>Test</h1>"
        mock_markdown.return_value = "# Test"

        result = await google_gemini_ask_deep_think("a thought")

        assert result == "# Test"
        mock_activate.assert_called_once_with(mock_page)
        mock_enter_prompt.assert_called_once_with(mock_page, "a thought")
        mock_click_send.assert_called_once_with(mock_page)
        mock_wait.assert_called_once()
        mock_extract.assert_called_once_with(mock_page)
        mock_markdown.assert_called_once_with("<h1>Test</h1>")


@pytest.mark.asyncio
@patch("playpi.providers.google.gemini.create_session")
async def test_google_gemini_ask(mock_create_session):
    """Test the google_gemini_ask function."""
    mock_session = AsyncMock()
    mock_page = AsyncMock()
    mock_session.get_authenticated_page.return_value = mock_page
    mock_create_session.return_value.__aenter__.return_value = mock_session

    with patch("playpi.providers.google.gemini._enter_prompt", new_callable=AsyncMock) as mock_enter_prompt,
         patch("playpi.providers.google.gemini._click_send_button", new_callable=AsyncMock) as mock_click_send,
         patch("playpi.providers.google.gemini._wait_for_completion", new_callable=AsyncMock) as mock_wait,
         patch("playpi.providers.google.gemini._extract_simple_response", new_callable=AsyncMock) as mock_extract:

        mock_extract.return_value = "## Test Result"

        result = await google_gemini_ask("a question")

        assert result == "## Test Result"
        mock_enter_prompt.assert_called_once_with(mock_page, "a question")
        mock_click_send.assert_called_once_with(mock_page)
        mock_wait.assert_called_once()
        mock_extract.assert_called_once_with(mock_page)
