# Soufflé: investigate dependency impact

Use this when a dependency several hops away can affect a release. Continue from
[the shared setup](scenario.md). You will compute all supported graph results,
explain one dependency path, and write a reusable native Datalog component.

## Understand the rules before exporting

The dependency view derives `reachable` recursively, joins reachable components
with the vulnerability catalogue to derive `exposure`, projects `affected`, and
uses stratified negation for `unaffected`. It counts **distinct vulnerable
components**, not the number of routes to them. `blocked` joins affected services
to requested releases. This is impact analysis; it does not run approval checks.

| Service | Vulnerable dependencies | Distinct count |
|---|---|---|
| checkout | serialization, ledger-db | 2 |
| payments | serialization, ledger-db | 2 |
| identity | serialization | 1 |
| ledger | ledger-db | 1 |
| inventory, reporting | none | no count row; both appear in `unaffected` |

Multiple paths from checkout to serialization still contribute one component.
The exporter does not invent a zero-count group from empty exposure facts.

<!-- gnd-run expect=0 -->
```sh
for variant in repaired patched cycle; do
  gnd export souffle release-governance/dependencies/model.orm.json "release-governance/dependencies/$variant.base.pop.json" --raw --out "souffle-$variant" --json
  gnd export souffle-verify "souffle-$variant" --json
done
```

Each bundle contains `program.dl`, fixed fact files, symbol/origin maps, a closed
manifest and source copies. Generated ordinal names avoid putting user values
into program identifiers. Raw source values are present here because the example
uses public synthetic inputs and explicitly selects `--raw`.

The checked result snapshot cannot substitute for base-only export input:

<!-- gnd-run expect=2 -->
```sh
gnd export souffle release-governance/dependencies/model.orm.json release-governance/dependencies/repaired.pop.json --raw --out asserted-answers-bundle --json
```

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
from gnd.api import check
root = Path("release-governance/dependencies")
expected = json.loads((root / "expected.json").read_text())
assert expected["repaired"]["vulnerability_count"] == [["checkout", 2], ["identity", 1], ["ledger", 1], ["payments", 2]]
assert expected["repaired"]["blocked"] == [["REL-101", "checkout"], ["REL-104", "payments"], ["REL-105", "ledger"]]
for variant in ("repaired", "patched", "cycle"):
    result = check(root / "model.orm.json", root / f"{variant}.pop.json")
    assert result["exit_code"] == 0 and result["counts"]["pass"] == 6
print("GND independently checks all six derived result relations in each checkpoint.")
```

## Detect a changed bundle

<!-- gnd-run expect=0 -->
```python
from pathlib import Path
import shutil
shutil.copytree("souffle-repaired", "souffle-altered")
program = Path("souffle-altered/program.dl")
program.write_text(program.read_text() + "\n// unexpected edit\n")
```

<!-- gnd-run expect=3 -->
```sh
gnd export souffle-verify souffle-altered --json
```

Verification rejects changed bytes. Keep a developer-owned extension in another
file; never patch a verified bundle and retain its original identity.

## Execute the real tool and compare exact results

The following commands require **Soufflé 2.5, 64-bit POSIX**:

<!-- gnd-run expect=0 lane=souffle -->
```sh
for variant in repaired patched cycle; do
  gnd export souffle-run "souffle-$variant" --executable "${GND_TUTORIAL_SOUFFLE:-souffle}" --raw --json > "gnd-$variant.json"
done
```

<!-- gnd-run expect=0 lane=souffle -->
```python
import json
from pathlib import Path
expected = json.loads(Path("release-governance/dependencies/expected.json").read_text())
for variant in ("repaired", "patched", "cycle"):
    result = json.loads(Path(f"gnd-{variant}.json").read_text())
    assert result["exit_code"] == 0 and result["tool"]["version"] == "2.5"
    assert result["tool"]["word_size"] == 64
    actual = {name: sorted([[cell["value"] for cell in row] for row in rows]) for name, rows in result["extensions"].items()}
    assert actual == {name: sorted(rows) for name, rows in expected[variant].items()}
