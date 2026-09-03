"""Unit tests for ``md_formatter.lists.format_bullet_list``."""

import pytest

from md_formatter.lists import format_bullet_list


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
