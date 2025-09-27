# PlayPi Package Specification

## Overview

PlayPi is a modular Python package that provides simple, accessible functions for automating browser interactions with Large Language Models (LLMs). The package wraps complex Playwright automation workflows into easy-to-use functions, enabling users to programmatically interact with various LLM chat interfaces through a unified API.

## Core Objectives

1. **Simplicity**: Provide single-function calls for complex LLM interactions
2. **Modularity**: Support multiple LLM providers through a unified interface
3. **Reliability**: Leverage proven browser automation patterns from existing projects
4. **Session Management**: Maintain persistent authentication and conversation contexts
5. **Cross-Platform**: Work consistently across Windows, macOS, and Linux

## Reference Implementation

The specification is informed by the example function `google_deep_research(input_prompt: str) -> str` found in `@01in/playwright-google-deep-research.py`, which demonstrates the target API simplicity.

## Architecture

### Core Package Structure

```
src/playpi/
├── __init__.py              # Main API exports
├── core/                    # Core infrastructure
│   ├── config.py           # Configuration management
│   ├── exceptions.py       # Custom exceptions
│   ├── session.py          # Session management
│   └── __init__.py
├── browser/                 # Browser automation layer
│   ├── manager.py          # Browser lifecycle management
│   ├── automation.py       # Core automation functions
│   └── __init__.py
├── providers/               # LLM provider modules
│   ├── base.py             # Abstract base provider
│   ├── gemini.py           # Google Gemini integration
│   ├── chatgpt.py          # OpenAI ChatGPT integration
│   ├── claude.py           # Anthropic Claude integration
│   └── __init__.py
├── utils/                   # Utility functions
│   ├── paths.py            # Cross-platform path management
│   ├── logger.py           # Logging configuration
│   ├── serialization.py    # JSON/data serialization
│   └── __init__.py
└── cli.py                   # Command-line interface
```

## Core Components

### 1. Browser Management (`browser/`)

Based on proven patterns from PlaywrightAuthor and geminpy projects:

#### `manager.py`
- **Purpose**: Manage browser lifecycle, installation, and process management
- **Key Features**:
  - Automatic Chrome for Testing installation
  - Cross-platform browser detection and setup
  - Process cleanup and resource management
  - Session persistence through browser profiles
  - Platform-specific optimizations (macOS GPU sandbox, Windows viewport, Linux headless)

#### `automation.py`
- **Purpose**: Core automation functions and element interaction
- **Key Features**:
  - Role-based element selection for reliability
  - Async/await patterns for non-blocking operations
  - Timeout management and error recovery
  - Page navigation and content extraction
  - Generic interaction patterns (click, type, wait)

### 2. Provider Modules (`providers/`)

Each provider module implements the standardized interface for specific LLM services:

#### `base.py` - Abstract Provider Interface
```python
class BaseLLMProvider:
    async def open_chat(self, **kwargs) -> Page
    async def send_prompt(self, page: Page, prompt: str) -> str
    async def get_response(self, page: Page) -> str
    async def close_session(self, page: Page) -> None
```

#### Provider-Specific Implementations

**`gemini.py`** - Google Gemini Provider
- Navigate to gemini.google.com
- Handle Google authentication flows
- Support for Deep Research mode activation
- Export and content extraction capabilities
- Based on patterns from `playwright-google-deep-research.py`

**`chatgpt.py`** - OpenAI ChatGPT Provider
- Navigate to chat.openai.com
- Handle OpenAI authentication
- Support for different model selection
- Conversation history management
- Response streaming handling

**`claude.py`** - Anthropic Claude Provider
- Navigate to claude.ai
- Handle Anthropic authentication
- Support for document uploads
- Multi-turn conversation management
- Context window optimization

### 3. Session Management (`core/session.py`)

Inspired by Virginia Clemm Poe's browser pooling system:

