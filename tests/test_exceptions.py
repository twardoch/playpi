# this_file: tests/test_exceptions.py
"""Tests for PlayPi exceptions."""

import pytest

from playpi.exceptions import (
    AuthenticationError,
    BrowserError,
    PlayPiError,
    PlayPiTimeoutError,
    ProviderError,
    SessionError,
)


def test_exception_hierarchy():
    """Test that all exceptions inherit from PlayPiError."""
    assert issubclass(BrowserError, PlayPiError)
    assert issubclass(AuthenticationError, PlayPiError)
    assert issubclass(ProviderError, PlayPiError)
    assert issubclass(SessionError, PlayPiError)
    assert issubclass(PlayPiTimeoutError, PlayPiError)


def test_exception_creation():
    """Test that exceptions can be created with messages."""
    msg = "Test error message"

    assert str(PlayPiError(msg)) == msg
    assert str(BrowserError(msg)) == msg
    assert str(AuthenticationError(msg)) == msg
    assert str(ProviderError(msg)) == msg
    assert str(SessionError(msg)) == msg
    assert str(PlayPiTimeoutError(msg)) == msg


def test_exception_raising():
    """Test that exceptions can be raised and caught."""
    msg = "Test"

    with pytest.raises(PlayPiError):
        raise PlayPiError(msg)

    with pytest.raises(BrowserError):
        raise BrowserError(msg)

    with pytest.raises(AuthenticationError):
        raise AuthenticationError(msg)

    with pytest.raises(ProviderError):
        raise ProviderError(msg)

    with pytest.raises(SessionError):
        raise SessionError(msg)

    with pytest.raises(PlayPiTimeoutError):
        raise PlayPiTimeoutError(msg)
