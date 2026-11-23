"""Run the PF2 answer key's inputs on both versions of each capability (E2, E3)."""
import importlib.util, json, sys, tempfile
from pathlib import Path

S = Path(sys.argv[1]); mapping = json.loads((S / "key/branch-map.json").read_text())
where = {v: S / "wt" / k for k, v in mapping.items()}
MOD = {"K1": "model_type_ids", "K2": "skill_names", "K3": "skill_of_file", "K4": "project_version"}

def load(label):
    k = label.split("-")[0]; root = where[label]
    spec = importlib.util.spec_from_file_location(f"{label}_{MOD[k]}".replace("-", "_"), root / "tools" / f"{MOD[k]}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m, root

def call(f, *a):
    try: return repr(f(*a))
    except Exception as e: return f"raises {type(e).__name__}: {e}"[:160]

tmp = Path(tempfile.mkdtemp()); rows = []
movie = (where["K1-control"] / "src/gnd/skills/gnd-model-from-text/examples/movie_catalog.orm.yaml").read_text()
k1 = {
 "quoted id": movie.replace("  - id: movie\n", '  - id: "movie"\n', 1),
 "id not the first key": movie.replace("  - id: movie\n    name: Movie\n", "  - name: Movie\n    id: movie\n", 1),
 "a comment after the id": movie.replace("  - id: movie\n", "  - id: movie  # the film\n", 1),
}
k2 = {
 "quoted name": '---\nname: "demo"\ndescription: A demo.\n---\n\n# Demo\n',
 "a description that holds ---": '---\ndescription: A demo --- with a rule.\nname: demo\n---\n\n# Demo\n',
 "a comment after the name": '---\nname: demo  # the skill\ndescription: A demo.\n---\n\n# Demo\n',
}
k3 = [
 "gnd-model-from-text/evals/fixtures/synthetic_good_user/README.md",
 "gnd-model-from-text/examples/movie_catalog.orm.yaml",
 "gnd-update-review-panel/agents/openai.yaml",
]
k4 = {
 "a version in an earlier table": '[tool.demo]\nversion = "9.9"\n\n[project]\nname = "demo"\nversion = "1.0"\n',
 "no spaces around =": '[project]\nname = "demo"\nversion="1.0"\n',
 "single quotes": "[project]\nname = 'demo'\nversion = '1.0'\n",
}
for kind in ("planted", "control"):
    m, root = load(f"K1-{kind}")
    for name, text in k1.items():
        d = tmp / f"k1-{kind}-{len(rows)}"; d.mkdir(); p = d / "model.orm.yaml"; p.write_text(text)
        rows.append(("K1", kind, name, call(m.object_type_ids, p)))
    m, root = load(f"K2-{kind}")
    for name, text in k2.items():
        d = tmp / f"k2-{kind}-{len(rows)}" / "demo"; d.mkdir(parents=True); (d / "SKILL.md").write_text(text)
        rows.append(("K2", kind, name, call(m.skill_names, d.parent)))
    m, root = load(f"K3-{kind}")
    skills = root / "src/gnd/skills"
    for rel in k3:
        rows.append(("K3", kind, rel, call(m.skill_of, skills / rel, skills)))
    m, root = load(f"K4-{kind}")
    for name, text in k4.items():
        p = tmp / f"k4-{kind}-{len(rows)}.toml"; p.write_text(text)
        rows.append(("K4", kind, name, call(m.project_version, p)))
for r in rows: print(" | ".join(r))
json.dump(rows, open(S / "key/key-runs.json", "w"), indent=1)
