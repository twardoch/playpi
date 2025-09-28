this_file: DEPENDENCIES.md
---

# Dependency Overview

## Core Runtime Packages
- playwright>=1.40.0 — Chromium automation layer
- playwrightauthor>=1.0.13 — Authoring utilities for Playwright sessions
- pydantic>=2.0.0 — Data validation and settings management
- rich>=13.0.0 — Terminal rendering for CLI output
- fire>=0.5.0 — CLI argument parsing and command dispatcher
- loguru>=0.7.0 — Structured logging with minimal boilerplate
- html2text>=2020.1.16 — HTML to Markdown conversion helpers
- platformdirs>=3.0.0 — Cross-platform directory resolution

## Development Extras (`playpi[dev]`)
- pre-commit>=4.1.0 — Pre-commit hook orchestration
- ruff>=0.9.7 — Linting and formatting
- mypy>=1.15.0 — Static type checking
- absolufy-imports>=0.3.1 — Import normalization
- pyupgrade>=3.19.1 — Syntax modernization
- isort>=6.0.1 — Import sorting

## Test Extras (`playpi[test]`)
- pytest>=8.3.4 — Core test runner
- pytest-cov>=6.0.0 — Coverage reporting
- pytest-xdist>=3.6.1 — Parallel test execution
- pytest-benchmark[histogram]>=5.1.0 — Performance baseline tracking
- pytest-asyncio>=0.25.3 — Async test integration
- pytest-playwright>=0.4.0 — Playwright fixtures and helpers
- coverage[toml]>=7.6.12 — Coverage measurement backend

## Documentation Extras (`playpi[docs]`)
- sphinx>=7.2.6 — Documentation generator
- sphinx-rtd-theme>=2.0.0 — Read the Docs theme
- sphinx-autodoc-typehints>=2.0.0 — Type hint integration for docs
- myst-parser>=3.0.0 — CommonMark and MyST support in Sphinx

## Build Tooling
- hatchling>=1.27.0 — Build backend
- hatch-vcs>=0.4.0 — VCS-integrated versioning

## Verification Notes
- Async-enabled tests must be executed with `PLAYPI_FORCE_AUTH_FAILURE=1 uvx hatch run test:python -m pytest` to ensure pytest-asyncio loads under Hatch.
