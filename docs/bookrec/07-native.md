# 7. Compute recommendations with PyRel and audit them separately

Ada is a minor. A proposer that chooses `night` has produced a business failure,
even if its query ran successfully. This chapter separates native calculation
from the exported policy check that decides whether a candidate can be published.
Continue after chapter 6; the native exercise starts with fresh installed resources.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="BookRec calculation and checking flow">
![BookRec facts feed native queries, then a separate policy audit; advisory warnings publish and strict genre failures withhold output.](../assets/applications/bookrec-flow.svg)
</div>

*Source: shipped baseline/strict models and measured advisory/strict checkpoints.
The same Ada/cosmos candidate warns under `preferred_genre` in advisory mode and
fails under the strict model. Query completion alone cannot publish output.*

On narrow screens, focus a diagram and scroll horizontally with arrow keys or touch.

## Keep the two interpreters explicit

GND runs in your base environment. Native PyRel runs in a separate environment
with PyRel 1.30.1 and DuckDB 1.5.5, following the [pinned runtime setup](../runtimes/pyrel.md).
The tutorial runner sets `GND_TUTORIAL_GND_PYTHON` from `--python`; set
`GND_TUTORIAL_PYREL_PYTHON` to your absolute pinned native interpreter path.
These blocks use only the standard library in that native interpreter and invoke
GND's CLI in the base interpreter. No account or remote database is required.

The default offline run skips native blocks and says so. Run this group with
`--lane pyrel --receipt bookrec-steps.json` to execute both paths. The receipt
records elapsed command execution, including deliberate failures, rather than
human model design, application authoring, runtime installation or review time.
The earlier chapters demonstrate scaffold generation and safe rule evolution;
this chapter reuses their models with a supplied native query extension.

For individual copy-and-run blocks, set both interpreter variables yourself:

```sh
export GND_TUTORIAL_GND_PYTHON=/absolute/base/bin/python
export GND_TUTORIAL_PYREL_PYTHON=/absolute/pinned/native/bin/python
```

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from pathlib import Path
import shutil
source = files("gnd").joinpath("examples", "bookrec")
shutil.copytree(str(source), "bookrec-native")
assert Path("bookrec-native/extension/bookrec/native_query.py").is_file()
```

## Advisory, strict, repair and completeness

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="BookRec reader, book and genre eligibility">
![Eligibility arrows show Ada to map/river and Ben to map/night/river. Ada/night violates age_appropriate; Ada/read and Ben/read violate unread_only. Cosmos is legal in baseline but outside the preferred complete set.](../assets/applications/bookrec-eligibility.svg)
</div>

*Source: complete-mode checkpoint's five eligible pairs and blocked/read pairs.
Arrows show the preferred complete set. The exclusion labels name the
rules checked when a bad proposer inserts those pairs.*

<!-- gnd-run expect=0 lane=pyrel -->
```python
import hashlib, json, os, subprocess, sys
from pathlib import Path
base = os.environ["GND_TUTORIAL_GND_PYTHON"]
native = os.environ["GND_TUTORIAL_PYREL_PYTHON"]
home = Path("bookrec-native").resolve()
source = home / "seed.population.json"
before = hashlib.sha256(source.read_bytes()).hexdigest()
for name, model, command, extra, expected in [
    ("advisory", "model.orm.yaml", "recommend", [], 0),
    ("strict", "strict.orm.yaml", "recommend", [], 1),
    ("preferred", "strict.orm.yaml", "recommend", ["--preferred-only"], 0),
    ("complete", "complete.orm.yaml", "complete", [], 0),
]:
    output = home / (name + ".json")
    argv = [base, "-m", "bookrec.cli", command, "--model", str(home/model),
            "--input", str(source), "--output", str(output), "--backend", "pyrel",
            "--pyrel-python", native, "--user", "ada", "--limit", "2", *extra]
    run = subprocess.run(argv, cwd=home/"extension", capture_output=True, text=True, timeout=150)
    assert run.returncode == expected, run.stdout + run.stderr
    result = json.loads(run.stdout)
    (home/(name+".report.json")).write_text(json.dumps(result, indent=2))
    assert result["accepted"] == (expected == 0)
    assert output.exists() == (expected == 0)
    genre = next(r for r in result["policy"]["verdicts"] if r["id"] == "preferred_genre")
    if name in {"advisory", "strict"}:
        assert result["calculation"]["selected_pairs"] == [{"user":"ada","book":"cosmos"}, {"user":"ada","book":"map"}]
        if name == "advisory":
            assert {(r["user"],r["book"]) for r in json.loads(output.read_text())["facts"]["recommendation"]} == {("ada","cosmos"),("ada","map"),("ben","night")}
        assert genre["status"] == ("warning" if name == "advisory" else "violated")
        assert genre["witnesses"] == [{"$u":"ada", "$b":"cosmos", "$g":"science"}]
    if name == "preferred":
        assert result["calculation"]["selected_pairs"] == [{"user":"ada","book":"map"}, {"user":"ada","book":"river"}]
    if name == "complete":
        pairs = result["calculation"]["eligible_pairs"]
        assert {(r["user"],r["book"]) for r in pairs} == {("ada","map"),("ada","river"),("ben","map"),("ben","night"),("ben","river")}
    print(name, result["policy"]["status"], "published", result["published"])
