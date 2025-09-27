# this_file: tests/test_session.py
"""Tests for PlayPi session management built on playwrightauthor."""

import pytest

from playpi.config import PlayPiConfig
from playpi.exceptions import BrowserError, SessionError
from playpi.session import PlayPiSession, create_session


async def _ensure_session(config: PlayPiConfig | None = None) -> PlayPiSession:
    session = PlayPiSession(config)
    try:
        await session.start()
        return session
    except BrowserError as exc:  # pragma: no cover - dependent on local Chrome setup
        pytest.skip(f"playwrightauthor unavailable: {exc}")


@pytest.mark.asyncio
async def test_session_lifecycle():
    config = PlayPiConfig(timeout=10_000)
    session = await _ensure_session(config)

    new_session = PlayPiSession(config)
    with pytest.raises(SessionError):
        await new_session.get_page()
    await new_session.close()

    page = await session.get_page()
    assert page is not None

    await session.close()

    with pytest.raises(SessionError):
        await session.get_page()


@pytest.mark.asyncio
async def test_session_context_manager():
    config = PlayPiConfig(timeout=10_000)
    try:
        async with create_session(config) as session:
            page = await session.get_page()
            assert page is not None
    except BrowserError as exc:  # pragma: no cover - depends on local Chrome setup
        pytest.skip(f"playwrightauthor unavailable: {exc}")


@pytest.mark.asyncio
async def test_create_session_helper():
    config = PlayPiConfig(timeout=10_000)

    async with create_session(config) as session:
        page = await session.get_page()
        assert page is not None


@pytest.mark.asyncio
async def test_get_authenticated_page():
    config = PlayPiConfig(timeout=10_000)

    async with create_session(config) as session:
        page = await session.get_authenticated_page("google")
        assert page is not None


@pytest.mark.asyncio
async def test_session_with_default_config():
    async with create_session() as session:
        page = await session.get_page()
        assert page is not None
