import copy, json, subprocess, sys, tempfile
from pathlib import Path
from ruamel.yaml import YAML
R=Path.cwd(); FX=R/"tests/fixtures/unattended"
base=YAML(typ="safe").load((FX/"conforming.orm.yaml").read_text())
span=base["object_types"][0]["provenance"]["spans"][0]
tmp=Path(tempfile.mkdtemp())
def run(d,*a):
    p=tmp/"m.json"; p.write_text(json.dumps(d))
    r=subprocess.run([sys.executable,"-m","gnd","validate",str(p),*map(str,a)],capture_output=True)
    return r.returncode, r.stdout.decode()
d=copy.deepcopy(base)
d["constraints"]=[{"type":"textual","expression":"Every order is shipped eventually.","source":"imported","status":"proposed","modality":"alethic",
  "provenance":{"framework":"gsd","artifact":"REQ.md","commit":"a"*40,"sha256":"b"*64,"anchor":"R1","spans":[span]}}]
c,o=run(d,"--format","json"); p=json.loads(o); print("imported textual alethic:",c,[(i["rule_id"],i["severity"]) for i in p["issues"]],[w["rule_id"] for w in p["warnings"]])
c,o=run(d); print("text:",c,o)
d2=copy.deepcopy(d); d2["object_types"][0]["provenance"]["spans"][0]=dict(span, excerpt_sha256="1"*64)
c,o=run(d2,"--format","json","--document",FX/"source.txt"); p=json.loads(o); print("with mismatch json:",c,[i["rule_id"] for i in p["issues"]],"warnings:",[w["rule_id"] for w in p["warnings"]])
c,o=run(d2,"--document",FX/"source.txt"); print("with mismatch text:",c,o)
c,o=run(d,"--document",FX/"source.txt"); print("ok doc text:",c,o)
# inline-constraint path in --document
d3=copy.deepcopy(base); d3["fact_types"][0]["constraints"][0]["provenance"]["spans"][0]["excerpt_sha256"]="1"*64
c,o=run(d3,"--format","json","--document",FX/"source.txt"); print("inline path:",c,[i["path"] for i in json.loads(o)["issues"]])