- **Connection Pooling**: Maintain pools of authenticated browser sessions
- **Session Reuse**: Preserve authentication across multiple interactions
- **Health Monitoring**: Automatic detection and recovery from stale sessions
- **Resource Management**: Proper cleanup and memory management
- **Profile Isolation**: Separate browser profiles for different accounts/services

### 4. Configuration System (`core/config.py`)

Based on geminpy's configuration patterns:

```python
@dataclass
class PlayPiConfig:
    headless: bool = True
    timeout: int = 30000
    browser_args: List[str] = field(default_factory=list)
    user_data_dir: Optional[Path] = None
    profiles_dir: Optional[Path] = None
    verbose: bool = False
```

Platform-specific configurations:
- **macOS**: Disable GPU sandbox for Apple Silicon compatibility
- **Windows**: Optimized viewport dimensions
- **Linux**: Headless mode for server environments

### 5. Utility Infrastructure (`utils/`)

Leveraging proven patterns from existing projects:

#### `paths.py`
- Cross-platform directory management using `platformdirs`
- Browser installation paths
- User data and configuration directories
- Session storage locations

#### `serialization.py`
- Custom JSON serializers for datetime objects
- Pydantic model serialization support
- Conversation history persistence
- Response caching mechanisms

#### `logger.py`
- Loguru-based structured logging
- Configurable verbosity levels
- Debug mode with screenshot capture
- Performance metrics tracking

## Public API

### Primary Functions

The main user-facing API provides simple function calls for complex operations:

```python
# Single-shot interactions
async def chat_with_gemini(prompt: str, **kwargs) -> str
async def chat_with_chatgpt(prompt: str, **kwargs) -> str
async def chat_with_claude(prompt: str, **kwargs) -> str

# Session-based interactions
async def open_chat_session(provider: str, **kwargs) -> ChatSession
class ChatSession:
    async def send_message(self, prompt: str) -> str
    async def get_history(self) -> List[Dict]
    async def close(self) -> None

# Multi-provider interface
async def chat_with_model(provider: str, prompt: str, **kwargs) -> str

# Deep research mode (Gemini-specific)
async def google_deep_research(prompt: str, **kwargs) -> str
```

### Configuration Options

```python
# Global configuration
configure_playpi(
    headless=True,
    timeout=30000,
    user_data_dir="/path/to/data",
    verbose=False
)

# Per-function configuration
response = await chat_with_gemini(
    "What is quantum computing?",
    timeout=60000,
    headless=False,
    profile="research_profile"
)
```

## Implementation Strategy

### Phase 1: Core Infrastructure
1. Set up browser management based on PlaywrightAuthor patterns
2. Implement cross-platform path management
3. Create base provider interface
4. Add basic logging and configuration

### Phase 2: Provider Implementation
1. Implement Gemini provider based on existing script
2. Add ChatGPT provider with OpenAI authentication
3. Create Claude provider with Anthropic integration
4. Test cross-provider functionality

### Phase 3: Session Management
1. Implement connection pooling system
2. Add session persistence and reuse
3. Create health monitoring and recovery
4. Optimize resource management

### Phase 4: Advanced Features
1. Add conversation history tracking
2. Implement response caching
3. Create CLI interface using Fire
4. Add performance monitoring and benchmarks

## Error Handling

### Exception Hierarchy
```python
class PlayPiError(Exception): pass
class BrowserError(PlayPiError): pass
class AuthenticationError(PlayPiError): pass
class ProviderError(PlayPiError): pass
class SessionError(PlayPiError): pass
class TimeoutError(PlayPiError): pass
```

### Recovery Strategies
- **Browser Crashes**: Automatic browser restart and session recovery
- **Authentication Failures**: Clear guidance for re-authentication
- **Network Issues**: Retry logic with exponential backoff
- **Provider Changes**: Graceful degradation and user notification
- **Timeout Handling**: Configurable timeouts with proper cleanup

## Dependencies

### Core Dependencies
- `playwright` - Browser automation
- `pydantic` - Data validation and serialization
- `platformdirs` - Cross-platform path management
- `loguru` - Structured logging
- `fire` - CLI interface
- `rich` - Terminal output formatting

