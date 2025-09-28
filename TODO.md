this_file: TODO.md
---

- [ ] Create `src/playpi/__main__.py` with Fire map delegating to provider helper callables
- [ ] Add `src/playpi/providers/google/cli_helpers.py` exposing `google_research_command`, `gemi_command`, `gemi_dr_command`, and `test_session_command`
- [ ] Implement `gemi_dr_command` to read stdin JSON, validate payload, and call `google_gemini_deep_research_multi`
- [ ] Implement `gemi_command` to merge file/string prompts, honor `--deep`, and write to stdout or file
- [ ] Rewire legacy `google` and `test` commands through helper module while preserving behavior
- [ ] Update `[project.scripts]` entry in `pyproject.toml` to `playpi.__main__:main` and add/deprecate shim for `playpi.cli`
- [ ] Write unit tests for helper parsing/output logic and CLI smoke tests (`python -m playpi ...`)
- [ ] Update README, CHANGELOG, WORK.md (with test results), and examples for new CLI structure
