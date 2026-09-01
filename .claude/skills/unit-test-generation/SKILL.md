---
name: unit-test-generation
description: Project unit-testing standard (pytest) — structure, coverage, mocks, parametrization. Used by test-engineer, code-reviewer.
---

# Unit Test Generation Standard

## Structure
- Tests mirror the source structure: `src/pkg/module.py` → `tests/pkg/test_module.py`.
- One test file per module. One test class/group of functions per tested class/function.
- Naming: `test_<function>_<scenario>_<expected_result>`, e.g. `test_calculate_retry_delay_negative_attempt_raises_value_error`.

## Mandatory minimum per function
1. Happy path.
2. Boundary values (0, empty collection, None, max/min).
3. Negative scenario (invalid input → exception/explicit error), where applicable.

## Tools
- `pytest` as the test runner.
- `pytest.mark.parametrize` for groups of similar cases instead of copy-paste.
- `unittest.mock` / `pytest-mock` for external dependencies (network, DB, filesystem, time — `freezegun` when deterministic time is needed).
- Fixtures in `conftest.py` for reusable setup.

## Coverage
- Target: 100% for new/changed business-logic code. Acceptable exceptions (e.g. trivial `__repr__`) must be explicitly recorded with justification.
- Command: `pytest --cov=<package> --cov-report=term-missing --cov-fail-under=85` (CI threshold is 85%; below that — pipeline fail).

## Forbidden
- Tests depending on external services (real JIRA/Confluence/network) — that's e2e/integration test territory, not unit.
- Tests without assertions ("the test only checks that it didn't crash").
