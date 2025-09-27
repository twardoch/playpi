# this_file: tests/test_config.py
"""Tests for PlayPi configuration."""

import platform
from pathlib import Path

import pytest

from playpi.config import PlayPiConfig


def test_default_config():
    """Test default configuration values."""
    config = PlayPiConfig()

    assert config.headless is True
    assert config.timeout == 30000
    assert config.max_concurrent == 3
    assert config.verbose is False
    assert isinstance(config.user_data_dir, Path)
    assert isinstance(config.profiles_dir, Path)
    assert len(config.browser_args) > 0


def test_custom_config():
    """Test custom configuration values."""
    config = PlayPiConfig(
        headless=False,
        timeout=60000,
        max_concurrent=5,
        verbose=True,
    )

    assert config.headless is False
    assert config.timeout == 60000
    assert config.max_concurrent == 5
    assert config.verbose is True


def test_browser_launch_options():
    """Test browser launch options generation."""
    config = PlayPiConfig(headless=False, timeout=45000)
    options = config.get_browser_launch_options()

    assert options["headless"] is False
    assert options["timeout"] == 45000
    assert isinstance(options["args"], list)
    assert len(options["args"]) > 0


def test_platform_specific_args():
    """Test platform-specific browser arguments."""
    config = PlayPiConfig()
    args = config.browser_args

    # All platforms should have these
    assert "--no-first-run" in args
    assert "--no-default-browser-check" in args

    # Platform-specific checks
    system = platform.system().lower()
    if system == "darwin":
        assert "--disable-gpu-sandbox" in args
    elif system in ["windows", "linux"]:
        assert "--disable-gpu" in args


def test_directories_created():
    """Test that configuration directories are created."""
    config = PlayPiConfig()

    assert config.user_data_dir.exists()
    assert config.profiles_dir.exists()
    assert config.profiles_dir.parent == config.user_data_dir
