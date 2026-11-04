"""MG6: the packaged growth example stays consistent with its model.

The two proposals bind the model's digest; rebuilding them must reproduce the
shipped bytes, so a model edit without a rebuild fails here rather than in the
how-to.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/growth"
BUILD = ROOT / "tools/build_growth_example.py"


def test_proposals_rebuild_byte_identically(tmp_path: Path) -> None:
    shutil.copy2(EXAMPLE / "model.orm.yaml", tmp_path / "model.orm.yaml")
    subprocess.run([sys.executable, str(BUILD), str(tmp_path)], check=True)
    for name in ("round-1.proposal.json", "round-2.proposal.json"):
        assert (tmp_path / name).read_bytes() == (EXAMPLE / name).read_bytes(), name


def test_the_model_validates() -> None:
    from gnd import api

    assert api.validate(str(EXAMPLE / "model.orm.yaml"))["exit_code"] == 0
