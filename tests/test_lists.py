"""Unit tests for ``md_formatter.lists.format_bullet_list`` and
``md_formatter.lists.format_numbered_list``.
"""

import pytest

from md_formatter.lists import format_bullet_list, format_numbered_list


def test_empty_input_returns_empty_list() -> None:
    """An empty input list yields an empty output list."""
    assert format_bullet_list([]) == []


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("first", "- first"),
        ("a", "- a"),
        ("hello world", "- hello world"),
    ],
)
def test_single_line_gets_bullet_prefix(line: str, expected: str) -> None:
    """A single non-empty line receives a ``"- "`` prefix."""
    assert format_bullet_list([line]) == [expected]


@pytest.mark.parametrize(
    "whitespace_line",
    ["", " ", "   ", "\t", "\t\t", " \t ", "\n", " \n\t "],
)
def test_whitespace_heavy_lines_map_to_empty_string(whitespace_line: str) -> None:
    """Empty and whitespace-only lines map to ``""`` rather than being dropped."""
    assert format_bullet_list([whitespace_line]) == [""]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  first ", "- first"),
        ("\tsecond\t", "- second"),
        ("   leading only", "- leading only"),
        ("trailing only   ", "- trailing only"),
        ("\n wrapped \n", "- wrapped"),
    ],
)
def test_leading_and_trailing_whitespace_is_stripped(raw: str, expected: str) -> None:
    """Leading/trailing whitespace on content lines is stripped before prefixing."""
    assert format_bullet_list([raw]) == [expected]


def test_internal_whitespace_is_preserved() -> None:
    """Only leading/trailing whitespace is stripped; internal spacing stays intact."""
    result = format_bullet_list(["  hello   world  "])
    assert result == ["- hello   world"]


def test_multiple_lines_mixing_content_and_blank_lines() -> None:
    """Content and blank lines interleave correctly, preserving order and length."""
    lines = ["first", "", "  ", "second", "\t", "third"]
    result = format_bullet_list(lines)
    assert result == ["- first", "", "", "- second", "", "- third"]
    assert len(result) == len(lines)


@pytest.mark.parametrize(
    "lines",
    [
        [],
        [""],
        ["single"],
        ["a", "b", "c"],
        ["  ", "content", "\t\t", ""],
    ],
)
def test_output_length_always_matches_input_length(lines: list[str]) -> None:
    """The output list always has the same length as the input (never filtered)."""
    assert len(format_bullet_list(lines)) == len(lines)


def test_does_not_mutate_input_list() -> None:
    """The function must not mutate the caller's input list."""
    original = ["  first ", "", "   ", "second\t"]
    original_copy = list(original)

    format_bullet_list(original)

    assert original == original_copy


def test_does_not_mutate_input_list_elements() -> None:
    """The function must not mutate the individual string elements in place."""
    line = "  keep me untouched  "
    lines = [line]

    format_bullet_list(lines)

    assert lines[0] == line
    assert lines[0] is line


def test_returns_new_list_object() -> None:
    """The function returns a new list instance, not the same object."""
    original = ["first", "second"]
    result = format_bullet_list(original)
    assert result is not original


# ---------------------------------------------------------------------------
# format_numbered_list
# ---------------------------------------------------------------------------


def test_numbered_empty_input_returns_empty_list() -> None:
    """An empty input list yields an empty output list."""
    assert format_numbered_list([]) == []


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("first", "1. first"),
        ("a", "1. a"),
        ("hello world", "1. hello world"),
    ],
)
def test_numbered_single_line_gets_numbered_prefix(line: str, expected: str) -> None:
    """AC #3: a single non-empty line receives a ``"1. "`` prefix."""
    assert format_numbered_list([line]) == [expected]


def test_numbered_multiple_lines_increment_counter() -> None:
    """AC #3: multiple content lines receive auto-incrementing prefixes."""
    lines = ["alpha", "beta", "gamma"]
    result = format_numbered_list(lines)
    assert result == ["1. alpha", "2. beta", "3. gamma"]
    assert len(result) == len(lines)


