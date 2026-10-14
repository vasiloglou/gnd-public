"""Run the BookRec command line from a copied project folder, from any directory.

Usage: python bookrec-native/app.py recommend --user ada --model ... --input ... --output ...
The application code lives in ``extension/bookrec``; this launcher only finds it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "extension"))

from bookrec.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
