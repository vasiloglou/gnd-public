from __future__ import annotations

import json
from pathlib import Path

import pytest
from support.cli_runner import run_main

REPO_ROOT=Path(__file__).resolve().parents[1]
CORPUS=REPO_ROOT/"tests/fixtures/phase3-consumers"


@pytest.fixture(autouse=True)
def _bind_actual_generic_v3_report(tmp_path: Path,monkeypatch: pytest.MonkeyPatch) -> None:
    # Current GND produces the complete generic predecessor check payload.
    # The original temporary coordinate is retained; no BookRec receipt is copied.
    population=tmp_path/"population.json"
    population.write_text(json.dumps({"population":{"model":"legacy-derived.orm.yaml","source":"synthetic","covers":["item_seeded","item_ranked"]},"facts":{"item_seeded":[{"item":"x"}],"item_ranked":[{"item":"x"}]}}),encoding="utf-8")
    from gnd.checker import band, check
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.report import build_check_payload

    model=load_model(CORPUS/"legacy-derived.orm.yaml")
    report=check(model,load_population(population,model=model))
    assert band(report)==0
    payload=build_check_payload(band(report),"legacy-derived.orm.yaml","population.json",schema_version=3,report=report)
    assert payload["schema_version"]==3
    assert payload["command"]=="check"
    path=tmp_path/"examples/bookrec/evidence/v1-check.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload),encoding="utf-8")
    monkeypatch.setitem(globals(),"REPO_ROOT",tmp_path)

def _run(arguments: list[str], *, cwd: Path) -> tuple[int, str]:
    result = run_main(arguments, cwd=cwd, capture_stderr=False)
    return result.returncode, result.stdout.decode("utf-8", errors="surrogatepass")

def test_coverage_refuses_version_mismatch_in_both_directions(tmp_path: Path) -> None:
    """P3-CV-3 refusals: v3-for-v4-model and v4-for-v3-model, version named."""

    code, stdout = _run(
        [
            "coverage",
            "eligibility.orm.yaml",
            "--check",
            str(REPO_ROOT / "examples/bookrec/evidence/v1-check.json"),
            "--format",
            "json",
        ],
        cwd=CORPUS,
    )
    assert code == 3
    assert "schema_version 3" in stdout

    code, stdout = _run(
        [
            "coverage",
            "legacy-derived.orm.yaml",
            "--check",
            str(CORPUS / "check-v4.exact.payload.json"),
            "--format",
            "json",
        ],
        cwd=CORPUS,
    )
    assert code == 3
    assert "schema_version 4" in stdout
