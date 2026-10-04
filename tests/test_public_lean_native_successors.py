"""Original native successors retain proof exclusions; no native pass claim."""
import pytest
import test_public_lean_export_successors as _current
from support.public_lean_successors import evaluate

from gnd import api

source = _current.source

# These are call-through helpers, not additional tests or mapped originals.
def test_fixed_extent_exact(*args, **kwargs):
    return _current.test_fixed_extent_exact(*args, **kwargs)
def test_guard_literal_carrier(*args, **kwargs):
    return _current.test_guard_literal_carrier(*args, **kwargs)
def test_derived_literal_extent(*args, **kwargs):
    return _current.test_derived_literal_extent(*args, **kwargs)
def test_review_guard_operands(*args, **kwargs):
    return _current.test_review_guard_operands(*args, **kwargs)
for _helper in (test_fixed_extent_exact, test_guard_literal_carrier,
                test_derived_literal_extent, test_review_guard_operands):
    _helper.__test__ = False

@pytest.mark.proof
@pytest.mark.parametrize("shape", ["extra", "empty"])
def test_native_fixed_extent_exact(tmp_path, shape):
    test_fixed_extent_exact(tmp_path, shape)
    bundle = tmp_path / "bundle"
    assert evaluate(bundle, "wellTyped concrete") == "false"


@pytest.mark.proof
def test_native_guard_literal(tmp_path):
    test_guard_literal_carrier(tmp_path)
    assert evaluate(tmp_path / "bundle", "c3 concrete") == "GND.Outcome.vacuous"


@pytest.mark.proof
def test_native_compiler_api(tmp_path):
    import os

    src = source(tmp_path)
    bundle = tmp_path / "bundle"
    assert (
        api.export_lean(
            src / "model.orm.json",
            src / "candidate.pop.json",
            toolchain="leanprover/lean4:v4.34.0",
            out=bundle,
            raw=True,
        )["exit_code"]
        == 0
    )
    before = {p.relative_to(bundle): p.read_bytes() for p in bundle.rglob("*") if p.is_file()}
    tool = os.environ.get("GND_V71_LEAN_LAKE")
    assert tool
    result = api.compile_lean(bundle, executable=tool, elaborate_stubs=True)
    assert result["exit_code"] == 0 and result["status"] == "compiled"
    assert result["proof_status"] == "unproved"
    assert result["definitions"]["status"] == result["stubs"]["status"] == "completed"
    assert before == {
        p.relative_to(bundle): p.read_bytes() for p in bundle.rglob("*") if p.is_file()
    }


@pytest.mark.proof
def test_native_derived_literal_extent(tmp_path):
    test_derived_literal_extent(tmp_path)
    assert evaluate(tmp_path / "bundle", "wellTyped concrete") == "false"


@pytest.mark.proof
@pytest.mark.parametrize("shape", ["nested-date", "iso-string", "tagged-date"])
def test_native_review_guard_operands(tmp_path, shape):
    test_review_guard_operands(tmp_path, shape)
    expected = "violated" if shape == "iso-string" else "satisfied"
    assert evaluate(tmp_path / "bundle", "c3 concrete") == "GND.Outcome." + expected
