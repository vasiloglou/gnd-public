import subprocess, sys, json, collections
"""Read-only census of recorded model digests; see README.md."""
from gnd.model import load_model
from gnd.values import model_digest
files = subprocess.check_output(["git","ls-files"],text=True).split("\n")
models=[f for f in files if f.endswith((".orm.yaml",".orm.json",".orm.yml"))]
ok={}
bad=0
for f in models:
    try:
        ok[f]=model_digest(load_model(f))
    except Exception as e:
        bad+=1
print("model files",len(models),"digested",len(ok),"unloadable",bad, file=sys.stderr)
byd=collections.defaultdict(list)
for f,d in ok.items(): byd[d].append(f)
print("distinct digests",len(byd),file=sys.stderr)
hits=collections.Counter(); hitfiles=collections.defaultdict(set)
import re
for f in files:
    if not f or f.startswith(".git"): continue
    try: t=open(f,encoding="utf-8").read()
    except Exception: continue
    for d in re.findall(r"[0-9a-f]{64}",t):
        if d in byd:
            hits[d]+=1; hitfiles[d].add(f)
allfiles=set().union(*hitfiles.values()) if hitfiles else set()
print("digests recorded somewhere:",len(hits),"files recording >=1 model digest:",len(allfiles),file=sys.stderr)
cat=collections.Counter()
for f in allfiles:
    top="/".join(f.split("/")[:2]) if f.startswith(("src/gnd","tests/fixtures")) else f.split("/")[0]
    cat[top]+=1
for k,v in cat.most_common(): print(v,k)
json.dump(sorted(allfiles),open(sys.argv[1],"w"))
