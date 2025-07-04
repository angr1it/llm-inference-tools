# AGENT instructions

These guidelines apply to the whole repository.

- See `docs/plan.md`, `docs/requirements.md` and `docs/structure.md` for context on how the stack is organised.
- `docs/features/core-stack-scaffold.md` describes the minimal scaffold implemented here.
- Keep `README.md` up to date with a short project overview, how to run the stack and the main directory structure.
- All documentation under `docs/` must be written in English.
- Provide unit tests under `tests/unit` and integration tests under `tests/integration`. Cover new code with tests.
- Run `pytest` for unit tests. Integration tests require `--runintegration`.
- Always run `pre-commit run --all-files` before committing; the hooks execute the unit tests and `mypy`.
