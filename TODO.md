this_file: TODO.md
---

# Current Tasks

## CLI Enhancement (issues/105.md)
- [ ] Add `gemi_dr` command that calls `google_gemini_deep_research_multi` and reads JSON config from stdin
- [ ] Add `gemi` command with --file_prompt, --prompt, --deep, and --output_file arguments
- [ ] Update existing CLI commands to use new refactored function names
- [ ] Test new CLI commands functionality
- [ ] Update CLI help text and documentation

## Final Validation
- [ ] Run comprehensive test suite with `uvx hatch run test:python -m pytest`
- [ ] Test all example scripts to ensure they work with refactored functions
- [ ] Verify all imports and entry points are correct
- [ ] Run smoke tests on main functionality
