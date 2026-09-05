"""Unit tests for ``md_formatter.tables.parse_delimiter_text``."""

import pytest

from md_formatter.tables import parse_delimiter_text


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
