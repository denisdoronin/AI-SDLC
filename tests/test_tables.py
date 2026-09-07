"""Unit tests for ``md_formatter.tables.parse_delimiter_text`` and
``md_formatter.tables.build_markdown_table``.
"""

import copy

import pytest

from md_formatter.tables import build_markdown_table, parse_delimiter_text


def test_empty_input_returns_empty_list() -> None:
    """An empty input string yields an empty matrix (human-confirmed contract)."""
    assert parse_delimiter_text("") == []


@pytest.mark.parametrize(
    "whitespace_text",
    ["   \n  \n", "\n", "   ", "\t", " \n\t \n "],
)
def test_whitespace_only_input_returns_empty_list(whitespace_text: str) -> None:
    """Whitespace-only input produces no rows (blank lines are dropped)."""
    assert parse_delimiter_text(whitespace_text) == []


def test_two_by_two_matrix_with_stripped_cells() -> None:
    """AC 1: a 2D matrix is parsed with every cell stripped of whitespace."""
    result = parse_delimiter_text("a, b\nc ,d")
    assert result == [["a", "b"], ["c", "d"]]


def test_internal_whitespace_is_preserved() -> None:
    """AC 1 strips only leading/trailing cell whitespace; internal spacing survives.

    Regression/mutation guard: a mutant that collapses internal whitespace (e.g.
    via ``" ".join(cell.split())``) would corrupt ``"a  b"`` into ``"a b"`` and
    must be caught here, per the same convention as
    ``test_lists.py::test_internal_whitespace_is_preserved``.
    """
    result = parse_delimiter_text("  a  b  ,c")
    assert result == [["a  b", "c"]]


@pytest.mark.parametrize(
    ("text", "delimiter", "expected"),
    [
        ("a, b\nc ,d", ",", [["a", "b"], ["c", "d"]]),
        ("a; b\nc ;d", ";", [["a", "b"], ["c", "d"]]),
        ("a\t b\nc \td", "\t", [["a", "b"], ["c", "d"]]),
    ],
)
def test_configurable_single_character_delimiters(
    text: str, delimiter: str, expected: list[list[str]]
) -> None:
    """AC 2: comma (default), semicolon and tab delimiters are all supported.

    The tab case is deliberately not covered by the module doctest, so it is
    exercised explicitly here.
    """
    assert parse_delimiter_text(text, delimiter=delimiter) == expected


@pytest.mark.parametrize(
    "text",
    ["a,b\nc,d", "a,b\r\nc,d", "a,b\rc,d"],
)
def test_row_splitting_handles_lf_crlf_and_cr(text: str) -> None:
    """LF, CRLF and bare CR line endings all separate rows, without a stray
    ``\\r`` surviving in the last cell of a row.
    """
    result = parse_delimiter_text(text)
    assert result == [["a", "b"], ["c", "d"]]
    assert "\r" not in result[0][-1]
    assert "\r" not in result[1][-1]


def test_crlf_does_not_leave_stray_carriage_return_in_last_cell() -> None:
    """Regression: a CRLF-terminated row must not leak ``\\r`` into its last cell."""
    result = parse_delimiter_text("name,age\r\nAlice,30\r\n")
    assert result == [["name", "age"], ["Alice", "30"]]
    assert result[1][-1] == "30"


def test_blank_lines_are_dropped_leading_trailing_and_interior() -> None:
    """Blank and whitespace-only lines produce no row, wherever they occur."""
    text = "\n   \na,b\n\t\nc,d\n\n"
    result = parse_delimiter_text(text)
    assert result == [["a", "b"], ["c", "d"]]


def test_consecutive_blank_lines_of_mixed_kinds_collapse_to_no_rows() -> None:
    """Consecutive blank lines, empty or whitespace-only, yield zero rows."""
    text = "a,b\n\n\n   \n\t\nc,d"
    result = parse_delimiter_text(text)
    assert result == [["a", "b"], ["c", "d"]]


def test_line_of_only_delimiters_is_not_blank() -> None:
    """A line consisting solely of delimiters yields a row of empty cells.

    Binding decision: a line is blank iff ``line.strip() == ""``, so a
    delimiter-only line does not qualify and is not dropped.
    """
    assert parse_delimiter_text(",") == [["", ""]]


def test_lone_delimiter_surrounded_by_whitespace_is_not_blank() -> None:
    """A whitespace-padded lone delimiter is still not blank after stripping.

    This is the case that distinguishes the "blank iff ``line.strip() == ''``"
    rule from a naive pre-split whitespace check: the raw line " , " is not
    empty/whitespace-only, so it still yields a row of (stripped) empty cells.
    """
    assert parse_delimiter_text(" , ") == [["", ""]]


