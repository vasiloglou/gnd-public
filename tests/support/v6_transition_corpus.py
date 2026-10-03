"""Original selector namespace using approved full runtime corpus and matrix coordinates."""
import atexit
import json
import tempfile
from pathlib import Path

from test_public_phase4_scope_rows import MATRIX
from test_public_phase4_transition_support import ANSWERS, BY_ID, assert_answer, observe

_TEMPORARY = tempfile.TemporaryDirectory(prefix="gnd-public-transition-selectors-")
atexit.register(_TEMPORARY.cleanup)
CORPUS = Path(_TEMPORARY.name)
assert len(MATRIX["rows"]) == 53
_RAW = json.dumps(MATRIX, separators=(",", ":")).encode("utf-8")
assert len(_RAW) <= 16384
(CORPUS / "matrix.json").write_bytes(_RAW)
(CORPUS / "matrix.json").chmod(0o644)

__all__ = ["ANSWERS", "BY_ID", "CORPUS", "assert_answer", "observe"]
