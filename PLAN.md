this_file: PLAN.md
---

# Current Status and Next Steps

## Snapshot
- CLI restructure and helper modules shipped; automated coverage in `tests/test_cli_helpers.py`
- Deep Research confirmation click logic restored and exercised via mocked DOM tests
- Full test suite passes with `PLAYPI_FORCE_AUTH_FAILURE=1 uvx hatch run test:python -m pytest` (Hatch wrapper timeout expected after success)
- Outstanding need: live Deep Research confirmation run plus minor documentation polish

## Objective 1 · Manual Deep Research Verification (issues/106.md)
- **Purpose**: Confirm the restored confirmation locator sequence works against the live Gemini UI
- **Pre-check**: Ensure Chromium profile has valid Google authentication and Deep Research access
- **Execution**:
  1. Pipe a JSON job into `playpi gemi_dr` (e.g. `printf '{"prompt": "smoke test prompt"}' | playpi gemi_dr`) to observe the workflow
  2. Capture whether `deep-research-confirmation-widget` appears and confirm primary locator click succeeds
  3. If locator fails, collect DOM snapshot and update selectors/tests accordingly
- **Acceptance**: Successful research completion without manual intervention; CHANGELOG updated with confirmation note
- **Risk**: Google UI variance; mitigate by recording fallback locator behavior and updating tests when DOM shifts

## Objective 2 · Documentation & Examples Refresh (issues/105.md)
- **Purpose**: Align README/examples with new `gemi` and `gemi_dr` commands once live verification succeeds
- **Tasks**:
  1. Update README quick-start snippets to use `python -m playpi` and the new commands
  2. Refresh `examples/` scripts to mirror documented flows and remove stale references
  3. Note the reliable test command in CONTRIBUTING/README as appropriate
- **Acceptance**: Docs describe verified behavior; examples runnable without edits

## Verification Strategy
- Automated: `uvx hatch test` (expected to fail), followed by `PLAYPI_FORCE_AUTH_FAILURE=1 uvx hatch run test:python -m pytest` (passes 34 tests)
- Manual: Browser-driven Deep Research smoke test outlined above
- Documentation: Cross-check README/examples snippets against CLI helper tests to keep arguments consistent

## Completed Work (Archive)
- Provider module split (`google/auth.py`, `google/gemini.py`) with renamed `google_gemini_*` APIs
- CLI entry point consolidation into `playpi.__main__` with Fire command map
- Regression tests for confirmation widget fallbacks and CLI prompt assembly
