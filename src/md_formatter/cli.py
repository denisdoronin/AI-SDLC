"""Command-line entry point for the Markdown formatter.

The module keeps the transformation and the I/O apart: :func:`format_text` is
pure and does the whole job in memory, while :func:`main` only parses the
command line, moves text between files or standard streams and maps failures
to exit codes. Every file is read and written as UTF-8 regardless of the
platform default encoding; the standard streams keep whatever encoding the
interpreter gave them.

All I/O happens in text mode, so line endings are translated as usual: any of
``"\\n"``, ``"\\r\\n"`` and ``"\\r"`` is accepted on input and normalised to
``"\\n"``, while on output ``"\\n"`` is written as the platform line ending,
which is ``"\\r\\n"`` on Windows.

Known limitations:

* A UTF-8 byte order mark at the start of an input file is not stripped. It
  survives decoding and ends up inside the first list item or the first table
  cell, which renders as ``"- \\ufeffalpha"`` for an input file whose first
  line is ``alpha``. Reading the file as ``utf-8-sig`` would strip it; that
  is a file-content decoding concern and is not handled here.
* Only files are pinned to UTF-8. The standard streams keep whatever encoding
  the interpreter gave them, so on a platform whose default encoding is not
  UTF-8 the same bytes can decode differently depending on whether they
  arrive through ``--input`` or through standard input, and likewise for
  ``--output`` and standard output.
"""

import argparse
import sys
from pathlib import Path

from md_formatter.lists import format_bullet_list, format_numbered_list
from md_formatter.tables import build_markdown_table, parse_delimiter_text

_PROG = "md-formatter"
"""Program name shown in usage and error messages, identical for every entry point."""

MODES = ("bullet", "numbered", "table")
"""Values accepted by the ``--mode`` flag."""


