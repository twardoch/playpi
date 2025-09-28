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

### Changed
- Restructured provider code into google/auth.py and google/gemini.py modules
- Renamed functions to follow google_gemini_* convention for clarity
- Updated imports and entry points across the codebase
- Improved test coverage for all new API functions

### Added
- Comprehensive test suite for new Google Gemini functions
- Support for Deep Research, Image Generation, Deep Think, and standard prompts
- Async context manager support for better resource management
- Enhanced error handling and response parsing

### Technical
- Test files now use proper async/await patterns with pytest-asyncio
- Improved code formatting and linting compliance
- Enhanced type hints and documentation