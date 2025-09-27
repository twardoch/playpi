# PlayPi Package Implementation Plan

## Problem Analysis
We need to implement a Python package that provides simple, high-level functions for automating browser-based AI chat workflows. The specifications reference `playwrightauthor` extensively, but this package doesn't exist publicly. We need to implement equivalent session management and browser automation functionality ourselves using standard Playwright.

## Constraints
- Must use `hatch` and `hatch-vcs` for build system
- Must use `uv` for dependency management
- Must use `ruff` for linting
- Must focus on lean, clean, performant code
- Max 3 concurrent browser sessions by default
- Browser memory usage limitations
- Cross-platform compatibility (Windows, macOS, Linux)

## Solution Options
1. **Build from scratch** - Implement all browser management and session handling ourselves
2. **Minimal wrapper** - Use standard Playwright with basic session management
3. **Hybrid approach** - Implement core session management while leveraging existing patterns

**Selected**: Hybrid approach - implement core session management with proven patterns from the example code.

## Edge Cases
- Browser crashes during long-running operations
- Network timeouts during authentication
- UI layout changes on target websites
- Multiple concurrent sessions exceeding memory limits
- Authentication token expiration
- Cross-platform browser installation differences

## Test Strategy
- Unit tests for core functions with mocked browser interactions
- Integration tests with real browser instances (opt-in)
- Smoke tests for basic workflows
- Memory usage and performance benchmarks
- Cross-platform compatibility tests

## Implementation Plan

### Phase 1: Core Infrastructure (Priority 1)

#### 1.1 Project Setup
- **Package Structure**: Create standard Python package structure with `src/playpi/`
- **Build System**: Configure `hatch` with `hatch-vcs` for git-tag-based versioning
- **Dependencies**: Set up `uv` for dependency management with core packages:
  - `playwright` - Browser automation
  - `pydantic` - Data validation and serialization
  - `rich` - Terminal output formatting
  - `fire` - CLI interface
  - `loguru` - Structured logging
  - `html2text` - HTML to Markdown conversion
  - `asyncio` - Async support
- **Development Tools**: Configure `ruff`, `pytest`, `pytest-cov`, `pytest-asyncio`

#### 1.2 Core Session Management (`src/playpi/session.py`)
Replace the missing `playwrightauthor` functionality with our own implementation:

```python
class PlayPiSession:
    """Manages browser lifecycle and authentication state"""

    async def __aenter__(self) -> 'PlayPiSession':
        """Async context manager entry"""

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensure cleanup on exit"""

    async def get_authenticated_page(self, provider: str) -> Page:
        """Get authenticated page for provider"""

    async def close(self):
        """Clean shutdown of browser resources"""
```

**Key Features:**
- **Browser Lifecycle**: Automatic Chrome installation and process management
- **Authentication State**: Persistent browser profiles for session reuse
- **Resource Management**: Proper cleanup and memory management
- **Cross-Platform**: Platform-specific optimizations (macOS GPU sandbox, Windows viewport, Linux headless)

#### 1.3 Configuration System (`src/playpi/config.py`)
```python
@dataclass
class PlayPiConfig:
    headless: bool = True
    timeout: int = 30000
    max_concurrent: int = 3
    browser_args: List[str] = field(default_factory=list)
    user_data_dir: Optional[Path] = None
    profiles_dir: Optional[Path] = None
    verbose: bool = False
```

#### 1.4 Exception Hierarchy (`src/playpi/exceptions.py`)
```python
class PlayPiError(Exception): pass
class BrowserError(PlayPiError): pass
class AuthenticationError(PlayPiError): pass
class ProviderError(PlayPiError): pass
class SessionError(PlayPiError): pass
class PlayPiTimeoutError(PlayPiError): pass
```

### Phase 2: Google Deep Research Implementation (Priority 1)

#### 2.1 Provider Base Class (`src/playpi/providers/base.py`)

#### 2.2 Google Gemini Provider (`src/playpi/providers/google.py`)
Based on the existing script in `external/01in/playwright-google-deep-research.py`:

```python
async def google_deep_research(
    prompt: str,
    *,
    headless: bool = True,
    timeout: int = 600,
    profile: Optional[str] = None
) -> str:
    """
    Perform Google Gemini Deep Research

    Args:
        prompt: Research query
        headless: Run browser in headless mode
        timeout: Maximum wait time in seconds
        profile: Browser profile name for authentication

    Returns:
        Research result as Markdown string

    Raises:
        AuthenticationError: If Google authentication fails
        PlayPiTimeoutError: If research exceeds timeout
        ProviderError: If UI elements not found
    """
```

