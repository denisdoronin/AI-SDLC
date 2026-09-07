# Run log — MDF-13

Ticket: [MDF-13 — Implement Aligned Markdown Table Generator](https://dedoronin-1786901899646.atlassian.net/browse/MDF-13)
Repo: `D:\Git\AI-SDLC` (Markdown Formatter)
Parent epic: [MDF-4 — Epic 3: Table Engine](https://dedoronin-1786901899646.atlassian.net/browse/MDF-4)
Branch: `feature/MDF-13-aligned-table-generator`, cut from `feature/MDF-12-delimited-text-parser` @ `ad76b06` (**not** from `main` — see the branch-base decision below).
Trigger: fresh orchestrator intake, explicit human request to implement MDF-13 end-to-end following the MDF-12 precedent.

---

## 2026-09-06 — Intake

Request type: **new feature** (Story, second function in an existing module). Contains a JIRA key,
so `requirements-analyst` was called per the process rule rather than working from the prompt text.

Repo state at intake: on `feature/MDF-12-delimited-text-parser` @ `ad76b06`, working tree clean,
local branch identical to origin (0 ahead, 0 behind). PR #6 (MDF-12) **OPEN and unmerged**,
`MERGEABLE`, base `main`.

Baseline quality gate run before touching anything, so that any later failure is attributable to
MDF-13 and not inherited: ruff clean, ruff format clean (26 files), mypy strict clean (6 files),
**88 passed**, 100% coverage. Matches the final state recorded in `MDF-12.md`.

Noted at intake, not actioned: `ad76b06` ("permissions...") is a **human's own commit** on the
MDF-12 branch adding Bash/MCP entries to `.claude/settings.json` and `.claude/settings.local.json`.
`MDF-12.md` records those files as deliberately kept out of the branch; they were committed
afterwards by the repo owner. Not mine to revert or re-exclude — but it does mean PR #6's head has
moved past `2c1b3bb`, the commit at which `MDF-12.md` records CI as verified green. Flagged for the
human; see "Open items".

---

## 2026-09-06 — `requirements-analyst` (single call)

**Input**
Extract MDF-13 verbatim (metadata, description, AC, in/out-of-scope), plus MDF-12 and epic MDF-4
for context. Strictly read-only — no transitions, no comments, no AC edits. Explicitly instructed
to **enumerate the Confluence space directly** rather than trust a keyword CQL search, citing the
MDF-12 failure where a zero-result search was wrongly reported as "no design docs exist"; given the
space key (`Markdown`, id `1736712`) and the three standing page ids up front. Asked eight specific
implementation-hinging questions (signature/module, alignment, header row, ragged rows, empty
input, pipe escaping, whether it must call `parse_delimiter_text`, separator width) with the
instruction to answer each verbatim-or-"NOT SPECIFIED". Asked for an MDF-10-style
Confluence-contradicts-AC defect check.

**Output**

- Story | Status **In Progress** | Parent epic MDF-4 | Assignee/Reporter Denis Doronin | no labels,
  components, fix versions, sprint. Created 2026-08-19, updated 2026-09-06. No comments, no
  attachments, `issuelinks: []`, no subtasks.
- Acceptance criteria (verbatim, inline under "Acceptance Criteria / DoD" — no dedicated AC field,
  same shape as MDF-10/MDF-11/MDF-12):
  1. First row treated as header row.
  2. Separator row (`'|---|---|'`) inserted between header and body.
  3. All cells padded with spaces to match the max width of their respective column.
- In-scope (verbatim): implement `build_markdown_table(rows: list[list[str]]) -> str`; calculate max
  column widths, add header separator `'|---|'`.
- Out-of-scope (verbatim): "Text alignment flags (left/right/center)."
- **Governing requirement found: FR-2.2 "Dynamic Table Alignment"**, Product Requirements section
  4.2 "Table Engine (FEAT-2)" (page id `1769473`, v2), verbatim:
  > **FR-2.2** | Dynamic Table Alignment | Constructs padded Markdown tables from 2D string
  > matrices. | Uses the first row as the table header. Generates header-body separator (`|---|`).
  > Pads every cell with trailing spaces to match the max string length of its respective column.
- PRD section 2 "Scope Boundary", out-of-scope (verbatim): "Custom column alignments (e.g.,
  right-aligned `:---:`) in table generation (defaults to left-aligned)."
- Confluence direct enumeration worked as instructed and returned 4 pages. **Both governing pages
  are unchanged since MDF-12** (Product Requirements still v2, Development Guidelines still v2 — its
  v2 edit of 2026-09-03 predates MDF-12's completion, so nothing has moved).
- **No MDF-10-style contradiction.** Development Guidelines contains exactly one code sample, the
  `format_bullet_list` one; there is no table-generator sample anywhere, so nothing can contradict
  MDF-13's AC. A gap, not a conflict — same finding as MDF-12.
- **No formal JIRA dependency on MDF-12** (`issuelinks: []` on both). The relationship is the shared
  parent epic plus an implicit data-contract dependency.
- Flagged by the analyst, outside its remit: MDF-12 is marked **Done** with a resolution date of
  2026-09-06, while its only comment still says "Awaiting AI code review, CI, and human approval.
  Not merged" and PR #6 is in fact still open. Carried to "Open items" — the orchestrator does not
  transition tickets.
- Returned status: **NEEDS_CLARIFICATION — 1 BLOCKING (ragged rows), 3 non-blocking** (empty input,
  pipe escaping, separator width).

No JIRA fields modified, no transitions, no comments; no Confluence pages created or edited.

---

## 2026-09-06 — Orchestrator decision on the BLOCKING item: DO NOT escalate, decide

The analyst marked ragged-row handling (pad short rows / truncate long ones / raise) BLOCKING and
recommended returning a question to the human. **Overruled after checking the in-repo record.**

The MDF-12 escalation was justified because two documented precedents pointed in *opposite*
directions, so "be consistent with the codebase" yielded no answer. That is not the situation here.
Every available signal converges:

| Signal | Source | Points to |
|---|---|---|
| "padding rows to a common width is **not this function's responsibility**" | `src/md_formatter/tables.py` lines 23-25, `parse_delimiter_text` docstring | someone downstream pads, i.e. MDF-13 |
| "ragged-row pass-through (**FR-2.2 owns padding**, so the parser leaving rows ragged is the natural split)" | `docs/run-log/MDF-12.md` lines 135-136 — this orchestrator's own recorded deferral | MDF-13 pads |
| No error handling required anywhere; MDF-12 deliberately added **no validation**, `lists.py` has none | ticket scope, PRD, DoD 2.1 "pure function principles" | rules out *raise* |
| No source anywhere uses truncation or dropping language | ticket AC, FR-2.2, PRD section 2 | rules out *truncate* |

"Raise" contradicts a strong, twice-applied repo convention. "Truncate" silently destroys user data
and is suggested by nothing. **Pad** is the only option with affirmative support, and that support
includes an explicit prior ruling in this very run-log directory that FR-2.2 owns padding.

Escalating a question my own process log already answers would spend the human's single escalation
budget on a settled point. Decided, not guessed; recorded here so it stays auditable and reversible.

**Derived sub-decision (pad to what width?): the global maximum column count across all rows,
header included.** Basis: no data loss. Padding only to the header's length would silently drop
cells from a body row wider than the header — the same data destruction that ruled out truncation.
Padding the header out with empty cells instead keeps every input cell in the output and still
yields a structurally valid table.

Unlike MDF-12's blank-line question, a wrong answer here is **cheap to unwind**: the return type is
`str` either way, the signature is fixed by the ticket, and ragged input is a malformed-input edge
case rather than the mainline path. That asymmetry is precisely why this one was decided and
blank-line semantics were not.

### The three non-blocking items, resolved with defaults

| # | Question | Decision | Basis |
|---|---|---|---|
| 1 | `build_markdown_table([])` | `""` | The only sane `str` for "no table"; mirrors `parse_delimiter_text("") == []`. No AC covers it. |
| 2 | Header-only matrix | Header row + separator row, no body rows | A header *is* a table; AC 1 and AC 2 are both satisfiable with no body rows. |
| 3 | Pipe escaping | **Not implemented** | Mentioned by no ticket, FR or guideline. Adding it would be unrequested behaviour — the same scope-creep reasoning that kept delimiter validation out of MDF-12. Documented as a known limitation instead. |

### Separator row width — decided *against* the analyst's recommendation

The analyst recommended a fixed three dashes (`|---|---|`) to be safe against a literal reading of
AC 2. **Rejected**, because a fixed-width separator defeats the entire purpose of AC 3:

- Cell padding is invisible in *rendered* Markdown — GFM renders `|Name|Age|` identically to
  `| Name  | Age |`. AC 3 ("all cells padded ... to match the max width of their respective column")
  therefore exists **solely** to align the raw text.
- A fixed `|---|---|` under width-padded cells leaves the pipes ragged, i.e. output that is not
  visually aligned — contradicting both the ticket title ("**Aligned** Markdown Table Generator")
  and its Context line ("visually **aligned** Markdown tables").
- The parenthetical is illustrative, not a literal expected string: FR-2.2 writes the same separator
  as `|---|`, a *single* group, for the general N-column case. A one-group literal cannot be the
  required output for a two-column table, so the notation is shorthand in both sources.

**Decision: separator dashes match the column width**, with effective column width
`max(3, longest cell in column)` so narrow columns still show at least the three dashes the AC
example uses and the pipes stay aligned. Purely cosmetic — both forms render identically — so it is
reversible via one constant, and it is flagged for the reviewer rather than escalated.

---

## 2026-09-06 — Orchestrator decision: branch base (cut from MDF-12, PR targets `main`)

Called out by the human as a real decision rather than a formality. Three options were weighed
against two hard, independently verified facts about this repo:

- **Fact A.** `src/md_formatter/tables.py` and `tests/test_tables.py` exist **only** on the MDF-12
  branch. Verified: `git cat-file -e main:src/md_formatter/tables.py` reports *"exists on disk, but
  not in 'main'"*.
- **Fact B.** `.github/workflows/ci.yml` is `on: pull_request: branches: [main]`. That filter
  matches the PR's **base**, so a PR based on anything other than `main` gets **no quality-check run
  at all** — only `claude-code-review.yml`, which carries no branch filter.

| Option | Outcome | Verdict |
|---|---|---|
| A. Cut from `main`, base `main` | Must re-create `tables.py` from scratch holding only `build_markdown_table`, producing a guaranteed **add/add conflict** with PR #6 on both `tables.py` and `tests/test_tables.py`, plus a second divergent copy of the module docstring. A human resolving that by hand could silently drop `parse_delimiter_text` or the blank-line asymmetry note. Integration against real parser output is untestable. | **Rejected** |
| B. Cut from MDF-12, base = MDF-12 branch (true stacked PR) | Minimal diff, no conflicts — but by Fact B **`ci.yml` never runs**, so the `release-manager` CI-watch gate cannot be satisfied at all. The only workaround would be editing `ci.yml`, unrequested scope creep on shared infrastructure. | **Rejected** |
| C. Cut from MDF-12, base `main` | Full CI runs; no conflicts; the parser is present, so the parse-to-build path is genuinely testable end to end. Cost: until #6 merges, this PR's diff-vs-`main` and commit list also contain MDF-12's commits. | **Chosen** |

Option C's cost is real and is **not** silently absorbed: if a human merged MDF-13's PR first, it
would carry MDF-12 into `main` without PR #6 having been approved. Mitigations applied — a prominent
"do not merge before #6" banner at the top of the PR body, the same warning in the JIRA comment, and
an explicit line in the final report. Once #6 merges, GitHub recomputes this PR's diff down to the
MDF-13 changes alone, with no action needed from anyone.

Not escalated: this is a version-control and engineering decision inside the orchestrator's remit
with a decisive technical tiebreaker (Fact B), not a requirements ambiguity. The escalation rule is
scoped to uncertainty *in requirements*, and spending the one-question budget here would have left
any genuine requirements gap unasked. Recorded in full so the owner can overrule it cheaply.

---

## 2026-09-06 — `developer`

**Input**
Verbatim ticket AC + In/Out-of-scope + FR-2.2 + the PRD scope-boundary line, plus the 13 binding
decisions above. Decisions were explicitly labelled **"orchestrator decisions derived from the
sources, not verbatim requirements"**, with an instruction to challenge any it believed *wrong*
rather than silently deviate — applying MDF-12 process lesson 3, where a derived constraint stated
as fact propagated a false claim into three artifacts before review caught it.
Constraints: touch only `src/md_formatter/tables.py`; do not alter `parse_delimiter_text`; no tests;
no git operations; no `uv.lock` changes. Told to write the doctests as
`print(build_markdown_table(...))` so a multi-line return renders readably instead of as a repr full
of escapes.

**Output**

- Added `build_markdown_table` to the existing `src/md_formatter/tables.py`. Module docstring opening
  line broadened to "Table parsing **and rendering** helpers"; the blank-line asymmetry paragraph
  from MDF-12 preserved verbatim, as instructed. `parse_delimiter_text` byte-for-byte untouched.
- Private `_MIN_COLUMN_WIDTH = 3` constant and a private pure helper `_fit(row, column_count)`
  returning a padded copy, which is what keeps the public function non-mutating.
- Five doctests, four using `print(...)` plus one repr case for `build_markdown_table([]) -> ''`
  (a `print("")` would emit a blank line that doctest reads as the end of the expected block — a
  real trap, correctly avoided).
- All 13 binding decisions implemented; none challenged. The agent independently flagged decision 7
  (width-matched separator) as the one most likely to draw review fire and agreed with the
  reasoning.

**Judgement calls accepted:** named constant over an inline `3`; the private `_fit` helper;
`zip(..., strict=True)` in the row renderer so a length mismatch surfaces loudly instead of silently
truncating; and a plain (non-raw) docstring with an escaped `"\n"`, deviating from
`parse_delimiter_text`'s `r"""` because only one escape is involved.

**Flagged by the developer, not actioned (correctly):** column widths use `len(cell)`, so wide East
Asian characters and combining marks align by character count but not by rendered display width. No
source requires display-width handling. Carried to "Open items" as a possible future ticket, not a
defect against MDF-13.

**Decision:** accepted, no rework requested.

---

## 2026-09-06 — `test-engineer`

**Input**
The 12-point behaviour contract, to be appended to the existing `tests/test_tables.py` following its
established conventions, without modifying any of the 30 `parse_delimiter_text` tests. Explicitly
told there are exactly **three** AC and not to invent "AC 4/AC 5" docstring citations (a defect
review had to correct on MDF-12), and not to write the vacuous `f(x) == f(x)` purity test that was
removed in review on both MDF-11 and MDF-12 — a genuine deep-copy mutate-then-recheck test instead.

**Mutation-guard requirement made mandatory**, citing MDF-12's review finding that a green 24-test
suite failed to pin the primary AC because two mutants survived it. Six specific mutants were
named and the agent was told to *build and run* scratch copies, not reason about them, keeping the
scratch files outside the repo.

**Output**

- `tests/test_tables.py` extended to **106 tests** total; `tables.py` at **100%** coverage (22/22).
- **All six named mutants confirmed killed**, by building isolated package copies and running the
  real suite against them via `PYTHONPATH`, then deleting the copies:

| Mutant | Killed by |
|---|---|
| `ljust` padding dropped | `test_cells_are_left_justified_to_the_max_column_width` (+11 others) |
| `_MIN_COLUMN_WIDTH` 3 -> 1 | `test_minimum_column_width_of_three_applies_even_to_single_char_cells` |
| Separator fixed `---` instead of width-matched | `test_separator_dashes_are_width_matched_not_a_literal_placeholder` |
| Column count from header length, not global max | `test_body_row_wider_than_header_widens_the_whole_table` |
| Header/separator order swapped | `test_header_is_immediately_followed_by_separator_row` (+12 others) |
| Trailing newline appended | `test_result_has_no_trailing_newline_and_lines_joined_with_newline` |

- Self-corrected an arithmetic slip while drafting (assumed `"a|b"` needed padding; it is exactly 3
  characters, the minimum width, so none applies) by running an interpreter rather than reasoning.
- Working tree left clean of scratch artifacts — verified independently by the orchestrator via
  `git status`.

**Decision:** accepted, no rework requested.

---

## 2026-09-06 — Local quality gate (orchestrator-run, independently verified)

Re-run by the orchestrator rather than taken from the subagents' self-reports, per the convention
established in `MDF-16.md` and followed in `MDF-12.md`:

| Gate | Command | Result |
|---|---|---|
| Lint | `uv run ruff check .` | All checks passed |
| Format | `uv run ruff format --check .` | 27 files already formatted |
| Types | `uv run mypy` (strict) | Success: no issues found in 6 source files |
| Tests + coverage | `uv run pytest` | **106 passed**, 100% total coverage (40/40 stmts), `tables.py` 22/22 |
| Doctests | `uv run pytest --no-cov --doctest-modules src` | 4 passed |

Zero rework cycles used (limit is 3). Baseline before MDF-13 was 88 passed / 25 stmts, so the
ticket added 18 tests and 15 statements with no regression.

**Behaviour spot-check against the AC, executed directly by the orchestrator** — not read off a
subagent report, because AC conformance is the one thing a passing suite cannot prove on its own
(the suite could faithfully encode the wrong contract):

| Input | Output | Matches |
|---|---|---|
| `[["Name","Age"],["Alice","30"],["Bob","7"]]` | header, separator, 2 body rows, all lines equal length | AC 1, 2, 3 |
| `[["id","value"]]` | `\| id  \| value \|` + `\| --- \| ----- \|` only | header-only decision |
| `[["a","b"],["c","d"]]` | all columns width 3 | min-width decision |
| `[["a"],["b","cc","ddd"]]` | 3 columns, header padded with 2 empty cells, **no cell lost** | ragged/global-max decision |
| `[["h1","h2","h3"],["x"]]` | short body row padded with empty cells | ragged decision |
| `[]` and `[[]]` | `""` | empty-input decision |
| `[["имя","возраст"],["Алиса","30"]]` | aligned | unicode |
| `[[" pad ","a\|b"]]` | `\|  pad  \| a\|b \|` — not stripped, not escaped | documented limitations |
| `build_markdown_table(parse_delimiter_text("a,b,c\nd,e"))` | 3-column aligned table, ragged source padded | MDF-12 -> MDF-13 pipeline |
| purity / trailing newline | input unmutated; no trailing `\n` | DoD 2.1, return contract |

Every case matches the AC and the recorded decisions. In particular the pipeline check confirms the
ragged-row decision does the job it was reasoned to do: MDF-12's parser emits `[['a','b','c'],
['d','e']]` and MDF-13 renders it as a complete, aligned 3-column table.

---

## 2026-09-06 — PR creation

- Commit `d3cdb35` — `docs(run-log): record MDF-13 intake, requirements and branch-base decision`.
- Commit `50f9b38` — `feat(tables): add aligned markdown table generator` (Conventional Commits).
- Commit `aefbb0d` — `docs(run-log): ...`, pushed to `feature/MDF-13-aligned-table-generator`.
- **PR #7** opened against `main`: https://github.com/denisdoronin/AI-SDLC/pull/7
- Incremental diff vs the MDF-12 base: `src/md_formatter/tables.py` +92, `tests/test_tables.py`
  +203, `docs/run-log/MDF-13.md` +294. **Product diff 295 lines**, under the 400-line guidance.
- PR body opens with a blockquoted **"STACKED PR — DO NOT MERGE BEFORE #6"** banner carrying the
  full branch-base rationale, since `git log main..HEAD` legitimately shows MDF-12's five commits
  as well as MDF-13's three.
- A first `git add -A` accidentally staged a tooling-generated `.claude/settings.local.json` edit.
  Caught by inspecting `git show --stat` rather than trusting the commit, then removed via
  `reset --soft` + `restore --staged` so the branch carries only intended files. Settings files are
  kept out of the branch per the MDF-16/MDF-12 precedent.
- Not merged, not approved.

## 2026-09-06 — JIRA comment

Comment `10034` added to MDF-13 with the PR link, the merge-order warning, the gate results, the
four decisions taken where the AC was silent, and the documented limitations:
https://dedoronin-1786901899646.atlassian.net/browse/MDF-13?focusedCommentId=10034
Comment only — no status transition (left at **In Progress**), no field or AC edits, no assignee
change. The agent re-confirmed read-only that the status and all three AC were unchanged.

---

## 2026-09-06/07 — `code-reviewer` (first/AI review, before human) — TWO CONFLICTING VERDICTS

**Input**
PR #7 + the verbatim three AC, FR-2.2, the PRD scope boundary, DoD 2.1, and the six orchestrator
rulings marked as settled — with the explicit carve-out that a ruling could be challenged if
*factually wrong* rather than merely different, and ruling 3 (width-matched separator) singled out
as the one I wanted pressure-tested. Told to review only `git diff feature/MDF-12-delimited-text-parser HEAD -- src tests`,
since the stacked branch makes `git diff main HEAD` include MDF-12. Instructed to probe rather than
inspect, to invent mutants the `test-engineer` had *not* already tried, and to fact-check every
claim in the docstring, PR body and this run log.

**This step produced two contradictory verdicts and had to be adjudicated.**

| Review | Verdict | Blocking | Notes |
|---|---|---|---|
| A (first run) | **APPROVE** | 0 | 22 mutants, 20 killed, 2 proved equivalent; 20,000-matrix property test; every claim verified |
| B (re-run) | **REQUEST_CHANGES** | 1 | AST-parsed the suite and found the body-row gap |

Review A completed but never posted to the PR, so the run was repeated. The repeat found a blocking
defect the first pass missed, despite the first pass being the more statistically thorough of the
two (20k random matrices vs. an AST scan). **The lesson is that volume of fuzzing did not
substitute for reasoning about what the test inputs structurally failed to cover:** A's random
matrices exercised the renderer heavily but A never asked whether the *suite* varied body-row count.

**Orchestrator adjudication: I reproduced B's finding myself rather than trusting either agent.**

```
*(render(_fit(row, column_count)) for row in body[:1]),   # drop all body rows after the first
```
Built as a copy outside the repo, run via `PYTHONPATH` override, with the import path asserted so
the mutant could not be shadowed by the real module: **`48 passed`.** A silent data-loss regression
stays green at 100% coverage.

Independently confirmed the root cause by AST-parsing every literal `build_markdown_table(...)` call
site in the suite: matrix row-counts were `{2 rows: 7, 1 row: 3}` — **never more than one body
row**, so any transformation of the body sequence was a no-op. `body[-1:]`, `reversed(body)` and
`sorted(body)` survive for the same reason.

**Verdict taken: REQUEST_CHANGES.** This is the identical failure mode that blocked MDF-12 — a green
suite at 100% coverage that does not actually pin the behaviour — recurring one ticket later, and
recurring *despite* the mandatory mutation-guard instruction, because the six mutants specified were
all about cell rendering and none about body-row iteration.

**Findings both reviews agreed on:**

- `tests/test_tables.py:362`, `assert result == "\n".join(result.split("\n"))` — a **mathematical
  identity**, true for every string, so no mutant can fail it. Verified by hand. Notable because the
  PR body and this log both claimed the MDF-11/MDF-12 tautological-assertion pattern had been
  avoided; it had reappeared in a new disguise.
- The docstring's limitations paragraph omits **control characters**, the worst limitation: a `\n`
  inside a cell renders a 3-row table as 4 physical lines and destroys alignment; a tab miscounts
  width.

**On ruling 3, which I asked to be attacked: both reviews independently argued *for* it.** A fixed
`|---|` separator under width-padded cells would make AC 2 and AC 3 contradict each other, since
cell padding is invisible in rendered GFM and so AC 3 would accomplish nothing. Review A also built
the *subtle* variant the `test-engineer` had not — constant `---` groups `ljust`-padded to column
width, so the pipes still line up and only the dash count differs — and confirmed the suite kills
it, i.e. the reading is genuinely pinned rather than accidentally satisfied. Review B added the
useful correction that AC 2's two-group `'|---|---|'` is **not** evidence against width-matching:
it reads as "one group per column" and is simply silent on width.

**Clean on both reviews:** implementation correctness (no defect found in the shipped logic by
either), deep purity by value *and* by nested-list `id()`, the no-data-loss property, no trailing
newline, minimum width 3, pipe alignment on every line, out-of-contract input failing loudly rather
than emitting garbage, performance, no security surface. `parse_delimiter_text` confirmed
byte-for-byte identical to the MDF-12 branch and the blank-line asymmetry paragraph verbatim —
checked by substring comparison against `feature/MDF-12-delimited-text-parser`, not by reading the
diff. All ten rows of this log's spot-check table reproduced exactly.

**Process note:** `gh pr review --request-changes` was rejected by GitHub ("Can not request changes
on your own pull request") because the PR author and the authenticated account are the same. The
review was posted with `gh pr comment` instead, with the verdict stated in the body. A formal
review state can only come from a different account — worth knowing for every future ticket in this
repo, since it means the AI review can never appear as a GitHub review state, only as a comment.

---

## 2026-09-07 — Rework (iteration 1 of max 3)

Two agents run concurrently on disjoint files, so they could not collide.

`test-engineer` — `tests/test_tables.py`, **the blocking fix**:

- Added `test_all_body_rows_are_rendered_in_input_order`: a header plus **three** body rows,
  deliberately out of alphabetical order (`h1/h2`, `z1/z2`, `a1/a2`, `m1/m2`), asserting the exact
  expected string so that row **count**, **order** and **content** are pinned at once. The
  out-of-order choice is what kills `sorted(body)`, which an in-order fixture would not.
- Deleted the vacuous `assert result == "\n".join(result.split("\n"))`, keeping the two genuine
  assertions in that test.
- Added `[[""]]` -> `"|     |\n| --- |"` and `[[], ["a"]]` -> `"|     |\n| --- |\n| a   |"` as
  characterisation tests, values obtained by **running** the function rather than assumed. The agent
  was told to report if either looked wrong rather than silently encode it; it judged both correct
  and consistent with the documented contract.

`developer` — `src/md_formatter/tables.py`, **docstrings only, zero logic lines changed**:

- Limitations paragraph widened from "neither stripped nor escaped" to "neither stripped, escaped
  nor validated", adding the two control-character cases: a cell containing a line break splits its
  row across physical lines (`[["a\nb","c"],["d","e"]]` renders as four physical lines, the first
  the unterminated `"| a"`), and a tab is measured by `len` as one character so the cell overflows
  its column once expanded. Framed as limitations outside the contract — **no validation, no
  raising, no sanitising added**, since no AC asks for it.
- The rendering paragraph now states the **one-space gutter** inside the pipes explicitly; without
  it a reader computing expected output from the docstring would derive `|Name |Age|`.
- Behaviour was executed before being described, not taken from my summary on trust.

**Orchestrator verification — done directly, not accepted from the agents' reports:**

- Re-built all four body-row mutants outside the repo and ran the real suite against each via
  `PYTHONPATH`, asserting `applied=1` each time so a silently-failed `sed` could not masquerade as a
  kill. Result: **all four now fail exactly one test**, the new body-row test.
  (Before the fix, the same harness gave `48 passed` — the mutants survived.)
- Proved the `tables.py` change is docstring-only by parsing the pre- and post-edit sources,
  stripping every docstring node, `ast.unparse`ing both and diffing: **0 lines**. This matches the
  developer's own independent AST check.
- Confirmed the vacuous assertion is gone (`grep -c` -> 0).

**Local quality gate after rework (orchestrator-run, independently verified):**

| Gate | Result |
|---|---|
| `ruff check .` | All checks passed |
| `ruff format --check .` | 27 files already formatted |
| `mypy` (strict) | Success: no issues found in 6 source files |
| `pytest` | **109 passed**, 100% coverage (40/40), `tables.py` 22/22 |
| `pytest --no-cov --doctest-modules src` | 4 passed |

Commit `509c847` — `fix(tables): close body-row test gap and document control-char limits`.
**1 of 3 rework iterations used.**

**Deliberately not actioned:**

- Review suggestion 5, `_fit`'s precondition being unenforced. The violating state is unreachable by
  construction (every caller fits the row first) and adding validation for an unreachable branch
  would be scope creep plus an uncoverable line, which the 90% coverage gate would then penalise.
- Review A's two surviving mutants, both **proved equivalent** rather than missed: `_fit` filler
  `""` -> `" "` (differentially fuzzed over 3,000 matrices, zero observable differences) and
  `strict=True` -> `False` (unreachable). Equivalent mutants are not test gaps.

An imprecise claim in the PR body — "reversible via one constant", when `render()`'s `ljust` would
still apply and yield `| ---   | --- |` rather than `|---|---|` — was corrected in the PR body
rather than left standing, per the MDF-12 lesson that false claims propagate across artifacts.
