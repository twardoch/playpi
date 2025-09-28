this_file: PLAN.md
---

# Current Status and Next Steps

I have been working on a major refactoring of the `playpi` library to support a wider range of Google Gemini features, as outlined in `issues/104.md`. This involved restructuring the provider code, implementing new functions for deep research, image generation, and different modes of asking Gemini, and renaming functions as requested.

During this process, I introduced syntax errors in `src/playpi/providers/google/gemini.py` and `tests/test_google_gemini.py`, which caused the test suite to fail. My immediate goal is to fix these errors and get the tests passing. Once the tests are green, I will continue with the validation phase of the refactoring.

# Refactor PlayPi for Gemini Workflows

## Goal
Refactor the `playpi` library to provide a structured and extensible framework for automating various Google Gemini features, including Deep Research, Image Generation, Deep Think, and standard prompts. This involves reorganizing the codebase, implementing a clearer API, and adding new functionalities as per `issues/104.md`.

## Phase 1: Project Restructuring

1.  **Create New Directory Structure:**
    *   Create the directory `src/playpi/providers/google/`.

2.  **Relocate and Organize Code:**
    *   Move the contents of `src/playpi/providers/google.py` into new, specialized files.
    *   Create `src/playpi/providers/google/auth.py` to handle Google authentication and session management.
    *   Create `src/playpi/providers/google/gemini.py` to contain all logic for interacting with the Gemini web interface (Deep Research, Image Generation, etc.).

3.  **Update Imports and Entry Points:**
    *   Modify `src/playpi/providers/__init__.py` to expose the new functions from the `google` module.
    *   Update `src/playpi/__init__.py` to make the high-level functions easily accessible to users (e.g., `from playpi import google_gemini_deep_research`).
    *   Modify `src/playpi/cli.py` to use the new functions.

4.  **Cleanup:**
    *   Delete the now-obsolete `src/playpi/providers/google.py` file.

## Phase 2: API Implementation

### Google Deep Research

1.  **`google_gemini_deep_research(prompt: str) -> str`:**
    *   Implement a simple, direct function in `src/playpi/providers/google/gemini.py` that takes a prompt and returns the Markdown result.

2.  **`google_gemini_deep_research_full(...)`:**
    *   Implement a comprehensive function that handles:
        *   Reading a base prompt from `prompt_path`.
        *   Appending an additional `prompt` string.
        *   Saving the output to `output_path` or returning it as a string.
        *   Returning the `pathlib.Path` object if the result is saved to a file.

3.  **`google_gemini_deep_research_multi(config: list[dict])`:**
    *   Implement a function to orchestrate multiple, concurrent research tasks.
    *   Manage a queue of research jobs defined in the `config` list.
    *   Ensure that no more than 3 research tasks run simultaneously, each in its own browser tab.
    *   Handle job completion and result collection.

### Google Gemini Image Generation

1.  **`google_gemini_generate_image(...)`:**
    *   Implement a function in `src/playpi/providers/google/gemini.py`.
    *   The function will toggle the "Create images" mode in the Gemini UI.
    *   It will submit the prompt and wait for image generation.
    *   It must handle downloading the generated image by monitoring the system's downloads folder, identifying the new file, and moving it to a specified destination.

### Google Gemini Deep Think

1.  **`google_gemini_ask_deep_think(...)`:**
    *   Implement a function similar to Deep Research, but it will toggle the "Deep Think" option in the UI before submitting the prompt.

### Simple Gemini Prompt (`google_gemini_ask`)

1.  **`google_gemini_ask(...)`:**
    *   Implement a function for standard Gemini prompts without any special modes.
    *   The function will submit the prompt and parse the complete response, including the main content, generated code, and any source links.

## Phase 3: Simplification and Validation

1.  **Simplify Example Script:**
    *   Radically simplify `examples/google_deep_research.py` to demonstrate the use of the new high-level API functions. It should not contain any low-level automation logic.

2.  **Add New Examples:**
    *   Create new example scripts for image generation, deep think, and standard prompts to showcase the new capabilities.

3.  **Update and Create Tests:**
    *   Create a new test file `tests/test_google_gemini.py`.
    *   Write unit and integration tests for all new API functions:
        *   `google_gemini_deep_research`, `google_gemini_deep_research_full`, `google_gemini_deep_research_multi`.
        *   `google_gemini_generate_image`.
        *   `google_gemini_ask_deep_think`.
        *   `google_gemini_ask`.
    *   Ensure existing tests continue to pass.

4.  **Final Verification:**
    *   Run all examples and tests to confirm that the refactoring is complete and all features work as expected.
