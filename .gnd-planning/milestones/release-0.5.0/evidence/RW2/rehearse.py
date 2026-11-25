"""Rehearse RW2 probes 1, 2, 4, 5 with the new tree's python and the 0.4.0 venv. Usage: rehearse.py WORK NEWPY OLDPY"""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path

work, new, old = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)

def run(py, *args, cwd):
    r = subprocess.run([py, "-I", *map(str, args)], cwd=cwd, capture_output=True, text=True, timeout=300)
    return r

def gnd(py, *args, cwd):
    return run(py, "-m", "gnd", *args, cwd=cwd)

def show(label, r, n=260):
    tail = (r.stderr.strip().splitlines() or r.stdout.strip().splitlines() or [""])[-1][:n]
    print(f"{label}: exit {r.returncode}  {tail}")

BIND = '''
import hashlib, json, sys
from pathlib import Path
from gnd.artifacts import canonical_json_bytes
from gnd.judgments import judgment_fact_digest
root = Path.cwd(); model, population, target = sys.argv[1:4]
sha = lambda raw: hashlib.sha256(raw).hexdigest()
doc = json.loads((root / model).read_bytes()); raw = (root / population).read_bytes()
fact = json.loads(raw)["facts"][target][0]
(root / "evidence.txt").write_bytes(b"evidence")
identity = {"identity_version": 1, "references": [{"id": r["id"], "sha256": r["sha256"]} for r in doc["reference_populations"]]}
receipts = [{"receipt_id": f"r-{j}", "judge_id": j, "verdict": "approve", "trust": "consumer-pinned",
  "subject": {"model_sha256": sha((root / model).read_bytes()), "population_sha256": sha(raw), "reference_identity": identity,
              "fact_type": target, "index": 0, "fact_sha256": judgment_fact_digest(target, 0, fact)},
  "sources": [{"path": "evidence.txt", "sha256": sha(b"evidence"), "quote": None}], "external_evidence": None} for j in ("a", "b")]
policy = {"admission": {"evidence_floor": None, "minimum_approvals": 2}, "judges": ["a", "b"], "policy_id": "rw2",
  "repair": {"evidence_floor": None, "minimum_rejections": 1}, "schema_version": 1, "targets": [{"fact_type": target, "index": 0}],
  "trust_mode": "consumer-pinned",
  "trusted_receipts": [{"judge_id": r["judge_id"], "receipt_sha256": sha(canonical_json_bytes(r, exact_numbers=True))} for r in receipts]}
(root / "policy.json").write_bytes(canonical_json_bytes(policy))
(root / "receipts.json").write_bytes(canonical_json_bytes({"schema_version": 1, "receipts": receipts}))
'''
JUDGE = ("judgments", "check", "checking.orm.json", "composed.population.json", "--policy", "policy.json",
         "--receipts", "receipts.json", "--trusted-root", ".", "--format", "json")

print("== P1 judging an include root")
interop = work / "interop"
show("new interop run", run(new, "-m", "gnd.examples.literature.interop", "run", "--out", interop, cwd=work))
show("new bind", run(new, "-c", BIND, "checking.orm.json", "composed.population.json", "paper_names_parent_method", cwd=interop))
r = gnd(new, *JUDGE, cwd=interop); out = json.loads(r.stdout)
print("new judge: exit", r.returncode, {k: out.get(k) for k in ("outcome", "error")}, out.get("judgment_policy", {}).get("admission"))
r = gnd(old, *JUDGE, cwd=interop)
print("old judge: exit", r.returncode, r.stdout[:600].replace("\n", " "), "| stderr:", r.stderr[-300:])
# behavior control: edit an include without a new pin
mut = work / "interop-mut"; shutil.copytree(interop, mut)
p = mut / "vocabulary/chronology.orm.json"; d = json.loads(p.read_bytes())
d["object_types"].append({"id": "extra_0", "kind": "value", "name": "Extra0", "primitive": "String"}); p.write_text(json.dumps(d))
r = gnd(new, *JUDGE, cwd=mut)
print("new judge, include edited: exit", r.returncode, r.stdout[:500].replace("\n", " "))

print("== P2 gnd flatten")
r = gnd(new, "flatten", "checking.orm.json", "--out", "flat", cwd=interop); show("new flatten", r); print(sorted(x.name for x in (interop / "flat").iterdir()))
rec = json.loads((interop / "flat/checking.orm.flattening.json").read_bytes()); print("record schema:", rec.get("schema"), sorted(rec)[:12])
show("new flatten again", gnd(new, "flatten", "checking.orm.json", "--out", "flat", cwd=interop))
show("new check flat", gnd(new, "check", "flat/checking.orm.flat.orm.json", "composed.population.json", cwd=interop))
show("old flatten", gnd(old, "flatten", "checking.orm.json", "--out", "flat-old", cwd=interop)); print("old out exists:", (interop / "flat-old").exists())

