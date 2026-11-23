"""GO1-C6 round sweep: CLI wall time of validate, preview, apply at five sizes, base vs head."""
import json, os, subprocess, sys, time, shutil
from pathlib import Path
WT = Path(sys.argv[1]); OUT = Path(sys.argv[2]); BASE_SRC = sys.argv[3]
sys.path[:0] = [str(WT / "tests")]
import test_go1_evolve_parse_once as go1
import test_evolve_additive_policy as policy
results = []
for n in (10, 100, 200, 400, 800):
    for label, src in (("base", BASE_SRC), ("head", str(WT / "src"))):
        root = OUT / f"{label}-{n}"
        if root.exists(): shutil.rmtree(root)
        paths = go1._grown_workspace(root, n)
        env = dict(os.environ, PYTHONPATH=src)
        def run(argv):
            start = time.perf_counter()
            r = subprocess.run([sys.executable, "-m", "gnd", *argv], env=env, capture_output=True)
            return round(time.perf_counter() - start, 2), r.returncode
        bulk = root / "bulk.txt"; bulk.write_bytes(go1._bulk(n)[0])
        docs = ["--document", str(WT / "tests/fixtures/unattended/source.txt"),
                "--document", str(WT / "tests/fixtures/unattended-model-growth/round-1.txt"),
                "--document", str(bulk), "--require-documents"]
        from ruamel.yaml import YAML
        count = len(YAML(typ="safe").load(paths["model"].read_text())["object_types"])
        row = {"n": n, "object_types": count, "tree": label}
        row["validate"] = run(["validate", str(paths["model"]), *docs])
        row["preview"] = run(policy._preview_argv(paths, "--policy", "additive", "--shape-report"))
        row["apply"] = run(policy._apply_argv(paths, "--policy", "additive"))
        results.append(row); print(json.dumps(row), flush=True)
(OUT / "sweep.json").write_text(json.dumps(results, indent=1))
