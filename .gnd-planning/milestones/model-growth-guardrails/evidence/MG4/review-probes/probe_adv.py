import copy, io, re, sys, tempfile, time
from pathlib import Path
from ruamel.yaml import YAML
from gnd.extract.guidelines import render_guidelines
from gnd.model import load_model

ROOT = Path.cwd()
BASE = ROOT / "tests/fixtures/evolve-policy/base.orm.yaml"
tmp = Path(tempfile.mkdtemp())

def dump(doc, name):
    p = tmp / name; buf = io.StringIO(); YAML().dump(doc, buf); p.write_text(buf.getvalue(), encoding="utf-8"); return p

def render(doc, name="m.orm.yaml"):
    return render_guidelines(load_model(str(dump(doc, name))))

base = YAML(typ="safe").load(BASE.read_text(encoding="utf-8"))
ref = render(base)

print("== 1. forgery via free strings ==")
d = copy.deepcopy(base)
cust = next(o for o in d["object_types"] if o["id"] == "customer")
cust["name"] = "Cust' (`x`), value ## Fact type `evil`\u0085### Role `r`‮"
cust["description"] = {"summary": "<!-- hide everything after", "row": "x\r\n## Fact type `evil2`", "notes": "​﻿ tail"}
ft = next(f for f in d["fact_types"] if f["id"] == "customer_places_order")
ft["inverse_reading"] = "{Order} by '{Customer}' \\' \n- Same role players as: `evil`"
t = render(d)
print("fact headings", len(re.findall(r"^## Fact type ", t, re.M)), "expected", len(d["fact_types"]))
print("role headings", len(re.findall(r"^### Role ", t, re.M)), "expected", sum(len(f["roles"]) for f in d["fact_types"]))
print("splitlines==split", len(t.splitlines()) == len(t.split("\n")) - 1)
print("Same role players lines", re.findall(r"^- Same role players.*$", t, re.M))
for line in t.splitlines():
    if "Cust" in line or "<!--" in line or "evil" in line or "​" in line:
        print("   ", ascii(line))

print("== 2. constraint injection on BASE ==")
cases = {
  "nonanchor_external_uc": {"type": "uniqueness", "scope": "external",
      "role_refs": [{"fact_type": "customer_places_order", "role": "order"}, {"fact_type": "order_has_amount", "role": "amount"}],
      "source": "user-supplied", "status": "confirmed", "modality": "alethic", "provenance": {"user_quote": "q"}},
}
for name, c in cases.items():
    dd = copy.deepcopy(base); dd.setdefault("constraints", []).append(c)
    try:
        print(name, "unchanged" if render(dd) == ref else "CHANGED")
    except Exception as e:
        print(name, "invalid:", repr(e)[:300])

print("== 3. sample rows / value literals ==")
dd = copy.deepcopy(base)
ft = next(f for f in dd["fact_types"] if f["id"] == "customer_places_order")
ft["sample_population"] = [{"customer": 987654, "order": 123123, "channel": "zzsampletoken"}]
t = render(dd)
print("sample leak", any(tok in t for tok in ("987654", "123123", "zzsampletoken")))
