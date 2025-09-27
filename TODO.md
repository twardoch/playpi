---
this_file: TODO.md
---

- [ ] Update prompt-entry logic to type immediately after the input is ready.
- [ ] Scope and click the Deep Research toggle within `mat-card:has(toolbox-drawer)` and confirm activation.
- [ ] Click the send button after Deep Research mode is active.
- [ ] Detect `deep-research-confirmation-widget` and click its `[data-test-id="confirm-button"]`.
- [ ] Ensure we wait for Deep Research completion and capture the final Markdown response.
- [ ] Add debug logs for each stage to support troubleshooting.
- [ ] Re-run `./examples/google_deep_research.py` and `uv run pytest tests/test_google_provider.py -k deep` to validate.
