import copy, json, hashlib, subprocess, sys, tempfile, os
from pathlib import Path
from ruamel.yaml import YAML
R = Path.cwd()
FX = R/"tests/fixtures/unattended"
base = YAML(typ="safe").load((FX/"conforming.orm.yaml").read_text())
tmp = Path(tempfile.mkdtemp())
def write(d, name="m.json"):
    p = tmp/name; p.write_text(json.dumps(d)); return p
def run(*args):
    r = subprocess.run([sys.executable, "-m", "gnd", *map(str,args)], capture_output=True, text=False)
    return r.returncode, r.stdout.decode("utf-8","replace"), r.stderr.decode("utf-8","replace")
# trailing newline e2e
d = copy.deepcopy(base); sha=d["source"]["documents"][0]["sha256"]
txt = json.dumps(d).replace(sha, sha+"\\n")
p = tmp/"nl.json"; p.write_text(txt)
print("trailing-newline e2e:", run("validate", p, "--format","json")[0])
m = write(base)
print("baseline ok:", run("validate", m)[:2])
print("json ok + doc:", run("validate", m, "--document", FX/"source.txt", "--format","json"))
print("text ok + doc:", run("validate", m, "--document", FX/"source.txt"))
# directory
print("directory:", run("validate", m, "--document", tmp, "--format","json"))
print("directory text:", run("validate", m, "--document", tmp))
# missing
print("missing json:", run("validate", m, "--document", tmp/"nope", "--format","json"))
print("missing text:", run("validate", m, "--document", tmp/"nope"))
# missing doc but invalid model
bad = copy.deepcopy(base); bad["source"]["reviewer"]="alice"; mb=write(bad,"bad.json")
print("missing doc + invalid model:", run("validate", mb, "--document", tmp/"nope", "--format","json")[0])
# non-utf8 declared
raw = b"\xff\xfe bad bytes secret-phrase"
(tmp/"nonutf8.txt").write_bytes(raw)
d = copy.deepcopy(base); d["source"]["documents"].append({"sha256": hashlib.sha256(raw).hexdigest(), "label":"n"})
mn = write(d,"n.json")
print("non-utf8 declared:", run("validate", mn, "--document", tmp/"nonutf8.txt", "--format","json"))
# large file declared
big = b"a"*((10<<20)+5)
(tmp/"big.txt").write_bytes(big)
d = copy.deepcopy(base); d["source"]["documents"].append({"sha256": hashlib.sha256(big).hexdigest(), "label":"b"})
mg = write(d,"g.json")
r = run("validate", mg, "--document", tmp/"big.txt", "--format","json"); print("big declared:", r[0], r[1][:600])
print("big digest real:", hashlib.sha256(big).hexdigest(), "prefix:", hashlib.sha256(big[:(10<<20)+1]).hexdigest())
# same doc twice / two paths
(tmp/"copy.txt").write_bytes((FX/"source.txt").read_bytes())
print("same doc twice:", run("validate", m, "--document", FX/"source.txt", "--document", FX/"source.txt")[:2])
print("same doc two paths:", run("validate", m, "--document", FX/"source.txt", "--document", tmp/"copy.txt")[:2])
# mismatch json payload shape vs normal 3 payload
d = copy.deepcopy(base); d["object_types"][0]["provenance"]["spans"][0]["excerpt_sha256"]="1"*64
mm = write(d,"mm.json")
r = run("validate", mm, "--document", FX/"source.txt", "--format","json"); print("mismatch json:", r[0], r[1])
r = run("validate", mb, "--format","json"); print("normal 3 json keys:", sorted(json.loads(r[1]))); 
r = run("validate", mm, "--document", FX/"source.txt"); print("mismatch text:", r)
# non-unattended model with warnings + document
