# PyRel: audit release approvals and write relational queries

Use this when you want a relational report explaining incomplete or conflicting
business facts. Continue from [the shared setup](scenario.md). The result is a
local approval audit and a developer-owned reporting program, not a deployment.

## Export a standalone policy audit

<!-- gnd-run expect=0 -->
```sh
gnd export pyrel release-governance/policy/model.orm.json --out release-policy.py
```

The export embeds the model and translation runtime. It imports no GND module at
execution time. Open `release-policy.py` to inspect its PEP 723 dependency header
and its supported constraint translation. Export alone requires no PyRel runtime.
The following two commands need the isolated **PyRel 1.30.1** interpreter:

<!-- gnd-run expect=0 lane=pyrel -->
```sh
"${GND_TUTORIAL_PYREL_PYTHON:?set the isolated interpreter}" release-policy.py release-governance/policy/invalid.pop.json --out invalid-audit.json
"${GND_TUTORIAL_PYREL_PYTHON:?set the isolated interpreter}" release-policy.py release-governance/policy/repaired.pop.json --out repaired-audit.json
```

Both commands return **zero**, even though the first report contains violations.
Zero means the report completed. The first snapshot has three violated constraints:
missing REL-103 approval, two REL-104 approvals, and unauthorized Alice/Zoe values.
The repaired snapshot has three satisfied constraints.

<!-- gnd-run expect=0 lane=pyrel -->
```python
import json
from pathlib import Path

bad = json.loads(Path("invalid-audit.json").read_text())
good = json.loads(Path("repaired-audit.json").read_text())
assert bad["backend"] == "duckdb-local" and bad["package"]["version"] == "1.30.1"
assert [r["status"] for r in bad["verdicts"]] == ["violated"] * 3
assert [r["witnesses"] for r in bad["verdicts"]] == [[["REL-103"]], [["REL-104"]], [["Alice"], ["Zoe"]]]
assert [r["status"] for r in good["verdicts"]] == ["satisfied"] * 3
print("Report completion is separate from policy satisfaction; all witnesses match.")
```

| Rule | Witness | Repair |
|---|---|---|
| Mandatory release coverage | REL-103 | Add Maya's approval |
| Unique release approval | REL-104 | Retain Maya and remove Noah's conflicting approval |
| Authorized reviewer subset | Alice, Zoe | Use Noah for REL-101 and REL-105 |

This model's subset rule catches Alice because she is unauthorized. It does not
encode the distinct-requester policy: an authorized requester could still approve
their own release. The next native query checks that separate business question.

## Build your own report with public PyRel APIs

`pyrel_queries.py` declares four relationships, defines supplied rows, joins the
request/approval/owner facts, uses `not_` for unauthorized reviewers, and groups
reviewer workload using **`count(release).per(reviewer)`**. Omitting `.per` computes
a global count and repeats it beside reviewers; a plausible table can be wrong.

```python
--8<-- "src/gnd/examples/release_governance/pyrel_queries.py"
```

`String.ref()` creates query variables; shared variables join rows. Python
`and`/`not` do not express PyRel logic: pass expressions to `where` and use `not_`.
`to_df()` executes the selected relation on local DuckDB. The program explicitly
supplies its local configuration, so it does not discover a remote connection.

<!-- gnd-run expect=0 lane=pyrel -->
```sh
"${GND_TUTORIAL_PYREL_PYTHON:?set the isolated interpreter}" release-governance/pyrel_queries.py release-governance/scenario-invalid.json --out native-invalid.json
"${GND_TUTORIAL_PYREL_PYTHON:?set the isolated interpreter}" release-governance/pyrel_queries.py release-governance/scenario-repaired.json --out native-repaired.json
```

<!-- gnd-run expect=0 lane=pyrel -->
```python
import json
from pathlib import Path

bad = json.loads(Path("native-invalid.json").read_text())
good = json.loads(Path("native-repaired.json").read_text())
assert bad["self_approval"] == [["REL-101", "Alice"]]
assert bad["conflicting_releases"] == [["REL-104"]]
assert bad["unauthorized"] == [["REL-101", "Alice"], ["REL-105", "Zoe"]]
assert bad["reviewer_workload"] == [["Alice", 1], ["Maya", 2], ["Noah", 1], ["Zoe", 1]]
assert len(bad["joined_approvals"]) == 5
assert all(not good[k] for k in ("self_approval", "conflicting_releases", "unauthorized"))
assert good["reviewer_workload"] == [["Maya", 3], ["Noah", 2]]
assert good["joined_approvals"][0] == ["REL-101", "checkout", "Alice", "Noah", "Alice"]
print("Native joins explain self-approval and conflicts; repaired workload is Maya 3 / Noah 2.")
```