assert expected["patched"]["blocked"] == []
assert expected["patched"]["vulnerability_count"] == []
assert ["ledger", "ledger"] in expected["cycle"]["reachable"]
print("Native results match every typed extension; patching removes exposure, cycles terminate.")
```

The cycle checkpoint adds ledger → payments plus a duplicate checkout → payments
edge. Reachability gains payments/ledger self-reachability. Datalog's set semantics
deduplicate the repeated edge; finite positive closure terminates. The unaffected
reporting component remains disconnected. These assertions check semantics, not
large-scale performance or a production vulnerability scanner.

## Explain one positive dependency and replay it

<!-- gnd-run expect=0 lane=souffle -->
```sh
gnd export souffle-witness souffle-repaired --targets release-governance/dependencies/reach.targets.json --executable "${GND_TUTORIAL_SOUFFLE:-souffle}" --raw --out reach-certificate.json --json > reach-result.json
gnd replay release-governance/dependencies/model.orm.json release-governance/dependencies/repaired.base.pop.json reach-certificate.json --json > replay-result.json
```

<!-- gnd-run expect=0 lane=souffle -->
```python
import json
from pathlib import Path
witness = json.loads(Path("reach-result.json").read_text())
replay = json.loads(Path("replay-result.json").read_text())
assert witness["exit_code"] == replay["exit_code"] == 0
assert witness["results"][0]["status"] == "proved"
certificate = json.loads(Path("reach-certificate.json").read_text())
base = {tuple(c["value"] for c in n["tuple"]) for n in certificate["nodes"] if n["kind"] == "base"}
assert base == {("checkout", "payments"), ("payments", "ledger"), ("ledger", "ledger-db")}
print("Explained checkout → payments → ledger → ledger-db; independent replay passed.")
```

A finite positive proof of one dependency does not prove the absence of another,
the completeness of all returned rows, or the truth of the supplied catalogue.
The following proof requests are deliberately refused:

<!-- gnd-run expect=2 lane=souffle -->
```sh
gnd export souffle-witness souffle-repaired --targets release-governance/dependencies/unaffected.targets.json --executable "${GND_TUTORIAL_SOUFFLE:-souffle}" --json
```

<!-- gnd-run expect=2 lane=souffle -->
```sh
gnd export souffle-witness souffle-repaired --targets release-governance/dependencies/vulnerability_count.targets.json --executable "${GND_TUTORIAL_SOUFFLE:-souffle}" --json
```

The witness profile excludes negation and aggregates. Exit 2 here means unsupported
proof, even though native evaluation successfully produced those result rows.

## Write readable Datalog outside the bundle

The supplied native program defines a `DependencyAnalysis` component and
instantiates it as `impact`. Component names scope both its relations and files.
This version uses readable values and numeric counts directly; it is authored
native code, not a modified GND export.

```datalog
--8<-- "src/gnd/examples/release_governance/dependency_analysis.dl"
```

<!-- gnd-run expect=0 lane=souffle -->
```sh
for variant in repaired patched cycle; do
  python release-governance/prepare_facts.py "release-governance/scenario-$variant.json" "native-facts-$variant"
  mkdir "native-output-$variant"
  "${GND_TUTORIAL_SOUFFLE:-souffle}" --no-preprocessor -F "native-facts-$variant" -D "native-output-$variant" release-governance/dependency_analysis.dl
done
```

<!-- gnd-run expect=0 lane=souffle -->
```python
import csv, json
from pathlib import Path
expected = json.loads(Path("release-governance/dependencies/expected.json").read_text())
names = {"Reachable": "reachable", "Exposure": "exposure", "Affected": "affected", "Unaffected": "unaffected", "VulnerabilityCount": "vulnerability_count", "Blocked": "blocked"}
for variant in ("repaired", "patched", "cycle"):
    actual = {}
    for native, semantic in names.items():
        with Path(f"native-output-{variant}/impact.{native}.csv").open() as handle:
            rows = list(csv.reader(handle, delimiter="\t"))
        if semantic == "vulnerability_count":
            rows = [[s, int(n)] for s, n in rows]
        actual[semantic] = sorted(rows)
    assert actual == {name: sorted(rows) for name, rows in expected[variant].items()}
print("The reusable developer-owned component matches all three scenario checkpoints.")
```

## Exercise and explicit handoff

Exercise: remove payments → ledger in a new snapshot. Predict which releases
retain a serialization exposure and which lose ledger-db exposure, then run the
native component against newly prepared facts. Never overwrite the old bundles.

> Use `gnd-export` to render and verify the dependency view. I explicitly select
> native Soufflé execution and one positive witness, followed by separate replay.
> Then hand off application development to extend the separate Datalog component;
> do not claim that native output is an approval verdict or certification.

If you cannot provision Soufflé, inspect the supplied checkpoints and source maps;
that is a reading path, not executed native validation. See the
[official tutorial](https://souffle-lang.github.io/tutorial),
[components](https://souffle-lang.github.io/components), and
[provenance guide](https://souffle-lang.github.io/provenance).
Continue with [finite policy proofs in Lean](lean.md).
