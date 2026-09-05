"""Unit tests for ``md_formatter.tables.parse_delimiter_text``."""

import pytest

from md_formatter.tables import parse_delimiter_text


def test_empty_input_returns_empty_list() -> None:
    """AC 5: an empty input string yields an empty matrix."""
    assert parse_delimiter_text("") == []


@pytest.mark.parametrize(
    "whitespace_text",
    ["   \n  \n", "\n", "   ", "\t", " \n\t \n "],
)
def test_whitespace_only_input_returns_empty_list(whitespace_text: str) -> None:
    """AC 5: whitespace-only input produces no rows."""
    assert parse_delimiter_text(whitespace_text) == []


def test_two_by_two_matrix_with_stripped_cells() -> None:
    """AC 1: a 2D matrix is parsed with every cell stripped of whitespace."""
    result = parse_delimiter_text("a, b\nc ,d")
    assert result == [["a", "b"], ["c", "d"]]


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
    """AC 4: blank and whitespace-only lines produce no row, wherever they occur."""
    text = "\n   \na,b\n\t\nc,d\n\n"
    result = parse_delimiter_text(text)
    assert result == [["a", "b"], ["c", "d"]]


def test_consecutive_blank_lines_of_mixed_kinds_collapse_to_no_rows() -> None:
    """AC 4: consecutive blank lines, empty or whitespace-only, yield zero rows."""
    text = "a,b\n\n\n   \n\t\nc,d"
    result = parse_delimiter_text(text)
    assert result == [["a", "b"], ["c", "d"]]


def test_line_of_only_delimiters_is_not_blank() -> None:
    """AC 6: a line consisting solely of delimiters yields a row of empty cells."""
    assert parse_delimiter_text(",") == [["", ""]]


def test_empty_interior_cell_is_preserved() -> None:
    """AC 6: an empty interior cell between two delimiters is preserved as ``""``."""
    assert parse_delimiter_text("a,,b") == [["a", "", "b"]]


def test_ragged_rows_are_not_padded() -> None:
    """AC 7: rows of differing lengths pass through un-padded (pinned design).

    Padding rows to a common width belongs to a future ticket; this test
    guards against an accidental "fix" being introduced here.
    """
    result = parse_delimiter_text("a,b,c\nd,e")
    assert result == [["a", "b", "c"], ["d", "e"]]
    assert len(result[0]) != len(result[1])


def test_single_line_with_no_delimiter_present() -> None:
    """AC 9: a line without the delimiter yields a single-cell row."""
    assert parse_delimiter_text("abc") == [["abc"]]


def test_multi_character_delimiter_does_not_raise() -> None:
    """AC 10: a multi-character delimiter is not validated or rejected.

    Behaviour simply follows ``str.split`` semantics; no exception is raised.
    """
    result = parse_delimiter_text("a::b::c", delimiter="::")
    assert result == [["a", "b", "c"]]


def test_unicode_cells_are_parsed_without_encoding_assumptions() -> None:
    """Cyrillic and emoji cells round-trip through parsing untouched."""
    result = parse_delimiter_text("Привет, мир\n😀, 😎")
    assert result == [["Привет", "мир"], ["😀", "😎"]]


def test_repeated_calls_return_equal_results() -> None:
    """AC 8: the function is pure - the same input always yields an equal result."""
    text = "a,b\nc,d"
    assert parse_delimiter_text(text) == parse_delimiter_text(text)


def test_mutating_returned_matrix_does_not_affect_subsequent_calls() -> None:
    """AC 8: mutating the returned matrix has no effect on a later call."""
    text = "a,b\nc,d"
    first = parse_delimiter_text(text)
    first.append(["mutated"])
    first[0].append("extra")

    second = parse_delimiter_text(text)

    assert second == [["a", "b"], ["c", "d"]]


# Note on negative-path coverage: parse_delimiter_text has no error paths - it
# never raises for any (text, delimiter) combination, including a
# multi-character delimiter (test_multi_character_delimiter_does_not_raise).
# In place of an exception test, purity
# (test_repeated_calls_return_equal_results,
# test_mutating_returned_matrix_does_not_affect_subsequent_calls) and the
# ragged-row invariant (test_ragged_rows_are_not_padded) serve as the
# substitute guarantees for this function.
