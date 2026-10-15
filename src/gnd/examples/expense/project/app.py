"""Run the expense command line from a copied project folder, from any directory.

Usage: python expense-native/app.py report --model ... --population ...
The application code lives in ``cli/``; this launcher only finds it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cli.expense_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
