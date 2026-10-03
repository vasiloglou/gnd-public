"""Runtime-only exact availability helpers for independent pure local controls.

This does not run or collect live PyRel seat tests. The historical parity import
resolves to the actual canonical-receipt module, keeping monkeypatches in the
same function global namespace. Foreign driver is exposed but never invoked.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import test_public_derivation_parity_corpus as parity
import test_public_derivation_parity_tools as driver

ROOT = Path(__file__).resolve().parents[2]
ORACLE = ROOT / "tests/oracles/pyrel_derivation_oracle.py"
parity.subprocess = subprocess
parity._pyrel_extensions = driver._pyrel_extensions
sys.modules["test_derivation_parity"] = parity
pytestmark = pytest.mark.pyrel_oracle

def require_driver():
    driver = getattr(parity, "_pyrel_extensions", None)
    assert callable(driver), "Phase 3 PyRel raw-path driver does not exist"
    assert ORACLE.is_file(), "Phase 3 PyRel derivation compiler does not exist"
    return driver

def _available_driver():
    driver = require_driver()  # absence is a failure, never an availability skip
    if shutil.which("uv") is None:
        pytest.skip("uv executable absent; PyRel derivation seat not measured")
    return driver
