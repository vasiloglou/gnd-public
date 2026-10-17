"""Bounded current successor for Phase 2 CLI/API and assurance contracts."""

import json
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.distribution

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "case", ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"]
)
def test_installed_behavior(package_probe, case):
    probe = package_probe
    run = subprocess.run(
        [
            str(probe["python"]),
            str(ROOT / "tests/support/public_probe.py"),
            str(ROOT / "tests/fixtures/public-launch-phase-2"),
            case,
        ],
        cwd=probe["outside"],
        env=probe["env"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    payload = json.loads(run.stdout)
    assert payload["case"] == case and payload["exit"] == 0
    assert Path(payload["gnd_file"]).is_relative_to(probe["venv"])


def test_installed_import_help_and_api_surface(package_probe):
    probe = package_probe
    for args in [["--help"], ["check", "--help"], ["review", "--help"]]:
        run = subprocess.run(
            [str(probe["venv"] / "bin/gnd"), *args],
            cwd=probe["outside"],
            env=probe["env"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert run.returncode == 0, run.stderr
    code = "from gnd import api; import importlib.util; assert api.__all__ == ('validate','check','transition','verbalize','diff','witness','replay','check_with_receipt','CheckReceipt','ReceiptRefused'); assert importlib.util.find_spec('faker') is None; assert importlib.util.find_spec('pytest') is None"
    run = subprocess.run(
        [str(probe["python"]), "-c", code],
        cwd=probe["outside"],
        env=probe["env"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert run.returncode == 0, run.stderr


@pytest.mark.parametrize("case", ["C1", "C3"])
def test_named_failure_causes_reject_mutants(package_probe, case):
    code = """import json,sys,runpy,subprocess
from pathlib import Path
from gnd import api
f=Path(sys.argv[1]);case=sys.argv[2]
if case=='C1':
 payload=api.check(f/'model.orm.yaml',f/'violation.population.json',unredacted=True)
 for row in payload['verdicts']:
  if row['verdict']=='fail':row['constraint_type']='unrelated-kind'
 api.check=lambda *a,**kw:payload
else:
 payload=api.validate(f/'invalid.orm.yaml',unredacted=True)
 for row in payload['issues']:row['rule_id']='unrelated-load-error'
 api.validate=lambda *a,**kw:payload
subprocess.run=lambda *a,**kw:subprocess.CompletedProcess(a[0],payload['exit_code'],json.dumps(payload),'')
sys.path.insert(0,str(Path(sys.argv[3]).parent))
sys.argv=[sys.argv[3],str(f),case]
runpy.run_path(sys.argv[0],run_name='__main__')
"""
    probe = package_probe
    run = subprocess.run(
        [
            str(probe["python"]),
            "-c",
            code,
            str(ROOT / "tests/fixtures/public-launch-phase-2"),
            case,
            str(ROOT / "tests/support/public_probe.py"),
        ],
        cwd=probe["outside"],
        env=probe["env"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert run.returncode == 1 and "AssertionError" in run.stderr, run.stdout + run.stderr