def test_numbered_interspersed_empty_lines_do_not_break_numbering() -> None:
    """AC #3: interspersed empty lines map to ``""`` and numbering stays unbroken."""
    lines = ["  alpha ", "", "beta", "   ", "gamma"]
    result = format_numbered_list(lines)
    assert result == ["1. alpha", "", "2. beta", "", "3. gamma"]


@pytest.mark.parametrize(
    "whitespace_line",
    ["", " ", "   ", "\t", "\t\t", " \t ", "\n", " \n\t "],
)
def test_numbered_whitespace_heavy_lines_map_to_empty_string(
    whitespace_line: str,
) -> None:
    """Empty/whitespace-only lines map to ``""`` and do not advance the counter."""
    result = format_numbered_list([whitespace_line, "content"])
    assert result == ["", "1. content"]


def test_numbered_leading_and_trailing_empty_lines_do_not_shift_numbering() -> None:
    """Leading/trailing blank lines don't offset the starting number."""
    lines = ["", "  ", "first", "second", "\t"]
    result = format_numbered_list(lines)
    assert result == ["", "", "1. first", "2. second", ""]


def test_numbered_consecutive_empty_lines() -> None:
    """Consecutive blank lines each map to ``""`` without consuming a number."""
    lines = ["first", "", "", "   ", "second"]
    result = format_numbered_list(lines)
    assert result == ["1. first", "", "", "", "2. second"]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  first ", "1. first"),
        ("\tsecond\t", "1. second"),
        ("   leading only", "1. leading only"),
        ("trailing only   ", "1. trailing only"),
        ("\n wrapped \n", "1. wrapped"),
    ],
)
def test_numbered_leading_and_trailing_whitespace_is_stripped(
    raw: str, expected: str
) -> None:
    """Leading/trailing whitespace on content lines is stripped before prefixing."""
    assert format_numbered_list([raw]) == [expected]


def test_numbered_internal_whitespace_is_preserved() -> None:
    """Only leading/trailing whitespace is stripped; internal spacing stays intact."""
    result = format_numbered_list(["  hello   world  "])
    assert result == ["1. hello   world"]


def test_numbered_counter_reaches_double_digits_without_padding() -> None:
    """The counter is not zero-padded or width-limited past single digits."""
    lines = [f"item{i}" for i in range(1, 13)]
    result = format_numbered_list(lines)
    expected = [f"{i}. item{i}" for i in range(1, 13)]
    assert result == expected
    assert result[8] == "9. item9"
    assert result[9] == "10. item10"
    assert result[11] == "12. item12"


def test_numbered_all_empty_lines_never_advance_counter() -> None:
    """An input consisting solely of blank lines never advances the counter."""
    lines = ["", "   ", "\t", " \n "]
    result = format_numbered_list(lines)
    assert result == ["", "", "", ""]


@pytest.mark.parametrize(
    "lines",
    [
        [],
        [""],
        ["single"],
        ["a", "b", "c"],
        ["  ", "content", "\t\t", ""],
    ],
)
def test_numbered_output_length_always_matches_input_length(
    lines: list[str],
) -> None:
    """The output list always has the same length as the input (never filtered)."""
    assert len(format_numbered_list(lines)) == len(lines)


def test_numbered_does_not_mutate_input_list() -> None:
    """The function must not mutate the caller's input list."""
    original = ["  first ", "", "   ", "second\t"]
    original_copy = list(original)

    format_numbered_list(original)

    assert original == original_copy


def test_numbered_returns_new_list_object() -> None:
    """The function returns a new list instance, not the same object."""
    original = ["first", "second"]
    result = format_numbered_list(original)
    assert result is not original


# Note on negative-path coverage: format_numbered_list has no error paths -
# it never raises for any list[str] input (empty, whitespace-only, or mixed
# content all resolve to a valid, same-length output). This mirrors the
# documented exception format_bullet_list took in MDF-10. In place of an
# exception test, purity (test_numbered_does_not_mutate_input_list) and the
# length/ordering invariants above
# (test_numbered_output_length_always_matches_input_length,
# test_numbered_all_empty_lines_never_advance_counter) serve as the
# substitute guarantees for this function.
