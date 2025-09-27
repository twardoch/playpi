---
this_file: spec-gpt.md
---

# playpi Package Specification

## 1. Scope (Single Sentence)
Automate opinionated AI chat workflows through Playwright by wrapping `playwrightauthor` sessions into simple, high-level Python functions such as `google_deep_research()` that return clean text output.

## 2. Product Goals
- Deliver a tiny, dependency-light Python package that exposes documented functions for specific browser automations.
- Reuse `playwrightauthor` abstractions for browser/process management; only add glue code plus selectors and parsing logic.
- Provide deterministic text responses for each supported workflow with optional debugging output.
- Ship with tests, docs, and examples that let users run each workflow in under five commands.

## 3. Non-Goals
- No generic "automate any website" API.
- No build-your-own workflow builder, configuration DSL, or GUI.
- No persistent background services, analytics, telemetry, or enterprise auth providers.
- No bundled credentials management beyond reading values from environment variables when needed.

## 4. External Dependencies & Tooling
- Mandatory: `playwrightauthor` (browser orchestration, profiles, logging), `playwright` (managed by playwrightauthor), `rich` (CLI formatting), `pydantic` (typed response models).
- Optional for development: `pytest`, `pytest-asyncio`, `pytest-playwright`, `anyio`, `loguru` (via playwrightauthor) – documented in `DEPENDENCIES.md`.
- Use `uv` for dependency management and `hatch` for running tests as per broader project conventions.

## 5. System Context
1. Consumer imports `playpi.actions` (or CLI) and calls a high-level function.
2. The action acquires a `playwrightauthor` session using stored profile data (e.g., Google account).
3. The action drives the target website (e.g., Gemini Deep Research) with stored selectors/steps until a response is produced.
4. The action extracts and cleans response HTML to markdown/plain text and returns it (plus structured metadata when appropriate).
5. Errors propagate as custom `PlaypiError` subclasses with helpful remediation messages; raw playwright errors remain accessible for debugging.

## 6. Package Layout
```
src/playpi/
  __init__.py              # Export public API and version
  errors.py                # Define PlaypiError, AuthenticationError, TimeoutError
  session.py               # Thin wrapper around playwrightauthor's sync/async contexts
  html.py                  # Shared HTML → markdown/plain-text helpers (reuse from crapi docs where possible)
  actions/
    __init__.py            # Export available actions
    google_deep_research.py# Initial flagship workflow implementation
  types.py                 # Pydantic models (ActionResult, StepDiagnostics)
  cli.py                   # Optional CLI entry using `fire`
```
- Keep files <200 lines; functions <20 lines by splitting the flow into composable helpers.
- Store selectors and XPath strings as module-level constants grouped by feature.
- Documentation for additional workflows goes into `docs/actions/<action>.md` (future work, not part of initial deliverable).

## 7. Core Abstractions
- `PlaypiSession`: contextmanager / asynccontextmanager that wraps `playwrightauthor`. Responsibilities:
  - Accepts `profile_name`, `headless`, `slow_mo`, `timeout` options.
  - Ensures browser cleanup (close page/context) via `playwrightauthor` primitives.
  - Provides `page` and `tracing` objects for action code.
- `ActionResult` (pydantic):
  ```python
  class ActionResult(BaseModel):
      raw_html: str
      text: str
      metadata: dict[str, Any] = Field(default_factory=dict)
  ```
- `run_action(action: Callable[[Page], Awaitable[ActionResult]], **session_opts)` helper to reduce boilerplate.
- Each workflow file exposes `run(prompt: str, *, options: Optional[ActionOptions] = None) -> ActionResult` plus a convenience `run_text(prompt: str, **kwargs) -> str`.
- Custom errors derive from `PlaypiError` for clearer user messaging.

