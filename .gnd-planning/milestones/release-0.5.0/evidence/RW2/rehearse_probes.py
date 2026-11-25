"""Rehearse the RW2 probe functions without a retained candidate.

Usage: rehearse_probes.py WORKTREE SCRATCH [--swap]
The candidate is the worktree's editable install; the sandbox prefix is empty; the checkout is a git
archive of HEAD plus the working-tree test file. With --swap the 0.4.0 interpreter stands in for the
candidate, and every probe must fail.
"""
import os, shutil, subprocess, sys, tarfile, traceback
from pathlib import Path

worktree, scratch = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
swap = "--swap" in sys.argv
sys.path.insert(0, str(worktree / "tests"))
import test_release_acceptance as t

shutil.rmtree(scratch, ignore_errors=True)
scratch.mkdir(parents=True)
checkout = scratch / "checkout"; checkout.mkdir()
raw = subprocess.run(["git", "archive", "HEAD"], cwd=worktree, capture_output=True, check=True).stdout
(scratch / "checkout.tar").write_bytes(raw)
with tarfile.open(scratch / "checkout.tar") as archive:
    archive.extractall(checkout, filter="data")
shutil.copyfile(worktree / "tests/test_release_acceptance.py", checkout / "tests/test_release_acceptance.py")

class Factory:
    def mktemp(self, name):
        path = scratch / name; path.mkdir(); return path

env = {k: v for k, v in os.environ.items() if k in {"PATH", "TMPDIR", "LANG", "LC_ALL"}}
env.update(HOME=str(scratch / "home"), PYTHONNOUSERSITE="1"); (scratch / "home").mkdir()
old_python, old_env = t.published_wheel(Factory(), "0.4.0")
print("published 0.4.0:", t.gnd(old_python, [], old_env, scratch, "--version", expected=0).stdout.strip())
new_python = worktree / ".venv/bin/python"
print("candidate stand-in:", t.gnd(new_python, [], env, scratch, "--version", expected=0).stdout.strip())
candidate = (old_python, old_env) if swap else (new_python, env)
installed = (scratch, checkout, candidate[0], None, candidate[1], [])
failures = 0
for name in ("test_installed_rw2_include_roots", "test_installed_rw2_pyrel_rules", "test_installed_rw2_count_certificates",
             "test_installed_rw2_ossie_relational", "test_installed_rw2_seeded_growth"):
    tmp = scratch / name; tmp.mkdir()
    try:
        getattr(t, name)(installed, (old_python, old_env), tmp)
        print(f"{name}: passed")
    except Exception as error:
        failures += 1
        line = traceback.extract_tb(error.__traceback__)[-1]
        first = str(error).strip().splitlines()[0][:200] if str(error).strip() else type(error).__name__
        print(f"{name}: FAILED at line {traceback.extract_tb(error.__traceback__)[1].lineno} ({type(error).__name__}): {first}")
print("failures:", failures)
