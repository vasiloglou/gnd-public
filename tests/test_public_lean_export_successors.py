import pytest
from support.public_lean_successors import INPUTS, load, materialize, write

from gnd import api
from gnd.export.lean_io import export_lean
from gnd.export.lean_runtime import compile_lean


def source(tmp_path):
    row = next(r for r in INPUTS["cases"] if r["id"] == "dispatch-S01-base")
    return materialize(row, tmp_path)[0]


@pytest.mark.parametrize("shape", ["extra", "empty"])
def test_fixed_extent_exact(tmp_path, shape):
    src = source(tmp_path)
    m, p = load(src / "model.orm.json"), load(src / "candidate.pop.json")
    node = m["object_types"][1]["id"]
    p["instances"][node] = ["WH-Z"]
    if shape == "empty":
        ref = load(src / "references/catalog.pop.json")
        ref["instances"][node] = []
        ref["facts"] = {fid: [] for fid in ref["facts"]}
        write(src / "references/catalog.pop.json", ref)
        import hashlib

        m["reference_populations"][0]["sha256"] = hashlib.sha256(
            (src / "references/catalog.pop.json").read_bytes()
        ).hexdigest()
        write(src / "model.orm.json", m)
    write(src / "candidate.pop.json", p)
    out = tmp_path / "bundle"
    result = export_lean(
        src / "model.orm.json",
        src / "candidate.pop.json",
        toolchain="leanprover/lean4:v4.34.0",
        out=out,
        raw=True,
    )
    assert result.exit_code == 0
    text = (out / "Definitions.lean").read_text()
    # The missing half of equality is an explicit public predicate, and a native
    # successor below checks its meaning against a literal alternative extent.
    assert "p.e1.all (fun n => " in text


@pytest.mark.parametrize("shape", ["directory", "invalid-bundle"])
def test_compile_closed_refusal(tmp_path, shape):
    src = source(tmp_path)
    out = tmp_path / "bundle"
    if shape == "directory":
        assert (
            api.export_lean(
                src / "model.orm.json",
                src / "candidate.pop.json",
                toolchain="leanprover/lean4:v4.34.0",
                out=out,
                raw=True,
            )["exit_code"]
            == 0
        )
        tool = tmp_path / "bad-lake"
        tool.mkdir()
        tool.chmod(0o755)
        result = compile_lean(out, executable=tool).model_dump()
        assert result["exit_code"] == 4 and result["reason"] == "tool-error"
    else:
        out.mkdir()
        (out / "manifest.json").write_text("{}")
        result = compile_lean(out).model_dump()
        assert result["exit_code"] == 3
    assert result["kind"] == "lean-compile-result"
    assert result["definitions"]["attempted"] is False
    assert result["proof_status"] == "unproved"


def test_guard_literal_carrier(tmp_path):
    src = source(tmp_path)
    m = load(src / "model.orm.json")
    m["constraints"][1]["antecedent"][0]["bind"]["job"] = "SHIP-1"
    # Other atom bindings still bind j, so the literal only filters start rows.
    write(src / "model.orm.json", m)
    out = tmp_path / "bundle"
    result = export_lean(
        src / "model.orm.json",
        src / "candidate.pop.json",
        toolchain="leanprover/lean4:v4.34.0",
        out=out,
        raw=True,
    )
    assert result.exit_code == 0
    carriers = load(out / "source-map.json")["carriers"]
    assert [x["value"] for x in carriers[0]["values"]] == ["SHIP-0", "SHIP-1"]


def test_derived_literal_extent(tmp_path):
    src = source(tmp_path)
    m = load(src / "model.orm.json")
    derived = m["fact_types"][6]
    derived["roles"][0]["object_type"] = m["object_types"][0]["id"]
    derived["reading"] = "{Shipment} reaches {Warehouse}"
    clause = derived["derivation_rule"]["clauses"][0]
    clause["head"]["source"] = "SHIP-1"
    derived["derivation_rule"]["clauses"] = [clause]
    write(src / "model.orm.json", m)
    bundle = tmp_path / "bundle"
    result = export_lean(
        src / "model.orm.json",
        src / "candidate.pop.json",
        toolchain="leanprover/lean4:v4.34.0",
        out=bundle,
        raw=True,
    )
    assert result.exit_code == 0
    assert "(r6 p).all (fun r => p.e0.contains r.1" in (bundle / "Definitions.lean").read_text()