def test_empty_interior_cell_is_preserved() -> None:
    """An empty interior cell between two delimiters is preserved as ``""``."""
    assert parse_delimiter_text("a,,b") == [["a", "", "b"]]


def test_trailing_delimiter_produces_trailing_empty_cell() -> None:
    """A trailing delimiter yields a trailing empty cell, not a dropped one.

    Mutation guard: a mutant that drops a trailing empty cell would turn this
    3-cell row into 2 cells.
    """
    assert parse_delimiter_text("a,b,") == [["a", "b", ""]]


def test_leading_delimiter_produces_leading_empty_cell() -> None:
    """A leading delimiter yields a leading empty cell."""
    assert parse_delimiter_text(",a") == [["", "a"]]


def test_ragged_rows_are_not_padded() -> None:
    """Rows of differing lengths pass through un-padded (pinned design).

    Padding rows to a common width belongs to a future ticket; this test
    guards against an accidental "fix" being introduced here.
    """
    result = parse_delimiter_text("a,b,c\nd,e")
    assert result == [["a", "b", "c"], ["d", "e"]]
    assert len(result[0]) != len(result[1])


def test_single_line_with_no_delimiter_present() -> None:
    """A line without the delimiter yields a single-cell row."""
    assert parse_delimiter_text("abc") == [["abc"]]


@pytest.mark.parametrize(
    ("text", "delimiter", "expected"),
    [
        ("a.b", ".", [["a", "b"]]),
        ("a|b|c", "|", [["a", "b", "c"]]),
    ],
)
def test_regex_metacharacter_delimiter_is_treated_literally(
    text: str, delimiter: str, expected: list[list[str]]
) -> None:
    """A delimiter that is a regex metacharacter is split on literally.

    ``str.split`` is not a regex operation, so ``"."`` and ``"|"`` behave as
    plain single-character delimiters rather than "match anything"/alternation.
    """
    assert parse_delimiter_text(text, delimiter=delimiter) == expected


def test_multi_character_delimiter_follows_str_split_semantics() -> None:
    """A multi-character delimiter is outside the AC 2 single-character contract,
    but is not validated or rejected. Behaviour simply follows ``str.split``
    semantics, and no exception is raised.
    """
    result = parse_delimiter_text("a::b::c", delimiter="::")
    assert result == [["a", "b", "c"]]


def test_empty_delimiter_pins_native_str_split_behaviour() -> None:
    """Pin (do not mandate) the ``delimiter=""`` behaviour inherited from
    ``str.split``.

    AC 2 scopes this function to single-character delimiters, so an empty
    string is out of contract and deliberately left unvalidated (ruling: no
    scope-creep validation is to be added). ``str.split("")`` raises
    ``ValueError: empty separator`` natively for any non-blank content, so that
    exception propagates unchanged from a content line. On blank/whitespace-only
    input the line is dropped before ``split`` is ever called, so no exception
    is raised. This test documents that native, input-dependent behaviour so a
    future reader does not mistake it for a designed feature.
    """
    with pytest.raises(ValueError, match="empty separator"):
        parse_delimiter_text("a", delimiter="")

    assert parse_delimiter_text("", delimiter="") == []
    assert parse_delimiter_text("   \n\t", delimiter="") == []


def test_unicode_cells_are_parsed_without_encoding_assumptions() -> None:
    """Cyrillic and emoji cells round-trip through parsing untouched."""
    result = parse_delimiter_text("Привет, мир\n😀, 😎")
    assert result == [["Привет", "мир"], ["😀", "😎"]]


def test_mutating_returned_matrix_does_not_affect_subsequent_calls() -> None:
    """The function is pure: mutating the returned matrix has no effect on a
    later call with the same input.
    """
    text = "a,b\nc,d"
    first = parse_delimiter_text(text)
    first.append(["mutated"])
    first[0].append("extra")

    second = parse_delimiter_text(text)

    assert second == [["a", "b"], ["c", "d"]]


# Note on negative-path coverage: parse_delimiter_text performs no validation of
# its own. For any delimiter within the AC 2 contract (a single character, or a
# multi-character string, per test_multi_character_delimiter_follows_str_split_
# semantics), it never raises for any text input. The one exception is a
# delimiter of "" - outside the AC 2 contract - which raises for non-blank
# content via native str.split semantics
# (test_empty_delimiter_pins_native_str_split_behaviour). Purity
# (test_mutating_returned_matrix_does_not_affect_subsequent_calls) and the
# ragged-row invariant (test_ragged_rows_are_not_padded) serve as additional
# guarantees for this function.


