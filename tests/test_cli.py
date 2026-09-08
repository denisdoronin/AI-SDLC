"""Unit tests for ``md_formatter.cli`` (``format_text``, ``build_parser``,
``main``) and, incidentally, for the ``python -m md_formatter`` entry point in
``md_formatter.__main__``.

Ticket: MDF-14. Acceptance criteria pinned throughout, by number:

    AC 1: Running ``md-formatter --help`` displays all flags and options.
    AC 2: Input read from file path or standard input (stdin).
    AC 3: Output written to specified output file path or standard output
          (stdout).

Governing Confluence requirements (PRD 4.3 "CLI & I/O Engine", FEAT-3), cited
as FR-3.1/FR-3.2/FR-3.3:

    FR-3.1 CLI Flags & Execution: supports ``--mode`` (bullet/numbered/table),
           ``--delimiter`` (default ``,``), ``--input`` and ``--output``.
    FR-3.2 Stream Compatibility: omitted ``--input`` reads stdin; omitted
           ``--output`` prints to stdout.
    FR-3.3 Error Handling: catches ``FileNotFoundError``/``PermissionError``,
           prints a clean message to stderr and exits ``1`` (no traceback).
"""

import io
import runpy
import sys
from pathlib import Path

import pytest

from md_formatter.cli import MODES, build_parser, format_text, main

# ---------------------------------------------------------------------------
# format_text
# ---------------------------------------------------------------------------


def test_format_text_bullet_mode_joins_multiple_lines_with_newline() -> None:
    """Happy path, bullet mode, 3 lines (never just 2 - see mutation notes at
    the bottom of this file). A mutant that joins with ``""`` instead of
    ``"\\n"`` would collapse the three bullets onto one line, which the exact
    equality below already catches.
    """
    result = format_text("first\nsecond\nthird", "bullet")
    assert result == "- first\n- second\n- third"


def test_format_text_numbered_mode_joins_and_increments() -> None:
    """Happy path, numbered mode, 3 lines. Distinguishes numbered from bullet
    dispatch: a mutant that routes ``"numbered"`` through
    ``format_bullet_list`` would produce ``"- alpha\\n- beta\\n- gamma"``
    instead of the auto-incrementing prefixes asserted here.
    """
    result = format_text("alpha\nbeta\ngamma", "numbered")
    assert result == "1. alpha\n2. beta\n3. gamma"


def test_format_text_table_mode_renders_header_and_two_body_rows() -> None:
    """Happy path, table mode, default delimiter, header plus **two** body
    rows (deliberately more than one, per the MDF-13 lesson that an
    always-one-body-row suite lets row-count/order mutants survive).
    """
    result = format_text("Name,Age\nAlice,30\nBob,25", "table")
    assert result == (
        "| Name  | Age |\n| ----- | --- |\n| Alice | 30  |\n| Bob   | 25  |"
    )


def test_format_text_table_mode_header_only_single_line() -> None:
    """Boundary: a single-line (header-only) input renders header + separator
    and no body row.
    """
    result = format_text("Name,Age", "table")
    assert result == "| Name | Age |\n| ---- | --- |"


def test_format_text_table_mode_respects_explicit_delimiter() -> None:
    """FR-3.1: an explicit, non-default delimiter is honoured in table mode.

    Mutation guard: if the table branch ignored ``delimiter`` and always split
    on ``","``, ``"a;b\\nc;d"`` would parse as two single-cell rows instead of
    two two-cell rows, producing a visibly different table.
    """
    result = format_text("a;b\nc;d", "table", delimiter=";")
    assert result == "| a   | b   |\n| --- | --- |\n| c   | d   |"


@pytest.mark.parametrize("mode", ["bullet", "numbered"])
@pytest.mark.parametrize("delimiter", [",", ";", "|"])
def test_format_text_delimiter_is_ignored_outside_table_mode(
    mode: str, delimiter: str
) -> None:
    """FR-3.1: ``delimiter`` is only consulted in table mode; bullet and
    numbered modes silently ignore it (not an error), so varying it never
    changes the result for the same text.
    """
    result = format_text("a,b\nc;d", mode, delimiter=delimiter)
    expected = "- a,b\n- c;d" if mode == "bullet" else "1. a,b\n2. c;d"
    assert result == expected