### Optional Dependencies
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `mypy` - Type checking

## Testing Strategy

### Test Categories
1. **Unit Tests**: Individual function testing with mocks
2. **Integration Tests**: End-to-end provider testing
3. **Cross-Platform Tests**: Compatibility across operating systems
4. **Performance Tests**: Response time and resource usage benchmarks
5. **Browser Tests**: Real browser automation validation

### Test Infrastructure
Based on Virginia Clemm Poe's comprehensive test suite:
- Browser lifecycle testing
- Session persistence validation
- Authentication flow testing
- Error condition handling
- Performance benchmarking

## Security Considerations

### Best Practices
- **Browser Isolation**: Separate profiles for different accounts
- **Local Operation**: All automation happens locally via CDP
- **No Credential Storage**: Store only email preferences, not passwords
- **Session Security**: Proper cleanup of sensitive browser data
- **Resource Cleanup**: Ensure browsers and connections are properly closed

### Privacy Protection
- **User Data Control**: Clear control over data storage locations
- **Profile Management**: Isolated profiles prevent cross-contamination
- **Cache Management**: Configurable cache retention policies
- **Logging Control**: Sensitive data exclusion from logs

## Performance Optimization

### Connection Pooling
- Reuse browser instances across multiple interactions
- Maintain authenticated sessions to avoid re-login
- Implement LRU eviction for resource management
- Platform-specific pool sizing based on system capabilities

### Caching Strategy
- Cache frequently used responses with TTL
- Store conversation contexts for session continuity
- Implement intelligent cache invalidation
- Support for custom cache backends

### Resource Management
- Automatic garbage collection for browser instances
- Memory monitoring and leak prevention
- Process cleanup on abnormal termination
- Configurable resource limits

## Documentation

### User Documentation
- Quick start guide with common examples
- Provider-specific setup instructions
- Configuration reference
- Troubleshooting guide

### Developer Documentation
- Architecture overview
- Adding new providers
- Contributing guidelines
- API reference with type hints

## Future Extensions

### Planned Features
1. **Multi-Modal Support**: Image, audio, and video input handling
2. **Streaming Responses**: Real-time response streaming for long outputs
3. **Conversation Templates**: Pre-defined prompt templates and workflows
4. **Plugin System**: Third-party provider integration framework
5. **Monitoring Dashboard**: Web-based session and performance monitoring

### Provider Expansion
- **Perplexity**: Web search integration
- **Cohere**: Enterprise AI capabilities
- **Hugging Face**: Open model integration
- **Local Models**: Support for self-hosted LLMs
- **Custom Providers**: Framework for adding proprietary LLMs

## Success Criteria

### Functional Requirements
1. ✓ Single function calls for LLM interactions
2. ✓ Support for major LLM providers (Gemini, ChatGPT, Claude)
3. ✓ Cross-platform compatibility
4. ✓ Session persistence and reuse
5. ✓ Robust error handling and recovery

### Performance Requirements
1. ✓ < 5 second initial session startup
2. ✓ < 2 second subsequent interactions
3. ✓ Support for concurrent sessions
4. ✓ Memory usage < 200MB per session
5. ✓ 99% success rate for basic interactions

### Quality Requirements
1. ✓ 90%+ test coverage
2. ✓ Type hints throughout codebase
3. ✓ Comprehensive documentation
4. ✓ Zero-dependency core functions
5. ✓ Semantic versioning compliance

## Conclusion

PlayPi provides a robust, modular foundation for LLM browser automation by leveraging proven patterns from existing projects while maintaining simplicity in its public API. The architecture supports extensibility, reliability, and performance while hiding the complexity of browser automation from end users.

The specification builds on the strengths of PlaywrightAuthor's browser management, geminpy's OAuth automation, and Virginia Clemm Poe's session pooling to create a unified package that makes LLM automation accessible through simple function calls like `google_deep_research(input_prompt: str) -> str`.