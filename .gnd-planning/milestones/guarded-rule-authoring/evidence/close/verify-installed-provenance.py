"""Check the installed package payloads against the clean rebuilt wheel."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source, wheel, base, extra, runs, wrapper, out = (Path(arg).absolute() for arg in sys.argv[1:])

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=source, text=True).strip()

    commit = git("rev-parse", "HEAD")
    assert commit == "618141de9975c4ef30871a979532654267a15de6"
    assert not git("status", "--porcelain", "--untracked-files=all")
    assert not git("ls-files", "-oi", "--exclude-standard", "--", "src")
    rebuild = wheel.parent.parent / "rebuild"
    rebuild.mkdir()
    command = ["uv", "build", "--wheel", "--offline", "--out-dir", str(rebuild), str(source)]
    subprocess.run(command, check=True)
    rebuilt, = rebuild.glob("*.whl")
    assert digest(rebuilt) == digest(wheel)

    results = {}
    with ZipFile(rebuilt) as archive:
        entries = [
            item for item in archive.namelist()
            if not item.endswith("/") and (item.startswith("gnd/") or item.endswith(".dist-info/METADATA"))
        ]
        assert entries
        for label, prefix in (("base_only", base), ("synth_extra", extra)):
            details = json.loads(subprocess.check_output(
                [str(prefix / "bin/python"), "-I", "-c",
                 "import importlib.metadata as m,json,pathlib,gnd; "
                 "print(json.dumps([m.version('get-nick-done'),str(pathlib.Path(gnd.__file__).parent.parent)]))"],
                cwd=runs, text=True,
            ))
            version, packages = details
            for entry in entries:
                assert (Path(packages) / entry).read_bytes() == archive.read(entry), entry
            results[label] = {"distribution": "get-nick-done", "version": version,
                              "matched_wheel_entries": len(entries), "wheel_sha256": digest(rebuilt)}
    assert not git("status", "--porcelain", "--untracked-files=all")
    phase = source / ".gnd-planning/milestones/guarded-rule-authoring/evidence/GA3/installed-smoke.py"
    out.write_text(json.dumps({
        "source_commit": commit,
        "clean_before_and_after": True,
        "ignored_files_under_src": 0,
        "observed_rebuild_argv": ["uv", "build", "--wheel", "--offline", "--out-dir", "rebuild", "source"],
        "rebuild_sha256": digest(rebuilt),
        "installed_payloads": results,
        "executed_scripts": {"candidate_installed_smoke_sha256": digest(phase),
                             "verify_installed_sha256": digest(wrapper)},
        "isolated_model_sha256": digest(runs / "ga1/isolated.json"),
    }, indent=2) + "\n", encoding="utf-8")
    print("Both installed payloads match the identical clean rebuild.")


if __name__ == "__main__":
    main()
