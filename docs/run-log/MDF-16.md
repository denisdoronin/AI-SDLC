# Run log — MDF-16

Ticket: [MDF-16 — Enforce Code Coverage Threshold in CI](https://dedoronin-1786901899646.atlassian.net/browse/MDF-16)
Repo: `D:\Git\AI-SDLC` (Markdown Formatter)
Branch: `chore/MDF-16-coverage-threshold` (created off `origin/main` @ `64256ed`, after the
`.claude/` AI-SDLC tooling recovery commit — see Context below)
Trigger: not a fresh orchestrator intake — this ticket was surfaced as a carried-over
follow-up from the MDF-10 and MDF-11 AI code reviews (`pytest-cov` missing, no coverage gate)
and picked up directly on the developer's request, along with two other follow-ups from the
same review round (doctest enforcement — no ticket; `.claude/` tooling repo hygiene).

---

## 2026-09-05 — Context

Before this ticket, the human resolved the long-standing repo-hygiene item flagged in
`docs/run-log/MDF-11.md` (Intake and Final state): 4 commits on the stale
`feature/MDF-10-bullet-list-formatter` local branch containing the `code-reviewer`,
`docs-writer`, `release-manager` agent definitions and the `code-review-checklist` skill had
never reached `main`. Decision: commit them directly to `main` (chore-only, no PR/ticket
ceremony, since this is AI-SDLC process tooling, not product work). Done in commit `64256ed`,
bundled with the matching `orchestrator.md` wiring (steps 7-9: `code-reviewer`,
`release-manager`, `docs-writer`) — without that wiring the new agent files would be dead
code. `.claude/settings.json` / `settings.local.json` were deliberately left out of that
commit: their working-tree diff includes an unrelated, locally-added `PreToolUse` hook that
auto-approves all `Bash`/`Task`/`Edit`/`Write` calls, which looked like local experimentation
and not something to push to `main` silently.

Confirmed via JQL search (`project = MDF`) that **MDF-16 "Enforce Code Coverage Threshold in
CI"** already exists as a Story (parent epic MDF-5 "Epic 5: Release & QA", status "To Do"),
matching follow-up #1 verbatim: "Configure pytest-cov in pyproject.toml and GitHub Actions
with `--cov-fail-under=90`." No ticket exists for doctest enforcement in CI (follow-up #2) —
bundled into this PR as a related, explicitly-flagged addition rather than left for a fourth
review cycle to re-raise.

---

## 2026-09-05 — Implementation (direct, no `developer`/`test-engineer` subagent handoff)

Config/CI-only chore, no new product code or new tests needed — coverage was already 100% on
the two existing source modules, so no test-engineer involvement was required to hit the
threshold.

**Changes:**

- `pyproject.toml`: added `pytest-cov>=5.0` to the `dev` dependency group; added
  `[tool.pytest.ini_options]` with
  `addopts = "--cov=md_formatter --cov-report=term-missing --cov-fail-under=90"` so the gate
  applies locally too, not just in CI (ticket explicitly names both).
- `uv.lock`: updated for the new dependency. Unlike MDF-10/MDF-11, this regeneration is
  **kept**, not reverted — it reflects a real, intentional dependency addition rather than
  incidental drift from `uv run`.
- `.github/workflows/ci.yml`, three changes beyond MDF-16's literal text, all carried over
  from prior review rounds rather than deferred a third time:
  1. Added a `ruff format --check .` step (previously only `ruff check` ran; format drift was
     never caught).
  2. Added a `pytest -o addopts="" --doctest-modules src` step (the `-o addopts=""` override
     prevents the coverage gate from firing on this src-only, no-tests invocation). No ticket
     covers this; flagged explicitly in the PR body.
  3. Removed the pytest exit-code-5 tolerance carried since the MDF-9 CI setup (when the
     suite was empty). Kept in place, it would now silently defeat the new coverage gate if
     test collection ever broke — a live risk once real tests exist, per the MDF-10 review's
     4th follow-up finding.

**Local quality gate** (`uv run`, independently verified, not self-reported):

| Gate | Command | Result |
|---|---|---|
| Lint | `ruff check .` | All checks passed |
| Format | `ruff format --check .` | 21 files already formatted |
| Types | `mypy` (strict) | Success: no issues found in 4 source files |
| Tests + coverage | `pytest` | 27 passed, **100% coverage** (7/7 statements), gate would pass at 90% |
| Doctests | `pytest -o addopts="" --doctest-modules src` | 1 passed |

27 tests, not 59 — this branch is off `main`, before MDF-11 has merged. The gate is
independent of merge order.

---

## 2026-09-05 — PR creation

- Commit `f9428d7` — `chore(ci): enforce 90% coverage gate and run doctests in CI`
  (Conventional Commits), pushed to `chore/MDF-16-coverage-threshold`.
- **PR #5** opened against `main`: https://github.com/denisdoronin/AI-SDLC/pull/5
- Diff: 264 insertions / 14 deletions across 3 files (`pyproject.toml`, `uv.lock`,
  `ci.yml`) — the bulk is the `uv.lock` dependency-resolution addition.
- Not merged, not approved — humans own approval and merge.
