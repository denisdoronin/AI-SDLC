---
name: code-review-checklist
description: A single code review checklist shared by the AI reviewer and humans — ensures consistent standards. Used by code-reviewer, and can also be used by a human reviewer as a reference.
---

# Code Review Checklist

## Functionality
- [ ] The implementation covers all acceptance criteria of the ticket
- [ ] No unimplemented functionality that is claimed in the PR description
- [ ] No changes outside the scope of the ticket (scope creep)

## Code quality
- [ ] `ruff check .` is clean
- [ ] Type hints on public functions
- [ ] Docstrings on public functions/classes
- [ ] No duplicated logic (DRY), no excessive abstraction (YAGNI)

## Tests
- [ ] Unit test for every new/changed public function
- [ ] Edge cases and negative scenarios covered
- [ ] Tests are deterministic (no flakiness due to time/order/network)

## Security
- [ ] No secrets/tokens in code
- [ ] User input is validated
- [ ] No unsafe operations (eval, unsafe deserialization, SQL concatenation)

## Compatibility and operations
- [ ] Public APIs/DB schemas not broken without migration/versioning
- [ ] Logging added for significant operations and errors
- [ ] Configuration changes are documented

## Verdict
`APPROVE` only if all blocking items are satisfied. Otherwise — `REQUEST_CHANGES` with a concrete list.