@pytest.mark.parametrize("mode", ["bullet", "numbered", "table"])
def test_format_text_empty_string_returns_empty_string(mode: str) -> None:
    """Boundary: an empty input formats to an empty string in every mode."""
    assert format_text("", mode) == ""


def test_format_text_bullet_mode_multiple_blank_lines_yield_bare_newline() -> None:
    """Boundary distinguishing 'no lines at all' from 'lines that are blank':
    two blank input lines still produce two (empty) output lines joined by
    ``"\\n"``, so the result is ``"\\n"``, not ``""``.
    """
    assert format_text("   \n\t", "bullet") == "\n"


def test_format_text_bullet_mode_preserves_blank_line_in_the_middle() -> None:
    """List modes preserve a blank line occurring in the *middle* of the
    input as an empty output line, distinct from a blank line at the end.
    """
    result = format_text("first\n\nsecond", "bullet")
    assert result == "- first\n\n- second"


def test_format_text_bullet_mode_trailing_blank_line_is_preserved() -> None:
    """Regression pin matching the function's own doctest: a trailing blank
    input line leaves the result ending in ``"\\n"`` in list modes.
    """
    assert format_text("x\n\n", "bullet") == "- x\n"


def test_format_text_table_mode_drops_blank_line_in_the_middle() -> None:
    """Unlike list modes, table mode drops a blank line wherever it occurs
    (delegated to ``parse_delimiter_text``), so it never produces an empty
    table row.
    """
    result = format_text("a,b\n\nc,d", "table")
    assert result == "| a   | b   |\n| --- | --- |\n| c   | d   |"


def test_format_text_bullet_mode_unicode_content_passes_through() -> None:
    """Non-ASCII (Cyrillic and emoji) content round-trips through bullet
    mode untouched.
    """
    result = format_text("Привет\n😀", "bullet")
    assert result == "- Привет\n- 😀"


def test_format_text_table_mode_unicode_content_passes_through() -> None:
    """Non-ASCII content round-trips through table mode: both the header and
    the body row keep their Cyrillic/emoji cells.
    """
    result = format_text("Имя,Возраст\nАлиса,😀", "table")
    lines = result.split("\n")
    assert len(lines) == 3
    assert "Имя" in lines[0] and "Возраст" in lines[0]
    assert "Алиса" in lines[2] and "😀" in lines[2]


@pytest.mark.parametrize("mode", ["Bullet", "BULLET", "unknown", ""])
def test_format_text_unknown_or_mis_cased_mode_raises_value_error(mode: str) -> None:
    """Negative path: any mode outside the exact three lower-case values
    raises ``ValueError``, including a mis-cased spelling of a valid mode
    (mode matching is case-sensitive, not normalised).
    """
    with pytest.raises(ValueError, match="unknown mode"):
        format_text("x", mode)


def test_modes_constant_lists_exactly_the_three_supported_values() -> None:
    """AC 1 / FR-3.1: ``MODES`` is the single source of truth for the
    ``--mode`` choices shown in ``--help``; pin its exact contents so a silent
    edit here is caught rather than only showing up as a help-text diff.
    """
    assert MODES == ("bullet", "numbered", "table")


# ---------------------------------------------------------------------------
# build_parser / --help (AC 1)
# ---------------------------------------------------------------------------


def test_build_parser_returns_parser_with_pinned_program_name() -> None:
    """The parser's program name is pinned to ``"md-formatter"`` so usage and
    help text read the same regardless of entry point.
    """
    parser = build_parser()
    assert parser.prog == "md-formatter"


def test_build_parser_help_text_lists_all_flags_and_mode_choices() -> None:
    """AC 1: ``--help`` (inspected here via ``format_help()``) displays every
    flag and, for ``--mode``, all three of its choices.
    """
    help_text = build_parser().format_help()
    for flag in ("--mode", "--delimiter", "--input", "--output"):
        assert flag in help_text
    for mode in MODES:
        assert mode in help_text


