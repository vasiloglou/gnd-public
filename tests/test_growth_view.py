"""Public compact growth view and search-handoff regression tests."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from gnd import api
from gnd.model import ModelValidationError, load_model

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "src/gnd/examples/seeded_growth"


def render(source):
    return api.verbalize_model(source, for_growth=True)


def test_cli_utf8_include_identity_and_stale_snapshot(tmp_path):
    copy = tmp_path / "copy"
    shutil.copytree(SEED, copy)
    root = copy / "root.orm.yaml"
    argv = [sys.executable, "-m", "gnd", "verbalize", "model", str(root), "--for-growth"]
    # An ordinary text-mode stream would translate/escape non-ASCII here.
    seed = copy / "seed.orm.yaml"
    old = hashlib.sha256(seed.read_bytes()).hexdigest()
    seed.write_bytes(seed.read_bytes().replace(b"WorkKey", "Caf\u00e9".encode()))
    raw = root.read_bytes().replace(
        old.encode(), hashlib.sha256(seed.read_bytes()).hexdigest().encode()
    )
    root.write_bytes(raw)
    text = render(root)
    assert "Caf\u00e9" in text
    env = dict(os.environ, PYTHONIOENCODING="ascii")
    for _ in range(2):
        result = subprocess.run(argv, capture_output=True, env=env, check=True)
        assert result.stdout == text.encode() and not result.stderr
    root.write_bytes(raw + b"\n# evidence snapshot changed\n")
    assert raw != root.read_bytes() and render(root) == text
    seed.write_bytes(seed.read_bytes() + b"\n")
    result = subprocess.run(argv, capture_output=True, check=False)
    assert result.returncode == 3 and b"include:hash-mismatch" in result.stdout
    assert b"gnd-growth-view-v1" not in result.stdout
    with pytest.raises(ModelValidationError):
        render(root)


def test_example_search_miss_retry_and_defer(tmp_path):
    readme = (SEED / "README.md").read_text()
    code = readme.split("```python\n", 1)[1].split("\n```", 1)[0]
    copy = tmp_path / "host"
    shutil.copytree(SEED, copy)
    rec = json.loads(subprocess.check_output([sys.executable, "-c", code], cwd=copy))
    assert rec["searches"][0]["shown"] == []
    assert rec["inspected_ids"] == ["work_has_version"]
    assert [r["decision"] for r in rec["decisions"]] == ["reuse", "defer"]
    a, b = rec["decisions"][0]["span"]
    assert (copy / "round-2.document.txt").read_text()[a:b] == "W-1 has version V-1"
    assert rec["decisions"][0]["bindings"] == {"work": "W-1", "version": "V-1"}
    assert rec["decisions"][0]["bindings"] != {"work": "V-1", "version": "W-1"}
    complete = render(copy / "root.orm.yaml")
    for search in rec["searches"]:
        assert search["partial"] is True
        assert search["view_sha256"] == hashlib.sha256(complete.encode()).hexdigest()
        assert all(row in json.loads(complete)["fact_types"] for row in search["shown"])
    assert [row["id"] for row in rec["direct_lookup"]["shown"]] == ["work_has_version"]
    ambiguous = rec["ambiguous_document"]
    deferred = rec["decisions"][1]
    assert deferred["document_sha256"] == hashlib.sha256(ambiguous.encode()).hexdigest()
    assert deferred["span"] == [0, len(ambiguous)] and "bindings" not in deferred
    assert "has version" in rec["searches"][1]["shown"][0]["reading"]

def test_public_growth_view_options_and_fact_metadata():
    model = load_model(ROOT / "tests/fixtures/rmap/cases/17-objectification/model.yaml")
    with pytest.raises(TypeError, match="for_growth"):
        api.verbalize_model(model, for_growth="yes")
    fact = next(f for f in model.fact_types if "objectified_as" in f)
    fact["objectification_independent"] = True
    projected = next(f for f in json.loads(render(model))["fact_types"] if f["id"] == fact["id"])
    assert projected["objectification_independent"] is True
    assert projected["derivation"] == fact.get("derivation", "asserted")
    assert projected.get("storage") == fact.get("storage")


def test_loaded_growth_model_refuses_invalid_role_player():
    model = load_model(SEED / "seed.orm.yaml")
    model.fact_types[0]["roles"][0]["object_type"] = "missing_object"
    with pytest.raises(ModelValidationError, match="undeclared object type"):
        render(model)


def test_changed_included_row_requires_reload():
    model = load_model(SEED / "root.orm.yaml")
    model.fact_types[0]["reading"] += " changed after verification"
    with pytest.raises(ModelValidationError, match="unresolved"):
        render(model)
