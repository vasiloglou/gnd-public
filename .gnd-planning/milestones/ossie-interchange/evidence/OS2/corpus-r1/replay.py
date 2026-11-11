"""Replay the hand-authored OS2 verdicts using the GND checker."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from gnd import api

root = Path(__file__).resolve().parent
source = root / "model.orm.json"
model = json.loads(source.read_bytes())
corpus = json.loads((root / "cases.json").read_bytes())
expected = json.loads((root / "expected.json").read_bytes())
assert set(corpus["cases"]) == set(expected)

refs = {constraint["id"]: f"constraints[{i}]" for i, constraint in enumerate(model["constraints"])}
for fact in model["fact_types"]:
    for i, constraint in enumerate(fact.get("constraints", ())):
        refs[constraint["id"]] = f"fact_types[{fact['id']}].constraints[{i}]"

with TemporaryDirectory() as directory:
    for name, overrides in corpus["cases"].items():
        authored = deepcopy(corpus["base"])
        authored["facts"].update(overrides.get("facts", {}))
        if "instances" in overrides:
            authored["instances"] = overrides["instances"]
        sample = Path(directory) / f"{name}.population.json"
        sample.write_text(json.dumps(authored))
        report = api.check(source, sample, unredacted=True)
        assert report["exit_code"] != 3, report["issues"]
        rule = expected[name]["rule"]
        if rule.startswith("derivation:"):
            actual = [
                row["verdict"] for row in report["derivations"] if row["derivation_ref"] == rule
            ]
        else:
            actual = [
                row["verdict"] for row in report["verdicts"] if row["constraint_ref"] == refs[rule]
            ]
        assert actual == [expected[name]["verdict"]], (name, actual)
        print(name, actual[0])
print(f"{len(expected)} hand-authored verdicts matched the GND checker.")
