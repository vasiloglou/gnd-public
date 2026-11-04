import json, subprocess, sys, shutil
from pathlib import Path
C = Path(sys.argv[1]); PY = sys.argv[2]
muts = json.loads((C/".gnd-planning/milestones/model-growth-guardrails/evidence/MG5/mutants.json").read_text())
extra = [
 {"id":"X1-no-u3","file":"src/gnd/model/_validation.py","old":"        if constraint.get(\"source\") in (\"explicit\", \"user-supplied\"):\n","new":"        if False:\n","tests":["tests/test_unattended_mode.py"]},
 {"id":"X2-out-of-range-off","file":"src/gnd/model/_validation.py","old":"        if span[\"end\"] > len(text):\n","new":"        if False:\n","tests":["tests/test_unattended_mode.py"]},
]
for m in muts+extra:
    f = C/m["file"]; orig = f.read_text()
    if orig.count(m["old"]) != 1:
        print(m["id"], "OLD TEXT NOT FOUND", orig.count(m["old"])); continue
    f.write_text(orig.replace(m["old"], m["new"]))
    try:
        r = subprocess.run([PY,"-m","pytest","-q","-x","-p","no:cacheprovider",*m["tests"]],cwd=C,capture_output=True,text=True,env={"PYTHONPATH":str(C/"src"),"PATH":"/usr/bin:/bin","PYTHONDONTWRITEBYTECODE":"1"})
        print(m["id"], "KILLED" if r.returncode else "SURVIVED", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:])
    finally:
        f.write_text(orig)
