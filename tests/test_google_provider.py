# this_file: tests/test_google_provider.py
"""Tests for Google provider functionality."""

import pytest

from playpi.exceptions import AuthenticationError, ProviderError
from playpi.providers.google import google_deep_research


def test_google_deep_research_import():
    """Test that google_deep_research can be imported."""
    assert callable(google_deep_research)


def test_google_deep_research_available_in_main_package():
    """Test that google_deep_research is available from main package."""
    from playpi import google_deep_research as gdr

    assert callable(gdr)


@pytest.mark.asyncio
async def test_google_deep_research_authentication_check():
    """Test that authentication is properly checked."""
    # This should fail with AuthenticationError since we're not logged in
    with pytest.raises((AuthenticationError, ProviderError)):
        await google_deep_research(
            "Test query",
            headless=True,
            timeout=10,  # Short timeout for testing
        )


def test_google_deep_research_parameters():
    """Test that google_deep_research accepts expected parameters."""
    import inspect

    sig = inspect.signature(google_deep_research)
    params = list(sig.parameters.keys())

    # Check that expected parameters are present
    assert "prompt" in params
    assert "headless" in params
    assert "timeout" in params
    assert "profile" in params
    assert "verbose" in params

    # Check that prompt is required (no default)
    assert sig.parameters["prompt"].default == inspect.Parameter.empty

    # Check defaults for optional parameters
    assert sig.parameters["headless"].default is True
    assert sig.parameters["timeout"].default == 600
    assert sig.parameters["profile"].default is None
    assert sig.parameters["verbose"].default is False
