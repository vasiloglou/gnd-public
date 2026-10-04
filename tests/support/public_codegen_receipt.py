from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]

def read_receipt(name: str) -> dict[str, object]:
    """One corpus answer-key section, with its underscore-prefixed notes gone."""
    answers = REPO_ROOT / "tests" / "fixtures" / "v51-generated-project" / "answers"
    receipt = json.loads((answers / "expected-tree.json").read_text(encoding="utf-8"))
    return {
        relpath: digest
        for relpath, digest in receipt[name].items()
        if not relpath.startswith("_")
    }