# --- Unit tests for md_formatter.tables.build_markdown_table -----------------


@pytest.mark.parametrize(
    "rows",
    [[], [[]], [[], []]],
    ids=["no-rows", "single-empty-row", "two-empty-rows"],
)
def test_empty_or_columnless_input_returns_empty_string(rows: list[list[str]]) -> None:
    """No rows, or rows with zero columns between them, render to ``""``."""
    assert build_markdown_table(rows) == ""


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        pytest.param([[""]], "|     |\n| --- |", id="single-empty-cell"),
        pytest.param(
            [[], ["a"]],
            "|     |\n| --- |\n| a   |",
            id="empty-header-row-with-nonempty-body-row",
        ),
    ],
)
def test_cases_adjacent_to_the_fully_empty_inputs_render_a_real_table(
    rows: list[list[str]], expected: str
) -> None:
    """Characterisation tests for two cases one code path away from the fully
    empty inputs in ``test_empty_or_columnless_input_returns_empty_string``: a
    single empty cell, and an empty header row paired with a non-empty body
    row. Both have at least one column overall, so both render a real
    (non-empty) header-plus-separator table rather than ``""``.
    """
    assert build_markdown_table(rows) == expected


def test_header_is_immediately_followed_by_separator_row() -> None:
    """AC 1 and AC 2: the first row is the header, and a separator row
    immediately follows it, before any body row.
    """
    result = build_markdown_table([["Name", "Age"], ["Alice", "30"]])
    lines = result.split("\n")
    assert lines[0] == "| Name  | Age |"
    assert lines[1] == "| ----- | --- |"
    assert lines[2] == "| Alice | 30  |"


def test_header_only_input_renders_header_and_separator_with_no_body() -> None:
    """AC 1 and AC 2: a single-row (header-only) matrix renders exactly two
    lines - the header and the separator - and no body row.
    """
    result = build_markdown_table([["id", "value"]])
    assert result == "| id  | value |\n| --- | ----- |"
    assert len(result.split("\n")) == 2


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        pytest.param(
            [["x", "long"], ["yy", "z"]],
            "| x   | long |\n| --- | ---- |\n| yy  | z    |",
            id="one-column-below-minimum-one-above",
        ),
        pytest.param(
            [["a", "b", "c"], ["d", "e", "f"]],
            "| a   | b   | c   |\n| --- | --- | --- |\n| d   | e   | f   |",
            id="every-cell-shorter-than-minimum-width",
        ),
    ],
)
def test_cells_are_left_justified_to_the_max_column_width(
    rows: list[list[str]], expected: str
) -> None:
    """AC 3: every cell is padded with trailing spaces to the width of its
    column, where a column's width is the longest cell in it (never
    narrower than the 3-character minimum).
    """
    assert build_markdown_table(rows) == expected


def test_minimum_column_width_of_three_applies_even_to_single_char_cells() -> None:
    """AC 3: a column whose longest cell is a single character is still
    rendered at the 3-character minimum width, not width 1.

    Mutation guard: catches a mutant that lowers ``_MIN_COLUMN_WIDTH`` from 3
    to 1, which would shrink the separator dashes and header padding below
    the pinned minimum.
    """
    result = build_markdown_table([["a"], ["b"]])
    lines = result.split("\n")
    assert lines[0] == "| a   |"
    assert lines[1] == "| --- |"
    assert lines[2] == "| b   |"


def test_separator_dashes_are_width_matched_not_a_literal_placeholder() -> None:
    """The separator row is not a fixed ``|---|---|`` literal: each group of
    dashes matches its column's actual width, so pipes line up across the
    header, separator and body lines.

    Mutation guard: catches a mutant that emits a constant ``"---"`` group
    per column regardless of width - it would pass a header-only check but
    misalign the pipes as soon as a column is wider than 3 characters.
    """
    result = build_markdown_table([["x", "longest"], ["y", "z"]])
    lines = result.split("\n")
    header, separator, body = lines

    assert separator == "| --- | ------- |"
    # Every rendered line has the same length, and each "|" lines up at the
    # same character offsets across header, separator and body.
    assert len({len(line) for line in lines}) == 1
    header_pipes = [i for i, ch in enumerate(header) if ch == "|"]
    separator_pipes = [i for i, ch in enumerate(separator) if ch == "|"]
    body_pipes = [i for i, ch in enumerate(body) if ch == "|"]
    assert header_pipes == separator_pipes == body_pipes


