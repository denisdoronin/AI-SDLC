# Markdown Formatter

A Python package for formatting Markdown.

## Install

```bash
pip install -e .
```

## Requirements

Python 3.11+

## Usage

Installing the package puts the `md-formatter` command on `PATH`:

```bash
md-formatter --mode bullet --input notes.txt --output notes.md
```

`python -m md_formatter` is an equivalent fallback when the script is not on `PATH`.

Flags:

- `--mode` (required): `bullet`, `numbered` or `table`.
- `--delimiter`: cell separator for `table` mode (default: `,`).
- `--input`: file to read; standard input is used when omitted.
- `--output`: file to write; standard output is used when omitted.

Exit codes: `0` success, `2` usage error, `1` a file or I/O failure. A missing or unreadable file is reported as a single-line message on stderr; some failures, notably a non-UTF-8 input file, currently surface as an unhandled Python error instead.

Run `md-formatter --help` for full details.
