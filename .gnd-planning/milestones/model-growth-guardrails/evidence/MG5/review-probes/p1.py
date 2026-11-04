import copy, json, hashlib, sys
from pathlib import Path
from ruamel.yaml import YAML
from gnd.model._validation import _rule_unattended, semantic_validate
R = Path.cwd()
base = YAML(typ="safe").load((R/"tests/fixtures/unattended/conforming.orm.yaml").read_text())
def ids(d): return [(i.rule_id, i.path, i.message) for i in _rule_unattended(d)]
def sem(d): return [(i.rule_id, i.message) for i in semantic_validate(d) if i.rule_id=="internal:rule-raised"]
def mk(f):
    d=copy.deepcopy(base); f(d); return d
ft=lambda d,i=0: d["fact_types"][i]
cases = {
 "trailing-newline-doc-sha": lambda d: (d["source"]["documents"][0].__setitem__("sha256", d["source"]["documents"][0]["sha256"]+"\n"),
     [s.__setitem__("document_sha256", s["document_sha256"]+"\n") for o in d["object_types"] for s in o["provenance"]["spans"]]),
 "sample_spans-dup-and-out-of-range": lambda d: ft(d)["provenance"]["sample_spans"].extend([{"row":0,"span":ft(d)["provenance"]["sample_spans"][0]["span"]},{"row":-1,"span":ft(d)["provenance"]["sample_spans"][0]["span"]},{"row":999,"span":ft(d)["provenance"]["sample_spans"][0]["span"]}]),
 "huge-offset": lambda d: d["object_types"][0]["provenance"]["spans"][0].update(end=10**30),
 "uppercase-hex": lambda d: d["object_types"][0]["provenance"]["spans"][0].update(excerpt_sha256="A"*64),
 "float-start": lambda d: d["object_types"][0]["provenance"]["spans"][0].update(start=1.0),
 "malformed-span-on-common-sense": lambda d: ft(d)["constraints"][2]["provenance"].update(spans=[{"x":1}]),
 "top-level-constraint-no-spans": lambda d: d.setdefault("constraints",[]).append({"type":"mandatory","role_ref":{"fact_type":"customer_listed","role":"customer"},"source":"llm-inferred","status":"proposed","modality":"deontic","provenance":{}}),
 "dup-declared-docs": lambda d: d["source"]["documents"].append(dict(d["source"]["documents"][0])),
 "mode-Unattended-case": lambda d: d["source"].update(mode="Unattended", reviewer="alice"),
 "rejected-explicit-confirmedish": lambda d: d.update(rejected_proposals=[{"type":"mandatory","status":"rejected","source":"user-supplied"}]),
 "fact_type-status-confirmed": lambda d: ft(d).update(status="confirmed"),
 "sample_spans-on-fact-without-rows": lambda d: ft(d,1)["provenance"].update(sample_spans=[{"row":0,"span":{"bogus":1}}]),
 "sample_population-dict": lambda d: ft(d).update(sample_population={"a":1}),
 "op-explicit": lambda d: d.update(operations=[{"id":"op","status":"proposed","source":"explicit"}]),
}
for k,f in cases.items():
    d=mk(f); print(k, "->", ids(d))
hostile = {
 "object_types-int": lambda d: d.update(object_types=5),
 "fact_types-int": lambda d: d.update(fact_types=5),
 "object_types-str": lambda d: d.update(object_types="abc"),
 "constraints-int": lambda d: d.update(constraints=5),
 "inline-constraints-int": lambda d: ft(d).update(constraints=5),
 "spans-dict": lambda d: d["object_types"][0]["provenance"].update(spans={"a":1}),
 "documents-entry-sha-list": lambda d: d["source"]["documents"][0].update(sha256=["x"]),
 "span-start-list": lambda d: d["object_types"][0]["provenance"]["spans"][0].update(start=[1]),
 "source-list": lambda d: d.update(source=["unattended"]),
 "operations-int": lambda d: d.update(operations=5),
 "doc-sha-unhashable-in-span": lambda d: d["object_types"][0]["provenance"]["spans"][0].update(document_sha256={"a":1}),
 "row-unhashable": lambda d: ft(d)["provenance"]["sample_spans"][0].update(row=[0]),
}
for k,f in hostile.items():
    d=mk(f)
    try: r=ids(d); direct="ok(%d issues)"%len(r)
    except Exception as e: direct="RAISES %s: %s"%(type(e).__name__,e)
    d2=mk(f); d2["source"]=dict(d2["source"]) if isinstance(d2.get("source"),dict) else d2.get("source")
    nomode=mk(f)
    if isinstance(nomode.get("source"),dict): nomode["source"].pop("mode",None)
    print("HOSTILE",k,"direct:",direct,"| rule-raised with mode:",[m for _,m in sem(d)],"| without mode:",[m for _,m in sem(nomode)])
