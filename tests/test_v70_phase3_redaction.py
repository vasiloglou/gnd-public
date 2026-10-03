import json
from pathlib import Path

from test_v70_phase3_opaque import run_case


def test_applied_admission_hides_opaque_label(tmp_path: Path) -> None:
    payload = run_case("W05-opaque-redaction-canary", tmp_path)
    assert "SECRET-OPAQUE-CANARY" not in json.dumps(payload, ensure_ascii=False)
