"""Bullet list formatting helpers for the Markdown formatter."""


def format_bullet_list(lines: list[str]) -> list[str]:
    """Format lines as a Markdown bullet list.

    Each line is stripped of leading and trailing whitespace. Non-empty lines
    receive a ``"- "`` prefix, while lines that are empty or contain only
    whitespace are mapped to an empty string. The input list is never mutated
    and the returned list always has the same length as the input.

    Args:
        lines: Lines to format as bullet list items.

    Returns:
        A new list with one formatted entry per input line.

    Examples:
        >>> format_bullet_list(["  first ", "   ", "second"])
        ['- first', '', '- second']
    """
    formatted: list[str] = []
    for line in lines:
        stripped = line.strip()
        formatted.append(f"- {stripped}" if stripped else "")
    return formatted
