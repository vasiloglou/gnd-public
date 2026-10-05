# Use GND from Python

Use `gnd.api` when your application already has a model and needs to validate
inputs, check candidate facts, explain them, or audit a state change. The API
returns ordinary dictionaries; your application decides how to display a
finding and what action to take.

The seven supported functions are `validate`, `check`, `transition`,
`verbalize`, `diff`, `witness`, and `replay`. Code generation, experiment
orchestration, and model evolution have CLI and skill workflows described in
the [task guides](../advanced.md).

## Set up the examples

Install GND using the [quickstart](../quickstart.md), then run these blocks in
order from a fresh directory. Every block starts a new Python process; the
files on disk carry the examples forward. The data is synthetic and all seven
examples run locally without an API key or native compiler.

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from pathlib import Path
from shutil import copytree

copytree(str(files("gnd") / "examples" / "dispatch"), "api-dispatch")
assert Path("api-dispatch/model.orm.json").is_file()
```

## `validate`: check the model before using it

<!-- gnd-run expect=0 -->
```python
from gnd import api

result = api.validate("api-dispatch/model.orm.json")
assert result["exit_code"] == 0, result
print("The model is structurally and semantically valid.")
```

`validate(model, *, unredacted=False, references=None)` accepts a string,
`Path`, or loaded `Model`. It checks the model's shape and semantic rules and
binds declared fixed references. It returns a report dictionary with
`exit_code`, issues/warnings as applicable, and versioned report metadata.
Success means the declaration is valid; it does not check a population or
establish that the domain rules are complete.

## `check`: inspect a failure and its repair

<!-- gnd-run expect=0 -->
```python
from gnd import api

model = "api-dispatch/model.orm.json"
failed = api.check(model, "api-dispatch/seed.pop.json", admission=True)
assert failed["exit_code"] == 1, failed
findings = [v for v in failed["report"]["verdicts"] if v["verdict"] == "fail"]
assert len(findings) == 1
assert findings[0]["constraint_ref"] == "constraints[1]"
print(findings[0]["message"])

repaired = api.check(model, "api-dispatch/repaired.pop.json", admission=True)
assert repaired["exit_code"] == 0, repaired
print("The repaired shipping facts satisfy the checked rules.")
```

`check(model, population, *, unredacted=False, anchors=None, document=None,
population_bytes=None, admission=False, references=None)` accepts paths or
loaded `Model`/`Population` objects. It returns the same payload as the CLI's
JSON check. The admission option also reports which asserted fact occurrences
are admitted or blocked; it does not edit or remove any facts.

For snapshot checking, band `0` means pass, `1` an alethic failure, `2` a
vacuous result, `3` invalid input, and `4` indeterminate. A deontic violation is
reported as a warning. Read the actual verdicts even when the band is zero.
Precedence when several conditions occur is `3 > 1 > 4 > 2 > 0`.

Anchors connect values to source document spans. Supply `anchors` and
`document` together; if using an in-memory population, supply its original
`population_bytes` so the source binding can be checked. The optional
`references` argument is a `BoundReferenceContext` for applications that
already manage fixed-reference binding. Path-based examples resolve declared
references beside the model automatically.

## `verbalize`: display the supplied facts

<!-- gnd-run expect=0 -->
```python
from gnd import api

