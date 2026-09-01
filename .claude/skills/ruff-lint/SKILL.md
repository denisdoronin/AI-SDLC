---
name: ruff-lint
description: How and when to run Ruff, what to do with issues found, which rules must not be ignored. Used by developer, code-reviewer, ci-cd-pipeline.
---

# Ruff Lint

## Commands
```bash
ruff check .            # lint
ruff check . --fix      # autofix safe issues
ruff format .           # formatting (black equivalent)
```

## Rule policy
- Configuration is unified, in `pyproject.toml` (`[tool.ruff]`). Local `# noqa` is allowed only with a justification comment right next to it:
  `x = eval(expr)  # noqa: S307 -- expr is controlled by internal config, not user input`
- Rule categories that are ENABLED and must not be disabled without an `architect`/Tech Lead decision:
  - `E`, `W` (pycodestyle) — PEP8
  - `F` (pyflakes) — undeclared variables, unused imports
  - `I` (isort) — import ordering
  - `B` (bugbear) — common bugs
  - `S` (bandit) — security
  - `ANN` — mandatory type hints for public functions

## developer agent's responsibility
- Run `ruff check . --fix && ruff format .` before reporting a task as complete.
- If issues remain after autofix — fix them manually rather than suppressing the rule.

## CI's responsibility
- `ruff check .` without `--fix` — the pipeline must fail on any violation (see the `ci-cd-pipeline` skill and `.github/workflows/ci.yml`).
