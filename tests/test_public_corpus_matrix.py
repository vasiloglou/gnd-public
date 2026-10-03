"""Exact complete487 metadata expansion guard; never executes corpus recipes."""
from __future__ import annotations

import atexit
import copy
import gzip
import hashlib
import io
import tempfile
from pathlib import Path
from types import SimpleNamespace

from test_public_finite_observer_support import read

from gnd.assurance_evidence import _json, _read

inputs = SimpleNamespace(_json=_json,_read=_read)

def _materialize():
    packed = (Path(__file__).parent / "fixtures/public-corpus-matrix/matrix.json.gz").read_bytes()
    assert len(packed) <= 32768
    assert hashlib.sha256(packed).hexdigest() == "e9ddfc983e4ac52de2a7f5d9f4fe6fb83977638c22904dd99e12f9444e47bd18"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(524289)
    assert len(raw) <= 524288
    assert hashlib.sha256(raw).hexdigest() == "9f35586f6011094fb2789dda976017bdb678099031c89d6e82d519e9dd0ac7ab"
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-corpus-matrix-")
    root = Path(temporary.name).resolve()
    path = root / "tests/fixtures/v6-assurance/matrix.json"
    path.parent.mkdir(parents=True)
    path.write_bytes(raw)
    return temporary, root, path

_TEMPORARY, ROOT, _MATRIX = _materialize()
atexit.register(_TEMPORARY.cleanup)
ROWS = read(_MATRIX)["rows"]

def matrix(root: Path = ROOT) -> list[dict]:
    """Expand the frozen matrix's shared-set encoding without test helpers."""
    document = inputs._json(inputs._read(root / "tests/fixtures/v6-assurance/matrix.json"))
    if document.pop("encoding", None) != "shared-sets-v1":
        raise ValueError("Phase 6 matrix has an unknown encoding")
    sets = document.pop("sets")
    defaults = document.pop("row_defaults")
    rows = document["rows"]
    for row in rows:
        for key, value in defaults.items():
            row.setdefault(key, copy.deepcopy(value))
        row["scope_ids"] = copy.deepcopy(sets[row.pop("scope_set")])
        for key in (
            "required_infrastructure",
            "applicable",
            "covered",
            "missing_infrastructure",
        ):
            reference = key + "_set"
            if reference in row["recipe"]:
                row["recipe"][key] = copy.deepcopy(sets[row["recipe"].pop(reference)])
    if len(rows) != 487 or len({row["case_id"] for row in rows}) != len(rows):
        raise ValueError("Phase 6 matrix is not the frozen 487-case census")
    return rows

corpus_observer = SimpleNamespace(matrix=matrix)

def test_observer_expands_the_exact_frozen_matrix_without_test_support():
    assert corpus_observer.matrix() == ROWS
