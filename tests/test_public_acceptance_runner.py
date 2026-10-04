"""Acceptance-runner instruments; no partial ledger can claim full acceptance."""
import copy
import gzip
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Historical migration accounting/storage; current product assertions remain in default tests.
pytestmark = pytest.mark.evidence

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("public_acceptance_runner_under_test",
                                            ROOT / "tools/run_public_acceptance.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
NODE = "tests/test_address.py::test_derivation_address_is_coherent_and_distinct"


def inputs():
    default = "tests/test_gate.py::test_current"
    optional = "tests/test_gate.py::test_optional"
    distribution = "tests/test_gate.py::test_distribution"
    rows = []
    for ident, kind, selection, targets in (
        ("s0", "current", "default", [default]),
        ("s1", "historical", "unselected", []),
        ("s2", "retained-private", "unselected", []),
        ("s3", "successor", "optional-unverified", [optional]),
        ("s4", "current", "distribution", [distribution]),
    ):
        rows.append({"source_node": ident, "source_sha256": "a" * 64,
                     "disposition": kind, "claim": "Synthetic isolated instrument claim",
                     "target_nodes": targets, "changed_boundary": "Explicit instrument boundary",
                     "archive_limit": "No execution credit" if not targets else None,
                     "selection": selection})
    collection = {"status": "collection only",
                  "selected": [{"node": default, "markers": []},
                               {"node": distribution, "markers": ["distribution"]}],
                  "deselected": [{"node": optional, "markers": ["proof"]}]}
    surfaces = {"surfaces": [{"id": "api:synthetic", "target_nodes": [default],
                              "execution": "current", "limitations": []}]}
    return {"rows": tuple(rows), "originals": {r["source_node"]: r["source_sha256"] for r in rows},
            "collection": collection, "private": {"s2": "a" * 64}, "surfaces": surfaces,
            "expected_surfaces": {"api:synthetic"}}


def test_planner_admits_complete_synthetic_instrument_and_selects_only_default():
    data = inputs()
    assert runner.plan(**data) == ("tests/test_gate.py::test_current",)


@pytest.mark.parametrize("mutation,reason", [
    ("omission", "missing-original"), ("duplicate", "duplicate-original"),
    ("digest", "source-digest-mismatch"), ("missing-target", "missing-target"),
    ("default-deselected", "default-node-deselected"),
    ("optional-selected", "optional-node-selected"),
    ("private-policy", "unapproved-private-original"),
    ("missing-surface", "missing-surface"),
    ("surface-outside-default", "surface-outside-default"),
    ("duplicate-collection", "duplicate-collected-node"),
])
def test_planner_dirty_controls_refuse_exact_causes(mutation, reason):
    data = copy.deepcopy(inputs())
    rows = list(data["rows"])
    if mutation == "omission": rows.pop()
    elif mutation == "duplicate": rows.append(rows[0])
    elif mutation == "digest": rows[0]["source_sha256"] = "b" * 64
    elif mutation == "missing-target": rows[0]["target_nodes"] = ["tests/test_missing.py::test_missing"]
    elif mutation == "default-deselected": rows[0]["target_nodes"] = rows[3]["target_nodes"]
    elif mutation == "optional-selected": rows[3]["target_nodes"] = rows[0]["target_nodes"]
    elif mutation == "private-policy": data["private"] = {}
    elif mutation == "missing-surface": data["surfaces"]["surfaces"] = []
    elif mutation == "surface-outside-default":
        data["surfaces"]["surfaces"][0]["target_nodes"] = rows[4]["target_nodes"]
    else: data["collection"]["selected"].append(data["collection"]["selected"][0])
    data["rows"] = tuple(rows)
    with pytest.raises(runner.MigrationRefusal) as caught:
        runner.plan(**data)
    assert caught.value.reason == reason


def test_actual_cli_refuses_incomplete_original_accounting_before_execution(tmp_path):
    out = tmp_path / "refused"
    result = subprocess.run([sys.executable, str(ROOT / "tools/run_public_acceptance.py"),
                             "--mapping", str(runner.MIGRATION / "b3-case-map.jsonl.gz"),
                             "--lane", "default", "--out", str(out)],
                            cwd=ROOT, capture_output=True, text=True, check=False, timeout=60)
    assert result.returncode == 1, result.stdout + result.stderr
    assert json.loads(result.stderr)["reason"] == "missing-original"
    assert "Traceback" not in result.stdout + result.stderr
    assert not out.exists()


def test_cli_usage_refuses_unknown_lane_before_work(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / "tools/run_public_acceptance.py"),
                             "--lane", "unknown", "--out", str(tmp_path / "out")],
                            cwd=ROOT, capture_output=True, text=True, check=False, timeout=60)
    assert result.returncode == 2 and "invalid choice" in result.stderr
    assert not (tmp_path / "out").exists()


