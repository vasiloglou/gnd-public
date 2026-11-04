import copy, json, subprocess, sys, tempfile
from pathlib import Path
from ruamel.yaml import YAML
R=Path.cwd(); FX=R/"tests/fixtures/unattended"
base=YAML(typ="safe").load((FX/"conforming.orm.yaml").read_text())
tmp=Path(tempfile.mkdtemp())
def run(d,*a):
    p=tmp/"m.json"; p.write_text(json.dumps(d))
    r=subprocess.run([sys.executable,"-m","gnd","validate",str(p),*map(str,a)],capture_output=True)
    return r.returncode, r.stdout.decode()[:300]
print("base:",run(base,"--document",FX/"source.txt"))
d=copy.deepcopy(base); d["object_types"][0]["provenance"]["spans"][0]["excerpt_sha256"]="1"*64
print("one edit:",run(d,"--document",FX/"source.txt"))
from gnd.model import load_model
p=tmp/"m.json"; p.write_text(json.dumps(d))
m=load_model(p); dump=m.model_dump(exclude={"warnings"})
print(dump["object_types"][1]["provenance"], dump["object_types"][0]["provenance"])
