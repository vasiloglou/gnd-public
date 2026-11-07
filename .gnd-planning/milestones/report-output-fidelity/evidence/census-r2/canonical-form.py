import subprocess, collections, sys
from gnd.model import load_model
from gnd.values import model_digest, canonical, MODEL_DIGEST_EXCLUDED_FIELDS
from gnd import artifacts
import hashlib
files=[f for f in subprocess.check_output(["git","ls-files"],text=True).split("\n") if f.endswith((".orm.yaml",".orm.json",".orm.yml"))]
n=0; raised=collections.Counter(); legacy={}; canon={}
for f in files:
    try: m=load_model(f)
    except Exception: continue
    n+=1; legacy[f]=model_digest(m)
    try:
        doc=canonical(m.model_dump(exclude=set(MODEL_DIGEST_EXCLUDED_FIELDS)|{"reference_populations"}),"$")
        canon[f]=hashlib.sha256(artifacts.canonical_json_bytes(doc)).hexdigest()
    except Exception as e:
        raised[type(e).__name__+":"+str(getattr(e,'rule_id',''))]+=1
print("loaded",n,"canonical ok",len(canon),"raised",dict(raised))
print("legacy distinct",len(set(legacy.values())),"canon distinct",len(set(canon.values())))
# partition equivalence: do legacy and canon identify the same classes?
from itertools import groupby
a=collections.defaultdict(set)
for f in canon: a[legacy[f]].add(canon[f])
print("legacy classes mapping to >1 canon:",sum(1 for v in a.values() if len(v)>1))
b=collections.defaultdict(set)
for f in canon: b[canon[f]].add(legacy[f])
print("canon classes mapping to >1 legacy:",sum(1 for v in b.values() if len(v)>1))
print(*[legacy[f] for f in sorted(legacy)[:3]])
