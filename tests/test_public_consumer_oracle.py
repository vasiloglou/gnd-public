"""Oracle promotion composition controls over reviewed unchanged inputs."""
from __future__ import annotations

import atexit
import shutil
import tempfile
from pathlib import Path

import pytest
from test_public_slice_runtime import CORPUS

from gnd.semantic_registry import REGISTRY, capture_branches

_TEMPORARY = tempfile.TemporaryDirectory(prefix="gnd-public-oracle-")
atexit.register(_TEMPORARY.cleanup)
_ROOT = Path(_TEMPORARY.name)
for _case in ("c01", "c02", "c03", "c09"):
    _target = _ROOT / "proof/v6/phase1/corpus/fixtures" / _case / "model.orm.yaml"
    _target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CORPUS / "fixtures" / _case / "model.orm.yaml", _target)
_ALIAS = _ROOT / "tests/test_public_consumer_oracle.py"
_ALIAS.parent.mkdir(parents=True)
_ALIAS.touch()

@pytest.fixture(autouse=True)
def _generic_module_coordinates(monkeypatch):
    monkeypatch.setitem(globals(), "__file__", str(_ALIAS))

def observe_oracle_compositions():
    from gnd.measure.promote import expected_exit_for
    from gnd.model import load_model
    from gnd.synth.provenance import ExpectedState, Sidecar

    root = Path(__file__).resolve().parents[1] / "proof/v6/phase1/corpus/fixtures"
    mandatory = "fact_types[reviewer_signs_report].constraints[0]"
    required = {row.scope_id for row in REGISTRY if row.family == "oracle-verdict"}
    # These are expectations given to the promotion composer, not checker
    # observations. Their supporting model fixtures are admitted unchanged.
    with capture_branches() as reached:
        for case, ref, truth, verdict, reason, expected_band in (
            ("c01", mandatory, "satisfied", "pass", None, 0),
            ("c02", mandatory, "violated", "fail", None, 1),
            ("c03", mandatory, "violated", "warning", None, 0),
            ("c09", "constraints[0]", "satisfied", "unchecked", "textual-not-mechanical", 4),
            ("c01", mandatory, "no-subjects", "vacuous", None, 2),
        ):
            model = load_model(root / case / "model.orm.yaml")
            sidecar = Sidecar(
                population="authored-input.json",
                population_sha256="a" * 64,
                class_="boundary",
                seed=1,
                gnd_version="0",
                model="fixture",
                model_digest="b" * 64,
                pool_source="fixture",
                pool_path="fixture.json",
                pool_sha256="c" * 64,
                pool_size=0,
                expectations={
                    ref: ExpectedState(ground_truth=truth, expected_verdict=verdict, reason=reason)
                },
            )
            assert expected_exit_for(model, sidecar) == expected_band, (case, verdict)
    assert required <= reached, sorted(required - reached)
    assert not any(scope.startswith(("snapshot:", "derivation:")) for scope in reached)

def test_authored_oracle_inputs_reach_the_promotion_composer():
    observe_oracle_compositions()