## 8. google_deep_research Workflow Specification
- Public signature: `def google_deep_research(prompt: str, *, retry: int = 1, profile: str | None = None, headless: bool = True, timeout: float = 60.0) -> str`
- Steps:
  1. Acquire Playwright session with `playwrightauthor` using the supplied profile; if missing, raise `AuthenticationError` instructing user to log in via `playwrightauthor auth google`.
  2. Navigate to `https://gemini.google.com/u/0/app` and wait for main chat pane; confirm Deep Research toggle is available (fail fast if UI changed).
  3. Paste prompt using `page.get_by_role("textbox", name="Enter a prompt here")`; ensure text area is focused and clear existing text.
  4. Toggle Deep Research option (selector defined in constants). If not found, raise `WorkflowChangedError` with note to update selectors.
  5. Click submit button, then wait for status element (spinner) to disappear or explicit "Research complete" text.
  6. Fetch rendered answer container HTML, strip extraneous UI, run through `html_to_markdown()` helper, return trimmed string.
  7. Capture diagnostics (timestamps, total duration, screenshot path when verbose) inside `ActionResult.metadata`.
  8. On timeout, optionally retry `retry` times before surfacing `TimeoutError`.
- Side effects: All screenshot/log files stored inside `playwrightauthor` profile directory (leveraging its logging settings).

## 9. Extensibility Guidelines
- Additional workflows (e.g., Claude search, You.com) follow the same pattern: dedicated module under `actions/`, exported in `actions.__all__` and `__init__`.
- Avoid creating inheritance hierarchies; prefer plain functions using shared helpers.
- Selector constants grouped per workflow to make maintenance easy.
- Provide opt-in asynchronous entrypoints (suffix `_async`) reusing same helpers but via `async with PlaypiSession.async_open(...)`.

## 10. Error Handling & Logging
- Default logging delegates to `playwrightauthor`; expose `verbose` flag that toggles INFO/DEBUG via environment variable consumed by `playwrightauthor`.
- Wrap known failure modes: missing profile, 2FA prompt detected, layout change, network offline.
- Provide actionable messages: e.g., "Deep Research toggle not found. Google UI changed on 2024-07-09; rerun with verbose=True and share screenshot.".

## 11. Configuration Inputs
- Environment variables (documented in README):
  - `PLAYPI_PROFILE_GEMINI` default profile name for Google.
  - `PLAYPI_HEADLESS=0/1` global override.
  - `PLAYPI_SLOWMO_MS` to slow interactions.
- Function keyword args always override env defaults.
- No config files in initial release.

## 12. Testing Strategy
- Unit tests (fast): mock `playwrightauthor` session/page to verify helper logic, html parsing, retry behavior.
- Selector smoke tests: run under `pytest -m e2e` (opt-in) using Playwright's `Page` fixtures and requiring valid credentials; mark as `xfail` when env vars missing.
- HTML parsing regression tests: store sanitized HTML fixtures (no PII) and assert markdown output matches expected snapshots.
- CLI test: invoke `python -m playpi.cli google-deep-research "prompt"` with monkeypatched action to ensure argument plumbing works.

## 13. Documentation & Examples
- Update/author `README.md` summary under 200 lines with quick start (install, authenticate with playwrightauthor, call function).
- Add `docs/actions/google-deep-research.md` covering prerequisites, sample output, troubleshooting.
- Maintain `WORK.md`, `PLAN.md`, `TODO.md`, and `CHANGELOG.md` in root per project process; specification informs upcoming updates.
- Provide Jupyter-friendly example snippet in `examples/google_deep_research.ipynb` (optional stretch) referencing core function only.

## 14. Release Checklist
1. Implement session wrapper + google deep research action.
2. Add synchronous & async APIs and expose via `__all__`.
3. Write fast unit tests and gated e2e test.
4. Document environment variables and workflow usage.
5. Run `uvx hatch test`, `uvx mypy .`, `uvx bandit -r .`; capture results in `WORK.md`.
6. Tag pre-release version `0.1.0` once manual QA completes.

## 15. Risks & Mitigations
- **UI drift (High)**: Mitigate with selector constants, verbose screenshot capture, and documented update steps.
- **Authentication failures (Medium)**: Delegate to `playwrightauthor`, validate profile existence before automation, surface remediation instructions.
- **Flaky tests (Medium)**: Separate mock-based unit tests from opt-in live tests to keep CI stable.
- **Dependency changes (Low)**: Pin `playwrightauthor` minor version, document upgrade procedure in `DEPENDENCIES.md`.

This specification defines the minimal, testable surface area for the initial `playpi` release and outlines how to extend it without introducing unnecessary complexity.
