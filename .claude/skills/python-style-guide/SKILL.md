---
name: python-style-guide
description: Python code conventions for the project — PEP8, typing, docstrings, module structure. Used by developer, code-reviewer.
---

# Python Style Guide

## Basic rules
- PEP8, enforced automatically via Ruff (`pyproject.toml` at the repository root is the single source of truth for the rules).
- Maximum line length: 100 characters (see `[tool.ruff]` in `pyproject.toml`).
- Type hints are required for all public functions/methods (checked by the `ANN` rule in Ruff).
- Docstrings — Google style, required for public modules/classes/functions:
```python
def calculate_retry_delay(attempt: int, base_delay: float = 1.0) -> float:
    """Calculates the delay before the next retry attempt (exponential backoff).

    Args:
        attempt: attempt number, starting from 1.
        base_delay: base delay in seconds.

    Returns:
        Delay in seconds before the next attempt.
    """
```

## Structure
- One public class/group of related functions per module.
- Business logic is separated from I/O (network, DB, filesystem) — makes unit testing easier.
- Exceptions — use project-specific custom exceptions instead of bare `Exception`.
- Configuration — via environment variables/config object, not hardcoded.

## Forbidden
- `except Exception: pass` without logging and a justification comment.
- Mutable default arguments (`def f(x=[])`).
- Global mutable state outside explicitly designated configuration modules.
