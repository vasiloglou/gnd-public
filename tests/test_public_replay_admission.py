"""A replay must run the selected nodes on the claimed clean commit."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import test_public_replay_driver_support as driver


def git(work, *args):
    return subprocess.check_output(["git", *args], cwd=work, text=True).strip()


@pytest.fixture
def replay(tmp_path):
    work = tmp_path / "checkout"
    work.mkdir()
    git(work, "init", "-q")
    git(work, "config", "user.email", "replay-test@example.invalid")
    git(work, "config", "user.name", "Replay unit fixture")
    (work / "test_selected.py").write_text("def test_present():\n    assert True\n")
    git(work, "add", "test_selected.py")
    git(work, "commit", "-qm", "Create unit fixture")
    commit = git(work, "rev-parse", "HEAD")
    control = tmp_path / "control"
    manifest = control / "proof/v6/assurance/replay.json"
    manifest.parent.mkdir(parents=True)
    spec = {
        "id": "unit-command",
        "context": "current",
        "run_at": ["start"],
        "argv": [sys.executable, "-c", "print('Executed unit command')"],
        "seconds": 10,
        "stdout_bytes": 65536,
        "stderr_bytes": 65536,
        "retained_bytes": 131072,
    }
    document = {"start_ceiling_seconds": 60, "contexts": {"current": commit}, "commands": [spec]}
    driver.write(manifest, document)
    out = tmp_path / "retained"
    out.mkdir()
    context = tmp_path / "contexts.json"
    driver.write(
        context,
        {
            "root": str(control),
            "out": str(out),
            "scratch": str(tmp_path),
            "setup_seconds": 0,
            "contexts": {"current": {"commit": commit, "path": str(work)}},
        },
    )
    return context, work, manifest, document


@pytest.mark.parametrize("change", ["staged", "untracked"])
def test_changed_source_cannot_run_as_the_clean_commit(replay, change):
    context, work, _, _ = replay
    path = work / ("test_selected.py" if change == "staged" else "extra_producer.py")
    path.write_text("raise RuntimeError('changed source')\n")
    if change == "staged":
        git(work, "add", path.name)
    with pytest.raises(ValueError, match="clean"):
        driver.run(context)


def test_actual_collection_must_equal_the_literal_bound_nodes(replay):
    context, _, manifest, document = replay
    spec = document["commands"][0]
    spec["argv"] = [sys.executable, "-m", "pytest", "-q", "test_selected.py"]
    inventory = manifest.parents[3] / "nodes.json"
    driver.write(inventory, {"commands": {"unit": ["test_selected.py::test_missing"]}})
    spec["node_inventory"] = {
        "path": "nodes.json",
        "sha256": driver.digest(inventory),
        "selector": "unit",
    }
    driver.write(manifest, document)
    with pytest.raises(ValueError, match="node"):
        driver.run(context)


def test_context_commit_is_validated_even_without_a_resume_amendment(replay):
    context, _, manifest, document = replay
    document["contexts"]["current"] = "0" * 40
    driver.write(manifest, document)
    with pytest.raises(ValueError, match="context"):
        driver.run(context)


def test_clean_context_and_exact_collection_execute_once(replay):
    context, _, manifest, document = replay
    spec = document["commands"][0]
    spec["argv"] = [sys.executable, "-m", "pytest", "-q", "test_selected.py"]
    inventory = manifest.parents[3] / "nodes.json"
    driver.write(inventory, {"commands": {"unit": ["test_selected.py::test_present"]}})
    spec["node_inventory"] = {
        "path": "nodes.json",
        "sha256": driver.digest(inventory),
        "selector": "unit",
    }
    driver.write(manifest, document)
    assert driver.run(context) == 0


def test_tracked_changes_inside_output_namespace_are_not_excused(replay):
    context, work, _, _ = replay
    target = work / ".gnd-planning/phase6-replay-output/producer.py"
    target.parent.mkdir(parents=True)
    target.write_text("# A staged source is not an allowed generated output\n")
    git(work, "add", str(target.relative_to(work)))
    with pytest.raises(ValueError, match="clean"):
        driver.run(context)


def test_collection_cannot_omit_nodes_outside_tests_directory(replay):
    context, work, manifest, document = replay
    for relative in ("tests/test_included.py", "examples/demo/test_smoke.py"):
        target = work / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("def test_real():\n    assert True\n")
        git(work, "add", relative)
    git(work, "commit", "-qm", "Add mixed collection roots")
    commit = git(work, "rev-parse", "HEAD")
    setup = driver.json.loads(context.read_text())
    setup["contexts"]["current"]["commit"] = commit
    driver.write(context, setup)
    document["contexts"]["current"] = commit
    spec = document["commands"][0]
    spec["argv"] = [sys.executable, "-m", "pytest", "-q", "tests", "examples"]
    inventory = manifest.parents[3] / "nodes.json"
    driver.write(inventory, {"commands": {"unit": ["tests/test_included.py::test_real"]}})
    spec["node_inventory"] = {
        "path": "nodes.json", "sha256": driver.digest(inventory), "selector": "unit",
    }
    driver.write(manifest, document)
    with pytest.raises(ValueError, match="node"):
        driver.run(context)
