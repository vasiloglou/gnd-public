"""Close repairs of include-root-routes, from the panel-light close review.

1. An include path that cannot be encoded is refused ``include:path`` by
   ``compose`` on every route, not reported as a codec error.
2. The PyRel export refuses an orphan attachment document
   ``include:declaration`` in every mode.
3. ``gnd judgments check`` judges the composed model ``gnd check`` evaluates:
   its mechanical report equals the check report for the same root.
"""
from __future__ import annotations

import json
import shutil

import pytest
from support.cli_runner import run_main
from test_ir1_judgments_includes import POPULATION, bind
from test_mc1_model_includes import write_case

from gnd.errors import ModelValidationError
from gnd.model import load_model


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    from gnd.examples.literature.interop import build

    out = tmp_path_factory.mktemp("close") / "interop"
    build(out)
    return out


@pytest.fixture
def case(built, tmp_path):
    root = tmp_path / "case"
    shutil.copytree(built, root)
    return root


def unencodable_root(tmp_path):
    root = tmp_path / "root.orm.json"
    root.write_text(json.dumps({"version": 5, "includes": [
        {"id": "v", "path": "bad\ud800", "sha256": "0" * 64}]}))
    return root


def test_compose_refuses_an_unencodable_path_as_path(tmp_path):
    with pytest.raises(ModelValidationError) as caught:
        load_model(unencodable_root(tmp_path))
    assert caught.value.issues[0].rule_id == "include:path"


@pytest.mark.parametrize("argv", [
    ["validate", "{root}"],
    ["flatten", "{root}", "--out", "{out}"],
    ["export", "pyrel", "{root}", "--out", "{out}/x.py"],
    ["export", "pyrel", "--rules", "duckdb", "{root}", "--out", "{out}/x.py"],
    ["export", "pyrel", "--rules", "lqp", "{root}", "--out", "{out}/x.py"],
], ids=["validate", "flatten", "export-default", "export-duckdb", "export-lqp"])
def test_routes_name_the_unencodable_path_refusal(tmp_path, argv):
    root = unencodable_root(tmp_path)
    args = [a.format(root=root, out=tmp_path / "out") for a in argv]
    result = run_main(args)
    assert result.returncode == 3
    assert b"include:path" in result.stdout + result.stderr


def test_judgments_names_the_unencodable_path_refusal(tmp_path):
    from gnd.api import judgments

    root = unencodable_root(tmp_path)
    for name, body in (("policy.json", "{}"), ("receipts.json", '{"schema_version": 1, "receipts": []}'),
                       ("population.json", "{}")):
        (tmp_path / name).write_text(body)
    (tmp_path / "policy.json").write_text(json.dumps({
        "admission": {"evidence_floor": None, "minimum_approvals": 1}, "judges": ["a"],
        "policy_id": "close", "repair": {"evidence_floor": None, "minimum_rejections": 1},
        "schema_version": 1, "targets": [{"fact_type": "x", "index": 0}],
        "trust_mode": "self-asserted", "trusted_receipts": []}))
    result = judgments(root, tmp_path / "population.json", tmp_path / "policy.json",
                       tmp_path / "receipts.json", trusted_root=tmp_path)
    assert result["outcome"] == 3
    assert result["error"] == {"reason": "binding", "message": "include:path"}


@pytest.mark.parametrize("mode", ["default", "duckdb", "lqp"])
def test_export_refuses_orphan_attachments_as_declaration(tmp_path, mode):
    path, own, _ = write_case(tmp_path)
    del own["includes"]
    own["fact_type_constraints"] = [
        {"fact_type": "component_imports_component", "constraints": [{"kind": "mandatory"}]}]
    path.write_text(json.dumps(own))
    argv = ["export", "pyrel", str(path), "--out", str(tmp_path / "x.py")]
    if mode != "default":
        argv += ["--rules", mode]
    result = run_main(argv)
    assert result.returncode == 3
    assert b"include:declaration" in result.stdout + result.stderr


def test_judgments_mechanical_report_equals_gnd_check(case):
    bind(case, "checking.orm.json")
    judged = run_main(["judgments", "check", str(case / "checking.orm.json"), str(case / POPULATION),
                       "--policy", str(case / "policy.json"), "--receipts", str(case / "receipts.json"),
                       "--trusted-root", str(case), "--format", "json"])
    checked = run_main(["check", str(case / "checking.orm.json"), str(case / POPULATION),
                        "--admission", "--format", "json"])
    mechanical = json.loads(judged.stdout)["mechanical_report"]
    report = json.loads(checked.stdout)
    assert judged.returncode == 0
    assert mechanical["model_digest"] == report["model_digest"]
    assert mechanical["report"]["verdicts"] == report["report"]["verdicts"]
    assert mechanical["reference_binding"] == report["reference_binding"]
