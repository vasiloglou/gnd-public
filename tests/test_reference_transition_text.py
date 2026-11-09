"""A walk on a model with reference populations renders in text as in JSON.

For such a model `gnd check --pre --steps` wraps its report in a reference
envelope (schema_version 12) that nests the walk report under "report". The
text route once read the computed post from the envelope's top level and died
with KeyError: 'transition'. It must read the nested report and print the
walk the way it does for a plain model.
"""

from __future__ import annotations

import json
from pathlib import Path

from support.cli_runner import run_main
from support.repository import REPO_ROOT

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "rof3-model-identity"
MODEL = FIXTURE / "models" / "reference-operations" / "model.orm.yaml"

PRE = {
    "population": {
        "model": "model.orm.yaml",
        "source": "fixture",
        "model_id": "urn:gnd-fixture:v71-dispatch-references@1",
        "covers": [
            "dispatch_subject_warehouse",
            "dispatch_subject_product",
            "dispatch_catalog_label",
        ],
    },
    "instances": {},
    "facts": {
        "dispatch_subject_warehouse": [{"shipment": "S-1", "warehouse": "WH-A"}],
        "dispatch_subject_product": [{"shipment": "S-1", "product": "GEAR-2"}],
    },
}

STEPS = {
    "steps_schema": 1,
    "model": "model.orm.yaml",
    "model_digest": "sha256:cc98b9acc5e175d468b3605493ce80780c296c2bdfbf1e7d3c71d6013ed9fd85",
    "operations_digest": "sha256:1e3bf9a63e9c3c0bce7fe428d9324f353078b2ede75f866e804805c01d0ebc34",
    "steps": [{"op": "label_warehouse", "bindings": {"warehouse": "WH-A"}}],
}


def _walk(tmp_path: Path, fmt: str, *, post: Path | None = None):
    pre = tmp_path / "pre.pop.json"
    steps = tmp_path / "walk.steps.json"
    pre.write_text(json.dumps(PRE))
    steps.write_text(json.dumps(STEPS))
    argv = ["check", str(MODEL), "--pre", str(pre), "--steps", str(steps), "--format", fmt]
    if post is not None:
        argv += ["--post", str(post)]
    return run_main(argv)


def test_json_walk_on_reference_model_is_a_reference_envelope(tmp_path: Path) -> None:
    result = _walk(tmp_path, "json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == 12
    assert "transition" not in payload
    assert payload["report"]["transition"]["computed_post"]["facts"]["dispatch_catalog_label"] == [
        {"warehouse": "WH-A"}
    ]


def test_text_walk_on_reference_model_prints_the_computed_post(tmp_path: Path) -> None:
    computed = json.loads(_walk(tmp_path, "json").stdout)["report"]["transition"]["computed_post"]
    result = _walk(tmp_path, "text")
    assert result.returncode == 0, result.stderr
    lines = result.stdout.decode().splitlines()
    assert lines[:3] == ["PRE-STATE", "STEP 1 (label_warehouse)", "COMPUTED POST"]
    assert json.loads(lines[3]) == computed
    assert lines[4:] == ["FRAME COMPARISON: not applicable -- post is computed", "POST-STATE"]


def test_text_walk_on_reference_model_with_declared_post(tmp_path: Path) -> None:
    computed = json.loads(_walk(tmp_path, "json").stdout)["report"]["transition"]["computed_post"]
    post = tmp_path / "post.pop.json"
    post.write_text(json.dumps(computed))
    result = _walk(tmp_path, "text", post=post)
    assert result.returncode == 0, result.stderr
    text = result.stdout.decode()
    assert "COMPUTED POST" not in text
    assert text.splitlines()[0] == "PRE-STATE"
