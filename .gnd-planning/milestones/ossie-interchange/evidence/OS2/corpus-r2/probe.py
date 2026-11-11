"""Check authored formula placement against the pinned local Ossie parser."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from gnd.export.ossie import render_ossie
from tools.ossie_oracle import OssieOracle


def targets(ontology):
    yield ontology
    for concept in ontology["ontology"]:
        yield concept
        yield from concept.get("relationships", ())


def locate(ontology, scope):
    if scope == "ontology":
        return ontology
    kind, _, name = scope.partition(":")
    owner, _, fact = name.partition(".")
    concept = next(row for row in ontology["ontology"] if row["concept"] == owner)
    if kind == "concept":
        return concept
    return next(row for row in concept["relationships"] if row["name"] == fact)


root = Path(__file__).resolve().parent
oracle = OssieOracle(Path(sys.argv[1]).resolve())
oracle.check_pins()
base = json.loads(render_ossie(root / "model.orm.json", output_format="json").document)
for target in targets(base):
    target.pop("requires", None)
    target.pop("derived_by", None)

expected = json.loads((root / "expected.json").read_bytes())
plans = {case["rule"]: case["placements"] for case in expected.values()}
observations = {}
with TemporaryDirectory() as directory:
    path = Path(directory) / "probe.ontology.json"
    for rule, placements in plans.items():
        ontology = deepcopy(base)
        section = "derived_by" if rule.startswith("derivation:") else "requires"
        for placement in placements:
            locate(ontology, placement["scope"]).setdefault(section, []).append(
                placement["formula"]
            )
        path.write_text(json.dumps(ontology))
        run = oracle.parse(path)
        assert run.returncode == 0, run.stdout + run.stderr
        observations[rule] = {"exit": run.returncode, "placements": placements}
    broken = deepcopy(base)
    cases = (
        ("malformed-count", "requires", "COUNT[Account >"),
        ("r1-derivation", "derived_by", "Account.account_classified.category_band(band)"),
    )
    for name, key, expression in cases:
        document = deepcopy(broken)
        scope = "ontology" if key == "requires" else "relationship:Account.account_band"
        locate(document, scope)[key] = [expression]
        path.write_text(json.dumps(document))
        run = oracle.parse(path)
        assert run.returncode == 1 and run.stderr
        diagnostic = run.stderr.strip().splitlines()[-1]
        observations[name] = {"exit": run.returncode, "diagnostic": diagnostic}
print(json.dumps(observations, indent=2))
