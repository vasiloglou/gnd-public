# 6. Change the rule, then ask for complete results

Suppose the product owner changes the requirement: every recommendation **must**
match a preferred genre. Your existing `cosmos` recommendation should now fail
even though its bytes have not changed. GND's evolution workflow makes that rule
change explicit and records which model was published.

Continue from [chapter 5](05-repair.md). This chapter has two parts: a real
modify-only evolution, then a separately supplied model checkpoint that teaches
derived eligibility and completeness.

## Preview the prepared change

`genre-proposal.json` binds the exact old model and contains the complete new
model, one constraint modification, a rationale and audit metadata. Unchanged
constraints retain their original provenance. This teaching proposal changes
only the genre rule from advisory to hard; it does not add the later derivations.

Save the recommendation and extension bytes for comparisons. Then preview the
proposal without changing the model.

<!-- gnd-run expect=0 -->
```python
from pathlib import Path
import shutil

shutil.copy2("bookrec-demo/model.orm.yaml", "bookrec-demo/before.orm.yaml")
shutil.copy2("bookrec-project/recommendations.json", "bookrec-demo/frozen-output.json")
shutil.copy2("bookrec-project/bookrec/cli.py", "bookrec-demo/cli.backup")
assert Path("bookrec-demo/genre-proposal.json").is_file()
```

<!-- gnd-run expect=0 -->
```sh
gnd evolve preview bookrec-demo/model.orm.yaml bookrec-demo/genre-proposal.json --workspace bookrec-demo --records bookrec-demo/records --out bookrec-demo/preview.json --format json
```

Inspect `bookrec-demo/preview.json`. Its candidate verbalization should say the
genre rule is alethic, and its blast-radius entries describe the affected model
surfaces. The proposal is modify-only, so the tool does not request a rename or
delete acceptance token. That does not replace your review of the intended rule.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path

preview = json.loads(Path("bookrec-demo/preview.json").read_text())
assert preview["breaking"] is False
assert preview["blast_radius"]["entries"]
assert Path("bookrec-demo/model.orm.yaml").read_bytes() == Path("bookrec-demo/before.orm.yaml").read_bytes()
print("Preview left the model unchanged; inspect its blast radius before applying.")
```

The next block performs the explicit tutorial change and retains stdout,
stderr, the exact argv and exit code. The proposal declares no linked projects;
its transaction covers the model in `bookrec-demo`. We inspect the generated
project separately immediately afterward. In a real project, declare selected
linked projects and their tracked rosters when authoring the proposal.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
import subprocess

argv = ["gnd", "evolve", "apply", "bookrec-demo/model.orm.yaml",
        "bookrec-demo/genre-proposal.json", "--preview", "bookrec-demo/preview.json",
        "--workspace", "bookrec-demo", "--records", "bookrec-demo/records", "--format", "json"]
run = subprocess.run(argv, capture_output=True, text=True, timeout=60)
Path("bookrec-demo/apply.stdout.txt").write_text(run.stdout)
Path("bookrec-demo/apply.stderr.txt").write_text(run.stderr)
Path("bookrec-demo/apply.exit.json").write_text(json.dumps({"argv": argv, "exit_code": run.returncode}, indent=2))
assert run.returncode == 0, run.stderr
record = json.loads(Path("bookrec-demo/records/prefer-genre/record.json").read_text())
assert record["cas"]["published"] is True
assert Path("bookrec-demo/model.orm.yaml").read_bytes() == Path("bookrec-demo/strict.orm.yaml").read_bytes()
print("Published strict genre policy; retained the immutable evolution record.")
```

## Check the same output against both policies

<!-- gnd-run expect=1 -->
```sh
gnd check bookrec-demo/model.orm.yaml bookrec-demo/frozen-output.json --format json --unredacted
```

<!-- gnd-run expect=0 -->
```python
from pathlib import Path
from gnd import api

population = "bookrec-demo/frozen-output.json"
before = api.check("bookrec-demo/before.orm.yaml", population)
after = api.check("bookrec-demo/model.orm.yaml", population)
assert before["exit_code"] == 0 and before["counts"]["warning"] == 1
assert after["exit_code"] == 1 and after["counts"]["fail"] == 1
assert Path(population).read_bytes() == Path("bookrec-project/recommendations.json").read_bytes()
print("Same output: accepted with a warning before, rejected after the rule change.")
```

