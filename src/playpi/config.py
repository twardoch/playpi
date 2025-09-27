# this_file: src/playpi/config.py
"""Configuration management for PlayPi package."""

import platform
from dataclasses import dataclass, field
from pathlib import Path

from platformdirs import user_data_dir


@dataclass
class PlayPiConfig:
    """Configuration for PlayPi browser automation.

    Attributes:
        headless: Run browser in headless mode
        timeout: Default timeout for operations in milliseconds
        max_concurrent: Maximum number of concurrent browser sessions
        browser_args: Additional arguments to pass to browser
        user_data_dir: Directory for browser user data
        profiles_dir: Directory for browser profiles
        verbose: Enable verbose logging
    """

    headless: bool = True
    timeout: int = 30000  # 30 seconds
    max_concurrent: int = 3
    browser_args: list[str] = field(default_factory=list)
    user_data_dir: Path | None = None
    profiles_dir: Path | None = None
    verbose: bool = False

    def __post_init__(self) -> None:
        """Set default paths and platform-specific browser arguments."""
        if self.user_data_dir is None:
            self.user_data_dir = Path(user_data_dir("playpi", "playpi"))

        if self.profiles_dir is None:
            self.profiles_dir = self.user_data_dir / "profiles"

        # Ensure directories exist
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

        # Add platform-specific browser arguments
        if not self.browser_args:
            self.browser_args = self._get_platform_browser_args()

    def _get_platform_browser_args(self) -> list[str]:
        """Get platform-specific browser arguments."""
        args = []

        # Common arguments for all platforms
        args.extend(
            [
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-web-security",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
            ]
        )

        # Platform-specific optimizations
        system = platform.system().lower()

        if system == "darwin":  # macOS
            args.extend(
                [
                    "--disable-gpu-sandbox",  # Fix for Apple Silicon
                    "--disable-software-rasterizer",
                ]
            )
        elif system == "windows":
            args.extend(
                [
                    "--disable-gpu",
                    "--window-size=1920,1080",
                ]
            )
        elif system == "linux":
            args.extend(
                [
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ]
            )

        return args

    def get_browser_launch_options(self) -> dict:
        """Get browser launch options for Playwright."""
        return {
            "headless": self.headless,
            "args": self.browser_args,
            "timeout": self.timeout,
        }
