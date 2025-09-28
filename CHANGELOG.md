this_file: CHANGELOG.md
---

# Changelog

All notable changes to PlayPi will be documented in this file.

## [Unreleased]

### Fixed
- Fixed syntax errors in test files with async context managers
- Fixed import errors in test_google_provider.py to use correct function names
- Resolved pytest-asyncio plugin loading issues
- Fixed line continuation syntax in multi-line with statements
- Restored Deep Research confirmation workflow with resilient selectors and fallbacks
- Corrected Gemini prompt, Deep Think, and image flows to pass timeout values in seconds to wait helpers (issues/110)

### Changed
- Restructured provider code into google/auth.py and google/gemini.py modules
- Renamed functions to follow google_gemini_* convention for clarity
- Updated imports and entry points across the codebase
- Improved test coverage for all new API functions
- CLI entry point now routes through `playpi.__main__` with helper module delegation

### Added
- Comprehensive test suite for new Google Gemini functions
- Support for Deep Research, Image Generation, Deep Think, and standard prompts
- Async context manager support for better resource management
- Enhanced error handling and response parsing
- `gemi` and `gemi_dr` CLI commands with stdin JSON ingestion and Deep Think support
- Regression tests for CLI helpers and confirmation widget handling

### Technical
- Test files now use proper async/await patterns with pytest-asyncio
- Improved code formatting and linting compliance
- Enhanced type hints and documentation
- Added `PLAYPI_FORCE_AUTH_FAILURE` environment guard to disable live authentication during automated tests
- Documented reliable test command (`PLAYPI_FORCE_AUTH_FAILURE=1 uvx hatch run test:python -m pytest`) to exercise asyncio suites successfully
- Re-verified `PLAYPI_FORCE_AUTH_FAILURE=1 uvx hatch run test:python -m pytest` executes 34 tests successfully (wrapper exits with timeout after summary)