result = api.verbalize(
    "api-dispatch/model.orm.json", "api-dispatch/repaired.pop.json"
)
assert result["exit_code"] == 0, result
assert result["rows"], result
print(result["rows"][0])
```

`verbalize(model, population, *, anchors=None, document=None,
population_bytes=None, unredacted=False)` returns
`{"rows": [...], "exit_code": ..., "error": ...}`. Each row describes a
supplied fact using the model's reading. This is useful for an inspection page
or a review screen. It performs no LLM call and does not turn a sentence into a
checker verdict. This function verbalizes a **population**; the model-authoring
skill produces the separate verbalization of the model's rules.

## `diff`: compare rules over the same vocabulary

The following comparison uses a catalog-only variation of the dispatch model:
shipping requests must name an approved warehouse. It changes that rule from
hard enforcement to advisory feedback. Both compared models retain the same
vocabulary. Temporal models are currently outside the diff consumer's support;
the date/window vocabulary is removed before either comparison model is saved.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
from shutil import copytree
from gnd import api

copytree("api-dispatch", "api-diff")
root = Path("api-diff").resolve()
document = json.loads((root / "model.orm.json").read_text())
keep = {"dispatch_request", "dispatch_allowed", "dispatch_leg", "dispatch_reachable"}
document["fact_types"] = [f for f in document["fact_types"] if f["id"] in keep]
document["object_types"] = [t for t in document["object_types"]
                            if t["id"] in {"dispatch_type_job", "dispatch_type_node"}]
document["constraints"] = [document["constraints"][0]]
(root / "model.orm.json").write_text(json.dumps(document))
document["constraints"][0]["modality"] = "deontic"
(root / "advisory.orm.json").write_text(json.dumps(document))
populations = Path("diff-populations").resolve()
populations.mkdir()
candidate = json.loads((root / "repaired.pop.json").read_text())
candidate["facts"] = {k: v for k, v in candidate["facts"].items() if k in keep}
candidate["population"]["covers"] = list(candidate["facts"])
candidate["facts"]["dispatch_request"][0]["node"] = "WH-C"
(populations / "unapproved.pop.json").write_text(json.dumps(candidate))

result = api.diff(
    root / "model.orm.json", root / "advisory.orm.json",
    populations=populations, seed=7,
)
report = result.get("report", result)
assert report["schema_version"] == "gnd-diff/1", report
assert report["populations"], report
assert api.check(root / "model.orm.json", populations / "unapproved.pop.json")["exit_code"] == 1
assert api.check(root / "advisory.orm.json", populations / "unapproved.pop.json")["exit_code"] == 0
print("Compared the same unapproved warehouse under hard and advisory rules.")
```

`diff(model_a, model_b, *, populations=None, unredacted=False, seed=0,
references=None, references_b=None)` compares compatible vocabularies. Its
`gnd-diff/1` report has `entailment`, `populations`, and `not_derivable` rows;
models with references wrap that report under `report` with binding metadata.
The base diff report does **not** share the check payload's `exit_code` field.
Bad or incompatible inputs can raise `gnd.diff.DiffError` or model-validation
exceptions; do not handle this
function as though every failure were a returned check report.

Entailment rows use a bounded catalogue of syntactic comparisons. `undecided`
does not mean a counterexample exists. Observations on a supplied population
describe that population, not every possible application state.

## `transition`: audit an operation, including its side effects

This complete fixture has one unary fact, “a token is active,” and an operation
that activates one token. It starts with `alpha`, adds `beta`, and checks the
declared post-state. The ordinary CLI trace supplies the required model and
operation digests; the example does not implement its own digest algorithm.

<!-- gnd-run expect=0 -->
```python
import json
import subprocess
import sys
from pathlib import Path
from gnd import api

root = Path("api-transition")
root.mkdir()
provenance = {
    "source": "explicit", "status": "confirmed", "modality": "alethic",
    "provenance": {"user_quote": "An active token occurs once."},
}
model = {
    "version": 2,
    "model_id": "urn:gnd-tutorial:activation@1",
    "source": {"kind": "text-conversation", "confidence": "standard", "mode": "one-shot"},
    "object_types": [{"id": "token", "name": "Token", "kind": "value", "primitive": "String"}],
    "fact_types": [{
        "id": "active", "reading": "{Token} is active",
        "roles": [{"role_name": "token", "object_type": "token"}],
        "constraints": [{"type": "uniqueness", "roles": ["token"], **provenance}],
    }],
    "constraints": [], "rejected_proposals": [],
    "operations": [{
        "id": "activate", "reading": "{Token} becomes active",
        "parameters": [{"name": "token", "object_type": "token"}],
        "effects": [{"assert": {"fact_type": "active", "bind": {"token": "$token"}}}],
        "frame": {"modality": "alethic"},
        "source": "explicit", "status": "confirmed",
        "provenance": {"user_quote": "Activation adds the requested token."},
    }],
}
(root / "model.orm.json").write_text(json.dumps(model))
for name, tokens in [("pre", ["alpha"]), ("post", ["alpha", "beta"])]:
    population = {
        "population": {"model": "model.orm.json", "model_id": model["model_id"],
                       "source": "fixture", "covers": ["active"]},
        "instances": {}, "facts": {"active": [{"token": t} for t in tokens]},
    }
    (root / f"{name}.pop.json").write_text(json.dumps(population))
trace = subprocess.run(
    [sys.executable, "-m", "gnd", "validate", str(root / "model.orm.json"), "--trace"],
    check=True, capture_output=True, text=True,
).stdout
digests = {}
for line in trace.splitlines():
    fields = line.split()
    if len(fields) == 2 and fields[0] in {"model_digest", "operations_digest"}:
        digests[fields[0]] = fields[1]
assert len(digests) == 2
steps = {"steps_schema": 1, "model": "model.orm.json", **digests,
         "steps": [{"op": "activate", "bindings": {"token": "beta"}}]}
(root / "steps.json").write_text(json.dumps(steps))
result = api.transition(root / "model.orm.json", root / "pre.pop.json", steps, root / "post.pop.json")
assert result["exit_code"] == 0, result
print("The activation walk agrees with the declared post-state.")
```

