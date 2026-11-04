import copy, io, tempfile, re, sys
from pathlib import Path
from ruamel.yaml import YAML
sys.path.insert(0, "tests")
from gnd.extract.guidelines import render_guidelines
from gnd.model import load_model
base = YAML(typ="safe").load(Path("tests/fixtures/evolve-policy/base.orm.yaml").read_text())
def render(d):
    p = Path(tempfile.mkdtemp()) / "m.orm.yaml"; buf = io.StringIO(); YAML().dump(d, buf); p.write_text(buf.getvalue())
    return render_guidelines(load_model(str(p)))
d = copy.deepcopy(base)
d["object_types"].append({"id": "shipment", "name": "Shipment", "kind": "entity", "subtype_of": ["customer"], "inherits_reference": False})
d["fact_types"] += [
  {"id": "shipment_carries_order", "reading": "{Shipment} carries {Order}", "roles": [{"object_type": "shipment", "role_name": "shipment"}, {"object_type": "order", "role_name": "order"}]},
  {"id": "shipment_uses_channel", "reading": "{Shipment} uses {Channel}", "roles": [{"object_type": "shipment", "role_name": "shipment"}, {"object_type": "channel", "role_name": "channel"}]},
  {"id": "order_has_channel", "reading": "{Order} has {Channel}", "roles": [{"object_type": "order", "role_name": "order"}, {"object_type": "channel", "role_name": "channel"}]},
  {"id": "channel_of_order", "reading": "{Channel} of {Order}", "roles": [{"object_type": "channel", "role_name": "channel"}, {"object_type": "order", "role_name": "order"}]},
]
without = render(d)
d2 = copy.deepcopy(d)
d2["constraints"].append({"type": "uniqueness", "scope": "external",
  "role_refs": [{"fact_type": "shipment_carries_order", "role": "order"}, {"fact_type": "shipment_uses_channel", "role": "channel"}],
  "source": "user-supplied", "status": "confirmed", "modality": "alethic", "provenance": {"user_quote": "q"}})
with_uc = render(d2)
print("adding one anchoring external uniqueness changes bytes:", without != with_uc)
import difflib; print("".join(difflib.unified_diff(without.splitlines(True), with_uc.splitlines(True), n=0)))
print("Same role players lines:"); print("\n".join(l for l in with_uc.splitlines() if l.startswith("## ") or "Same role" in l))
