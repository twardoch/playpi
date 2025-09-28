# this_file: src/playpi/cli.py
"""Legacy entry point delegating to `playpi.__main__`."""

from __future__ import annotations

from playpi.__main__ import main

__all__ = ["main"]


if __name__ == "__main__":
    main()
