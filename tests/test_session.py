# this_file: tests/test_session.py
"""Tests for PlayPi session management."""

import pytest

from playpi.config import PlayPiConfig
from playpi.exceptions import SessionError
from playpi.session import PlayPiSession, create_session


@pytest.mark.asyncio
async def test_session_lifecycle():
    """Test basic session lifecycle."""
    config = PlayPiConfig(headless=True, timeout=10000)
    session = PlayPiSession(config)

    # Session should not be started initially
    with pytest.raises(SessionError):
        await session.get_page()

    # Start session
    await session.start()

    # Should be able to get page now
    page = await session.get_page()
    assert page is not None

    # Close session
    await session.close()

    # Should not be able to get page after closing
    with pytest.raises(SessionError):
        await session.get_page()


@pytest.mark.asyncio
async def test_session_context_manager():
    """Test session as async context manager."""
    config = PlayPiConfig(headless=True, timeout=10000)

    async with PlayPiSession(config) as session:
        page = await session.get_page()
        assert page is not None


@pytest.mark.asyncio
async def test_create_session_helper():
    """Test create_session helper function."""
    config = PlayPiConfig(headless=True, timeout=10000)

    async with create_session(config) as session:
        page = await session.get_page()
        assert page is not None


@pytest.mark.asyncio
async def test_get_authenticated_page():
    """Test getting authenticated page for a provider."""
    config = PlayPiConfig(headless=True, timeout=10000)

    async with create_session(config) as session:
        page = await session.get_authenticated_page("google")
        assert page is not None


@pytest.mark.asyncio
async def test_session_with_default_config():
    """Test session with default configuration."""
    async with create_session() as session:
        page = await session.get_page()
        assert page is not None
