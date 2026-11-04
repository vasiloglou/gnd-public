"""Corpus probes: totality, determinism, structure, corpus-wide constraint blindness."""
import copy, glob, io, json, re, sys, tempfile, traceback
from pathlib import Path
from ruamel.yaml import YAML

ROOT = Path.cwd()
from gnd.extract.guidelines import render_guidelines
from gnd.model import load_model
from gnd import refscheme

def dump(doc, path):
    buf = io.StringIO(); YAML().dump(doc, buf); path.write_text(buf.getvalue(), encoding="utf-8")

models = sorted({*ROOT.glob("tests/fixtures/**/*.orm.yaml"), *ROOT.glob("examples/**/*.orm.yaml")})
parity = json.load(open(".gnd-planning/milestones/model-growth-guardrails/evidence/MG4/parity-after.json"))["models"]
accepted = [m for m in models if parity.get(m.relative_to(ROOT).as_posix(), {}).get("exit") == 0]
print("accepted", len(accepted))
raised = []; struct_bad = []; blind_bad = []; strip_invalid = []; nonanchor_seen = 0
tmp = Path(tempfile.mkdtemp())
for path in accepted:
    try:
        model = load_model(str(path))
        text = render_guidelines(model)
        assert text == render_guidelines(load_model(str(path)))
    except Exception as e:
        raised.append((str(path), repr(e))); continue
    heads = re.findall(r"^## Fact type ", text, re.M)
    roles = re.findall(r"^### Role ", text, re.M)
    if len(heads) != len(model.fact_types) or len(roles) != sum(len(f.get("roles") or []) for f in model.fact_types):
        struct_bad.append(str(path))
    # corpus-wide blindness: keep only external UCs that anchor on some object type
    doc = YAML(typ="safe").load(path.read_text(encoding="utf-8"))
    oids = [o["id"] for o in doc.get("object_types") or []]
    kept = []
    for c in doc.get("constraints") or []:
        if c.get("type") == "uniqueness" and c.get("scope") == "external":
            rr = c.get("role_refs") or []
            if rr and any(refscheme._anchors_on(rr, o, model) for o in oids):
                kept.append(c)
            else:
                nonanchor_seen += 1
    stripped = copy.deepcopy(doc); stripped["constraints"] = kept
    for ft in stripped.get("fact_types") or []:
        ft.pop("constraints", None)
    for key in ("derivation_rules", "dynamic_rules", "rules"):
        pass
    p = tmp / path.name; dump(stripped, p)
    try:
        t2 = render_guidelines(load_model(str(p)))
    except Exception as e:
        strip_invalid.append((str(path), repr(e)[:200])); continue
    if t2 != text:
        blind_bad.append(str(path))
print("raised", raised)
print("struct_bad", struct_bad)
print("blind_bad", blind_bad)
print("non-anchoring external UCs stripped:", nonanchor_seen)
print("strip_invalid", len(strip_invalid), strip_invalid[:5])