**Implementation Steps:**
1. Navigate to `https://gemini.google.com/u/0/app`
2. Handle authentication (manual login required first time)
3. Enter prompt in text area: `page.get_by_role("textbox", name="Enter a prompt here")`
4. Click Tools button and select Deep Research
5. Submit prompt and wait for confirmation dialog
6. Click confirm button to start research
7. Wait for completion (export button becomes available)
8. Extract result HTML and convert to Markdown
9. Return cleaned Markdown text

#### 2.3 HTML Processing (`src/playpi/html.py`)
```python
def html_to_markdown(html_content: str) -> str:
    """Convert HTML content to clean Markdown"""

def extract_research_content(page: Page) -> str:
    """Extract research content from page"""
```

### Phase 3: Session Management & Connection Pooling (Priority 2)

#### 3.1 Session Pool (`src/playpi/pool.py`)
```python
class SessionPool:
    """Manage pool of browser sessions with max concurrency limits"""

    def __init__(self, max_concurrent: int = 3):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.sessions: Dict[str, PlayPiSession] = {}

    async def acquire_session(self, provider: str) -> PlayPiSession:
        """Get or create session for provider"""

    async def release_session(self, provider: str):
        """Return session to pool"""

    async def cleanup(self):
        """Close all sessions"""
```

#### 3.2 Concurrent Execution
Implement semaphore-based concurrency control from the example in `issues/101.md`:

```python
class ResearchRunner:
    def __init__(self, max_concurrent=3):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def run_single_research(self, research_id, query):
        async with self.semaphore:  # Ensures only 3 run at once
            # Actual research logic here
```

### Phase 4: CLI Interface & Additional Features (Priority 3)

#### 4.1 CLI Interface (`src/playpi/cli.py`)
```python
def main():
    """Main CLI entry point using Fire"""

def google_deep_research_cli(prompt: str, **kwargs):
    """CLI wrapper for google_deep_research"""

def batch_research(prompts_file: str, **kwargs):
    """Process multiple research queries from file"""
```

#### 4.2 Additional Providers (Future)
- `src/playpi/providers/chatgpt.py` - OpenAI ChatGPT integration
- `src/playpi/providers/claude.py` - Anthropic Claude integration

### Phase 5: Testing & Quality Assurance (Priority 1)

#### 5.1 Test Structure
```
tests/
├── test_session.py           # Session management tests
├── test_google_provider.py   # Google Deep Research tests
├── test_html_processing.py   # HTML conversion tests
├── test_pool.py             # Connection pooling tests
├── test_cli.py              # CLI interface tests
└── conftest.py              # Pytest configuration
```

#### 5.2 Test Categories
1. **Unit Tests**: Mock browser interactions, test individual functions
2. **Integration Tests**: Real browser automation (opt-in with `pytest -m integration`)
3. **Performance Tests**: Memory usage, response times, concurrent sessions
4. **Cross-Platform Tests**: Windows, macOS, Linux compatibility

#### 5.3 Test Requirements
- 90%+ test coverage
- All functions must have tests
- Mock external dependencies in unit tests
- Use `pytest-playwright` for browser tests, enabling video/trace recording on failure to simplify debugging.
- Performance benchmarks for memory and timing

### Phase 6: Documentation & Packaging

#### 6.1 Documentation Files
- `README.md` - Quick start guide (under 200 lines)
- `DEPENDENCIES.md` - Package dependencies and justification
- `CHANGELOG.md` - Version history
- `docs/` - Detailed documentation

#### 6.2 Package Configuration
- `pyproject.toml` - Hatch configuration with `hatch-vcs`
- `src/playpi/__init__.py` - Public API exports
- Version from git tags using `hatch-vcs`

## Technical Architecture

### Package Structure
```
src/playpi/
├── __init__.py              # Public API exports
├── session.py               # Browser session management
├── config.py                # Configuration classes
├── exceptions.py            # Custom exceptions
├── pool.py                  # Session pooling
├── html.py                  # HTML processing utilities
├── providers/               # LLM provider implementations
│   ├── __init__.py
│   ├── base.py             # Abstract base provider
│   └── google.py           # Google Gemini provider
└── cli.py                   # Command-line interface
```

### Public API
```python
# Simple function calls
async def google_deep_research(prompt: str, **kwargs) -> str

# Session-based usage
async def open_session(provider: str, **kwargs) -> PlayPiSession

# Multi-query processing
async def batch_research(prompts: List[str], **kwargs) -> List[str]

# Configuration
def configure_playpi(**kwargs) -> None

### Architectural Note
The high-level functions (`google_deep_research`, `batch_research`) will internally use the `SessionPool` to acquire a `PlayPiSession`. This session provides an authenticated `Page` object, which is then passed to a provider-specific class (e.g., `GoogleGeminiProvider`) to manage UI interactions. This composes the low-level components into a simple, high-level API.
```

## Dependencies Strategy

