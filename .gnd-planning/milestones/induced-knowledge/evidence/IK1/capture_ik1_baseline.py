"""Capture IK1 baseline digests (spec section 6 rows 1-7) from the repo in cwd."""
import hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path.cwd()
FIXTURES = ["full_vocabulary", "library", "keywords", "v2_worked_example"]
ENV = {**os.environ, "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "0"}
PY = sys.executable


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run(argv, check_codes=None):
    p = subprocess.run(argv, cwd=ROOT, env=ENV, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def norm(b: bytes, t: str) -> bytes:
    return b.replace(t.encode(), b"<T>")


GND = [PY, "-m", "gnd"]
out = {"rows": {}, "exits": {}}
for stem in FIXTURES:
    f = f"tests/fixtures/models/{stem}.orm.yaml"
    rows = {}
    exits = {}
    c, o, _ = run([PY, "-c", "from gnd.model_verbalization import render_model_verbalization as r; import sys; sys.stdout.write(r(sys.argv[1]))", f])
    rows["1"], exits["1"] = sha(o), c
    c, o, _ = run([PY, "-c", "from gnd.model import load_model; from gnd.vocabulary import render_verbalization as r; import sys; sys.stdout.write(r(load_model(sys.argv[1])))", f])
    rows["2"], exits["2"] = sha(o), c
    with tempfile.TemporaryDirectory() as t:
        t = str(Path(t).resolve())
        c, _, e = run(GND + ["extract", "--out", f"{t}/x", f])
        exits["3"] = c
        rows["3"] = sha((Path(t) / "x" / f"{stem}.projection.schema.json").read_bytes())
        c, _, e = run(GND + ["codegen", "--out", f"{t}/p", f])
        exits["4"] = c
        rows["4"] = sha(norm((Path(t) / "p" / ".gnd-codegen.json").read_bytes(), t))
        c, o, _ = run(GND + ["conformance", "--format", "json", f, f"{t}/p"])
        exits["5"] = c
        o = norm(o, t)
        o = re.sub(rb'("gnd_version"\s*:\s*)"[^"]*"', rb'\1"<V>"', o)
        rows["5"] = sha(o)
    c, o, _ = run(GND + ["diff", "--format", "json", f, f])
    rows["6"], exits["6"] = sha(o), c
    out["rows"][stem] = rows
    out["exits"][stem] = exits

# row 7: evolve preview, once
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import test_model_evolution as tme  # noqa: E402
with tempfile.TemporaryDirectory() as t:
    t = str(Path(t).resolve())
    paths = tme._write_cli_workspace(Path(t), case_name="evolution-safe-additive")
    c, _, e = run(GND + tme._preview_argv(paths))
    out["exits"]["evolve_preview"] = c
    out["rows"]["evolve_preview"] = sha(norm(Path(paths["preview"]).read_bytes(), t))
json.dump(out, sys.stdout, indent=2, sort_keys=True)
print()
