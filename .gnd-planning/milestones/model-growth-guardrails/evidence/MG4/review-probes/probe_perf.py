import time, sys
from gnd.documents import Model
from gnd.extract.guidelines import render_guidelines
from gnd.extract.vocabulary import render_verbalization
N = int(sys.argv[1]); E = int(sys.argv[2]); UCS = int(sys.argv[3])
ots = [{"id": f"v{i}", "name": f"V{i}", "kind": "value", "primitive": "String"} for i in range(100)]
# entities with no printable reference value (external mode) -> composite search over all constraints
ots += [{"id": f"e{i}", "name": f"E{i}", "kind": "entity", "reference": {"mode": "external"}} for i in range(E)]
fts = [{"id": f"f{i}", "reading": "{A} r {B}", "roles": [{"object_type": f"e{i % E}", "role_name": "a"},
        {"object_type": f"v{i % 100}", "role_name": "b"}]} for i in range(N)]
cons = [{"type": "uniqueness", "scope": "external", "role_refs": [{"fact_type": f"f{j}", "role": "b"}, {"fact_type": f"f{j+1}", "role": "b"}],
         "source": "user-supplied", "status": "confirmed", "modality": "alethic", "provenance": {"user_quote": "q"}} for j in range(UCS)]
m = Model.model_validate({"version": 1, "model_id": "s", "object_types": ots, "fact_types": fts, "constraints": cons})
t = time.perf_counter(); render_guidelines(m); g = time.perf_counter() - t
t = time.perf_counter(); render_verbalization(m); v = time.perf_counter() - t
print(f"N={N} E={E} UCs={UCS}: guidelines {g:.2f}s verbalization {v:.2f}s")