`transition(model, pre, steps, post=None, *, unredacted=False,
references=None)` accepts a steps path or mapping. It checks the operation
bindings, preconditions, intermediate states, and declared effects. Supplying
`post` requests an audit; omitting it asks GND to compute the final population.
The function returns the versioned transition report dictionary. Frame checks
cover fact types touched by the walk, so audit application changes outside that
set separately. See [data and transitions](../guides/data-and-transitions.md).

## `witness`: explain one derived fact with a finite proof

The dispatch catalog includes a route from `WH-A` through intermediate
warehouses to `DEST-D`. Request a proof for that specific reachable pair. Tuple
order and primitive names must agree with the model's role order.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
from gnd import api

targets = {"version": 1, "targets": [{
    "fact_type": "dispatch_reachable",
    "tuple": [{"primitive": "String", "value": "WH-A"},
              {"primitive": "String", "value": "DEST-D"}],
}]}
Path("targets.json").write_text(json.dumps(targets))
result = api.witness(
    "api-dispatch/model.orm.json", "api-dispatch/repaired.pop.json", "targets.json"
)
assert result["exit_code"] == 0, result
assert result["results"][0]["status"] == "proved"
assert result["certificate"]["nodes"]
Path("route-certificate.json").write_text(json.dumps(result["certificate"]))
print("The requested route has a finite derivation witness.")
```

`witness(model_path, population_path, targets_path, *, reference_root=None)`
uses file paths. It returns `exit_code`, per-target `results`, `certificate`,
`reason`, and bounded `work` information. The Python result contains raw values
in the certificate; the CLI's default witness view removes them. Store or
display the raw certificate only when those values are appropriate for your
audience.

## `replay`: check that proof independently

<!-- gnd-run expect=0 -->
```python
from gnd import api

result = api.replay(
    "api-dispatch/model.orm.json", "api-dispatch/repaired.pop.json",
    "route-certificate.json",
)
assert result["exit_code"] == 0, result
assert result["results"][0]["status"] == "proved"
print("The route proof replayed against the bound inputs.")
```

`replay(model_path, population_path, certificate_path, *,
reference_root=None)` checks a raw finite certificate with an independent
inference kernel and returns the same witness-result envelope. The certificate
binds the model, candidate, and fixed references; changed inputs can invalidate
that binding. The witness/replay bands have their own meaning: `0` all targets
proved, `1` invalid proof, `2` missing/unknown/unsupported, `3` invalid inputs,
and `4` work bound reached. A missing proof does not establish a false fact.

## Integrate reports deliberately

- Keep the model and its fixed reference files together, and treat malformed
  input separately from a failed domain rule.
- Branch on documented fields and `schema_version`. Reference and temporal
  features select report variants; do not assume one version for all models.
- Model-based redaction applies by default to checking, verbalization, and
  diff reports. `unredacted=True` is an explicit request to retain source values.
- Wrong Python argument types can raise `TypeError` before evaluation. Returned
  report failures are not a substitute for ordinary exception handling.
- A mechanical pass checks supplied facts against supplied rules. Assurance
  metadata is a separate result; missing or stale evidence remains unavailable.

The current signatures live in
[the public API module](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/api.py).
The [format index](formats.md) points to the authoritative contracts for each
report and input family.