assert hashlib.sha256(source.read_bytes()).hexdigest() == before
```

| Checkpoint | Ada proposal | Expected policy | Output |
|---|---|---|---|
| Advisory | cosmos, map | accepted with genre warning | Published |
| Strict, same proposal | cosmos, map | preferred_genre violated | Absent |
| Strict repair | map, river | accepted | Published |
| Complete | all five preferred eligible pairs | accepted | Published |

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="BookRec advisory, strict and complete rules">
![The same cosmos/map candidate warns with advisory genre fit and fails with strict fit; preferred-only repairs Ada to map/river. Complete mode requires all five eligible pairs.](../assets/applications/bookrec-evolution.svg)
</div>

*Source: advisory, strict, preferred and complete native checkpoint reports.
Legal recommendations and the complete eligible set answer different questions;
`all_eligible` checks omissions under the complete model.*

## Make checking catch what filtering cannot

Deliberately add Ada/read after a successful proposal, then run the standalone
export with `--accept`. This bypasses proposer filtering so the audit must catch
the violation. The bad file is an exercise input, never an application publication.

<!-- gnd-run expect=0 lane=pyrel -->
```python
import json, os, subprocess
from pathlib import Path
home = Path("bookrec-native").resolve()
base, native = os.environ["GND_TUTORIAL_GND_PYTHON"], os.environ["GND_TUTORIAL_PYREL_PYTHON"]
candidate = json.loads((home/"preferred.json").read_text())
candidate["facts"]["recommendation"].append({"user":"ada", "book":"read"})
(home/"bad.json").write_text(json.dumps(candidate))
export = subprocess.run([base,"-m","gnd","export","pyrel",str(home/"strict.orm.yaml"),"--out",str(home/"checker.py")],capture_output=True,text=True,timeout=30)
assert export.returncode == 0, export.stderr
bad = subprocess.run([native,"-I",str(home/"checker.py"),str(home/"bad.json"),"--out",str(home/"bad.report.json"),"--accept"],cwd=home,capture_output=True,text=True,timeout=90)
assert bad.returncode == 1, bad.stdout + bad.stderr
report = json.loads((home/"bad.report.json").read_text())
rule = next(r for r in report["verdicts"] if r["id"] == "unread_only")
assert rule["status"] == "violated" and rule["witnesses"] == [{"$u":"ada","$b":"read"}]
repair = subprocess.run([native,"-I",str(home/"checker.py"),str(home/"preferred.json"),"--out",str(home/"repaired.report.json"),"--accept"],cwd=home,capture_output=True,text=True,timeout=90)
assert repair.returncode == 0, repair.stderr
print("Inserted already-read recommendation rejected; original repair accepted.")
```

## Read the extension and troubleshoot

Open the copied `extension/bookrec/native_query.py` and `cli.py`. Native joins and
negation calculate candidates; Python deduplicates, orders, selects the user and
limits presentation. The shared GND parent captures source bytes, preserves
nonowned facts, runs a fresh exported checker and publishes only accepted bytes.
Model constraints live in the model; query logic remains developer-owned.

A missing/wrong PyRel interpreter fails preflight; install the pinned runtime and
pass its absolute path. Missing `covers_fact_types` is unknown coverage, including
empty asserted relations; retain that metadata rather than inventing observations.
Exit 2 means incomplete/unsupported evidence, exit 3 malformed input and exit 70
operational failure. None publishes. An SDK exit 0 is not acceptance without the
full policy report. The tiny alphabetic recommender demonstrates integration,
not ranking quality, production storage or actor permission.

??? note "Read the shipped native query source"

    ```python
    --8<-- "docs/assets/applications/bookrec-native-query.txt"
    ```