### Core Dependencies (Required)
- `playwright` - Browser automation engine
- `pydantic` - Data validation and configuration
- `rich` - Terminal output formatting
- `fire` - CLI interface generation
- `loguru` - Structured logging
- `html2text` - HTML to Markdown conversion

### Development Dependencies
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `pytest-playwright` - Browser testing
- `ruff` - Linting and formatting
- `mypy` - Type checking

### Build Dependencies
- `hatch` - Build system
- `hatch-vcs` - Git-based versioning
- `uv` - Fast dependency resolution

## Risk Mitigation

### UI Drift Risk (High)
- **Mitigation**: Store selectors as constants, verbose error messages with screenshots
- **Detection**: Regular integration tests, user reports
- **Response**: Fast selector updates, fallback strategies

### Authentication Failures (Medium)
- **Mitigation**: Clear setup instructions, helpful error messages
- **Detection**: Test authentication flows regularly
- **Response**: Detailed troubleshooting guides

### Memory Issues (Medium)
- **Mitigation**: Session pooling, automatic cleanup, monitoring
- **Detection**: Memory usage tests, production monitoring
- **Response**: Resource limits, garbage collection

### Cross-Platform Issues (Low)
- **Mitigation**: Platform-specific configurations, CI testing
- **Detection**: Multi-platform test matrix
- **Response**: Platform-specific workarounds

### Anti-Bot Measures (Medium-High)
- **Risk**: Websites may employ CAPTCHAs, rate limiting, or other anti-automation techniques.
- **Mitigation**: Use robust, human-like interaction patterns. For CAPTCHAs, the primary mitigation is reusing authenticated sessions where challenges are less frequent. The system should detect challenges and exit gracefully with a clear error.
- **Detection**: Integration tests failing on new, unexpected UI elements or prompts.
- **Response**: Update automation logic. For persistent blocks, this may require manual intervention or exploring alternative providers/APIs.

## Success Criteria

### Functional Requirements
- ✅ Single function call for Google Deep Research
- ✅ Session persistence and reuse
- ✅ Cross-platform compatibility
- ✅ Robust error handling and recovery
- ✅ Memory efficient concurrent execution

### Performance Requirements
- ✅ < 10 second initial session startup
- ✅ < 3 second subsequent interactions
- ✅ Support for 3 concurrent sessions
- ✅ Memory usage < 300MB per session
- ✅ 95% success rate for basic operations

### Quality Requirements
- ✅ 90%+ test coverage
- ✅ Type hints throughout codebase
- ✅ Comprehensive documentation
- ✅ Semantic versioning compliance
- ✅ Clean code standards (functions < 20 lines, files < 200 lines)

## Implementation Timeline (Revised to 6 Weeks for Realism)

*Browser automation is often unpredictable. This revised timeline allocates more time for testing, debugging, and documentation throughout the process.*

### Sprint 1 (Weeks 1-2): Core & Google Provider
- **Goal**: A working `google_deep_research` function for a single query.
- **Tasks**:
    - Project setup (`hatch`, `uv`, `ruff`).
    - Implement `PlayPiSession`, `PlayPiConfig`, and `PlayPiError` hierarchy.
    - Implement the `google_deep_research` workflow, including authentication and HTML processing.
    - **Testing**: Write unit tests for config and HTML processing. Write an initial integration test for the full Google workflow.

### Sprint 2 (Weeks 3-4): Concurrency & Robustness
- **Goal**: Support for robust, concurrent research tasks.
- **Tasks**:
    - Implement `SessionPool` for concurrent browser management.
    - Refactor `google_deep_research` and implement `batch_research` to use the pool.
    - Implement comprehensive error handling and logging.
    - **Testing**: Write unit and integration tests for the session pool. Add tests for failure cases (e.g., auth failure, timeout). Aim for 70% coverage.

### Sprint 3 (Weeks 5-6): CLI, Docs & Release
- **Goal**: A polished, installable package.
- **Tasks**:
    - Implement the CLI using `fire`.
    - Write all user-facing documentation (`README.md`, etc.).
    - Finalize packaging configuration (`pyproject.toml`).
    - **Testing**: Write tests for the CLI. Perform full cross-platform testing. Run performance benchmarks. Increase test coverage to 90%+.
    - Prepare for `v0.1.0` release.

## Next Steps

1. **Initialize Project**: Set up package structure with `hatch` and `uv`
2. **Core Session Management**: Implement `PlayPiSession` class
3. **Google Provider**: Build working Google Deep Research function
4. **Testing**: Write comprehensive test suite
5. **Documentation**: Create user and developer documentation
6. **Release**: Package and distribute v0.1.0

This plan provides a solid foundation for implementing the PlayPi package while maintaining simplicity and focusing on the core functionality of browser automation for AI chat workflows.