No recommendation was silently repaired. The same model identifier permits a
comparison while the report's model digest identifies the selected rule bytes.

## Refresh the generated project deliberately

Copy the evolved model into the project. Its existing generated artifacts are
now stale; a conformance check reports that before you explicitly regenerate.

<!-- gnd-run expect=0 -->
```python
import shutil
shutil.copy2("bookrec-demo/model.orm.yaml", "bookrec-project/model.orm.yaml")
```

<!-- gnd-run expect=13 -->
```sh
gnd conformance bookrec-project/model.orm.yaml bookrec-project --format json
```

<!-- gnd-run expect=0 -->
```sh
gnd codegen bookrec-project/model.orm.yaml --out bookrec-project
```

<!-- gnd-run expect=0 -->
```sh
gnd conformance bookrec-project/model.orm.yaml bookrec-project --format json
```

<!-- gnd-run expect=0 -->
```python
from pathlib import Path
assert Path("bookrec-project/bookrec/cli.py").read_bytes() == Path("bookrec-demo/cli.backup").read_bytes()
print("Derived artifacts refreshed; authored CLI preserved.")
```

A proposal that declares linked projects can publish the model and then return
13 because one of those projects drifted. Always read the publication record;
a nonzero conformance result is not evidence that the model change rolled back.

The old algorithm still proposes a science book first. Under the strict model,
checked publication refuses it. Then explicitly enable the preferred-genre
selection already present in the authored checkpoint.

<!-- gnd-run expect=1 -->
```sh
(cd bookrec-project && python -m bookrec.cli recommend --model model.orm.yaml --input seed.population.json --output strict-rejected.json --user ada --limit 2)
```

<!-- gnd-run expect=0 -->
```sh
(cd bookrec-project && python -m bookrec.cli recommend --model model.orm.yaml --input seed.population.json --output strict-accepted.json --user ada --limit 2 --preferred-only)
```

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path

assert not Path("bookrec-project/strict-rejected.json").exists()
output = json.loads(Path("bookrec-project/strict-accepted.json").read_text())
assert [r["book"] for r in output["facts"]["recommendation"] if r["user"] == "ada"] == ["map", "river"]
```

The project's developer-owned architecture contract still declares a successful
example using the old selection policy. Update that example to use the same
preferred-genre option; regeneration preserves this file and cannot decide its
new behavior for you. Keep the unknown-user refusal unchanged.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path

path = Path("bookrec-project/architecture.contract.yaml")
contract = json.loads(path.read_text())  # This supplied YAML checkpoint uses JSON syntax.
success = next(row for row in contract["smoke"] if row["id"] == "recommend-known-user")
assert success["expect_exit"] == 0
success["argv"].append("--preferred-only")
path.write_text(json.dumps(contract, indent=2) + "\n")
```

Static conformance does not run the project's declared smoke examples. Execute
them against the evolved model as well. This uses the same versioned testing
support as the generated pytest module, without requiring pytest; it is separate
from the seven stable application API functions.

<!-- gnd-run expect=0 -->
```python
from pathlib import Path
import tempfile
from gnd.archsmoke import run_row, smoke_rows

project = Path("bookrec-project").resolve()
rows = smoke_rows(project)
assert rows
for row in rows:
    with tempfile.TemporaryDirectory() as scratch:
        outcome = run_row(row, project_root=project, tmp=Path(scratch), timeout=30)
        assert outcome.passed, outcome.message
        print(outcome.message)
```

Recheck static conformance after changing the authored contract:

<!-- gnd-run expect=0 -->
```sh
gnd conformance bookrec-project/model.orm.yaml bookrec-project --format json
```

## Derive eligibility and require every eligible pair

The separate `complete.orm.yaml` checkpoint adds two derived relationships and
one completeness rule:

- `book_is_blocked_for(book, user)` joins an adult-rated book with a minor reader.
- `book_is_eligible(book, user)` joins book genre and user preference, excluding
  blocked and already-rated pairs.