def test_ragged_body_rows_are_padded_with_empty_cells() -> None:
    """A body row shorter than the widest row is rendered as if it ended
    with empty cells, rather than raising or shifting columns.
    """
    result = build_markdown_table([["a", "b", "c"], ["d", "e"]])
    assert result == "| a   | b   | c   |\n| --- | --- | --- |\n| d   | e   |     |"


def test_body_row_wider_than_header_widens_the_whole_table() -> None:
    """A body row wider than the header widens the entire table: the header
    itself gains empty trailing cells rather than the extra body column
    being dropped or the header staying narrow.

    Mutation guard: catches a mutant that takes the column count from
    ``len(header)`` instead of the global maximum row length - such a
    mutant would drop the third column entirely instead of widening the
    header.
    """
    result = build_markdown_table([["a"], ["b", "cc"]])
    lines = result.split("\n")
    assert lines[0] == "| a   |     |"
    assert lines[1] == "| --- | --- |"
    assert lines[2] == "| b   | cc  |"
    assert len(lines[0].split("|")) == len(lines[2].split("|"))


def test_all_body_rows_are_rendered_in_input_order() -> None:
    """AC 1 and AC 2: every body row is rendered, in input order, not just the
    first or last body row.

    Mutation guard: a matrix with more than one body row is required to
    catch a mutant that keeps only ``body[:1]``, only ``body[-1:]``, reverses
    the body, or sorts it - each of those would leave every other test in
    this module (deliberately at most one body row) green. The body rows
    here are chosen out of alphabetical order so that "first only", "last
    only", "reversed" and "sorted" each produce a different, wrong result.
    """
    result = build_markdown_table(
        [["h1", "h2"], ["z1", "z2"], ["a1", "a2"], ["m1", "m2"]]
    )
    assert result == (
        "| h1  | h2  |\n| --- | --- |\n| z1  | z2  |\n| a1  | a2  |\n| m1  | m2  |"
    )


def test_result_has_no_trailing_newline_and_lines_joined_with_newline() -> None:
    """The rendered table's lines are joined with ``"\\n"`` and the result
    carries no trailing newline.

    Mutation guard: catches a mutant that appends a trailing ``"\\n"`` to the
    joined result.
    """
    result = build_markdown_table([["a", "b"], ["c", "d"]])
    assert not result.endswith("\n")
    assert result.count("\n") == 2


def test_input_matrix_and_rows_are_not_mutated() -> None:
    """Purity (Definition of Done 2.1): neither the input matrix nor its
    nested row lists are mutated by rendering.
    """
    rows = [["a", "bb"], ["ccc"]]
    snapshot = copy.deepcopy(rows)

    build_markdown_table(rows)

    assert rows == snapshot


def test_cells_are_not_stripped_documented_limitation() -> None:
    """Documented limitation: cells are rendered exactly as given, so
    surrounding whitespace in a cell is not stripped and widens the column
    accordingly. This is not a desirable feature, just the pinned behaviour.
    """
    result = build_markdown_table([[" pad ", "x"]])
    lines = result.split("\n")
    assert lines[0] == "|  pad  | x   |"
    assert " pad " in lines[0]


def test_literal_pipe_in_cell_is_not_escaped_documented_limitation() -> None:
    """Documented limitation: a literal ``"|"`` inside a cell is emitted
    as-is, unescaped, which will visually split the column when the
    Markdown is rendered. This is a pinned limitation, not intended
    behaviour, per the function's docstring.
    """
    result = build_markdown_table([["a|b", "y"]])
    lines = result.split("\n")
    assert lines[0] == "| a|b | y   |"
    assert "a|b" in lines[0]


def test_unicode_cells_render_with_codepoint_based_widths() -> None:
    """Cyrillic and emoji cells round-trip through rendering, with column
    widths computed from codepoint length (``len``), not display width.
    """
    result = build_markdown_table([["Имя", "Возраст"], ["Алиса", "😀"]])
    lines = result.split("\n")
    assert lines[0] == "| Имя   | Возраст |"
    assert lines[2] == "| Алиса | 😀       |"


def test_integration_with_parse_delimiter_text_on_ragged_source() -> None:
    """The two MDF-12/MDF-13 functions compose end to end: parsing a ragged
    delimited text and rendering it produces a fully aligned table where the
    short row is padded rather than raising.
    """
    result = build_markdown_table(parse_delimiter_text("a,b,c\nd,e"))
    assert result == "| a   | b   | c   |\n| --- | --- | --- |\n| d   | e   |     |"


def test_integration_with_parse_delimiter_text_header_only() -> None:
    """The pipeline also composes correctly for header-only delimited text."""
    result = build_markdown_table(parse_delimiter_text("Name,Age"))
    assert result == "| Name | Age |\n| ---- | --- |"
