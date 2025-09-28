this_file: TODO.md
---

# Current Tasks

- [ ] Fix syntax error in `src/playpi/providers/google/gemini.py`.
- [ ] Fix syntax error in `tests/test_google_gemini.py`.
- [ ] Run tests to confirm fixes.

# Refactor PlayPi for Gemini Workflows

- [x] Create directory `src/playpi/providers/google/`.
- [x] Create `src/playpi/providers/google/auth.py` for authentication logic.
- [x] Create `src/playpi/providers/google/gemini.py` for Gemini UI interactions.
- [x] Move existing logic from `src/playpi/providers/google.py` to the new `auth.py` and `gemini.py` files.
- [x] Delete the old `src/playpi/providers/google.py` file.
- [x] Update `src/playpi/__init__.py` and `src/playpi/providers/__init__.py` to expose new functions.
- [ ] Update `src/playpi/cli.py` to use the new refactored functions.

- [x] Implement `google_gemini_deep_research(prompt: str) -> str` in `gemini.py`.
- [x] Implement `google_gemini_deep_research_full(...)` with file I/O capabilities in `gemini.py`.
- [x] Implement `google_gemini_deep_research_multi(...)` for concurrent research tasks in `gemini.py`.

- [x] Implement `google_gemini_generate_image(...)` in `gemini.py`.
- [x] Add logic to handle image downloads by monitoring the downloads folder.

- [x] Implement `google_gemini_ask_deep_think(...)` in `gemini.py`.

- [x] Implement `google_gemini_ask(...)` for standard prompts in `gemini.py`.
- [x] Add response parsing to `google_gemini_ask` to extract content and sources.

- [x] Simplify `examples/google_deep_research.py` to use the new high-level API.
- [x] Create new example scripts for image generation, deep think, and `google_gemini_ask`.

- [x] Create `tests/test_google_gemini.py`.
- [x] Write tests for all new public API functions.
- [ ] Run all tests and examples to validate the refactoring.