@pytest.mark.parametrize("shape", ["nested-date", "iso-string", "tagged-date"])
def test_review_guard_operands(tmp_path, shape):
    src = source(tmp_path)
    m = load(src / "model.orm.json")
    comparison = m["constraints"][1]["consequent"]["comparison"]
    if shape == "nested-date":
        comparison["left"]["args"][0] = {"fn": "date_sub", "args": ["$start", {"duration_days": 1}]}
    elif shape == "iso-string":
        comparison.update(left="$j", operator="=", right="2026-01-01")
    else:
        comparison["right"] = {"date": "2026-01-04"}
    write(src / "model.orm.json", m)
    out = tmp_path / "bundle"
    result = export_lean(
        src / "model.orm.json",
        src / "candidate.pop.json",
        toolchain="leanprover/lean4:v4.34.0",
        out=out,
        raw=True,
    )
    assert result.exit_code == 0


def test_review_object_derivation_refuses(tmp_path):
    src = source(tmp_path)
    m = load(src / "model.orm.json")
    m["object_types"][0].update(derivation="derived", derivation_rule="Opaque extent definition.")
    write(src / "model.orm.json", m)
    result = export_lean(
        src / "model.orm.json", src / "candidate.pop.json", toolchain="leanprover/lean4:v4.34.0"
    )
    assert result.exit_code == 2 and result.reason == "fragment-unsupported"


def test_review_cwd_output_limit(tmp_path):
    import sys
    from dataclasses import replace

    from gnd.export.lean_types import DEFAULT_LIMITS

    src = source(tmp_path)
    out = tmp_path / "bundle"
    assert (
        api.export_lean(
            src / "model.orm.json",
            src / "candidate.pop.json",
            toolchain="leanprover/lean4:v4.34.0",
            out=out,
            raw=True,
        )["exit_code"]
        == 0
    )
    tool = tmp_path / "lake"
    tool.write_text(
        "#!"
        + sys.executable
        + "\nimport sys\nfrom pathlib import Path\nif '--version' in sys.argv:\n print('Lake version 4.34.0')\nelse:\n Path('runaway').write_bytes(b'x'*2097152)\n"
    )
    tool.chmod(0o755)
    result = compile_lean(
        out, executable=tool, limits=replace(DEFAULT_LIMITS, native_output_bytes=1048576)
    )
    assert result.exit_code == 4 and result.reason == "output-limit"


def test_review_carrier_work_admission(tmp_path, monkeypatch):
    from dataclasses import replace

    from gnd.export.lean import Renderer
    from gnd.export.lean_types import DEFAULT_LIMITS

    def forbid_render(*args):
        raise AssertionError("carrier work exceeded its budget before allocation")

    monkeypatch.setattr(Renderer, "render", forbid_render)
    src = source(tmp_path)
    result = export_lean(
        src / "model.orm.json",
        src / "candidate.pop.json",
        toolchain="leanprover/lean4:v4.34.0",
        limits=replace(DEFAULT_LIMITS, emission_visits=15),
    )
    assert result.exit_code == 4 and result.reason == "work-limit"


@pytest.mark.parametrize("operator", ["<", "<=", ">", ">="])
@pytest.mark.parametrize("modality", ["alethic", "deontic"])
def test_boolean_ordering_refuses(tmp_path, operator, modality):
    src = source(tmp_path)
    model = load(src / "model.orm.json")
    constraint = model["constraints"][1]
    constraint["modality"] = modality
    constraint["consequent"]["comparison"] = {"left": False, "operator": operator, "right": True}
    write(src / "model.orm.json", model)
    result = export_lean(
        src / "model.orm.json", src / "candidate.pop.json", toolchain="leanprover/lean4:v4.34.0"
    )
    assert result.exit_code == 2 and result.reason == "fragment-unsupported"