def test_build_parser_help_text_describes_each_flag_correctly() -> None:
    """AC 1 (S3): ``--help`` must display the flags' *options* (their help
    text), not merely their names. Whitespace is collapsed before matching so
    the assertion does not depend on argparse's terminal-width-sensitive line
    wrapping.

    Mutation guard: kills a mutant that swaps the ``--input``/``--output``
    help strings (both would still be *present* in the text, just attached to
    the wrong flag, which a mere ``"... in help_text"`` check cannot catch)
    and a mutant that drops the ``(default: ',')`` note from ``--delimiter``.
    """
    normalized = " ".join(build_parser().format_help().split())
    assert "--input INPUT path to the input file; standard input is read" in normalized
    assert (
        "--output OUTPUT path to the output file; standard output is written"
        in normalized
    )
    assert "cell separator, used by 'table' mode only (default: ',')" in normalized


def test_main_help_flag_exits_zero_and_prints_flags_to_stdout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AC 1, exercised end to end through ``main``: ``--help`` prints usage
    to stdout (not stderr) and exits with code 0, per the ``SystemExit``
    contract documented on ``main``.
    """
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    for flag in ("--mode", "--delimiter", "--input", "--output"):
        assert flag in captured.out
    for mode in MODES:
        assert mode in captured.out


def test_main_missing_required_mode_flag_exits_two() -> None:
    """Orchestrator-settled behaviour: ``--mode`` is required, so a usage
    error (argparse) exits with code 2, not 0 or 1.

    Mutation guard: kills a mutant that flips ``required=True`` to
    ``required=False`` on ``--mode``, which would let ``main([])`` proceed
    instead of raising here.
    """
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2


def test_main_invalid_mode_choice_exits_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A ``--mode`` value outside ``MODES`` is rejected by argparse itself
    (choices constraint) with a usage-error exit code of 2, before
    ``format_text`` is ever called.
    """
    with pytest.raises(SystemExit) as exc_info:
        main(["--mode", "invalid"])
    assert exc_info.value.code == 2
    assert "invalid" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# main: input source (AC 2 / FR-3.2)
# ---------------------------------------------------------------------------


