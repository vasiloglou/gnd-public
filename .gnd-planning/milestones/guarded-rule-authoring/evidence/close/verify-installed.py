"""Verify clean source provenance and both installation paths for close."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    source, wheel, root, receipt, base_python = (Path(value).absolute() for value in sys.argv[1:6])
    expected = sys.argv[6]
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=source, text=True).strip()

    assert git("rev-parse", "HEAD") == expected
    assert not git("status", "--porcelain", "--untracked-files=all")
    phase_script = source / ".gnd-planning/milestones/guarded-rule-authoring/evidence/GA3/installed-smoke.py"
    phase_receipt = root.parent / "installed-plus-extra.json"
    subprocess.run(
        [sys.executable, "-I", str(phase_script), str(source), str(wheel), str(root), str(phase_receipt)],
        cwd=source, env=environment, check=True,
    )
    extra = json.loads(phase_receipt.read_bytes())
    assert extra["source_commit"] == expected and extra["wheel_sha256"] == sha256(wheel.read_bytes())

    def run(python, cwd, args, expected_exit):
        result = subprocess.run([str(python), "-I", "-m", "gnd", *args], cwd=cwd,
                                env=environment, capture_output=True, timeout=60, check=False)
        assert result.returncode == expected_exit, (args, result.stdout, result.stderr)
        return {
            "args": args,
            "exit": result.returncode,
            "stdout": json.loads(result.stdout),
            "stdout_sha256": sha256(result.stdout),
            "stderr_sha256": sha256(result.stderr),
        }

    ga1 = root / "ga1"
    scoped = json.loads((ga1 / "corpus/ordinary/scoped.orm.yaml").read_bytes())
    scoped["fact_types"][0]["constraints"][0]["rationale"] = "Metadata-only digest control."
    amended = ga1 / "scoped-metadata.json"
    amended.write_text(json.dumps(scoped), encoding="utf-8")
    wrong_model = []
    for name in ("model.orm.yaml", amended.name):
        result = run(sys.executable, ga1, [
            "measure", name, "--populations", "corpus/ordinary/corpus", "--format", "json",
        ], 3)
        assert "model_digest" in result["stdout"]["error"]
        assert "a wrong-model sidecar" in result["stdout"]["error"]
        wrong_model.append(result)

    base = root / "base"
    base.mkdir()
    shutil.copyfile(ga1 / "model.orm.yaml", base / "model.orm.yaml")
    preflight = subprocess.check_output(
        [str(base_python), "-I", "-c", "import importlib.util,pathlib,gnd,sys; "
         "assert importlib.util.find_spec('faker') is None; "
         "assert pathlib.Path(gnd.__file__).resolve().is_relative_to(pathlib.Path(sys.prefix)); "
         "print(sys.version.split()[0])"],
        cwd=base, env=environment, text=True,
    ).strip()
    without = run(base_python, base, [
        "synth", "model.orm.yaml", "--guarded-cases", "--out", "corpus", "--format", "json",
    ], 5)
    assert "get-nick-done[synth]" in without["stdout"]["error"]
    assert not (base / "corpus").exists()
    assert not git("status", "--porcelain", "--untracked-files=all")
    receipt.write_text(json.dumps({
        **extra,
        "clean_tree_before_and_after": True,
        "wheel_build": ["uv", "build", "--wheel", "--offline", "source"],
        "base_only": {**without, "python": preflight, "faker_absent": True,
                      "output_root_absent": True, "model_sha256": sha256((base / "model.orm.yaml").read_bytes())},
        "measure_digest_refusals": wrong_model,
        "metadata_control_sha256": sha256(amended.read_bytes()),
    }, indent=2) + "\n", encoding="utf-8")
    print("Clean installed wheel passed all three workflows, base-only exit 5, and two exact measure digest refusals.")


if __name__ == "__main__":
    main()
