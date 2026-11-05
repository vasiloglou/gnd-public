"""The packaged composition example stays consistent with its model.

Every sidecar binds the model's vocabulary digest and raw-byte digests of its
population and document; rebuilding must reproduce the shipped bytes, so an
edit without a rebuild fails here rather than in the how-to.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/composition"
BUILD = ROOT / "tools/build_composition_example.py"
GENERATED = ("composition", "composition-conflict", "targets.json")


def _files(root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for name in GENERATED
                  for path in ([root / name] if (root / name).is_file() else (root / name).rglob("*"))
                  if path.is_file())


def test_sources_rebuild_byte_identically(tmp_path: Path) -> None:
    shutil.copy2(EXAMPLE / "model.orm.yaml", tmp_path / "model.orm.yaml")
    subprocess.run([sys.executable, str(BUILD), str(tmp_path)], check=True)
    assert _files(tmp_path) == _files(EXAMPLE)
    for name in _files(EXAMPLE):
        assert (tmp_path / name).read_bytes() == (EXAMPLE / name).read_bytes(), name


def test_the_model_validates_and_both_directories_compose() -> None:
    from gnd import api

    model = str(EXAMPLE / "model.orm.yaml")
    assert api.validate(model)["exit_code"] == 0
    for directory in ("composition", "composition-conflict"):
        assert api.compose(model, str(EXAMPLE / directory))["exit_code"] == 0, directory