def format_text(text: str, mode: str, delimiter: str = ",") -> str:
    r"""Format text as a Markdown bullet list, numbered list or table.

    In ``"bullet"`` and ``"numbered"`` mode the text is split with
    :meth:`str.splitlines` and passed to :func:`~md_formatter.lists.format_bullet_list`
    or :func:`~md_formatter.lists.format_numbered_list`, then joined back with
    ``"\n"``. Those helpers return one entry per element of
    :meth:`str.splitlines` and map blank lines to empty strings, so the result
    holds one line per element that ``splitlines`` produced and a trailing blank
    input line leaves the result ending in ``"\n"``. That is not always one line
    per physical input line: ``splitlines`` also breaks on ``"\v"``, ``"\f"``,
    ``"\x1c"``, ``"\x1d"``, ``"\x1e"``, ``"\x85"`` and the Unicode separators
    U+2028 and U+2029, so a single physical line holding any of those yields
    several output lines. In ``"table"`` mode the text is parsed by
    :func:`~md_formatter.tables.parse_delimiter_text` and rendered by
    :func:`~md_formatter.tables.build_markdown_table`, which drop blank lines
    and treat the first surviving line as the table header; a table result never
    ends with a newline.

    ``delimiter`` is only consulted in ``"table"`` mode and is ignored by the
    two list modes. No I/O is performed and the input string is never mutated.

    Args:
        text: Text to format, with one list item or one table row per line.
        mode: One of ``"bullet"``, ``"numbered"`` or ``"table"``.
        delimiter: Separator between cells, used in ``"table"`` mode only.

    Returns:
        The formatted Markdown. The list modes emit one output line per element
        of ``text.splitlines()``, blank ones included, so an input whose
        ``splitlines()`` yields ``n`` elements comes back holding ``n - 1``
        newlines; whitespace-only input of ``n`` lines therefore returns
        ``n - 1`` newlines and nothing else, not the empty string. From the
        list modes the empty string comes back only when ``splitlines()``
        yielded nothing or yielded a single blank line. ``"table"`` mode drops
        blank lines instead, so it returns the empty string for any input
        without a non-blank line.

    Raises:
        ValueError: If ``mode`` is not one of the three supported values.
            Also propagated from :meth:`str.split` in ``"table"`` mode when
            ``delimiter`` is the empty string and at least one non-blank line
            is parsed; the two list modes never raise it because they ignore
            ``delimiter``. The command line rejects an empty ``--delimiter``
            before it reaches this function, so only a direct caller can
            trigger that case.

    Examples:
        >>> print(format_text("first\nsecond", "bullet"))
        - first
        - second
        >>> print(format_text("alpha\nbeta", "numbered"))
        1. alpha
        2. beta
        >>> print(format_text("Name,Age\nAlice,30", "table"))
        | Name  | Age |
        | ----- | --- |
        | Alice | 30  |

        The delimiter is honoured in ``"table"`` mode:

        >>> print(format_text("a;b", "table", delimiter=";"))
        | a   | b   |
        | --- | --- |

        The list modes keep one output line per input line even when every line
        is blank, so only a single whitespace-only line formats to nothing:

        >>> format_text("   ", "bullet")
        ''
        >>> format_text("   \n\t", "bullet")
        '\n'
        >>> format_text(" \n \n ", "bullet")
        '\n\n'

        ``"table"`` mode drops blank lines, so the same input formats to
        nothing whatever its length:

        >>> format_text(" \n \n ", "table")
        ''

        A trailing blank line is preserved by the list modes:

        >>> format_text("x\n\n", "bullet")
        '- x\n'
    """
    if mode == "bullet":
        return "\n".join(format_bullet_list(text.splitlines()))
    if mode == "numbered":
        return "\n".join(format_numbered_list(text.splitlines()))
    if mode == "table":
        return build_markdown_table(parse_delimiter_text(text, delimiter))
    raise ValueError(f"unknown mode: {mode!r}")


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ``md-formatter`` command.

    The parser is returned unused so that the command line can be inspected and
    tested without running the command. Its program name is pinned to
    ``"md-formatter"``, so usage and help text read the same whether the tool is
    started through the console script or through ``python -m md_formatter``.

    Returns:
        A parser accepting ``--mode``, ``--delimiter``, ``--input`` and
        ``--output``, of which only ``--mode`` is required. ``--mode`` is
        restricted to :data:`MODES` and ``--delimiter`` is checked by
        :func:`_non_empty_delimiter`, so both reject a bad value as a usage
        error rather than letting it reach :func:`format_text`.
    """
    parser = argparse.ArgumentParser(
        prog=_PROG,
        description="Format plain text as a Markdown list or table.",
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=MODES,
        help="output format to produce",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        type=_non_empty_delimiter,
        help="cell separator, used by 'table' mode only (default: ',')",
    )
    parser.add_argument(
        "--input",
        help="path to the input file; standard input is read when omitted",
    )
    parser.add_argument(
        "--output",
        help="path to the output file; standard output is written when omitted",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the ``md-formatter`` command.

    The input is read from the ``--input`` file or, when that flag is omitted,
    from standard input. It is formatted according to ``--mode`` and written to
    the ``--output`` file or, when that flag is omitted, to standard output.
    A non-empty result is written with exactly one ``"\\n"`` appended to it,
    subject to the text-mode line ending translation described in the module
    docstring; an empty result is written as nothing at all, so no file is left
    holding a lone newline.

    Args:
        argv: Command-line arguments without the program name. When ``None``,
            ``sys.argv[1:]`` is used.

    Returns:
        ``0`` on success, or ``1`` when an input or output file cannot be read
        or written, in which case a single-line message is printed to standard
        error.

    Raises:
        SystemExit: Propagated from :mod:`argparse` with code ``2`` for a usage
            error, which includes a missing or unknown ``--mode`` and an empty
            ``--delimiter``, and with code ``0`` for ``--help``. Nothing else
            escapes: the parser guarantees ``--mode`` is one of :data:`MODES`
            and ``--delimiter`` is non-empty, which are the only two inputs
            :func:`format_text` can raise on, and both file operations catch
            :class:`OSError` and return ``1``.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    input_path: str | None = args.input
    output_path: str | None = args.output

    try:
        text = _read_input(input_path)
    except OSError as error:
        return _fail(error)

    result = format_text(text, args.mode, args.delimiter)

    try:
        _write_output(output_path, f"{result}\n" if result else "")
    except OSError as error:
        return _fail(error)

    return 0


def _non_empty_delimiter(value: str) -> str:
    """Validate a ``--delimiter`` value on behalf of :mod:`argparse`.

    Only the empty string is rejected, and it is rejected in every mode, even
    though the list modes ignore the delimiter: an invalid value for a flag is
    a usage error whether or not the run would have consulted it. Nothing else
    is checked, so a multi-character delimiter stays legal and is matched
    literally by :func:`~md_formatter.tables.parse_delimiter_text`.

    Args:
        value: Value as typed on the command line, or the ``","`` default,
            which :mod:`argparse` also feeds through this callable because it
            is a string.

    Returns:
        ``value`` unchanged.

    Raises:
        argparse.ArgumentTypeError: If ``value`` is the empty string, carrying
            the message ``"value must not be empty"``. The flag is not named in
            it on purpose, because :mod:`argparse` already prefixes the message
            with ``"argument --delimiter: "``. The parser turns the exception
            into a usage error, printing one line to standard error that reads
            ``md-formatter: error: argument --delimiter: value must not be
            empty`` and exiting with code ``2``.

    Examples:
        >>> _non_empty_delimiter(";")
        ';'
        >>> _non_empty_delimiter("||")
        '||'

        The message names no flag, so that :mod:`argparse` does not repeat it:

        >>> _non_empty_delimiter("")
        Traceback (most recent call last):
          ...
        argparse.ArgumentTypeError: value must not be empty
    """
    if not value:
        raise argparse.ArgumentTypeError("value must not be empty")
    return value


def _read_input(path: str | None) -> str:
    """Read the text to format.

    Args:
        path: File to read as UTF-8, or ``None`` to read standard input.

    Returns:
        The text that was read.

    Raises:
        OSError: If the file cannot be read.
    """
    if path is None:
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _write_output(path: str | None, payload: str) -> None:
    """Write the formatted text.

    Args:
        path: File to write as UTF-8, truncating it, or ``None`` to write to
            standard output.
        payload: Exact text to write, line terminator included.

    Raises:
        OSError: If the file cannot be written.
    """
    if path is None:
        sys.stdout.write(payload)
        return
    Path(path).write_text(payload, encoding="utf-8")


def _fail(error: OSError) -> int:
    """Report a failed file operation on standard error.

    Args:
        error: The error to report, rendered as ``"md-formatter: error: ..."``.

    Returns:
        The exit code to hand back to the shell, always ``1``.
    """
    print(f"{_PROG}: error: {error}", file=sys.stderr)
    return 1
