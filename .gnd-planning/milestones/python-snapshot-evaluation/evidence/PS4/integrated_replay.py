"""Run this fixture with an interpreter containing the built GND wheel."""
import json
import subprocess
import sys
import tempfile
from hashlib import sha256
from importlib.metadata import distribution, version
from urllib.parse import unquote, urlparse
from unittest.mock import patch
from pathlib import Path

from gnd import api, extensions
from gnd.checker import _core
from gnd.model import load_model
from gnd.population import load_population


def main(root):
    model = root / "model.orm.json"
    value = {"id": "item", "name": "Item", "kind": "value", "primitive": "String"}
    roles = [{"role_name": "key", "object_type": "item"}]
    facts = [{"id": name, "reading": "{Item} is " + name, "roles": roles}
             for name in ("listed", "active", "blocked")]
    facts[1].update(derivation="derived", derivation_rule={
        "body": [{"fact_type": "listed", "bind": {"key": "$x"}}], "negate": [{"fact_type": "blocked", "bind": {"key": "$x"}}],
        "head": {"key": "$x"}})
    model.write_text(json.dumps({"version": 1, "model_id": "host", "object_types": [value], "fact_types": facts}))
    population = {"population": {"model": model.name, "source": "fixture", "covers": ["listed", "blocked"]},
                  "facts": {"listed": [{"key": "x"}, {"key": "y"}], "blocked": [{"key": "y"}]}}
    pop = root / "pop.json"
    pop.write_text(json.dumps(population))
    with patch.object(_core, "check_legacy", wraps=_core.check_legacy) as check, patch.object(
        extensions, "evaluate_derivations", wraps=extensions.evaluate_derivations
    ) as derive:
        values = api.check_with_extensions(model, pop, fact_types=["active"])
        work_counts = {"check": check.call_count, "derive": derive.call_count}
        assert work_counts == {"check": 1, "derive": 1}
    assert values["extensions"][0]["rows"] == [{"key": "x"}]
    loaded_model = load_model(model)
    loaded_population = load_population(pop, model=loaded_model)
    targets = [{"fact_type": "active", "tuple": [{"primitive": "String", "value": v}]} for v in ("x", "y")]
    batch = api.why_not(loaded_model, loaded_population, "active", targets=targets)
    statuses = [r["status"] for r in batch["results"]]
    assert statuses == ["derived", "blocked"]
    request = root / "request.json"
    request.write_text(json.dumps({"version": 1, "targets": targets[:1]}))
    witness = api.witness(model, pop, request)
    assert witness["exit_code"] == 0
    certificate = root / "certificate.json"
    certificate.write_text(json.dumps(witness["certificate"]))
    replay = api.replay(model, pop, certificate)
    assert replay["exit_code"] == 0
    req = {"version": 1, "id": "first", "model": str(model), "population": population}
    lines = [req, {**req, "version": 0, "id": "bad"}, {**req, "id": "again"}]
    run = subprocess.run([sys.executable, "-I", "-m", "gnd.snapshot_worker"],
                         input="".join(json.dumps(r) + "\n" for r in lines),
                         capture_output=True, text=True, check=True, timeout=15)
    first, invalid, again = map(json.loads, run.stdout.splitlines())
    assert invalid["error"] == "unsupported-version"
    assert first["model_reused"] is False and again["model_reused"] is True
    assert api.snapshot_verdict(again["report"]) == api.snapshot_verdict(values["report"])
    def exchange(process, message):
        process.stdin.write(json.dumps(message) + "\n")
        process.stdin.flush()
        return json.loads(process.stdout.readline())

    def launch():
        return subprocess.Popen([sys.executable, "-I", "-m", "gnd.snapshot_worker"],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    with launch() as worker:
        try:
            claimed = json.loads(json.dumps(population))
            claimed["population"]["covers"].append("active")
            claimed["facts"]["active"] = []
            failed = exchange(worker, {**req, "population": claimed})
            pop.write_text(json.dumps(claimed))
            assert api.snapshot_verdict(failed["report"]) == api.snapshot_verdict(api.check(model, pop))
            invalid_pop = exchange(worker, {**req, "population": {"bad": True}})
            assert invalid_pop["error"] == "invalid-input"
            claimed["facts"]["active"] = [{"key": "x"}]
            passed = exchange(worker, {**req, "population": claimed})
            assert failed["report"]["exit_code"] == 1 and passed["report"]["exit_code"] == 0
            assert passed["model_reused"]
            pop.write_text(json.dumps(claimed))
            assert api.snapshot_verdict(passed["report"]) == api.snapshot_verdict(api.check(model, pop))
            model_doc = json.loads(model.read_text())
            del model_doc["fact_types"][1]["derivation_rule"]["negate"]
            model.write_text(json.dumps(model_doc))
            changed = exchange(worker, {**req, "population": claimed})
            assert changed["report"]["exit_code"] == 1
            assert api.snapshot_verdict(changed["report"]) == api.snapshot_verdict(api.check(model, pop))
            assert not changed["model_reused"] and changed["model_sha256"] != first["model_sha256"]
        finally:
            worker.kill()
    with launch() as cold:
        try:
            restarted = exchange(cold, {**req, "population": claimed})
            assert restarted["report"] == changed["report"]
            assert not restarted["model_reused"] and restarted["model_sha256"] == changed["model_sha256"]
        finally:
            cold.stdin.close()
    origin = json.loads(distribution("get-nick-done").read_text("direct_url.json"))
    wheel = Path(unquote(urlparse(origin["url"]).path))
    return {"wheel_sha256": sha256(wheel.read_bytes()).hexdigest(), "evaluation_calls": work_counts,
            "changed_claim_exit": changed["report"]["exit_code"], "invalid_population": invalid_pop["error"],
            "claim_verdicts": [api.snapshot_verdict(r["report"])["status"] for r in (failed, passed, changed)],
            "claim_exit_codes": [failed["report"]["exit_code"], passed["report"]["exit_code"]],
            "replacement_and_cold_restart_sha256": changed["model_sha256"], "python": sys.version.split()[0], "pydantic": version("pydantic"), "gnd": version("get-nick-done"),
            "why_not": statuses, "replay_exit": replay["exit_code"],
            "ids": [first["id"], invalid["id"], again["id"]], "model_sha256": first["model_sha256"],
            "run_status": api.snapshot_verdict(first["report"])["status"], "derived_rows": values["extensions"][0]["rows"]}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        print(json.dumps(main(Path(directory).resolve()), sort_keys=True))
