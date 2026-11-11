import difflib
import json
import os
import subprocess
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import yaml

root = Path(__file__).resolve().parent
os.chdir(root)
out = Path("cases")
ossie = Path("ossie")
converters = Path("converters")
schema = ossie / "ontology/ontology.json"
flights = ossie / "examples/flights.ontology.yaml"
config = converters / "relationalai/tests/config/raiconfig.yaml"
fixtures = root / "input"
fixtures.mkdir(exist_ok=True)
home = root / "isolated-home"
home.mkdir(exist_ok=True)


def save(name, payload):
    (out / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def fixture(name, doc):
    path = (fixtures / (name + ".yaml")).relative_to(root)
    path.write_text(yaml.safe_dump(doc, sort_keys=False))
    return path


def observe(*args):
    args = list(map(str, args))
    env = {"PATH": os.defpath, "HOME": str(home), "PYTHONUTF8": "1"}
    run = subprocess.run(args, capture_output=True, text=True, env=env, timeout=120, check=False)
    return {
        "command": args,
        "exit": run.returncode,
        "stdout": run.stdout.replace(str(root), "<scratch>"),
        "stderr": run.stderr.replace(str(root), "<scratch>"),
    }


def validate(path):
    return observe("a/bin/python", "ossie/validation/validate.py", "--schema", schema, path)


def parse(path):
    return observe("b/bin/python", "parse.py", path)


def both(path):
    return {"validator": validate(path), "parser": parse(path)}


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


pins = {
    "ossie_commit": subprocess.check_output(
        ["git", "-C", ossie, "rev-parse", "HEAD"], text=True
    ).strip(),
    "ossie_converters_commit": subprocess.check_output(
        ["git", "-C", converters, "rev-parse", "HEAD"], text=True
    ).strip(),
    "ossie_sha256": {
        name: sha(ossie / name)
        for name in (
            "ontology/ontology.json",
            "ontology/mapping.json",
            "validation/validate.py",
            "ontology/ontology.md",
            "examples/flights.ontology.yaml",
        )
    },
    "relationalai_wheels_sha256": {
        path.name: sha(path) for path in sorted(root.glob("relationalai-*.whl"))
    },
    "offline_config_sha256": sha(config),
    "environments": {},
}
assert pins["ossie_commit"] == "ee89dbdc2844d8b7d293ed42c8613928bb99505f"
assert pins["ossie_converters_commit"] == "83ddc294c8840f5f497a2bdbec2348a128fc2254"
assert len(pins["relationalai_wheels_sha256"]) == 2
for env in "abcd":
    code = "import sys,importlib.metadata as m,json;print(json.dumps([sys.version.split()[0],dict(sorted((d.metadata['Name'],d.version) for d in m.distributions()))]))"
    run = observe(f"{env}/bin/python", "-c", code)
    assert run["exit"] == 0, run
    pins["environments"][env] = json.loads(run["stdout"])
assert pins["environments"]["c"][1]["relationalai"] == "1.39.0"
assert pins["environments"]["d"][1]["relationalai"] == "2.0.1"
save("pins.json", pins)

refunds = yaml.safe_load((out / "refunds.yaml").read_bytes())
minimal = deepcopy(refunds)
minimal["ontology"] = [
    concept for concept in refunds["ontology"] if concept["concept"] in {"Customer", "CustomerCode"}
]
payload = {"gnd": {"test": True}}
e1 = {
    "limits": "Validation and parser admission only. The converter's preservation of an extension is untested."
}
for where in ("baseline", "concept", "relationship"):
    variant = deepcopy(minimal)
    entity = variant["ontology"][1]
    if where == "concept":
        entity["custom_extensions"] = payload
    if where == "relationship":
        entity["relationships"][0]["custom_extensions"] = payload
    e1[where] = both(fixture("e1-" + where, variant))
assert e1["baseline"]["validator"]["exit"] == e1["baseline"]["parser"]["exit"] == 0, e1
e1["OD2"] = (
    "in-document"
    if all(
        e1[where][instrument]["exit"] == 0
        for where in ("concept", "relationship")
        for instrument in ("validator", "parser")
    )
    else "digest-bound-sidecar"
)
save("E1.json", e1)

flights_doc = yaml.safe_load(flights.read_bytes())
broken = deepcopy(flights_doc)
target = next(
    concept["relationships"][0]
    for concept in broken["ontology"]
    if concept.get("relationships") and concept["relationships"][0].get("roles")
)
target["roles"][0]["concept"] = "GndOs0Undeclared"
invalid_schema = deepcopy(broken)
invalid_schema["version"] = 700
e5 = {
    "limits": "Validating pinned upstream examples and one fault pair. The check order is observed for these faults only.",
    "valid": both(flights),
    "undeclared_role_concept": both(fixture("e5-unknown-role", broken)),
    "unknown_role_and_wrong_version_type": both(fixture("e5-schema-and-name", invalid_schema)),
    "authored_refunds": both(out / "refunds.yaml"),
}
save("E5.json", e5)

e3_results = {}
for env, experiment in (("c", "E3"), ("d", "E3b")):
    results = {
        "relationalai_version": pins["environments"][env][1]["relationalai"],
        "limits": "Offline conversion and AST reading of PyRel source. No execution of the emitted program.",
    }
    for name, document in (("flights", flights), ("refunds", out / "refunds.yaml")):
        artifact = out / (experiment + "-" + name + ".pyrel.txt")
        result = observe(f"{env}/bin/python", "convert.py", config, document, artifact)
        if result["exit"] == 0:
            result["source_sha256"] = sha(artifact)
            result["declarations"] = json.loads(result["stdout"].splitlines()[-1])
        results[name] = result
    e3_results[experiment] = results
    save(experiment + ".json", results)
for name in ("flights", "refunds"):
    previous = out / ("E3-" + name + ".pyrel.txt")
    current = out / ("E3b-" + name + ".pyrel.txt")
    if previous.exists() and current.exists():
        diff = "".join(
            difflib.unified_diff(
                previous.read_text().splitlines(keepends=True),
                current.read_text().splitlines(keepends=True),
                fromfile=previous.name,
                tofile=current.name,
            )
        )
        e3_results["E3b"][name]["source_diff"] = diff
save("E3b.json", e3_results["E3b"])
for name in ("E1", "E5", "E3", "E3b"):
    data = json.loads((out / (name + ".json")).read_bytes())
    print(
        name,
        {
            key: (
                value.get("exit")
                if "exit" in value
                else {k: v["exit"] for k, v in value.items() if isinstance(v, dict) and "exit" in v}
            )
            for key, value in data.items()
            if isinstance(value, dict)
        },
    )
