"""NM2-Q2: gnd fidelity end to end in the three disclosure modes; outputs must be byte-identical."""
import hashlib, os, subprocess, sys, tempfile
from pathlib import Path
repo = Path(sys.argv[1]); sys.path.insert(0, str(repo / "tests"))
import test_fidelity_payload as fp
from gnd.cli import main
work = Path(tempfile.mkdtemp(dir=sys.argv[2]))
artifacts = work / "artifacts"; assert main(["extract", str(fp.MODEL), "--out", str(artifacts)]) == 0
cases = work / "cases"; fp.write_case(cases / "case-a", artifacts)
env = {k: v for k, v in os.environ.items() if k != "GND_DISCLOSURE"}
digests = {}
for mode, extra_env, root in (("unset", {}, []), ("internal", {}, ["--disclosure", "internal"]),
                              ("customer", {"GND_DISCLOSURE": "customer"}, [])):
    out = work / f"{mode}.json"
    r = subprocess.run(["gnd", *root, "fidelity", str(fp.MODEL), "--cases", str(cases), "--artifacts", str(artifacts),
                        "--format", "json", "--out", str(out)], env={**env, **extra_env}, capture_output=True, text=True)
    digests[mode] = (r.returncode, hashlib.sha256(out.read_bytes()).hexdigest()[:16], hashlib.sha256(r.stdout.encode()).hexdigest()[:16])
    print(mode, *digests[mode])
print("identical in every mode:", len(set(digests.values())) == 1)
