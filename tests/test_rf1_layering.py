"""RF1 lane L-LAYER: the strict-xfail layering test (spec 6.8, decision D4).

Cases are keyed by module pair, not by line, so a moved import does not XPASS.
A pair XPASSes only when every edge between the two modules is gone, and strict
mode then fails the run until its marker is removed (SM4 widens the scope).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("gnd_arch_rf1", ROOT / "tools" / "gnd_arch.py")
arch = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("gnd_arch_rf1", arch)
_SPEC.loader.exec_module(arch)

# D4 (a): edges leaving these layers are strict xfail now; lanes -> entry joins at RF4.
SCOPE = ("model", "checking", "semantics")
# The 23 wrong-way module pairs measured in metrics-RF0.json (27 edges), with the
# phase expected to remove each.
KNOWN_PAIRS = {
    ("gnd.admission_validation", "gnd.report"): "RF3",
    ("gnd.checker", "gnd.correspondence"): "RF3",
    ("gnd.checker", "gnd.extract.anchors"): "RF3",
    ("gnd.checker", "gnd.extract.identity"): "RF3",
    ("gnd.checker", "gnd.proof_bridge"): "RF3",
    ("gnd.checker", "gnd.proof_kernel"): "RF3",
    ("gnd.checker", "gnd.semantic_registry"): "RF3",
    ("gnd.judgments", "gnd.extract.manifest"): "RF3",
    ("gnd.model", "gnd.verbalize"): "RF3",
    ("gnd.model_verbalization", "gnd.extract.refscheme"): "RF3",
    ("gnd.model_verbalization", "gnd.extract.vocabulary"): "RF3",
    ("gnd.popvalidate", "gnd.verbalize"): "RF3",
    ("gnd.references", "gnd.checker"): "RF3",
    ("gnd.references", "gnd.transition"): "RF3",
    ("gnd.verbalize_population", "gnd.extract.anchors"): "RF3",
    ("gnd.verbalize_population", "gnd.redaction"): "RF3",
    ("gnd.exp.session", "gnd.report"): "RF4",
    ("gnd.exp.session_eval", "gnd.report"): "RF4",
    ("gnd.exp.session_store", "gnd.report"): "RF4",
    ("gnd.exp.session_v7", "gnd.report"): "RF4",
    ("gnd.export.lean_cli", "gnd.api"): "RF4",
    ("gnd.export.souffle_cli", "gnd.api"): "RF4",
    ("gnd.witness.cli", "gnd.api"): "RF4",
}


def _layer_map() -> dict:
    return json.loads((ROOT / "tools" / "gnd_layers.json").read_text())


def _in_scope() -> list[tuple[str, str]]:
    modules = _layer_map()["modules"]
    return sorted(pair for pair in KNOWN_PAIRS if modules[pair[0]]["layer"] in SCOPE)


@pytest.fixture(scope="module")
def measured() -> dict:
    return arch.measure(ROOT, ROOT / "tools" / "gnd_layers.json")


def _pairs(metrics: dict) -> set[tuple[str, str]]:
    return {(edge["from"], edge["to"]) for edge in metrics["layering"]["wrong_way"]}


@pytest.mark.parametrize(
    "pair",
    [
        pytest.param(pair, id=f"{pair[0]}->{pair[1]}",
                     marks=() if KNOWN_PAIRS[pair] == "RF3" else pytest.mark.xfail(
                         strict=True, reason=f"{pair[0]} -> {pair[1]}: {KNOWN_PAIRS[pair]} removes"))
        for pair in _in_scope()
    ],
)
def test_layer_edge_absent(pair, measured):
    assert pair not in _pairs(measured)


def test_layer_ratchet(measured):
    """No new wrong-way pair in any layer, and every declared-clean layer stays clean."""
    assert _pairs(measured) <= set(KNOWN_PAIRS)
    dirty = {edge["from_layer"] for edge in measured["layering"]["wrong_way"]}
    assert not (set(_layer_map()["declared_clean"]) & dirty)


def test_layer_scope():
    """T-LAYER-SCOPE: the case list is exactly the known pairs that leave the ruled layers."""
    modules = _layer_map()["modules"]
    expected = sorted(pair for pair in KNOWN_PAIRS if modules[pair[0]]["layer"] in SCOPE)
    assert _in_scope() == expected
    assert len(expected) == 16
    assert {modules[a]["layer"] for a, _b in KNOWN_PAIRS} - set(SCOPE) == {"lanes"}


def test_layer_ratchet_detects_a_new_pair(tmp_path):
    """Negative control: a generated tree with an unknown wrong-way edge fails the ratchet predicate."""
    root = tmp_path / "repo"
    (root / "src/gnd").mkdir(parents=True)
    (root / "src/gnd/__init__.py").write_text("")
    (root / "src/gnd/low.py").write_text("def f():\n    import gnd.high\n")
    (root / "src/gnd/high.py").write_text("")
    layers = _layer_map()
    layers = {**layers, "modules": {"gnd": {"layer": "infrastructure"}, "gnd.low": {"layer": "infrastructure"},
                                    "gnd.high": {"layer": "entry"}}, "declared_clean": [], "allow_list": []}
    path = tmp_path / "layers.json"
    path.write_text(json.dumps(layers))
    metrics = arch.measure(root, path)
    assert not _pairs(metrics) <= set(KNOWN_PAIRS)
