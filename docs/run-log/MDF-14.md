# Run log — MDF-14

Ticket: [MDF-14 — Build CLI Argument Parser & Entry Point](https://dedoronin-1786901899646.atlassian.net/browse/MDF-14)
Repo: `D:\Git\AI-SDLC` (Markdown Formatter)
Branch: `feature/MDF-14-cli-argument-parser`, cut from **`main` @ `eadfb73`**.
Trigger: fresh orchestrator intake, explicit human request to implement MDF-14 end-to-end following
the MDF-13 precedent, with the ticket body supplied verbatim in the prompt.

---

## 2026-09-07 — Intake

Request type: **new feature** (Story, first *new module* since `tables.py`, and the first ticket in
this repo that ships a user-facing executable rather than a pure library function).

Repo state at intake: on `main` @ `eadfb73`, working tree clean, local identical to `origin/main`
(0 ahead, 0 behind).

**Branch base is trivial this time, unlike MDF-13.** Both open PRs have merged since: `9b5c218`
merged PR #6 (MDF-12) and `eadfb73` squash-merged PR #7 (MDF-13). `main` therefore already contains
`lists.py`, `tables.py` and both test files, so the stacked-PR reasoning that dominated `MDF-13.md`
does not apply — MDF-14 cuts from `main` and targets `main`, and `ci.yml`'s
`on: pull_request: branches: [main]` filter will fire normally. Open item 1 of `MDF-13.md`
("PR #6 must merge before PR #7") is **resolved by events**; merge order was respected.

Baseline quality gate run before touching anything, so any later failure is attributable to MDF-14
and not inherited:

| Gate | Command | Result |
|---|---|---|
| Lint | `uv run ruff check .` | All checks passed |
| Format | `uv run ruff format --check .` | 27 files already formatted |
| Types | `uv run mypy` (strict) | Success: no issues found in 6 source files |
| Tests + coverage | `uv run pytest` | **109 passed**, 100% coverage (40/40 stmts) |
| Doctests | `uv run pytest --no-cov --doctest-modules src` | 4 passed |

Matches the final state recorded in `MDF-13.md` exactly — nothing drifted across the two merges.

### Requirements handling — deviation from the standing rule, recorded deliberately

The process rule is "for requests containing a Jira ticket key always call `requirements-analyst`".
The human supplied the full ticket body inline and explicitly authorised skipping the re-fetch.
`requirements-analyst` was called **anyway**, but scoped to *verification* rather than extraction:
confirm the pasted text is verbatim and complete, and — the real reason — enumerate Confluence for a
governing FR.

Justification: on MDF-13 the analyst surfaced **FR-2.2**, which materially shaped the design, and on
MDF-10 it caught a Confluence statement that *contradicted* the ticket AC. A pasted ticket body
cannot surface either. The marginal cost is one read-only agent call; the downside risk is building
the wrong CLI. Strictly read-only: no transitions, no comments, no AC edits, no Confluence writes.

---

## 2026-09-07 — `requirements-analyst` (verification call)

**Input**
Confirm the pasted ticket is verbatim and complete; enumerate the Confluence space **directly**
(space key `Markdown`, id `1736712`) rather than trusting a keyword CQL search, per the MDF-12
failure recorded in `MDF-12.md`; hunt for a governing FR; run an MDF-10-style contradiction check;
and answer eight implementation-hinging questions verbatim-or-"NOT SPECIFIED".

**Output — the call justified itself: it found a governing FR the pasted ticket does not mention.**

- Ticket text confirmed **verbatim and complete**. Only cosmetic difference: the human joined the two
  Out-of-Scope bullets onto one line. Fields the human omitted: parent epic **MDF-5 "Epic 4: CLI &
  I/O"** (status To Do), priority Medium, created 2026-08-19, updated today, assignee/reporter Denis
  Doronin. No labels, components, sprint, issuelinks, subtasks, comments or attachments.
- Confluence direct enumeration returned **4 pages**: space home, Product Requirements (v2),
  Development Guidelines (v2), Definition of Done (v1).

**Governing requirements found — PRD section 4.3 "CLI & I/O Engine (FEAT-3)", page `1769473` v2:**

| FR | Title | Acceptance criteria (verbatim) |
|---|---|---|
| **FR-3.1** | CLI Flags & Execution | "Supports `--mode` (`bullet`, `numbered`, `table`), `--delimiter` (default `,`), `--input`, and `--output`." |
| **FR-3.2** | Stream Compatibility | "If `--input` is omitted, reads from `stdin`. If `--output` is omitted, prints to `stdout`." |
| **FR-3.3** | Error Handling | "Catches `FileNotFoundError` and `PermissionError`. Prints clean error messages to `stderr` and exits with code `1` (no raw tracebacks)." |

**Also normative — Development Guidelines page `1802241` v2, section 1 "Architectural Principles":**
> "Separation of Concerns: Keep CLI parsing (`cli.py`), file I/O operations, and transformation
> logic strictly isolated from one another."

This is the *same class* of statement as the one that normatively names `lists.py`/`tables.py`, and
it independently confirms **two** decisions this orchestrator had already issued to the developer
before the analyst reported: the module name `cli.py`, and the split of a pure `format_text` from
the I/O in `main`. Section 2.3's `table_engine.py` is again the illustrative example row, not
normative — the distinction flagged on MDF-13 held.

**No contradiction found** between Confluence and the three ACs; FR-3.1/FR-3.2 are a strict superset
of AC 2 and AC 3. One **gap** flagged, adjudicated in the next section.

Explicitly **NOT SPECIFIED** in any source: character encoding, trailing newline, success exit code,
`--delimiter` behaviour in non-table modes, `--version`, and `python -m` support. The
`[project.scripts]` mechanism and the literal name `md-formatter` appear **only** in JIRA AC 1 — no
Confluence page documents the entry-point wiring, though the PRD does require a "PEP 621 compliant
`pyproject.toml`", which is exactly where `[project.scripts]` lives.

PRD Scope Boundary declares nothing CLI-related out of scope; it lists "CLI & Stream Support" as
in-scope and "PyPI distribution (publishing restricted to GitHub Releases)" as out. Adding a console
script is **not** publishing, so `[project.scripts]` does not touch that boundary.

MDF-12 and MDF-13 both now **Done** — consistent with both PRs having merged, which resolves open
item 2 of `MDF-13.md` (the status/reality disagreement) by events.

No JIRA fields modified, no transitions, no comments; no Confluence pages created or edited.

---

## 2026-09-07 — Orchestrator adjudication of the three "BLOCKING" items: none escalated

The analyst returned **NEEDS_CLARIFICATION with 3 BLOCKING**. All three were resolved from sources
already in hand, none required the human's escalation budget. Same posture as MDF-13, where the
analyst's single BLOCKING item was also overruled on the record.

**1. "Is `--mode` required?" — not actually open.** The analyst is right that no *source document*
says so, but the human's own written design notes in the task prompt state: "`--mode` is required and
one of: bullet, numbered, table." That is a direct instruction from the requester, which outranks a
silent spec. Independently, no default is *constructible*: the tool cannot guess whether text should
become a bullet list or a table, and inventing one would be unrequested behaviour. **Required.**

**2. "Is FR-3.3 error handling in MDF-14's scope?" — the one genuinely interesting question.**
Deferred pending a check of Epic MDF-5's other children; adjudicated below.

**3. "Console-script wiring has no governing source."** A gap, not an ambiguity. AC 1 requires the
literal command `md-formatter --help` to run, and the ticket summary is "Build CLI Argument Parser
**& Entry Point**". Under PEP 621 — which the PRD mandates — `[project.scripts]` is *the* mechanism
that makes that command exist. Confluence not naming the mechanism does not make the requirement
unclear; it makes the docs incomplete. **Proceed**, and flag the doc gap as an open item.

### The five NON-BLOCKING items, resolved with recorded defaults

| # | Question | Decision | Basis |
|---|---|---|---|
| 4 | `--delimiter` in bullet/numbered mode | **Silently ignored**, documented in help text | Ticket asks only that table-only applicability be documented. Erroring is stricter than any source requires. |
| 5 | Success exit code | **`0`** | Universal shell convention; FR-3.3 fixes the failure code at 1, implying 0 for success. |
| 6 | Encoding / trailing newline | **Explicit UTF-8 on all file I/O; exactly one trailing `\n` on non-empty output, nothing at all on empty output** | Not scope creep but cross-platform correctness: this repo is developed on Windows (cp1252 default) and CI runs Linux, and the suite already carries Cyrillic fixtures. Relying on the platform default would corrupt non-ASCII files. Trailing newline is standard Unix text-tool behaviour. |
| 7 | `--version` flag | **Not implemented** | Unrequested by every source; DoD "Scope Adherence" forbids adding out-of-scope capability. |
| 8 | `python -m md_formatter` | **Implemented** as a 13-line `__main__.py` | Not required by any source, but **explicitly authorised by the human** in the task prompt ("a `python -m md_formatter` fallback is reasonable too"). Recorded as human-authorised, not source-required. |

---

## 2026-09-07 — Orchestrator decision on FR-3.3 vs MDF-15: KEEP the `OSError` handling, do not escalate

The analyst's second BLOCKING item deserved a real answer, so a second read-only call enumerated
Epic MDF-5's children. It found the decisive fact:

> **MDF-15 — "Implement Safe File I/O & Exception Handling"** (Story, **To Do**, parent MDF-5).
> In-Scope (verbatim): "Handle FileNotFoundError, PermissionError, and empty input scenarios"
> AC (verbatim): "Gracefully catches missing file errors, printing user-friendly error to stderr."
> / "Returns non-zero exit status code (exit code 1) on fatal runtime error without raw traceback dumps."

That is FR-3.3 almost word for word. MDF-5 has exactly **two** children — MDF-14 and MDF-15 — and no
other ticket in the project owns error handling. The analyst's inference was that implementing
FR-3.3 inside MDF-14 is scope creep against the DoD's Scope Adherence rule. **Partially overruled**,
on three grounds, after establishing a fourth fact by experiment.

**1. The DoD rule does not actually forbid it.** Verbatim: *"All functional code strictly implements
the In-Scope items defined in the story's specification. **No Out-of-Scope capabilities are added.**"*
MDF-14's Out-of-Scope section names exactly two things — "Interactive prompt mode" and "GUI".
Error handling is not among them. The rule bars capabilities a ticket has explicitly excluded; it
does not bar every capability the ticket fails to enumerate.

**2. Shipping the entry point while knowingly violating its own governing FR is the worse outcome.**
MDF-14 is the ticket that turns this library into a user-facing executable. Merging a `md-formatter`
command that dumps a Python traceback when a user typos a filename would put `main` in a state that
contradicts FR-3.3 of the PRD, for however long MDF-15 takes.

**3. It is ~10 lines and trivially reversible** (`_fail`, plus two `try/except OSError` blocks). Per
the reversibility test applied on MDF-13, a cheap-to-unwind decision is decided and flagged, not
escalated; the escalation budget is reserved for expensive, mainline-semantics questions.

**4. The fact that settles it: MDF-15 is NOT gutted — it retains concrete, demonstrable work.**
Established by running the built CLI, not by reasoning:

| Failure mode | Exception | Caught by MDF-14's `except OSError`? | Observed |
|---|---|---|---|
| Missing input file | `FileNotFoundError` | **Yes** (subclass of `OSError`) | clean stderr, exit 1 |
| Unwritable output dir | `FileNotFoundError` | **Yes** | clean stderr, exit 1 |
| Directory given as `--input` | `PermissionError` | **Yes** | clean stderr, exit 1 |
| **Input file that is not valid UTF-8** | **`UnicodeDecodeError`** | **NO — it subclasses `ValueError`, not `OSError`** | **raw traceback, exit 1** |
| Empty input file | — | n/a | empty output, exit 0 |

So the boundary lands in a defensible place on its own merits: **MDF-14 handles the `OSError`
family**, which is the minimum for the entry point not to be user-hostile, while **MDF-15 still owns
the genuinely separate work** its In-Scope names — the non-`OSError` decode failure demonstrated
above, "empty input scenarios", and a systematic safe-I/O review.

**Deliberately NOT fixed here: the `UnicodeDecodeError` traceback.** Fixing it would be the actual
scope creep, since it is squarely MDF-15's In-Scope and no MDF-14 AC touches it. It is recorded as a
known limitation and carried to "Open items" so MDF-15 inherits a documented starting point rather
than a surprise.

**Not escalated**, but flagged prominently in the PR body and the JIRA comment so the human can
overrule cheaply. If the team wants strict ticket boundaries, deleting `_fail` and the two
`try/except` blocks reverts MDF-14 to the narrow reading in one small commit.

---

## 2026-09-07 — `developer`

**Input**
Verbatim ticket AC + In/Out-of-scope, plus 17 binding decisions labelled explicitly as
**"orchestrator decisions derived from the ticket, the human's design notes and repo convention —
NOT all verbatim requirements"**, with an instruction to challenge any believed *factually wrong*
rather than silently deviate (MDF-12 process lesson 3). Constraints: no git, no tests, no changes to
`lists.py`/`tables.py`/`uv.lock`/settings. Warned about the MDF-13 doctest trap where an empty-string
`print` emits a blank line that doctest reads as the end of the expected block.

**Output**

- `src/md_formatter/cli.py` — `format_text` (pure), `build_parser`, `main`, module constant `MODES`,
  private `_read_input`/`_write_output`/`_fail`/`_PROG`.
- `src/md_formatter/__main__.py` — 13 lines, delegates to `main()`.
- `pyproject.toml` — `[project.scripts]` mapping `md-formatter` to `md_formatter.cli:main`.
- All 17 decisions implemented; none challenged.

**Judgement calls accepted:** `prog` pinned to `md-formatter` so both entry points print identical
help; `MODES` as a single source of truth shared by `choices` and the tests; `format_text` raising
`ValueError` on an unknown mode (unreachable through `choices`, but it is a public pure function and
must not silently return garbage); default argparse metavars, so help text is predictable to assert
against; `str(error)` as the message body, giving argparse-identical framing.

**Flagged by the developer, correctly, rather than hidden:** `Path.write_text` writes in *text*
mode, so on Windows the appended newline reaches disk as CRLF. It chose platform-native endings over
forcing LF, because `sys.stdout` on Windows also emits CRLF and forcing LF would make the file and
stdout paths disagree with each other. It then **corrected its own draft docstring**, which had
wrongly claimed the result "never ends with a newline", after executing the code — the MDF-12
false-claim lesson applied unprompted.

**Decision:** accepted, no rework requested.

---

## 2026-09-07 — `test-engineer`

**Input**
The full behaviour contract, ticket AC and FR-3.1/3.2/3.3, as a new `tests/test_cli.py` following
the conventions of the two existing test files. Framed by the MDF-13 post-mortem: the instruction was
**not** merely a named-mutant list (MDF-13 lesson 2 records that naming mutants steers the agent
toward them and away from everything unnamed) but a required **coverage-of-input-shapes argument** —
"which structural dimensions of the input does the suite never vary?" Ten mutants named on top of
that, to be *built and run*, not reasoned about, in copies outside the repo. Warned about the CRLF
trap: assert on `read_text()`, never `read_bytes()`, or the suite passes locally and fails on the
Linux runner.

**Output**

- `tests/test_cli.py`, **47 new tests** (156 total). `cli.py` **51/51** and `__main__.py` **4/4** —
  100%, whole package 95/95. No `conftest.py` needed.
- The `sys.exit(main())` guard line in `__main__.py`, unreachable on import, was genuinely covered
  via `runpy.run_module` with `run_name="__main__"` inside `pytest.raises(SystemExit)`, so no
  coverage exception had to be recorded at all.
- **9 of 10 mutants killed.** The survivor was dropping the explicit UTF-8 encoding, reported as an
  *environment-equivalent* mutant rather than a test gap.
- Structural dimensions varied on purpose: 0/1/2/3-line inputs — never letting "many" always mean 2,
  which was the exact MDF-13 failure — all three modes distinguished by output *shape* rather than
  merely exercised, blank lines in the middle vs at the end vs all-blank, non-ASCII (Cyrillic and
  emoji) through a real file round-trip, default vs explicit delimiter, file vs stdin, file vs
  stdout, and empty vs non-empty result. All four source-by-sink combinations covered.

**Orchestrator verification of the "equivalent mutant" claim — checked, not accepted.** The claim
rests on the preferred encoding already being UTF-8 here. Executed directly:
`locale.getpreferredencoding(False)` returns **cp65001**, the Windows code page *for* UTF-8, with
`sys.flags.utf8_mode = 0`. The claim holds; the mutant is genuinely unobservable in this environment
and on the Linux runner. The nuance is worth recording because it cuts both ways: on a default
Windows machine (cp1252) that mutant **would** be killed, which is precisely why the explicit
encoding earns its place rather than being decoration.

**Orchestrator audit for the recurring tautology defect.** Every assertion in the new file was
scanned. The pattern removed in review on MDF-11, MDF-12 *and* MDF-13 — an assertion true for every
possible input — does **not** appear: the assertions are exact string equalities, exit codes, and a
one-line-stderr check that pins "no raw traceback" by construction. Handed to `code-reviewer` anyway,
since this orchestrator has been wrong about this before.

**Decision:** accepted, no rework requested.

---

## 2026-09-07 — Local quality gate (orchestrator-run, independently verified)

Re-run by the orchestrator rather than taken from the subagents self-reports, per the convention
established in `MDF-16.md` and followed since:

| Gate | Command | Result |
|---|---|---|
| Lint | `uv run ruff check .` | All checks passed |
| Format | `uv run ruff format --check .` | 31 files already formatted |
| Types | `uv run mypy` (strict) | Success: no issues found in 9 source files |
| Tests + coverage | `uv run pytest` | **156 passed**, 100% (95/95); `cli.py` 51/51, `__main__.py` 4/4 |
| Doctests | `uv run pytest --no-cov --doctest-modules src` | 5 passed |

Zero rework cycles used at this point (limit 3). Baseline before MDF-14 was 109 passed / 40 stmts,
so the ticket added 47 tests and 55 statements with no regression.

**Behaviour spot-check against the AC, executed directly by the orchestrator** — not read off a
subagent report, because AC conformance is the one thing a passing suite cannot prove on its own
(a suite can faithfully encode the wrong contract):

| Check | Result | Pins |
|---|---|---|
| `md-formatter --help` | all four flags + all three choices listed | **AC 1** |
| `python -m md_formatter --help` | identical output to the console script | prog decision |
| Console script metadata | entry point resolves to `md_formatter.cli:main`; `md-formatter.exe` present in the venv | **AC 1** |
| stdin to stdout, bullet | correct bullets | **AC 2, AC 3** |
| file to stdout, numbered, blank line mid-input | numbering continues unbroken across the blank | **AC 2**, blank-line semantics |
| file to stdout, table | 4-line aligned table | **AC 2, AC 3** |
| explicit delimiter + Cyrillic | correctly parsed and aligned | FR-3.1, UTF-8 decision |
| file to file | 96 bytes, CRLF on Windows | **AC 3**, line-ending decision |
| whitespace-only in, with `--output` | **0-byte file**, no lone newline | empty-result decision |
| missing input file | one-line stderr message, exit 1, no traceback | FR-3.3 |
| unwritable output dir | same shape, exit 1 | FR-3.3 |
| directory passed as `--input` | `PermissionError` caught, exit 1 | FR-3.3 |
| bad mode / missing mode | exit 2 | required + usage decisions |
| CRLF input file | accepted and normalised | universal newlines |
| explicit delimiter in bullet mode | ignored, exit 0 | decision 4 |

**Docstring fact-check, executed rather than read.** Every factual claim in `cli.py` was run:
"the result has exactly as many lines as the input" (true for 1-, 2- and 3-line inputs, with and
without interior blanks); "a trailing blank input line leaves the result ending in a newline" (true);
"a table result never ends with a newline" (true); "delimiter is ignored by the list modes" (true);
unknown mode raises `ValueError` (true); whitespace-only input yields the empty string in all three
modes (true); parser defaults are comma, None, None (true).

### Two further uncaught-exception paths, found by the orchestrator probing beyond the suite

| Trigger | Exception | Caught? | Observed |
|---|---|---|---|
| Empty string passed to `--delimiter` | `ValueError: empty separator` from `str.split` | **No** — not an `OSError` | raw traceback, exit 1 |
| Input file with a UTF-8 BOM | none | n/a | the BOM survives into the first item; `utf-8-sig` would strip it |
| `--input` and `--output` naming the same file | none | n/a | **works correctly** — the file is read in full before it is written |

The empty-delimiter case is the sharper of the two, because unlike `UnicodeDecodeError` it is
reachable through **MDF-14 own flag**. It is nonetheless the same category — exception handling,
MDF-15 In-Scope — and `parse_delimiter_text` already declares that input "outside this function
contract" as a documented `ValueError`, an MDF-12 decision. Carried into the review round for a
documentation decision rather than fixed by reflex.

---

## 2026-09-07 — PR creation

- Commit `bc719e3` — `docs(run-log): record MDF-14 intake, requirements and scope adjudication`.
- Commit `fa31468` — `feat(cli): add argparse CLI and md-formatter console entry point`.
- **PR #8** opened against `main`: https://github.com/denisdoronin/AI-SDLC/pull/8
- Files staged **explicitly by path**, never with `git add -A`, per the MDF-13 incident where a
  tooling-generated `.claude/settings.local.json` edit was accidentally staged. `git status` after
  committing confirmed the branch carries only the intended files.
- Diff vs `main`: `cli.py` +221, `tests/test_cli.py` +627, this log +195, `__main__.py` +13,
  `pyproject.toml` +3 = **864 lines**.

**PR size exceeds the `github-workflow` skill 400-line guidance — flagged, not silently absorbed.**
627 of the 864 lines are the test file and 195 are this log; **product code is 237 lines**. The skill
says to suggest a split when larger, so: the ticket is judged **not meaningfully splittable**,
because all three AC depend on the same entry point existing — a PR containing the parser but no
entry point satisfies none of them, and one containing the entry point but no tests would fail the
DoD coverage rule. Recorded in the PR body for the human to overrule.

## 2026-09-07 — JIRA comment

Comment `10067` added to MDF-14 with the PR link, the AC evidence, the gate results, the six
decisions taken where the ticket was silent, the MDF-15 overlap needing a human decision, and the
documented limitations:
https://dedoronin-1786901899646.atlassian.net/browse/MDF-14?focusedCommentId=10067
Comment only — no status transition (left at **In Progress**), no field or AC edits. The agent
re-confirmed read-only afterwards that the status and all three AC were unchanged.

---

## 2026-09-07 — `docs-writer`

**Input**
The new user-facing surface, with an explicit instruction to **assess first** and that "no change
needed" was an acceptable outcome — it was the correct outcome on MDF-13. Told to read the MDF-13
docs reasoning and then *test* it rather than inherit it, and given both sides of the argument
honestly. Constrained to repository files; **Confluence edits not authorised**. Told to verify every
flag, default and exit code against the implementation rather than copying the orchestrator summary,
and specifically **not** to claim the tool handles errors it does not.

**Output — status: CHANGED. `README.md` gains a `## Usage` section. Assessment accepted.**

All five facts the MDF-13 skip relied on were re-verified and all still hold: `README.md` is
install-only, the four library functions are still absent from it, `__init__.py` re-exports nothing,
no `CHANGELOG.md` exists, and there is still no testing section.

**The reason to change course is that MDF-14 breaks the precedent rather than extending it,** and
the agent identified the distinction precisely: the earlier skips were about *selective API
reference*, where documenting one library function while three siblings stayed undocumented would
invent a convention the README does not have. MDF-14 does not add a function to document — it
**changes what `pip install -e .` does**, and that command is already on line 8 of the README. After
this PR that instruction installs an executable on the user PATH which the README never mentions, so
its Install section is now factually incomplete about the outcome of its own instruction. That is
documentation *drift*, a different defect from uneven API coverage. Discoverability reinforces it:
`--help` is self-documenting only to someone who already knows the command exists.

Restraint the agent exercised unprompted, and correctly: it did **not** also document the four
library functions (that would resurrect exactly the selective-reference problem the precedent
avoids), did **not** create a `CHANGELOG.md` (a project-wide structural decision, not one ticket to
make unilaterally), and deliberately worded the exit-code line as "file I/O error" rather than "all
errors" so that the unhandled non-UTF-8 traceback is not overclaimed away.

**Orchestrator verification — necessary here, because the agent could not execute anything.** It has
no Bash tool, so it read `build_parser()` and `main()` as its ground truth instead of running the
command, and said so plainly rather than implying it had verified. That honesty is right, but it
leaves the claims unexecuted, so they were checked directly:

- The example command `md-formatter --mode bullet --input notes.txt --output notes.md` was run
  verbatim in a scratch directory: **exit 0**, and `notes.md` contains the expected bullets.
- Exit codes 0 / 1 / 2 confirmed against the spot-check table above.
- `python -m md_formatter` confirmed equivalent.
- Flag names, the required-ness of `--mode`, the three choices and the comma default all match
  `--help` output.
- The README was re-read in full: the new section is well-formed Markdown, the nested fenced block
  is correctly closed, and it matches the file terse existing style and heading level.

No changes to `src/`, `tests/`, `pyproject.toml` or Confluence.

---

## 2026-09-07 — `code-reviewer` (first/AI review, before human) — REQUEST_CHANGES, 5 blocking

**Input**
PR #8 plus the verbatim three AC, FR-3.1/3.2/3.3, the normative Development Guidelines separation
rule, the DoD rules, and the seven orchestrator rulings marked settled — with the carve-out that a
ruling could be challenged if *factually wrong* rather than merely different. Ruling 7 (keeping
`OSError` handling despite MDF-15) was singled out to be attacked. Told to **probe rather than
inspect**: run the installed console script against inputs nobody had tried, invent mutants outside
the ten the `test-engineer` had already built, AST-parse the *test file* to find structural
dimensions the suite never varies, hunt tautological assertions, and fact-check every claim in the
docstrings, the PR body and this log by executing it. Warned that `gh pr review --request-changes` is
rejected in this repo (author == authenticated account, per `MDF-13.md`), so the review had to be
posted with `gh pr comment`.

**Output — verdict `REQUEST_CHANGES`, 5 blocking findings, all reproduced, plus 8 suggestions.**
Review posted as a PR comment: https://github.com/denisdoronin/AI-SDLC/pull/8#issuecomment-5570595902

The reviewer independently re-ran the whole gate and confirmed it genuinely passes, verified the
wheel ships `__main__.py` with a correct `entry_points.txt`, and confirmed
`locale.getpreferredencoding(False) == "cp65001"`. **36 mutants built, 28 killed, 8 survived
(2 proved equivalent).**

| # | Blocking finding | Verified by orchestrator |
|---|---|---|
| B1 | Empty `--delimiter` raises an uncaught `ValueError` from `str.split` and dumps a **raw traceback** through the installed script; the same flag+value succeeds silently in bullet mode | Yes — reproduced before the review, independently |
| B2 | `format_text` `Raises:` documents only the unknown-mode `ValueError`; `main` `Raises:` documents only `SystemExit`, yet an exception genuinely escaped `main` | Yes |
| B3 | `Returns:` claims `""` for "empty or **whitespace-only**" input — **false** for list modes | Yes: `format_text("   \n\t","bullet") == "\n"` and `(" \n \n ")` gives `"\n\n"` |
| B4 | The suite **cannot detect a wrong file encoding**: flipping both sites to `latin-1` leaves all 47 tests green | Yes — confirmed `mojibake.encode("latin-1") == raw` is `True`, so the round trip is byte-symmetric and the wrong codec cancels out exactly |
| B5 | `f"{result}\n"` -> `f"{result.strip()}\n"` **survives**; no `main()`-level test has a result containing a blank line | Yes — `"x\n\n"` yields `'- x\n\n'` today, mutant gives `'- x\n'` |

**B3 is the sharpest of the five**: the shipped docstring and a shipped test (`tests/test_cli.py:112`,
asserting `== "\n"`) **contradicted each other inside one PR**, and both the orchestrator's own
docstring fact-check and the `test-engineer` pass had missed it. The orchestrator's check had used
single-line whitespace input (`"   "`), for which the docstring *is* true; the falsity only appears
at two or more lines. A fact-check that varies only one input shape reproduces the very failure mode
this repo keeps rediscovering — this time in the *verification*, not the tests.

**B4 revises a claim in this log.** The earlier entry recorded the surviving `encoding=` mutant as
"environment-equivalent", which is true for *dropping* the argument (cp65001 is UTF-8 here). But
flipping it to `latin-1` is **not** equivalent and also survived, which means the suite pinned the
encoding contract not at all. The narrower claim was right; the reassurance drawn from it was wrong.
Corrected here rather than left standing, per the MDF-12 lesson about false claims propagating.

**Tautology hunt: none found**, confirming the orchestrator's own scan. The closest were three
strictly-redundant assertions implied by an exact-equality assertion above them — unable to fail
independently, but not always-true, so a different family from the MDF-11/12/13 pattern.

**Attack on ruling 7: ruling UPHELD, but its supporting record shown to be incomplete.** The reviewer
declined to call it scope creep and supplied a stronger defence than the log had led with — FR-3.3 is
a *property of the artifact MDF-14 creates*, not a separable capability, so deferring it guarantees a
knowingly non-compliant `main` on mainline with no way to fix it later without editing MDF-14's own
code. But it found that the adjudication table above **omitted a sixth failure mode** (`--delimiter ""`)
while reading as an exhaustive enumeration, and that under the boundary as originally stated
("MDF-14 owns the `OSError` family, MDF-15 owns the rest") that case was **orphaned** — it is neither
file I/O nor an empty-input scenario.

**Boundary restated, and now in force:** *MDF-14 owns argument-domain errors — choices, required
flags, `--delimiter` validity — plus the `OSError` family reachable from the entry point it creates.
MDF-15 owns file-content and decoding failures, empty-input semantics, and the systematic safe-I/O
review.* This keeps `UnicodeDecodeError` with MDF-15 for a principled reason rather than the accident
of its base class, and lands B1 unambiguously inside MDF-14. Accepted in full; the earlier table has
been left in place above with this section as its correction, so the revision stays auditable.

---

## 2026-09-07 — Rework (iteration 1 of max 3)

Run **sequentially**, not concurrently as on MDF-13, because B1 changes observable behaviour that
the tests must then pin: letting a `test-engineer` write assertions against a contract the
`developer` had not yet settled would have risked a wasted cycle.

`developer` — `src/md_formatter/cli.py` only:

- **B1 fixed** with a private `type=` callable on `--delimiter`, the idiomatic argparse mechanism.
  Binding semantics dictated by the orchestrator: an empty delimiter is rejected **in every mode**,
  not only `table`. Rationale — an invalid *value* should be rejected exactly as `--mode bogus` is,
  regardless of whether that run would have consulted it; "silently ignored in list modes" means "has
  no effect on the output", not "any value is accepted". Uniform beats mode-dependent. Rejection goes
  through the parser, so it is a **usage error, exit 2**, preserving ruling 5. Only emptiness is
  checked — multi-character delimiters stay legal, since `parse_delimiter_text` documents them as
  matched literally and no source forbids them.
- **B2, B3, S5 fixed** in the docstrings; **S2 documented, not fixed** (a UTF-8 BOM survives into the
  first item; `utf-8-sig` would strip it, but BOM handling is decoding, which the restated boundary
  assigns to MDF-15).
- **The developer caught one of its own claims being false by executing it**: it had written that
  argparse does not apply `type=` to a default value. A probe showed argparse **does** call the
  callable on the string default, so the `Args:` text was rewritten before shipping. Third
  consecutive pass in which executing a claim beat asserting it.
- A second, cosmetic pass followed: the first fix produced
  `md-formatter: error: argument --delimiter: --delimiter must not be empty`, stuttering because
  argparse prepends the flag name itself. The developer flagged it and asked; the message was changed
  to `value must not be empty`. It also **corrected the orchestrator's brief** — the task said stderr
  should be "exactly one line", but argparse prints a two-line usage block before the error line.
  What is one line is the *error* line, with no traceback. The brief was wrong; the code is right.

`test-engineer` — `tests/test_cli.py` only:

- **B4 closed** by replacing the false test. The old one's docstring called it a "functional proxy for
  the UTF-8 explicit contract", which was untrue. The replacement uses **table mode with non-ASCII
  content**, because `build_markdown_table` sizes columns with `len()`: a latin-1 misread turns
  `café` (4 chars) into `cafÃ©` (5), changing the rendered padding and dash count — an asymmetry the
  byte-symmetric round trip structurally could not expose.
- **B5 closed** with a `main()`-level test feeding `"x\n\n"` and pinning `"- x\n\n"` on disk.
- **Validator branch covered** for all three modes, asserting exit 2 *and* the exact stderr line, plus
  a multi-character-delimiter acceptance case. Package back to **100%** (was 98.99%).
- **S3, S4, S6, S8 folded in**: per-flag help *text* assertions (AC 1 says "flags **and options**",
  and swapping the `--input`/`--output` help strings previously survived); the three redundant
  assertions removed and their docstrings corrected to stop calling them mutation guards; a
  multi-body-row table case at the `main()` layer; and a truncation test seeding a non-empty output
  file first.
- All six required mutants reported **killed**.

**Orchestrator verification — the two blocking mutants reproduced directly, not accepted from the report:**

| Mutant | Harness result |
|---|---|
| `encoding="utf-8"` -> `"latin-1"` at both sites | **KILLED** — `1 failed, 163 passed`, the failure being exactly the new table-mode UTF-8 test |
| `f"{result}\n"` -> `f"{result.strip()}\n"` | **KILLED** — `1 failed, 163 passed`, the failure being exactly the new trailing-newline test |

Both were built as isolated copies outside the repo, with the import path asserted to resolve into
the copy so the real module could not shadow the mutant, and the copies deleted afterwards.

**A process trap worth recording, because it nearly produced a false result.** The first attempt at
the B5 mutant reported `164 passed` — which reads exactly like "the mutant survived". It had not:
the replacement string never matched, because backslash escapes in the heredoc were consumed before
Python received them, so `f"{result}\n"` was searched for with a **real newline** instead of a
backslash-n. The only reason this was caught is the standing rule to **assert the edit actually
applied** before trusting the run; the assertion fired with "expected 1 occurrence, found 0". The
retry used `chr(92)` to sidestep escaping entirely and re-read the file from disk to confirm. Without
that assertion this log would now contain a confident, wrong claim that a real defect was unpinned.

**Local quality gate after rework (orchestrator-run, independently verified):**

| Gate | Result |
|---|---|
| `ruff check .` | All checks passed |
| `ruff format --check .` | 31 files already formatted |
| `mypy` (strict) | Success: no issues found in 9 source files |
| `pytest` | **164 passed**, **100%** coverage (99/99); `cli.py` 55/55 |
| `pytest --no-cov --doctest-modules src` | 6 passed |

**B1 re-verified end to end through the installed console script:** empty `--delimiter` gives
`exit=2`, `0` tracebacks and the single error line `md-formatter: error: argument --delimiter: value
must not be empty` in **all three** modes; a multi-character delimiter and the default comma both
still exit 0 and render correctly.

**1 of 3 rework iterations used.**

**Deliberately not actioned:**

- **S2 (BOM)** and the `UnicodeDecodeError` traceback — both decoding concerns, both assigned to
  MDF-15 by the restated boundary, both documented rather than fixed.
- **S1** (`--input ""` yields a slightly misleading `Permission denied: '.'`) — cosmetic, and it is
  already the `OSError` path behaving as designed.
- **S7** (`allow_abbrev` is on by default, so `--mod` and `--in` are accepted) — stock argparse
  behaviour, required by no AC; pinning or disabling it would be unrequested scope.
- The `test-engineer` reported one **remaining** structural gap honestly rather than declaring
  victory: at the `main()` layer, `"numbered"` mode is exercised for real content exactly once, with
  a single fixed 2-line ASCII shape. Judged **non-blocking** and not worth a third pass: numbered
  mode is thoroughly varied at the `format_text` layer, and the dispatch mutant that would exploit
  a gap here (`numbered` calling `format_bullet_list`) was already built and killed. Carried to open
  items.
