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

---

## 2026-09-05 — `code-reviewer` (first/AI review, before human)

**Input**
PR #5 + the verbatim MDF-16 AC, plus an explicit request to adversarially probe the three
riskiest decisions rather than just inspect them: the `exit-code-5` tolerance removal,
whether `--cov=md_formatter` resolves correctly for a src-layout package, and the
`-o addopts=""` override on the doctest step.

**Output — verdict: APPROVE. 0 BLOCKING / 6 suggestions (2 praise, 4 non-blocking).**

Reviewer independently re-ran every gate on both Windows/uv (local) and cross-checked against
the actual Linux/pip CI run, then went further than inspection — since the AC is a *negative*
assertion ("CI fails below 90%"), a green run at 100% proves nothing on its own:

- **Probe 1** — dropped a temporary untested 10-statement module into `src/md_formatter/`:
  coverage dropped to 41%, gate correctly failed (exit 1). Confirms `--cov=md_formatter`
  would catch a landed-but-untested module, not just measure what's already exercised.
- **Probe 2** — ran `pytest -k zzz_nonexistent` (0 tests selected): coverage dropped to 29%,
  gate correctly failed. This is exactly the scenario the old exit-5 tolerance would have
  masked — confirming its removal is correct and arguably in-scope for MDF-16 rather than
  scope creep, since the old tolerance would have **bypassed** this ticket's own AC.
- Confirmed via the real CI log that `--cov=md_formatter` resolves against the editable
  `src/` tree (not a stale `site-packages` copy) — misresolution would have shown as a loud
  0%, not a silent pass.

One fix applied as a result (all others left as non-blocking suggestions for the human):

- `-o addopts=""` on the doctest CI step replaced with `--no-cov` — the former clears *all*
  addopts, not just the coverage ones, so any future non-coverage option would have silently
  stopped applying to the doctest run too. Verified locally (1 passed). Commit `11b27c0`.

Non-blocking suggestions left as-is (not applied, no ticket exists for most of them):

1. Consider `testpaths = ["tests", "src"]` + folding `--doctest-modules` into `addopts` to
   collapse to one pytest invocation; if keeping two steps, add `testpaths = ["tests"]` since
   bare `pytest` currently only skips `src/` because nothing there is named `test_*.py`.
2. Consider `[tool.coverage.run] branch = true` — at 7 statements, a 90% *statement*
   threshold reads softer than it behaves (effectively "100% or fail").
3. `README.md` has no testing section; a partial local run like
   `pytest tests/test_lists.py::test_x` now fails on the coverage gate even though all
   selected tests pass. Flagged as an undocumented behavior change.
4. Traceability: the doctest CI step has no ticket at all (only `ruff format --check` and the
   coverage gate map to MDF-16/prior review items) — suggested a retro ticket or a YAML
   comment. Already explicitly flagged in the PR body, so not blocking.

Also independently verified: `uv.lock` diff is 252 additions / **zero** removals, confined to
`pytest-cov`, `coverage`, and transitives — a genuine dependency addition, not incidental
drift (unlike MDF-10/MDF-11's reverted regenerations). No secrets, no third-party coverage
upload (respects Out-of-Scope), `permissions: contents: read` unchanged, no source/public-API
change.

Review posted as PR comment: https://github.com/denisdoronin/AI-SDLC/pull/5#issuecomment-5551603005

---

## 2026-09-05 — CI verification

| Check | Result |
|---|---|
| `Lint, type-check and test (Python 3.11)` | **pass** (15s) |
| `claude-review` | **pass** (42s) |

PR state: `OPEN`, `mergeable: MERGEABLE`. Re-verify after the `--no-cov` follow-up commit
(`11b27c0`) before merge — not yet re-run as of this log entry.

---

## 2026-09-05 — Final state

**All 4 follow-ups from the MDF-11 review round, addressed:**

| # | Follow-up | Resolution |
|---|---|---|
| 1 | `pytest-cov` / 90% coverage gate missing | **Done** — this PR (#5), MDF-16 |
| 2 | Doctests unenforced in CI | **Done** — bundled into this PR, no ticket existed |
| 3 | `.claude/` AI-SDLC tooling uncommitted (repo hygiene) | **Done** — committed directly to `main`, commit `64256ed`, per explicit human decision |
| 4 | Tautological test in `tests/test_lists.py` | **Done** — removed on the MDF-11 branch (PR #4), commit `b868bc0` |

**New items surfaced by this round, for the human (none blocking, none actioned):**

1. `README.md` has no testing section and the coverage gate is now a genuine behavior change
   for anyone running a partial/filtered local `pytest` invocation.
2. Coverage is statement-only; `branch = true` would tighten the gate as the codebase grows
   past trivial-size modules.
3. The doctest CI step itself has no tracking ticket — only surfaced via review discussion,
   never formally requested. Human should decide whether to retro-ticket it.

---

## 2026-09-05 — Merged

**PR #5 merged to `main`** by `denisdororonin` (fast-forward, merge commit `58ca9b0`), on
explicit human instruction. Branch `chore/MDF-16-coverage-threshold` deleted on merge. MDF-16
pipeline complete — all 4 MDF-11-review follow-ups are now resolved and on `main`.