def test_environment_contains_no_inherited_keys_or_python_injection(monkeypatch, tmp_path):
    for key in ("OPENROUTER_API_KEY", "ZAI_API_KEY", "PYTHONPATH", "PYTHONHOME",
                "PYTEST_ADDOPTS", "PYTEST_PLUGINS", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"):
        monkeypatch.setenv(key, "synthetic-canary")
    env = runner.clean_environment(tmp_path, Path(sys.executable).parent)
    assert not {"OPENROUTER_API_KEY", "ZAI_API_KEY", "PYTHONPATH", "PYTHONHOME",
                "PYTEST_ADDOPTS", "PYTEST_PLUGINS", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"} & env.keys()
    assert env["HOME"] == str(tmp_path)
    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"


def test_real_executor_runs_exact_node_and_checks_runtime_and_metadata_origins(tmp_path):
    observed = runner.execute_nodes(ROOT, (NODE,), python=sys.executable, origin=ROOT / "src/gnd",
                                    metadata_origin=Path(sys.prefix), scratch=tmp_path,
                                    env=runner.clean_environment(executable_dir=Path(sys.executable).parent))
    assert observed["observation"]["selected"] == [NODE]
    assert observed["observation"]["passed"] == [NODE]
    assert observed["observation"]["runtime_origin_checked"] is True
    assert observed["observation"]["metadata_origin_checked"] is True


def test_real_executor_refuses_wrong_runtime_origin(tmp_path):
    with pytest.raises(runner.MigrationRefusal, match="stage-failed"):
        runner.execute_nodes(ROOT, (NODE,), python=sys.executable, origin=tmp_path,
                             metadata_origin=Path(sys.prefix), scratch=tmp_path,
                             env=runner.clean_environment(executable_dir=Path(sys.executable).parent))


def test_executor_refuses_skips_instead_of_reporting_success(tmp_path):
    root = tmp_path / "project"
    (root / "tests").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[tool.pytest.ini_options]\n")
    (root / "tests/test_gate.py").write_text("import pytest\ndef test_skip():\n    pytest.skip('synthetic skip')\n")
    node = "tests/test_gate.py::test_skip"
    scratch = tmp_path / "work"
    scratch.mkdir()
    with pytest.raises(runner.MigrationRefusal, match="stage-failed"):
        runner.execute_nodes(root, (node,), python=sys.executable, origin=ROOT / "src/gnd",
                             metadata_origin=Path(sys.prefix), scratch=scratch,
                             env=runner.clean_environment(executable_dir=Path(sys.executable).parent))
    assert runner.document(scratch / "observed.json")["skipped"] == [node]


def test_command_cap_and_deadline_refuse_without_unbounded_wait(tmp_path):
    env = runner.clean_environment(executable_dir=Path(sys.executable).parent)
    with pytest.raises(runner.MigrationRefusal, match="stage-output-cap"):
        runner.command([sys.executable, "-c", "import sys;sys.stdout.buffer.write(b'x'*1048577)"],
                       cwd=tmp_path, env=env, timeout=5)
    started = time.monotonic()
    with pytest.raises(runner.MigrationRefusal, match="stage-timeout"):
        runner.command([sys.executable, "-c", "import time;time.sleep(20)"],
                       cwd=tmp_path, env=env, timeout=0.05)
    assert time.monotonic() - started < 5


def test_receipts_are_append_only_bounded_and_reject_symlinks(tmp_path):
    out = tmp_path / "out"
    value = {"status": "synthetic instrument; no production acceptance"}
    assert runner.publish_receipt(out, value) == "run-0001.json.gz"
    first = (out / "run-0001.json.gz").read_bytes()
    assert runner.publish_receipt(out, value) == "run-0002.json.gz"
    assert (out / "run-0001.json.gz").read_bytes() == first
    assert json.loads(gzip.decompress(first)) == value
    link = tmp_path / "link"
    link.symlink_to(out)
    with pytest.raises(runner.MigrationRefusal, match="unsafe-output-path"):
        runner.publish_receipt(link, value)
    with pytest.raises(runner.MigrationRefusal, match="oversize-receipt"):
        runner.publish_receipt(out, {"value": "x" * runner.MAX_RECEIPT_BYTES})


def test_input_reader_refuses_nonregular_symlink_oversize_and_duplicate_json(tmp_path):
    file = tmp_path / "input.json"
    file.write_text('{"value":1,"value":2}')
    with pytest.raises(runner.MigrationRefusal, match="duplicate-key"):
        runner.document(file)
    link = tmp_path / "link"
    link.symlink_to(file)
    with pytest.raises(runner.MigrationRefusal, match="symlink-input"):
        runner.read_bytes(link)
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    with pytest.raises(runner.MigrationRefusal, match="nonregular-input"):
        runner.read_bytes(fifo)
    file.write_bytes(b"xx")
    with pytest.raises(runner.MigrationRefusal, match="oversize-input"):
        runner.read_bytes(file, cap=1)


def test_static_executor_runs_only_attributed_authored_paths(monkeypatch, tmp_path):
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    (tmp_path / "gate.py").write_text("value = 1\n")
    (tmp_path / "retained.py").write_text("import os\nimport sys\n")
    monkeypatch.setattr(runner, "audit", lambda root: {"files": [
        {"path": "gate.py", "kind": "authored"},
        {"path": "retained.py", "kind": "identical-import"},
    ]})
    result = runner.static(tmp_path)
    assert result["paths"] == ["gate.py"]
    assert result["lint"]["exit"] == result["diff"]["exit"] == result["staged_diff"]["exit"] == 0


@pytest.mark.distribution
def test_installed_executor_builds_fresh_wheel_and_denies_workspace_access(tmp_path):
    observed = runner.installed(ROOT, runner.audit(ROOT), (NODE,), tmp_path)
    assert observed["filesystem_isolation_checked"] is True
    assert observed["noneditable_wheel"] is True
    assert observed["private_history_exported"] is False
    assert observed["execution"]["observation"]["passed"] == [NODE]
