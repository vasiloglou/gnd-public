import hashlib, time, copy
from gnd.model._validation import unattended_span_issues, _rule_unattended
raw = ("é" + "a"*((10<<20)//1 - 10)).encode()[: (10<<20)]
raw = raw.decode("utf-8","ignore").encode()
dig = hashlib.sha256(raw).hexdigest()
n = 200
span = {"document_sha256": dig, "start": 0, "end": len(raw.decode())-1, "excerpt_sha256": "0"*64}
doc = {"source": {"mode": "unattended", "reviewer": "none", "documents": [{"sha256": dig, "label": "x"}]},
       "object_types": [{"id": f"o{i}", "provenance": {"spans": [span]}} for i in range(n)]}
t=time.perf_counter(); iss=unattended_span_issues(doc, {"x": raw}); dt=time.perf_counter()-t
print(f"{n} full-document spans over a {len(raw)} byte doc: {dt:.2f}s, {len(iss)} issues -> {dt/n*1000:.1f} ms/span")
