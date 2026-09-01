# Run log — MDF-8

Ticket: [MDF-8 — Configure Code Quality Tools (Ruff & Mypy)](https://dedoronin-1786901899646.atlassian.net/browse/MDF-8)
Repo: `D:\Git\AI-SDLC` (Markdown Formatter, `src/md_formatter/`)
Orchestrator run started: 2026-09-01

---

## 2026-09-01 — `requirements-analyst`

**Input**
Fetch MDF-8 from Jira; extract user story, acceptance criteria, linked Confluence
docs, scope/non-goals, technical constraints. Explicitly flag anything missing,
ambiguous, or contradictory; do not guess.

**Output (summary)**

- Issue type: Story | Status: To Do | Priority: Medium | Parent epic: MDF-2 "Infrastructure Setup"
- No Confluence pages or issue links are attached to the ticket. Three pages were
  located by space-wide search and treated as *supporting context only*:
  Development Guidelines, Product Requirements, Definition of Done.
- Acceptance criteria taken from the ticket:
  1. `[tool.ruff]` section added to `pyproject.toml`; `ruff check .` runs without config errors.
  2. `[tool.mypy]` section added to `pyproject.toml`; `mypy .` runs without config errors.
  3. On the current project layout, `ruff check .` and `mypy .` report zero warnings/errors.
  4. Mypy configured with `strict = true`.
- Out of scope (explicit in ticket): GitHub Actions / CI integration (`ci.yml`).
- Returned status: **NEEDS_CLARIFICATION**

**Open questions raised by the analyst**

1. AC #3 says "empty project layout", but the repo already contains
   `src/md_formatter/__init__.py` and `tests/__init__.py`. Which target must be clean?
2. **Ruff rule selection is entirely unspecified** — no rule sets, no line length,
   no `target-version` in either the ticket or the Confluence pages. This is the
   substantive "settings" the ticket asks for.
3. `ruff format .` is a required pre-commit step per Development Guidelines but is
   absent from the ticket; include or not?
4. No mypy options beyond `strict = true` specified (no `python_version`, `files`,
   or `tests/` overrides).
5. Confluence reference pages are not linked from the ticket; traceability unconfirmed.

**Orchestrator decision**

**HALT — escalate to human.** Open question #2 is material and cannot be guessed:
"configure Ruff settings" without a rule set is the core deliverable of the ticket,
and choosing rules unilaterally risks a scope disagreement between the ticket's
narrow reading ("Ruff configured, check passes") and the broader lint policy implied
by the Confluence Development Guidelines. Per hard rule "on any uncertainty in
requirements — ask ONE clarifying question, do not guess", the pipeline is stopped
before the Implementation stage.

Questions #1, #3 and #4 have low-risk default answers that were prepared and offered
to the human alongside the question, but were **not** applied.

**Pipeline state:** Requirements = BLOCKED. `developer` not invoked.
`test-engineer` not invoked. No repo files changed other than this log.

---

## 2026-09-01 — Human decision (clarifying question resolved)

**Question asked:** Ruff on defaults, or an explicit ruleset encoding the Confluence
Development Guidelines?

**Human answer:** Broad ruleset — `["E", "F", "I", "UP", "B", "N"]`, `line-length`
per judgment (88 standard; the Guidelines page specifies no line length),
`target-version = "py311"`. The three proposed defaults (AC #3 = current repo state,
`ruff format` out of scope, mypy `strict` + `python_version = "3.11"` with no
`tests/` exemption) were confirmed as-is.

**Decision:** Requirements UNBLOCKED. Proceed to Implementation.

---

## 2026-09-01 — `developer`

**Input**
Full context package: the 4 ticket ACs, the human-confirmed Ruff/Mypy decisions
above, explicit out-of-scope list (no CI, no feature code, no commit/push/PR),
verified current repo state, and Confluence naming/stdlib constraints.

**Output**

- Changed exactly one tracked file: `pyproject.toml`.
- Added `[dependency-groups] dev` (PEP 735) with `ruff>=0.6`, `mypy>=1.11`.
  Chosen over an optional-dependencies extra because dev tooling is not a
  distributable extra of the wheel and `uv` consumes dependency-groups natively.
- Added `[tool.ruff]` (`line-length = 88`, `target-version = "py311"`,
  `src = ["src", "tests"]`) and `[tool.ruff.lint]` (`select = ["E","F","I","UP","B","N"]`).
  `select` placed under `[tool.ruff.lint]`; top-level `select` is deprecated in
  modern Ruff and would emit a config warning, violating AC #1.
- Added `[tool.mypy]`: `python_version = "3.11"`, `strict = true`, `mypy_path = "src"`,
  `files = ["src", "tests"]`. `mypy_path` is the src-layout fix, applied instead of
  weakening `strict`. No `tests/` override, per the human decision.
- Byproducts: new untracked `uv.lock`, and `.venv/` (already gitignored).

**Verification (re-run and confirmed independently by the orchestrator)**

    ruff check .                 -> All checks passed!            EXIT=0
    mypy --no-incremental .      -> Success: no issues in 2 files  EXIT=0

Toolchain: ruff 0.16.5, mypy 2.3.1, CPython 3.11.11.

The developer also ran a negative control (a temporary file with an unused import,
unsorted imports, an untyped function and a `Bad_Name` function) which correctly
produced I001/F401/N802 from Ruff and `no-untyped-def` from mypy, confirming the
config is genuinely enforcing rather than inert. That file was deleted; the tree
again contains only `src/md_formatter/__init__.py` and `tests/__init__.py`.

**Decision:** AC #1-#4 all satisfied and verified. Implementation ACCEPTED.
Zero fix->test->fix iterations were needed (limit is 3).

---

## 2026-09-01 — `test-engineer` — SKIPPED (intentional)

**Not an omission.** MDF-8 is a configuration-only ticket: it adds no Python code
and therefore introduces no new public functions or methods to cover. The standard
rule "coverage for every new public function" is vacuously satisfied.

The only meaningful test would be a config-smoke test asserting `ruff check .` and
`mypy .` exit 0 — that is a CI quality-gate concern, and CI integration (`ci.yml`)
is explicitly Out-of-Scope on this ticket, deferred to a separate one. Confirmed
with the human before skipping.

In lieu of unit tests, enforcement was validated by the developer's negative-control
run documented above.

---

## Final state

**Pipeline:** Requirements = ok (after one human clarification) -> Implementation =
done -> Tests = skipped (intentional, no new code) -> Awaiting human review.

**Files changed (MDF-8 scope):** `pyproject.toml` only.
**Untracked byproducts for reviewer to triage:** `uv.lock`, `docs/` (pre-existing).
**Not authored by this pipeline:** `.claude/settings.local.json` shows as modified;
that is the permission system recording tool approvals, unrelated to MDF-8. Exclude
it from the MDF-8 diff.

**No commit, no push, no PR, no merge.** All changes left in the working tree for
human review, per hard rule.

**Open items flagged for the human reviewer:**
1. Dependency floors are open-ended (`ruff>=0.6` resolved to 0.16.5;
   `mypy>=1.11` resolved to 2.3.1). A future sync could pull a new major with new
   default checks and turn the build red with no code change. Either commit
   `uv.lock` or add upper caps when the deferred CI ticket lands.
2. Decide whether this repo commits lockfiles; `uv.lock` is currently untracked.
3. Machine default `python` on PATH is 3.12.0 while the config declares 3.11 —
   anyone running the tools outside `.venv` tests a different interpreter.
