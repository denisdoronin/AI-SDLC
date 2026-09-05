r"""Table parsing helpers for the Markdown formatter.

Unlike the helpers in :mod:`md_formatter.lists`, which preserve blank input
lines as empty strings so that the output length matches the input length, the
parser in this module drops blank lines entirely. That asymmetry is deliberate:
a blank line carries no cells and therefore no table row.
"""


def parse_delimiter_text(text: str, delimiter: str = ",") -> list[list[str]]:
    r"""Parse delimited text into a 2D matrix of cell values.

    The text is split into lines with :meth:`str.splitlines`, so ``"\n"``,
    ``"\r\n"`` and ``"\r"`` all act as row separators. Lines that are empty or
    contain only whitespace are dropped and do not produce a row; an empty
    string therefore yields an empty matrix. Every line that survives is split
    on ``delimiter`` and each resulting cell is stripped of leading and
    trailing whitespace. A line consisting only of delimiters is not blank and
    yields a row of empty cells.

    Rows are returned exactly as parsed, so a ragged input produces rows with
    differing cell counts; padding rows to a common width is not this
    function's responsibility. The input string is never mutated.

    Args:
        text: Delimited text to parse, with one row per line.
        delimiter: Single-character separator between cells within a row.

    Returns:
        A new list of rows, each row a list of stripped cell values.

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
