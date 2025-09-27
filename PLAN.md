---
this_file: PLAN.md
---

# Fix Google Deep Research Automation

## Goal
Ensure `google_deep_research` reliably activates Gemini's Deep Research workflow end-to-end: prompt entry → deep-research toggle → message submission → confirmation → completion wait.

## Required Changes
1. **Prompt Entry Timing**
   - After navigating to `https://gemini.google.com/u/0/app`, wait only for the editable prompt field to become ready and enter the prompt immediately.
   - Avoid unnecessary idle waits before interacting with the input box.

2. **Deep Research Toggle**
   - Target the button at `toolbox-drawer-item button[mat-list-item]` within `mat-card:has(toolbox-drawer)`.
   - Ensure we actually click the button (not just highlight it) and confirm `aria-pressed="true"` or similar state indicating Deep Research mode is active.

3. **Message Submission**
   - Click the send button inside the `.send-button-container` (`button[data-test-id='send-button']` equivalent / existing selector) immediately after Deep Research mode is confirmed.

4. **Confirmation Dialog**
   - Wait for `deep-research-confirmation-widget` to appear.
   - Click the `[data-test-id="confirm-button"]` button inside the widget (text may be localized, e.g., "Zacznij wyszukiwanie").

5. **Research Progress Wait**
   - Keep waiting for the completion condition (existing `_wait_for_completion`) after confirmation so we capture the final Markdown response.

6. **Error Handling & Logging**
   - Log distinct debug messages for each stage (prompt fill, toggle click, send click, confirmation click) to simplify troubleshooting.

## Validation
- Manual run: `./examples/google_deep_research.py` should complete both prompts and save outputs.
- Automated: `uv run pytest tests/test_google_provider.py -k deep` continues to pass.
