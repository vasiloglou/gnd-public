"""PF2 E5: run every input the eight reviews reported, on the version it was reported against."""
import importlib.util, json, sys, tempfile
from pathlib import Path

S = Path(sys.argv[1]); held = Path(sys.argv[2])
mapping = json.loads((held / "key/branch-map.json").read_text())
MOD = {"K1": "model_type_ids", "K2": "skill_names", "K3": "skill_of_file", "K4": "project_version"}

def load(branch):
    k = mapping[branch].split("-")[0]; root = S / "wt" / branch
    spec = importlib.util.spec_from_file_location(branch.replace("-", "_"), root / "tools" / f"{MOD[k]}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m, root

def call(f, *a):
    try: return repr(f(*a))
    except Exception as e: return f"raises {type(e).__name__}"

tmp = Path(tempfile.mkdtemp()); rows = []
def model(text):
    d = Path(tempfile.mkdtemp(dir=tmp)); p = d / "m.orm.yaml"; p.write_text(text); return p
def skill(text):
    d = Path(tempfile.mkdtemp(dir=tmp)); (d / "demo").mkdir(); (d / "demo/SKILL.md").write_text(text); return d
def toml(text):
    p = Path(tempfile.mkdtemp(dir=tmp)) / "pyproject.toml"; p.write_text(text); return p

OT = "object_types:\n  - id: title\n    name: Title\n    kind: value\n    primitive: String\n"
k1 = {  # change-f, reported F1/F2
 "object_types first": OT + "version: 1\nfact_types: []\n",
 "quoted id, version first": "version: 1\n" + OT.replace("id: title", 'id: "title"') + "fact_types: []\n",
 "fact_types before object_types, later source id": "version: 1\nfact_types: []\n" + OT + "source:\n  entries:\n  - id: metadata\n",
}
k2 = {  # change-a F1/F2 and change-c F1
 'name: "demo"': '---\nname: "demo"\ndescription: d\n---\n\nbody\n',
 "name: demo # comment": "---\nname: demo # comment\ndescription: d\n---\n\nbody\n",
 '"name": demo': '---\n"name": demo\ndescription: d\n---\n\nbody\n',
 "folded name": "---\nname: >-\n  demo\ndescription: d\n---\n\nbody\n",
 'description "Use --- to separate"': '---\ndescription: "Use --- to separate sections."\nname: demo\n---\n\nbody\n',
 "block-scalar description holding ---": "---\ndescription: |\n  ---\n  A demo skill.\nname: demo\n---\n\nbody\n",
}
k3 = ["gnd-update-review-panel/agents/openai.yaml", "gnd-solve/references/nested/guide.md",
      "gnd-solve/../gnd-adopt/SKILL.md"]
k3_expect = ["gnd-update-review-panel", "gnd-solve", "gnd-adopt"]
k4 = {
 "earlier table": '[tool.demo]\nversion = "9.9.9"\n[project]\nname = "demo"\nversion = "1.2.3"\n',
 "no spaces": '[project]\nname = "demo"\nversion="1.2.3"\n',
 "single quotes": "[project]\nname = 'demo'\nversion = '1.2.3'\n",
 "dynamic version, tool table version": '[project]\nname = "demo"\ndynamic = ["version"]\n[tool.demo]\nversion = "9.9.9"\n',
}
for branch, label in sorted(mapping.items()):
    m, root = load(branch); k = label.split("-")[0]
    if k == "K1":
        for n, t in k1.items(): rows.append((branch, label, n, "['title']", call(m.object_type_ids, model(t))))
    if k == "K2":
        for n, t in k2.items(): rows.append((branch, label, n, "{'demo': 'demo'}", call(m.skill_names, skill(t))))
    if k == "K3":
        sk = root / "src/gnd/skills"
        for rel, want in zip(k3, k3_expect): rows.append((branch, label, rel, repr(want), call(m.skill_of, sk / rel, sk)))
    if k == "K4":
        want = {"dynamic version, tool table version": "None"}
        for n, t in k4.items(): rows.append((branch, label, n, want.get(n, "'1.2.3'"), call(m.project_version, toml(t))))
for r in rows: print(" | ".join(r) + ("" if r[3] == r[4] else "   <-- WRONG"))
json.dump(rows, open(held / "key/grade-runs.json", "w"), indent=1)