- `all_eligible` requires a recommendation for every eligible user/book pair.

This is model format version 2 because it uses structured derivations. It is a
new supplied checkpoint, not an unrecorded modification of the just-evolved
project. The application can check output under it by selecting that model
explicitly. The library proposes derived claims; GND computes their expected
extensions independently and compares them before accepting the whole output.

<!-- gnd-run expect=0 -->
```sh
gnd validate bookrec-demo/complete.orm.yaml --format json
```

<!-- gnd-run expect=0 -->
```sh
(cd bookrec-project && python -m bookrec.cli complete --model ../bookrec-demo/complete.orm.yaml --input seed.population.json --output complete.json)
```

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
from gnd import api

output = json.loads(Path("bookrec-project/complete.json").read_text())
facts = output["facts"]
expected = {("ada", "map"), ("ada", "river"), ("ben", "map"), ("ben", "night"), ("ben", "river")}
assert {(r["user"], r["book"]) for r in facts["recommendation"]} == expected
assert {(r["user"], r["book"]) for r in facts["book_is_eligible"]} == expected
assert facts["book_is_blocked_for"] == [{"book": "night", "user": "ada"}]
assert output == json.loads(Path("bookrec-demo/complete.population.json").read_text())
report = api.check("bookrec-demo/complete.orm.yaml", "bookrec-project/complete.json")
assert report["exit_code"] == 0 and report["counts"]["pass"] == 8
print("Five eligible pairs, five recommendations, two checked derivations.")
```

## Distinguish an omitted recommendation from an incorrect derivation

An output can contain only legal recommendations and still omit a required
one. Delete Ada's `river` recommendation while retaining the correct eligible
set. The completeness constraint catches that omission.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path

output = json.loads(Path("bookrec-project/complete.json").read_text())
output["facts"]["recommendation"].remove({"user": "ada", "book": "river"})
Path("bookrec-demo/missing-recommendation.json").write_text(json.dumps(output, indent=2))
```

<!-- gnd-run expect=1 -->
```sh
gnd check bookrec-demo/complete.orm.yaml bookrec-demo/missing-recommendation.json --format json --unredacted
```

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
from gnd import api

report = api.check("bookrec-demo/complete.orm.yaml",
                   "bookrec-demo/missing-recommendation.json", unredacted=True)
assert report["exit_code"] == 1 and report["counts"]["fail"] == 1
failed = [r for r in report["verdicts"] if r["verdict"] == "fail"]
assert failed[0]["constraint_ref"] == "constraints[3]"
output = json.loads(Path("bookrec-project/complete.json").read_text())
output["facts"]["book_is_eligible"].remove({"book": "river", "user": "ada"})
Path("bookrec-demo/missing-derived-claim.json").write_text(json.dumps(output, indent=2))
derivation_report = api.check("bookrec-demo/complete.orm.yaml",
                              "bookrec-demo/missing-derived-claim.json", unredacted=True)
assert derivation_report["exit_code"] == 1
assert any(finding["kind"] == "derived-extension-incomplete"
           for row in derivation_report["derivations"] for finding in row["findings"])
print("Missing recommendation and missing derived claim are separate failures.")
```

For your own rule change, explicitly select `gnd-model-evolve`:

> Preview the change from advisory genre fit to a hard requirement. Preserve
> all unchanged constraint provenance and declare the selected linked project.
> Show the full blast radius before applying. Report model publication and
> project conformance separately. Wait for my separate selection before
> regenerating code or repairing the application.

**Exercise:** Add an unsupported eligible claim for Ada/`night` in a scratch
copy. Predict a derived-extension failure even if you also add a recommendation:
the recommendation additionally violates the age rule. Passing a completeness
rule cannot make an unsupported derived claim true.

You have now built a checked application, repaired facts, observed file drift,
published an explicit rule change, and checked complete derived output. Continue
with [expense approvals](../expense/01-model.md), explore the
[capability map](../reference/capabilities.md), or read the
[agent skill handoffs](../agents/index.md).

[Next: native queries and independent audit](07-native.md).
