"""Module entry point so that ``python -m md_formatter`` runs the CLI.

The console script declared in ``pyproject.toml`` is the supported way to start
the tool; this module is the equivalent fallback for an environment where the
package is importable but its scripts are not on ``PATH``.
"""

import sys

from md_formatter.cli import main

if __name__ == "__main__":
    sys.exit(main())
