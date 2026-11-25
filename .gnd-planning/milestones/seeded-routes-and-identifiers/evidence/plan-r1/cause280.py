"""Split issue 280's identification-differs rows by the cause of each unidentified player."""
import json, subprocess, collections
from pathlib import Path
from gnd.model import load_model
from gnd.export.ossie import render_ossie
files = subprocess.run(["git", "ls-files", "*.orm.json", "*.orm.yaml"], capture_output=True, text=True, check=True).stdout.split()
rows = collections.Counter(); models = collections.defaultdict(set); detail = []
multi = []
for f in files:
    try:
        model = load_model(Path(f))
        art = render_ossie(Path(f), output_format="json")
    except Exception:
        continue
    if art.mapping is None:
        continue
    objs = {str(o["id"]): o for o in model.object_types}
    facts = {str(ft["id"]): ft for ft in model.fact_types}
    objectified = {str(ft.get("objectified_as") or ft.get("objectification") or "") for ft in model.fact_types} - {""}
    objectified |= {oid for oid, o in objs.items() if o.get("objectifies")}
    def cause(oid, seen=()):
        o = objs.get(oid, {})
        if o.get("kind") == "value":
            return None
        mode = (o.get("reference") or {}).get("mode")
        if mode == "unit-based": return "unit-based"
        if oid in objectified: return "objectification"
        parents = [str(p) for p in o.get("subtype_of") or ()]
        if len(parents) > 1: return "multi-supertype"
        if parents and o.get("inherits_reference"):
            pc = cause(parents[0], seen + (oid,))
            pmode = (objs.get(parents[0], {}).get("reference") or {}).get("mode")
            if pc: return f"via-parent:{pc}"
            if pmode not in ("popular", "general"): return f"single-parent-{pmode or 'inherited'}"
        return None
    for o in model.object_types:
        ps = [str(p) for p in o.get("subtype_of") or ()]
        if len(ps) > 1:
            modes = [((objs.get(p) or {}).get("reference") or {}).get("mode") for p in ps]
            multi.append((f, str(o["id"]), ps, modes, bool(o.get("inherits_reference"))))
    doc = json.loads(art.mapping)
    def unwrap(n):
        if isinstance(n, dict):
            return {k: (unwrap(json.loads(v)) if k == 'data' and isinstance(v, str) and v[:1] in '{[' else unwrap(v)) for k, v in n.items()}
        if isinstance(n, list): return [unwrap(v) for v in n]
        return n
    doc = unwrap(doc)
    def walk(n):
        if isinstance(n, dict):
            for k, v in n.items():
                if k in ("unmapped_links", "concepts") and isinstance(v, list):
                    for row in v:
                        if not isinstance(row, dict) or row.get("reason") != "identification-differs": continue
                        if k == "unmapped_links":
                            ft = facts.get(row["fact_type"], {})
                            players = [str(r.get("object_type")) for r in ft.get("roles", ())]
                        else:
                            players = [oid for oid, o in objs.items() if str(o.get("name", oid)) == row["concept"] or oid == row["concept"]]
                        causes = sorted({c for p in players if (c := cause(p))}) or ["unclassified"]
                        key = (k, "+".join(causes)); rows[key] += 1; models[key].add(f)
                        detail.append((k, f, row.get("fact_type") or row.get("concept"), causes))
                walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(doc)
for key, n in sorted(rows.items()):
    print(f"{key[0]:15} {key[1]:40} {n:3} rows in {len(models[key])} models")
print()
for d in detail: print(" ", d)
print("\nmulti-supertype subtypes:")
for m in multi: print(" ", m)
