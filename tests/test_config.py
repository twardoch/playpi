# this_file: tests/test_config.py
"""Tests for the simplified PlayPi configuration layer."""

from playpi.config import PlayPiConfig


def test_default_config_values():
    config = PlayPiConfig()

    assert config.headless is True
    assert config.timeout == 30_000
    assert config.verbose is False
    assert config.profile == "default"
    assert config.playwrightauthor_kwargs() == {"verbose": False, "profile": "default"}


def test_custom_config_values():
    config = PlayPiConfig(headless=False, timeout=45_000, verbose=True, profile="custom")

    assert config.headless is False
    assert config.timeout == 45_000
    assert config.verbose is True
    assert config.profile == "custom"
    assert config.playwrightauthor_kwargs() == {"verbose": True, "profile": "custom"}
