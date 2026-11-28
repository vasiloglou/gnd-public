"""Run this fixture with an interpreter containing the built GND wheel."""
import json
import subprocess
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path

from gnd import api


def main(root):
    model = root / "model.orm.json"
    value = {"id": "item", "name": "Item", "kind": "value", "primitive": "String"}
    roles = [{"role_name": "key", "object_type": "item"}]
    facts = [{"id": name, "reading": "{Item} is " + name, "roles": roles}
             for name in ("listed", "active")]
    facts[1].update(derivation="derived", derivation_rule={
        "body": [{"fact_type": "listed", "bind": {"key": "$x"}}], "head": {"key": "$x"}})
    model.write_text(json.dumps({"version": 1, "model_id": "host", "object_types": [value], "fact_types": facts}))
    population = {"population": {"model": model.name, "source": "fixture", "covers": ["listed"]},
                  "facts": {"listed": [{"key": "x"}]}}
    pop = root / "pop.json"
    pop.write_text(json.dumps(population))
    values = api.check_with_extensions(model, pop, fact_types=["active"])
    assert values["extensions"][0]["rows"] == [{"key": "x"}]
    req = {"version": 1, "id": "first", "model": str(model), "population": population}
    lines = [req, {**req, "version": 0, "id": "bad"}, {**req, "id": "again"}]
    run = subprocess.run([sys.executable, "-I", "-m", "gnd.snapshot_worker"],
                         input="".join(json.dumps(r) + "\n" for r in lines),
                         capture_output=True, text=True, check=True, timeout=15)
    first, invalid, again = map(json.loads, run.stdout.splitlines())
    assert invalid["error"] == "unsupported-version"
    assert first["model_reused"] is False and again["model_reused"] is True
    assert api.snapshot_verdict(again["report"]) == api.snapshot_verdict(values["report"])
    return {"python": sys.version.split()[0], "pydantic": version("pydantic"), "gnd": version("get-nick-done"),
            "ids": [first["id"], invalid["id"], again["id"]], "model_sha256": first["model_sha256"],
            "run_status": api.snapshot_verdict(first["report"])["status"], "derived_rows": values["extensions"][0]["rows"]}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        print(json.dumps(main(Path(directory).resolve()), sort_keys=True))
