"""Table parsing and rendering helpers for the Markdown formatter.

Unlike the helpers in :mod:`md_formatter.lists`, which preserve blank input
lines as empty strings so that the output length matches the input length, the
parser in this module drops blank lines entirely. That asymmetry is deliberate:
a blank line carries no cells and therefore no table row.
"""

_MIN_COLUMN_WIDTH = 3
"""Narrowest rendered column, wide enough for the ``---`` separator group."""


def parse_delimiter_text(text: str, delimiter: str = ",") -> list[list[str]]:
    r"""Parse delimited text into a 2D matrix of cell values.

    The text is split into lines with :meth:`str.splitlines`, so any line
    boundary that method recognises acts as a row separator: ``"\n"``,
    ``"\r\n"`` and ``"\r"`` are the common ones, but form feeds, vertical tabs
    and the Unicode line separators are treated the same way. Lines that are
    empty or contain only whitespace are dropped and do not produce a row; an
    empty string therefore yields an empty matrix. Every line that survives is
    split on ``delimiter`` and each resulting cell is stripped of leading and
    trailing whitespace. A line consisting only of delimiters is not blank and
    yields a row of empty cells.

    Rows are returned exactly as parsed, so a ragged input produces rows with
    differing cell counts; padding rows to a common width is not this
    function's responsibility. The input string is never mutated.

    Args:
        text: Delimited text to parse, with one row per line.
        delimiter: Separator between cells within a row, expected to be a
            single character. A multi-character delimiter is not rejected and
            is matched literally, following :meth:`str.split` semantics.

    Returns:
        A new list of rows, each row a list of stripped cell values.

    Raises:
        ValueError: Propagated from :meth:`str.split` when ``delimiter`` is
            the empty string and at least one non-blank line is parsed. That
            input is outside this function's contract.

    Examples:
        >>> parse_delimiter_text("a, b\nc ,d")
        [['a', 'b'], ['c', 'd']]
        >>> parse_delimiter_text("1;2;3", delimiter=";")
        [['1', '2', '3']]
        >>> parse_delimiter_text("a,b\n   \n\nc")
        [['a', 'b'], ['c']]
        >>> parse_delimiter_text("")
        []
    """
    matrix: list[list[str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        matrix.append([cell.strip() for cell in line.split(delimiter)])
    return matrix


def build_markdown_table(rows: list[list[str]]) -> str:
    """Build an aligned Markdown table from a 2D matrix of cell values.

    The first row is the table header and is followed by a separator row; every
    remaining row becomes a body row. The table has as many columns as the
    longest row, header included, so no cell is ever dropped; rows that are
    shorter are rendered as if they ended with empty cells. Each column is as
    wide as its longest cell, but never narrower than three characters, and
    every cell is left-justified with trailing spaces to that width. Each
    padded cell is additionally surrounded by a one-space gutter inside the
    pipes: a row is the opening ``"| "``, then the padded cells joined with
    ``" | "``, then the closing ``" |"``, so a column of width ``n`` occupies
    ``n`` + 2 characters between its pipes. The separator row uses the same
    widths, so the pipes of the separator line up with the pipes of the header
    and body rows.

    Cells are rendered exactly as given: they are neither stripped, escaped nor
    validated. A cell containing a literal ``"|"`` is emitted as-is and will
    split the column when the Markdown is rendered. A cell containing a line
    break is emitted as-is too and therefore splits its row across several
    physical lines: ``[["a\\nb", "c"], ["d", "e"]]`` renders as four physical
    lines instead of three, the first of them the unterminated ``"| a"``. A
    cell containing a tab is measured by :func:`len` as a single character, so
    its column is sized as if the tab were one character wide and the cell
    overflows that width wherever the tab is expanded. Escaping, sanitising and
    rejecting such cells are all outside this function's contract. The input
    matrix and its rows are never mutated.

    Args:
        rows: Table rows, each a list of cell values, with the header first.
            Rows may have differing lengths.

    Returns:
        The rendered table as a single string whose lines are joined with
        ``"\\n"`` and which has no trailing newline. An empty string is
        returned when there are no rows or when no row has any cells.

    Examples:
        >>> print(build_markdown_table([["Name", "Age"], ["Alice", "30"]]))
        | Name  | Age |
        | ----- | --- |
        | Alice | 30  |

        A header-only matrix renders as a header and a separator:

        >>> print(build_markdown_table([["id", "value"]]))
        | id  | value |
        | --- | ----- |

        Short rows are padded with empty cells, and a body row that is wider
        than the header widens the whole table:

        >>> print(build_markdown_table([["a"], ["b", "cc"]]))
        | a   |     |
        | --- | --- |
        | b   | cc  |

        >>> build_markdown_table([])
        ''
    """
    column_count = max((len(row) for row in rows), default=0)
    if column_count == 0:
        return ""

    widths = [
        max(
            _MIN_COLUMN_WIDTH,
            max(len(row[index]) for row in rows if index < len(row)),
        )
        for index in range(column_count)
    ]

    def render(cells: list[str]) -> str:
        padded = [cell.ljust(width) for cell, width in zip(cells, widths, strict=True)]
        return f"| {' | '.join(padded)} |"

    header, *body = rows
    lines = [
        render(_fit(header, column_count)),
        render(["-" * width for width in widths]),
        *(render(_fit(row, column_count)) for row in body),
    ]
    return "\n".join(lines)


def _fit(row: list[str], column_count: int) -> list[str]:
    """Return a copy of ``row`` extended with empty cells to ``column_count``.

    Args:
        row: Row to copy; never mutated.
        column_count: Target number of cells, never smaller than ``len(row)``.

    Returns:
        A new list of exactly ``column_count`` cells.
    """
    return row + [""] * (column_count - len(row))