def test_main_reads_input_from_file_when_input_flag_given(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC 2: input is read from the file named by ``--input`` when given."""
    input_file = tmp_path / "in.txt"
    input_file.write_text("first\nsecond\n", encoding="utf-8")

    exit_code = main(["--mode", "bullet", "--input", str(input_file)])

    assert exit_code == 0
    assert capsys.readouterr().out == "- first\n- second\n"


def test_main_reads_input_from_stdin_when_input_flag_omitted(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC 2 / FR-3.2: omitting ``--input`` reads from standard input."""
    monkeypatch.setattr(sys, "stdin", io.StringIO("alpha\nbeta\n"))

    exit_code = main(["--mode", "numbered"])

    assert exit_code == 0
    assert capsys.readouterr().out == "1. alpha\n2. beta\n"


def test_main_uses_input_file_content_not_stdin_when_both_available(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Mutation guard for ``_read_input``: proves the file path is actually
    consulted and stdin is not read unconditionally. Stdin is primed with
    content that would produce a visibly different result if it leaked
    through.
    """
    monkeypatch.setattr(sys, "stdin", io.StringIO("WRONG\n"))
    input_file = tmp_path / "in.txt"
    input_file.write_text("correct\n", encoding="utf-8")

    exit_code = main(["--mode", "bullet", "--input", str(input_file)])

    assert exit_code == 0
    assert capsys.readouterr().out == "- correct\n"


# ---------------------------------------------------------------------------
# main: output sink (AC 3 / FR-3.2)
# ---------------------------------------------------------------------------


def test_main_writes_output_to_file_and_nothing_to_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC 3: ``--output`` writes the result to that file, and stdout stays
    empty.

    Mutation guard for ``_write_output``: kills a mutant that ignores the
    path and always writes stdout - here stdout would then be non-empty and
    the file would stay absent/unwritten.
    """
    input_file = tmp_path / "in.txt"
    input_file.write_text("first\nsecond\n", encoding="utf-8")
    output_file = tmp_path / "out.md"

    exit_code = main(
        ["--mode", "bullet", "--input", str(input_file), "--output", str(output_file)]
    )

    assert exit_code == 0
    assert capsys.readouterr().out == ""
    assert output_file.read_text(encoding="utf-8") == "- first\n- second\n"


def test_main_reads_stdin_and_writes_to_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC 2 + AC 3 combined the other way round: stdin in, file out. Covers
    the input-source x output-sink combination not exercised by the other
    tests (file->stdout, stdin->stdout, file->file are covered elsewhere).
    """
    monkeypatch.setattr(sys, "stdin", io.StringIO("solo\n"))
    output_file = tmp_path / "out.md"

    exit_code = main(["--mode", "bullet", "--output", str(output_file)])

    assert exit_code == 0
    assert capsys.readouterr().out == ""
    assert output_file.read_text(encoding="utf-8") == "- solo\n"


def test_main_output_file_has_exactly_one_trailing_newline(tmp_path: Path) -> None:
    """Orchestrator-settled behaviour: a non-empty result is written with
    exactly one trailing ``"\\n"``.

    Read back with ``read_text`` (text mode, universal newlines), never
    ``read_bytes``, so this assertion is not sensitive to the
    ``"\\n"``-on-disk-as-``"\\r\\n"`` translation on Windows.

    Mutation guard: kills a mutant that writes bare ``result`` without the
    appended newline. The exact-equality assertion below already pins the
    count of trailing newlines, so no separate ``endswith`` checks are needed.
    """
    input_file = tmp_path / "in.txt"
    input_file.write_text("only\n", encoding="utf-8")
    output_file = tmp_path / "out.md"

    exit_code = main(
        ["--mode", "bullet", "--input", str(input_file), "--output", str(output_file)]
    )

    assert exit_code == 0
    assert output_file.read_text(encoding="utf-8") == "- only\n"


def test_main_pins_trailing_newline_contract_when_result_has_a_blank_line(
    tmp_path: Path,
) -> None:
    """B5 mutation guard: ``main`` appends exactly one ``"\\n"`` to ``result``
    as given, never a stripped copy of it. An input whose formatted result
    already ends in a blank line makes that distinguishable: bullet mode on
    ``"x\\n\\n"`` formats (per :func:`format_text`'s own doctest) to
    ``"- x\\n"``, so the file written by ``main`` must hold *two* trailing
    newlines, not one.

    Mutation guard: kills a mutant that writes
    ``f"{result.strip()}\\n"`` instead of ``f"{result}\\n"`` - the stripped
    variant would collapse this to a single trailing newline and drop the
    interior leading/trailing whitespace contract entirely.
    """
    input_file = tmp_path / "in.txt"
    input_file.write_text("x\n\n", encoding="utf-8")
    output_file = tmp_path / "out.md"

    exit_code = main(
        ["--mode", "bullet", "--input", str(input_file), "--output", str(output_file)]
    )

    assert exit_code == 0
    assert output_file.read_text(encoding="utf-8") == "- x\n\n"


def test_main_empty_result_writes_nothing_to_output_file(tmp_path: Path) -> None:
    """Orchestrator-settled behaviour: an empty formatted result writes
    nothing at all to the output file - not a lone ``"\\n"``.

    Mutation guard: kills a mutant that writes ``f"{result}\\n"``
    unconditionally, dropping the ``if result else ""`` guard.
    """
    input_file = tmp_path / "blank.txt"
    input_file.write_text("\n   \n\t\n", encoding="utf-8")
    output_file = tmp_path / "out.md"

    exit_code = main(
        ["--mode", "table", "--input", str(input_file), "--output", str(output_file)]
    )

    assert exit_code == 0
    assert output_file.read_text(encoding="utf-8") == ""


def test_main_empty_result_prints_nothing_to_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The stdout counterpart of the previous test: an empty result prints
    nothing, not a bare newline, to standard output either.
    """
    input_file = tmp_path / "blank.txt"
    input_file.write_text("\n   \n\t\n", encoding="utf-8")

    exit_code = main(["--mode", "table", "--input", str(input_file)])

    assert exit_code == 0
    assert capsys.readouterr().out == ""


def test_main_table_mode_non_ascii_column_width_pins_utf8_decoding(
    tmp_path: Path,
) -> None:
    """B4: kills a mutant that reads/writes files as ``"latin-1"`` instead of
    ``"utf-8"``.

    A byte-symmetric round trip (write UTF-8, misread as latin-1, write the
    resulting mojibake back as latin-1) reproduces the original bytes exactly
    whenever the transformation only prefixes or numbers each line, which is
    why a bullet-mode round-trip test cannot detect the wrong codec: encoding
    the mojibake back with the same wrong codec regenerates the original UTF-8
    bytes. Table mode breaks that symmetry because column width is computed
    with :func:`len` on the *decoded* string: the two UTF-8 bytes of ``"é"``
    decode to one character under UTF-8 but to two mojibake characters
    (``"Ã"`` + ``"©"``) under latin-1, so a latin-1 misread widens the ``café``
    column by one character. That extra width changes the number of dashes in
    the separator row and the padding of every other cell in that column, an
    asymmetry the byte-symmetric round trip cannot hide.

    Verified by building the mutant: swapping ``encoding="utf-8"`` for
    ``encoding="latin-1"`` at both I/O sites in ``cli.py`` turns the expected
    ``"| café | age |\\n| ---- | --- |\\n| b    | 5   |\\n"`` into
    ``"| café | age |\\n| ----- | --- |\\n| b     | 5   |\\n"`` (five dashes
    and an extra padding space instead of four), so this assertion fails
    under that mutant.
    """
    input_file = tmp_path / "in.txt"
    input_file.write_text("café,age\nb,5\n", encoding="utf-8")
    output_file = tmp_path / "out.md"

    exit_code = main(
        ["--mode", "table", "--input", str(input_file), "--output", str(output_file)]
    )

    assert exit_code == 0
    assert output_file.read_text(encoding="utf-8") == (
        "| café | age |\n| ---- | --- |\n| b    | 5   |\n"
    )


# ---------------------------------------------------------------------------
# main: FR-3.1 flags (delimiter default vs explicit, through the real CLI)
# ---------------------------------------------------------------------------


def test_main_delimiter_defaults_to_comma_when_omitted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """FR-3.1: ``--delimiter`` defaults to ``","`` when omitted."""
    input_file = tmp_path / "in.txt"
    input_file.write_text("a,b\nc,d\n", encoding="utf-8")

    exit_code = main(["--mode", "table", "--input", str(input_file)])

    assert exit_code == 0
    assert capsys.readouterr().out == ("| a   | b   |\n| --- | --- |\n| c   | d   |\n")


def test_main_delimiter_flag_overrides_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """FR-3.1: an explicit ``--delimiter`` overrides the ``","`` default,
    exercised end to end through ``main`` rather than only via
    ``format_text`` directly.
    """
    input_file = tmp_path / "in.txt"
    input_file.write_text("a;b\nc;d\n", encoding="utf-8")

    exit_code = main(
        ["--mode", "table", "--input", str(input_file), "--delimiter", ";"]
    )

    assert exit_code == 0
    assert capsys.readouterr().out == ("| a   | b   |\n| --- | --- |\n| c   | d   |\n")


def test_main_multi_character_delimiter_is_still_accepted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``_non_empty_delimiter`` only rejects the empty string, so a
    multi-character delimiter such as ``"||"`` remains legal end to end
    through ``main`` (and is matched literally, per
    :func:`~md_formatter.tables.parse_delimiter_text`).
    """
    input_file = tmp_path / "in.txt"
    input_file.write_text("a||b\nc||d\n", encoding="utf-8")

    exit_code = main(
        ["--mode", "table", "--input", str(input_file), "--delimiter", "||"]
    )

    assert exit_code == 0
    assert capsys.readouterr().out == ("| a   | b   |\n| --- | --- |\n| c   | d   |\n")


def test_main_table_mode_through_the_real_cli_renders_multiple_body_rows(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """S6: at the ``main()`` layer (not just via ``format_text`` directly),
    a table with more than one body row is rendered in full, header through
    every row, per the MDF-13 lesson that an always-one-body-row suite lets
    row-count/order mutants survive.
    """
    input_file = tmp_path / "in.txt"
    input_file.write_text("Name,Age\nAlice,30\nBob,25\nCarol,40\n", encoding="utf-8")

    exit_code = main(["--mode", "table", "--input", str(input_file)])

    assert exit_code == 0
    assert capsys.readouterr().out == (
        "| Name  | Age |\n"
        "| ----- | --- |\n"
        "| Alice | 30  |\n"
        "| Bob   | 25  |\n"
        "| Carol | 40  |\n"
    )


def test_main_output_file_truncates_pre_existing_content_instead_of_appending(
    tmp_path: Path,
) -> None:
    """S8: ``--output`` at a pre-existing non-empty file truncates it rather
    than appending, per the ``_write_output`` docstring's "truncating it"
    contract.

    Mutation guard: kills a mutant that opens the output file in append mode
    - the leftover ``"OLD CONTENT THAT MUST BE GONE"`` would still be present
    (before or after the new result) if the file were not truncated first.
    """
    input_file = tmp_path / "in.txt"
    input_file.write_text("first\nsecond\n", encoding="utf-8")
    output_file = tmp_path / "out.md"
    output_file.write_text("OLD CONTENT THAT MUST BE GONE\n" * 5, encoding="utf-8")

    exit_code = main(
        ["--mode", "bullet", "--input", str(input_file), "--output", str(output_file)]
    )

    assert exit_code == 0
    assert output_file.read_text(encoding="utf-8") == "- first\n- second\n"


def test_main_uses_sys_argv_when_argv_is_none(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """``argv=None`` falls back to ``sys.argv[1:]``. This branch is otherwise
    never exercised, since every other test injects argv explicitly.
    """
    monkeypatch.setattr(sys, "argv", ["md-formatter", "--mode", "bullet"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("only\n"))

    exit_code = main()

    assert exit_code == 0
    assert capsys.readouterr().out == "- only\n"


# ---------------------------------------------------------------------------
# main: --delimiter validation (_non_empty_delimiter, usage error)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", ["bullet", "numbered", "table"])
def test_main_empty_delimiter_is_a_usage_error_in_every_mode(
    mode: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """An empty ``--delimiter`` is rejected by argparse itself (via the
    ``type=_non_empty_delimiter`` callable) before ``format_text`` ever runs,
    in *every* mode, even the two list modes that would have ignored the
    delimiter anyway: an invalid flag value is a usage error regardless of
    whether the run would have consulted it.

    Pins the exact contract: ``SystemExit`` code ``2``, and the last line of
    stderr is exactly ``"md-formatter: error: argument --delimiter: value
    must not be empty"`` with no traceback (argparse prints a usage block
    before that line, which is why the assertion targets the last line
    rather than the whole of stderr).

    Mutation guard: kills a mutant that makes ``_non_empty_delimiter`` accept
    the empty string (return it unchanged instead of raising), which would
    make this whole test raise nothing and fail at ``pytest.raises``.
    """
    with pytest.raises(SystemExit) as exc_info:
        main(["--mode", mode, "--delimiter", ""])

    assert exc_info.value.code == 2
    err_lines = capsys.readouterr().err.splitlines()
    assert "Traceback" not in "\n".join(err_lines)
    assert err_lines[-1] == (
        "md-formatter: error: argument --delimiter: value must not be empty"
    )


# ---------------------------------------------------------------------------
# main: FR-3.3 error handling
# ---------------------------------------------------------------------------


def test_main_returns_one_and_reports_missing_input_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """FR-3.3: a missing ``--input`` file raises a real (unmocked)
    ``FileNotFoundError``, which is caught, reported as a single clean line
    on stderr with no traceback, and mapped to exit code 1. Real filesystem
    behaviour is used here (rather than mocking) because a non-existent path
    is deterministic and portable across Windows and Linux.
    """
    missing = tmp_path / "does-not-exist.txt"

    exit_code = main(["--mode", "bullet", "--input", str(missing)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    err_lines = captured.err.splitlines()
    assert len(err_lines) == 1
    assert err_lines[0].startswith("md-formatter: error: ")


def test_main_returns_one_when_output_parent_directory_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """FR-3.3: an ``--output`` path whose parent directory does not exist
    raises a real ``FileNotFoundError`` on write, caught the same way as the
    read-side error. No file is left behind.
    """
    input_file = tmp_path / "in.txt"
    input_file.write_text("x\n", encoding="utf-8")
    bad_output = tmp_path / "missing-dir" / "out.md"

    exit_code = main(
        ["--mode", "bullet", "--input", str(input_file), "--output", str(bad_output)]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    err_lines = captured.err.splitlines()
    assert len(err_lines) == 1
    assert err_lines[0].startswith("md-formatter: error: ")
    assert not bad_output.exists()


def _read_text_raises_permission_error(
    self: Path, encoding: str | None = None, errors: str | None = None
) -> str:
    """Stand-in for ``Path.read_text`` that always raises ``PermissionError``.

    Used instead of creating a real unreadable file, which is unreliable on
    Windows (and would make the test filesystem/permission-model dependent).
    """
    raise PermissionError("permission denied (simulated)")


def _write_text_raises_permission_error(
    self: Path,
    data: str,
    encoding: str | None = None,
    errors: str | None = None,
    newline: str | None = None,
) -> int:
    """Stand-in for ``Path.write_text`` that always raises ``PermissionError``,
    for the same reason as ``_read_text_raises_permission_error`` above.
    """
    raise PermissionError("permission denied (simulated)")


def test_main_returns_one_on_permission_error_reading_input(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """FR-3.3: ``PermissionError`` on the read side is caught the same way
    as ``FileNotFoundError`` (both are ``OSError`` subclasses caught by the
    same ``except OSError`` clause in ``main``).

    Technique: ``Path.read_text`` is monkeypatched to raise directly, rather
    than attempting to create a real permission-denied file on disk.
    """
    monkeypatch.setattr(Path, "read_text", _read_text_raises_permission_error)

    exit_code = main(["--mode", "bullet", "--input", "irrelevant.txt"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    err_lines = captured.err.splitlines()
    assert len(err_lines) == 1
    assert "permission denied" in err_lines[0]


def test_main_returns_one_on_permission_error_writing_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """FR-3.3: ``PermissionError`` on the write side is likewise caught,
    reported and mapped to exit code 1.

    The real input file is written *before* ``Path.write_text`` is
    monkeypatched, so only the CLI's own write attempt is affected.
    """
    input_file = tmp_path / "in.txt"
    input_file.write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(Path, "write_text", _write_text_raises_permission_error)

    exit_code = main(
        ["--mode", "bullet", "--input", str(input_file), "--output", "out.md"]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    err_lines = captured.err.splitlines()
    assert len(err_lines) == 1
    assert "permission denied" in err_lines[0]


# ---------------------------------------------------------------------------
# python -m md_formatter (src/md_formatter/__main__.py)
# ---------------------------------------------------------------------------


def test_dunder_main_module_runs_cli_and_exits_with_its_return_code(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Covers ``sys.exit(main())`` under ``if __name__ == "__main__":`` in
    ``md_formatter/__main__.py``, which is unreachable via a plain import.
    ``runpy.run_module`` executes the package's ``__main__`` submodule when
    given the package name with ``run_name="__main__"``, genuinely exercising
    that guarded line rather than special-casing it as an exception.
    """
    monkeypatch.setattr(sys, "argv", ["md-formatter", "--mode", "bullet"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("z\n"))

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("md_formatter", run_name="__main__")

    assert exc_info.value.code == 0
    assert capsys.readouterr().out == "- z\n"


# ---------------------------------------------------------------------------
# Note on mutation coverage (see the MDF-14 test-engineer report for the full
# kill/survive table run against isolated package copies outside this repo):
#
# One mutant was found to be an environment-dependent equivalent rather than
# a genuine gap: dropping `encoding="utf-8"` from `_read_input`/`_write_output`
# survives on this Windows/UTF-8-locale runner (and would very likely survive
# in CI too, since GitHub-hosted Linux runners also default to a UTF-8
# locale), because Path.read_text/write_text without an explicit `encoding`
# then falls back to `locale.getpreferredencoding(False)`, which happens to
# already be UTF-8 in both environments. It is not equivalent on every
# platform (a non-UTF-8-locale Windows box, for instance, would behave
# differently), so the explicit `encoding="utf-8"` argument is still correct
# and worth keeping - the mutant's survival here is a limitation of what a
# unit test running on a UTF-8-locale machine can observe, not evidence that
# the parameter is dead code.
# ---------------------------------------------------------------------------