print("== P4 COUNT certificates")
for who, py in (("new", new), ("old", old)):
    c = work / f"count-{who}"
    r = run(new, "-c", 'import shutil,sys; from importlib.resources import files; shutil.copytree(str(files("gnd")/"examples"/"literature"/"count_fixture"), sys.argv[1])', c, cwd=work)
    show(f"{who} check", gnd(py, "check", "model.orm.yaml", "population.json", cwd=c))
    show(f"{who} witness-count flow", gnd(py, "witness-count", "model.orm.yaml", "population.json", "--request", "group.json", "--raw", "--out", "flow.cert.json", cwd=c))
    if who == "new":
        show("new replay-count flow", gnd(py, "replay-count", "model.orm.yaml", "population.json", "flow.cert.json", "--request", "group.json", "--raw", cwd=c))
        show("new witness-count empty", gnd(py, "witness-count", "model.orm.yaml", "population.json", "--request", "empty-group.json", "--raw", "--out", "empty.cert.json", cwd=c))
        show("new replay-count empty", gnd(py, "replay-count", "model.orm.yaml", "population.json", "empty.cert.json", "--request", "empty-group.json", "--raw", cwd=c))
        cert = json.loads((c / "flow.cert.json").read_bytes()); print("cert keys:", sorted(cert)[:14]); print("empty cert count/roster:", {k: v for k, v in json.loads((c / "empty.cert.json").read_bytes()).items() if k in ("count", "roster", "members")})
        pop = json.loads((c / "population.json").read_bytes()); print("facts:", {k: len(v) for k, v in pop["facts"].items()})
        (c / "population.orig.json").write_bytes((c / "population.json").read_bytes())
print("old has count fixture:", run(old, "-c", "from importlib.resources import files; print(files('gnd').joinpath('examples/literature/count_fixture').is_dir())", cwd=work).stdout.strip())

print("== P5 Ossie relational files")
for who, py in (("new", new), ("old", old)):
    o = work / f"ossie-{who}"; o.mkdir()
    run(new, "-c", 'import shutil,sys; from importlib.resources import files; shutil.copyfile(str(files("gnd")/"examples"/"refunds"/"model.orm.yaml"), sys.argv[1])', o / "model.orm.yaml", cwd=work)
    show(f"{who} export ossie", gnd(py, "export", "ossie", "model.orm.yaml", "--out", "o.yaml", cwd=o)); print(sorted(x.name for x in o.iterdir()))
    show(f"{who} export --ontology-only", gnd(py, "export", "ossie", "model.orm.yaml", "--out", "t.yaml", "--ontology-only", cwd=o)); print(sorted(x.name for x in o.iterdir() if x.name.startswith("t.")))
    show(f"{who} export --max-output-bytes 1", gnd(py, "export", "ossie", "model.orm.yaml", "--out", "s.yaml", "--max-output-bytes", "1", cwd=o))
o = work / "ossie-new"
(o / "c.yaml.mapping.yaml").write_text("x"); show("new collision on mapping path", gnd(new, "export", "ossie", "model.orm.yaml", "--out", "c.yaml", cwd=o)); print(sorted(x.name for x in o.iterdir() if x.name.startswith("c.")))
run(new, "-c", 'import shutil,sys; from importlib.resources import files; shutil.copyfile(str(files("gnd")/"examples"/"refunds"/"physical-binding.json"), sys.argv[1])', o / "binding.json", cwd=work)
show("new export with binding", gnd(new, "export", "ossie", "model.orm.yaml", "--out", "b.yaml", "--physical-binding", "binding.json", cwd=o)); print(sorted(x.name for x in o.iterdir() if x.name.startswith("b.")))
show("new binding + ontology-only", gnd(new, "export", "ossie", "model.orm.yaml", "--out", "u.yaml", "--physical-binding", "binding.json", "--ontology-only", cwd=o))
for name in ("o.yaml", "o.yaml.gnd.json", "o.yaml.loss.json"):
    a = hashlib.sha256((work / "ossie-new" / name).read_bytes()).hexdigest(); b = hashlib.sha256((work / "ossie-old" / name).read_bytes()).hexdigest()
    print(name, "same bytes as 0.4.0:", a == b)
show("new import", gnd(new, "import", "ossie", "o.yaml", "--out", "restored.orm.json", cwd=o))
