"""Projection contract for compact model growth context."""
import hashlib
import json
from pathlib import Path

import pytest

from gnd import api
from gnd.constraint_families import FAMILIES
from gnd.model import ModelValidationError, load_model
from gnd.model_verbalization import _growth_constraint, render_growth_view

ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "tests/fixtures/models/full_vocabulary.orm.yaml"
SEED = ROOT / "src/gnd/examples/seeded_growth"


def render(source):
    return render_growth_view(load_model(source) if isinstance(source, Path) else source)


def test_full_inventory_and_size():
    model = load_model(VOCAB)
    text = render(model)
    assert hashlib.sha256(text.encode()).hexdigest() == (
        "2bfe0b0d0ff3e46167bba1f5c92c43f628b89ace635e16e754c478b04f2267f1"
    )
    result = json.loads(text)
    assert result["format"] == "gnd-growth-view-v1"
    assert text.endswith("\n") and len(text.splitlines()) == 1
    assert len(text.encode()) < min(
        len(VOCAB.read_bytes()), len(api.verbalize_model(model).encode())
    )
    assert [r["id"] for r in result["object_types"]] == sorted(r["id"] for r in model.object_types)
    facts = {f["id"]: f for f in result["fact_types"]}
    for f in model.fact_types:
        assert facts[f["id"]]["roles"] == [[r["role_name"], r["object_type"]] for r in f["roles"]]
        assert facts[f["id"]]["reading"] == f["reading"]
    assert result["subtypes"] == sorted(
        [o["id"], parent] for o in model.object_types for parent in o.get("subtype_of", [])
    )
    original = [(None, c) for c in model.constraints] + [
        (f["id"], c) for f in model.fact_types for c in f.get("constraints", [])
    ]
    assert len(result["constraints"]) == len(original)
    assert {c["type"] for _, c in original} | {"anchored", "guarded"} == set(FAMILIES)
    for host, c in original:
        expected = {
            key: value for key, value in c.items()
            if key in {
                "type", "id", "status", "modality", "scope", "role", "roles", "role_ref",
                "role_refs", "variant", "bound", "range", "ranges", "allowed", "preferred",
                "subset_role_seq", "superset_role_seq", "role_seqs", "role_seq_a", "role_seq_b",
                "role_a", "role_b", "operator", "object_type", "supertype", "subtypes",
                "exclusive", "exhaustive", "formal_language",
            }
        }
        expected["host"] = host
        if c.get("status") == "rejected":
            expected["archived"] = True
        assert expected in result["constraints"]
    for source, projected in zip(sorted(model.object_types, key=lambda o: o["id"]),
                                 result["object_types"], strict=True):
        for key in ("reference", "derivation", "storage", "independent"):
            assert source.get(key) == projected.get(key)


def test_guarded_and_anchored_signatures():
    atom = {"fact_type": "visits", "bind": {"visitor": "$person", "place": "$city"}}
    sig = _growth_constraint(
        {
            "type": "guarded",
            "antecedent": [atom],
            "consequent": {"any_of": [{"absence": atom}, {"exists": {"atoms": [atom]}}]},
        },
        None,
    )
    assert len(sig["atoms"]) == 3
    assert all(a[1:] == ["visits", ["place", "visitor"]] for a in sig["atoms"])
    assert len({a[0] for a in sig["atoms"]}) == 3
    assert _growth_constraint(
        {"type": "anchored", "role": "price", "recognise": ["decimal"]}, "cost"
    )["recognise"] == ["decimal"]


def test_determinism_and_evidence_only_changes():
    model = load_model(VOCAB)
    expected = render(model)
    model.fact_types.reverse()
    model.object_types.reverse()
    model.constraints.reverse()
    for f in model.fact_types:
        f["sample_population"] = [{"arbitrary": "private sample"}]
        f["provenance"] = {"user_quote": "private quote"}
        for c in f.get("constraints", []):
            c["rationale"] = "private rationale"
    assert render(model) == expected
    model.fact_types[0]["reading"] += " changed"
    assert render(model) != expected



def test_empty_view_and_unresolved_include(tmp_path):
    empty = tmp_path / "empty.json"
    empty.write_text('{"version":1,"object_types":[],"fact_types":[]}')
    assert render(empty) == (
        '{"constraints":[],"fact_types":[],"format":"gnd-growth-view-v1",'
        '"object_types":[],"subtypes":[]}\n'
    )
    model = load_model(SEED / "root.orm.yaml").model_copy(deep=True)
    model._included = ()
    with pytest.raises(ModelValidationError, match="unresolved"):
        render(model)


def test_direct_lookup_preserves_role_direction():
    view = json.loads(render(SEED / "root.orm.yaml"))
    hits = [fact for fact in view["fact_types"] if "has version" in fact["reading"]]
    assert [(fact["id"], fact["roles"]) for fact in hits] == [
        ("work_has_version", [["work", "work"], ["version", "version"]])
    ]


@pytest.mark.parametrize(("field", "first", "second"), [
    ("modality", "alethic", "deontic"),
    ("status", "confirmed", "proposed"),
    ("variant", "symmetric", "asymmetric"),
])
def test_signature_distinguishes_semantic_parameters(field, first, second):
    constraint = {"type": "ring", "variant": "symmetric", "status": "confirmed",
                  "modality": "alethic"}
    assert _growth_constraint({**constraint, field: first}, "f") != _growth_constraint(
        {**constraint, field: second}, "f"
    )
