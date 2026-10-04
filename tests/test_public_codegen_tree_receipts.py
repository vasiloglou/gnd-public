from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[1]
ANSWERS=REPO_ROOT/"tests/fixtures/v51-generated-project/answers"

def _gnd(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "gnd", *argv],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

def _model_arg(case: str) -> str:
    """The corpus model path AS THE RECEIPT WAS MEASURED: relative to the repo.

    The emitted banner in `model/__init__.py` and `model/tools.py` records the
    model path exactly as it was passed, so an absolute path here would produce
    different bytes for the same model -- the same class of path dependence
    IF-P1-3 recorded for `.gnd-codegen.json` (IF-P1-4).
    """
    return f"tests/fixtures/v51-generated-project/{case}/model.orm.yaml"

def test_the_generated_trees_match_the_committed_receipt(tmp_path: Path) -> None:
    """C1/T1.1a. The receipt is the answer key the owner approved; a null row is
    asserted present-only because those bytes embed the invocation path."""
    import hashlib

    receipt = json.loads((ANSWERS / "expected-tree.json").read_text(encoding="utf-8"))
    for case in ("alpha", "beta"):
        out = tmp_path / case
        assert _gnd(
            "codegen", _model_arg(case), "--out", str(out)
        ).returncode == 0
        actual = {
            str(path.relative_to(out)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in out.rglob("*")
            if path.is_file()
        }
        expected = {key: value for key, value in receipt[case].items() if not key.startswith("_")}
        assert set(actual) == set(expected), case
        for relpath, digest in expected.items():
            if digest is None:
                continue
            assert actual[relpath] == digest, f"{case}/{relpath}"

