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
