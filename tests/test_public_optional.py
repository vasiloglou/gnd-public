"""Base-wheel refusal and declared synth-extra behavior, outside the checkout."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _probe(python, program, outside, env, *args):
    result = subprocess.run(
        [str(python), "-c", program, *map(str, args)],
        cwd=outside,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_base_wheel_refuses_missing_synth_extra_and_still_checks(package_probe):
    probe = package_probe
    program = """import importlib.util,json,sys
from pathlib import Path
from random import Random
import gnd.synth
from gnd import api
from gnd.synth.values import SynthDependencyError,make_value
assert importlib.util.find_spec('faker') is None
assert importlib.util.find_spec('pytest') is None
try:
    make_value('String',Random(0))
except SynthDependencyError as error:
    assert str(error)==SynthDependencyError.REMEDIATION
else:
    raise AssertionError('missing synth extra did not refuse')
f=Path(sys.argv[1])
payload=api.check(f/'model.orm.yaml',f/'clean.population.json',unredacted=True)
assert payload['exit_code']==0 and payload['assurance']['semantic_decision']=='accept'
assert payload['assurance']['assurance_level']=='none'
print(json.dumps({'refusal':'SynthDependencyError','check_exit':payload['exit_code']}))
"""
    observed = _probe(
        probe["python"], program, probe["outside"], probe["env"],
        ROOT / "tests/fixtures/public-launch-phase-2",
    )
    assert observed == {"refusal": "SynthDependencyError", "check_exit": 0}


def test_declared_synth_extra_is_seeded_and_loader_valid(package_probe, tmp_path):
    probe = package_probe
    venv = tmp_path / "synth"
    for argv in (
        ["uv", "venv", "--python", sys.executable, str(venv)],
        ["uv", "pip", "install", "--python", str(venv / "bin/python"),
         str(probe["wheel"]) + "[synth]"],
    ):
        result = subprocess.run(
            argv, cwd=probe["outside"], env=probe["env"], capture_output=True,
            text=True, check=False, timeout=300,
        )
        assert result.returncode == 0, result.stdout + result.stderr
    program = """import importlib.util,json
from random import Random
from gnd.synth.values import make_value,predicate_for
assert importlib.util.find_spec('faker') is not None
assert importlib.util.find_spec('pytest') is None
primitives=('String','Date','DateTime','Binary')
outputs={}
for primitive in primitives:
    first_rng=Random(101)
    second_rng=Random(101)
    first=[make_value(primitive,first_rng) for _ in range(16)]
    second=[make_value(primitive,second_rng) for _ in range(16)]
    assert first==second and all(predicate_for(primitive)(value) for value in first)
    outputs[primitive]=len(first)
print(json.dumps(outputs))
"""
    observed = _probe(venv / "bin/python", program, probe["outside"], probe["env"])
    assert observed == {"String": 16, "Date": 16, "DateTime": 16, "Binary": 16}