The missing approval does not appear in an inner join. This is why the generated
mandatory audit and the native reporting query answer complementary questions.
Neither report substitutes for the other. Reviewer counts are distinct release
counts, not an occurrence audit of duplicate identical input rows.

Now isolate self-approval from authorization: add Ben to the allowlist and let
Ben approve REL-102. The exported rules still pass; the separate native question
must detect self-approval. This prevents a successful subset check from being
mistaken for a complete business policy.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
root = Path("release-governance")
scenario = json.loads((root / "scenario-repaired.json").read_text())
scenario["authorized_reviewers"].append("Ben")
scenario["approvals"][1] = ["REL-102", "Ben"]
Path("authorized-self.json").write_text(json.dumps(scenario))
population = json.loads((root / "policy/repaired.pop.json").read_text())
population["facts"]["authorized"].append({"reviewer": "Ben"})
population["facts"]["approval"][1]["reviewer"] = "Ben"
Path("authorized-self.pop.json").write_text(json.dumps(population))
```

<!-- gnd-run expect=0 -->
```sh
gnd check release-governance/policy/model.orm.json authorized-self.pop.json --format json
```

<!-- gnd-run expect=0 lane=pyrel -->
```sh
"${GND_TUTORIAL_PYREL_PYTHON:?set the isolated interpreter}" release-policy.py authorized-self.pop.json --out authorized-self-audit.json
"${GND_TUTORIAL_PYREL_PYTHON:?set the isolated interpreter}" release-governance/pyrel_queries.py authorized-self.json --out authorized-self-native.json
```

<!-- gnd-run expect=0 lane=pyrel -->
```python
import json
from pathlib import Path
audit = json.loads(Path("authorized-self-audit.json").read_text())
native = json.loads(Path("authorized-self-native.json").read_text())
assert [r["status"] for r in audit["verdicts"]] == ["satisfied"] * 3
assert native["self_approval"] == [["REL-102", "Ben"]]
assert native["unauthorized"] == []
print("Authorization passes; the separate self-approval finding remains.")
```

## Recognize unsupported execution

<!-- gnd-run expect=0 lane=pyrel -->
```sh
"${GND_TUTORIAL_PYREL_PYTHON:?set the isolated interpreter}" release-policy.py release-governance/policy/repaired.pop.json --mode require --out reserved-require.json
```

<!-- gnd-run expect=0 lane=pyrel -->
```python
import json
from pathlib import Path
rows = json.loads(Path("reserved-require.json").read_text())["verdicts"]
assert len(rows) == 3
assert all(r["status"] == "unsupported" and r["reason"] == "require-mode-needs-lqp-runtime" for r in rows)
print("Require mode is reserved; it did not check the policy.")
```

`require` is not an available enforcement backend here. Named remote connection
execution is also unavailable through this GND exporter. Unsupported results must
not become satisfied or violated verdicts. Temporal models are refused at export.
This tutorial teaches the supported local exporter and separate native code, not
Snowflake deployment or every PyRel capability.

## Read checkpoints and try an exercise

If you skipped native steps, inspect `checkpoints/pyrel-*.json` and their
[recorded provenance](decision.md). They are supplied results, not a local run.

Exercise: change Maya's REL-102 approval to Ben. Predict both unauthorized and
self-approval findings. Run the native program against a new snapshot and a new
output path. Then repair it; do not edit the generated export to suppress a rule.

> Use `gnd-export` to export the supplied non-temporal policy model. Stop after
> inspecting the generated program. I explicitly hand off native reporting to
> application development: implement the supplied joins using public PyRel APIs,
> keep its findings separate from GND verdicts, and check the expected workload.

Continue with [dependency analysis in Soufflé](souffle.md). For broader native
modeling and query APIs, see the [official PyRel guide](https://docs.relational.ai/get-started/start-building-with-pyrel).
