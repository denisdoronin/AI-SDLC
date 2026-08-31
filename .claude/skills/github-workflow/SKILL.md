---
name: github-workflow
description: Rules for working with GitHub — branching, PR formatting, commits, JIRA linkage. Used by developer, orchestrator, code-reviewer, release-manager.
---

# GitHub Workflow

## Branching
- Branch name format: `<type>/<JIRA-KEY>-<short-slug>`, e.g. `feature/PROJ-1234-add-retry-policy`.
- `type`: `feature` | `fix` | `refactor` | `chore`.
- Never commit directly to `main`/`develop`.

## Commits
- Conventional Commits: `feat(scope): summary`, `fix(scope): summary`, `test(scope): summary`.
- Each commit should be atomic and pass lint/tests locally (not required, but preferred).

## Pull Request
PR description template (required):
```
## JIRA: <link>
## What was done
...
## How it was tested
...
## Checklist
- [ ] Ruff clean
- [ ] Unit tests added/updated
- [ ] Documentation updated (if needed)
- [ ] Backward compatibility verified
```
- The PR must reference the JIRA ticket and, if applicable, the ADR in Confluence.
- PR size: aim for <400 lines of diff; if larger — suggest to the orchestrator that the task be split.

## Review
- At least 1 AI review (`code-reviewer`) + at least 1 human approval before merge.
- Merge only after CI is green.
- Merge strategy: squash merge, to keep main's history clean.

## Prohibited for agents
- Merging PRs.
- Force-pushing to others' branches.
- Deleting branches/tags without an explicit request.
