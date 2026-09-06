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
