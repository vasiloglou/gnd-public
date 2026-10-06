"""Original eight reader-body identity and shared publisher forwarding guards."""
import ast
import atexit
import hashlib
import json
import tempfile
from pathlib import Path

import gnd
from gnd.exp import session_store


def _materialize():
    raw = (Path(__file__).parent / "fixtures/public-v72-reader-boundaries.json").read_bytes()
    assert len(raw) <= 4096
    assert hashlib.sha256(raw).hexdigest() == "d62dc1ae2c321613056aab542f1d1d188531d10168ac1d74037ffaa3244a84cd"
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-v72-reader-boundaries-")
    root = Path(temporary.name).resolve()
    (root / "src").mkdir()
    (root / "src/gnd").symlink_to(Path(gnd.__file__).resolve().parent, target_is_directory=True)
    instrument = root / "evidence/author-baseline.py"
    instrument.parent.mkdir()
    instrument.with_name("reader-boundaries-before.json").write_bytes(raw)
    return temporary, root, instrument

_TEMPORARY, ROOT, INSTRUMENT = _materialize()
atexit.register(_TEMPORARY.cleanup)

def test_reader_decisions_remain_independent_of_producer_declarations():
    saved = json.loads((Path(__file__).parent.parent / ".gnd-planning/milestones/code-refactoring/evidence/RF8/reader-base.json").read_text())
    for row in saved["functions"]:
        physical = "src/gnd/exp/session_replay.py" if row["path"] == "src/gnd/exp/session_v7.py" else row["path"]
        source = (ROOT / physical).read_text()
        node = next(
            node
            for node in ast.walk(ast.parse(source))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == row["function"]
        )
        from support.rf8_sources import predecessor_body, reader_expected
        assert hashlib.sha256(predecessor_body(node).encode()).hexdigest() == reader_expected(row)
        assert not row["calls_entry_helper"]
    for path, name in [
        ("src/gnd/exp/session_replay.py", "_entry"),
        ("src/gnd/exp/session_judgments.py", "entry"),
    ]:
        tree = ast.parse((ROOT / path).read_bytes())
        node = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == name
        )
        assert isinstance(node.body[0], ast.Return)
        assert isinstance(node.body[0].value, ast.Call)
        assert node.body[0].value.func.id == "_evidence_entry"
    assert "_evidence_entry" not in session_store.__all__
