# Use GND from Python

Use `gnd.api` when your application already has a model and needs to validate
inputs, check candidate facts, explain them, or audit a state change. The API
returns ordinary dictionaries; your application decides how to display a
finding and what action to take.

The supported functions are `validate`, `check`, `check_with_receipt`, `transition`,
`verbalize`, `diff`, `witness`, `replay` and `why_not`: nine functions, the one
count other pages refer to. The opt-in `EvaluationSession`
class reuses eligible work between calls. Code generation, experiment
orchestration, and model evolution have CLI and skill workflows described in
the [task guides](../advanced.md).

## Set up the examples

Install GND using the [quickstart](../quickstart.md), then run these blocks in
order from a fresh directory. Every block starts a new Python process; the
files on disk carry the examples forward. The data is synthetic and every
example runs locally without an API key or native compiler.

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

## `why_not`: find where a derivation stops

The seed population has no route from `WH-A` to `DEST-E`. Ask why that row is
not derived.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
from gnd import api

row = {"version": 1, "targets": [{
    "fact_type": "dispatch_reachable",
    "tuple": [{"primitive": "String", "value": "WH-A"},
              {"primitive": "String", "value": "DEST-E"}],
}]}
Path("why-not-row.json").write_text(json.dumps(row))
result = api.why_not(
    "api-dispatch/model.orm.json", "api-dispatch/seed.pop.json",
    "dispatch_reachable", row_path="why-not-row.json",
)
assert result["exit_code"] == 0 and result["status"] == "blocked", result
direct, onward = result["clauses"]
assert direct["blocker"]["fact_type"] == "dispatch_leg"
assert direct["blocker"]["samples"] == [{"source": "WH-A", "target": "DEST-E"}]
assert onward["blocker"]["samples"] == [{"source": "WH-B", "target": "DEST-E"}]
print("No leg from WH-A to DEST-E; the onward route stops at WH-B.")
```

`why_not(model_path, population_path, fact_type, *, row_path=None,
reference_root=None)` uses file paths. Without `row_path` it asks why the fact
type has no rows at all. The result's `status` is `derived`, `blocked`,
`unsupported`, `unavailable` or `refused`. For each clause, `clauses` gives the
binding count after each step and the first step that left none. When that
step is a derived fact type, `descent` explains its row in turn. The Python
result carries raw values; the CLI's default view removes them. The
[why-not reference](why-not.md) defines the steps and the exit bands.

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

### Compiled snapshot operation obligations

`api.check(model, population, compiled_operations=True)` adds eligible standing
operation subsets to a snapshot check. Default checking still excludes operations.
Known alethic violations appear as `compiled-subset` verdicts and band 1; missing
coverage/unknown inputs appear as unchecked. Reports carry no proof-backed
assurance for this new mode. `admission=True` cannot be combined with it. Use
`api.transition` for step, dynamic, intermediate-state and frame obligations.

## Reusing a checked pre-state

`check_with_receipt(model, population, *, unredacted=False)` accepts loaded objects
and returns `(payload, receipt)`. The payload is the same as `check` produces.
Pass the receipt as `transition(..., pre_receipt=receipt)` to skip the pre-state
check. Intermediate and post checks still run.

The `CheckReceipt` docstring defines the receipt contract. GND alone mints these
opaque values. Reuse binds the same model object and unchanged model content,
a validated population with the same content, the stored report and branch ids,
and default check options. Exit 0 or 2 can be reused; anchored models and models
without a cacheable key cannot.

Invalid reuse raises `ReceiptRefused`, a `ValueError` with a `reason` attribute.
The first failing guard wins, in this order:

| Reason | Meaning |
|---|---|
| `foreign` | GND did not mint this receipt |
| `path-inputs` | Model or pre-state is a path |
| `not-reusable` | The check failed or its route cannot be reused |
| `options` | References or different check options were requested |
| `model-object` | A different model object was supplied |
| `model-changed` | Model content changed, including operations |
| `population-unvalidated` | The pre-state lacks a current validation marker |
| `population-changed` | Validated pre-state content differs from the receipt |

Receipts stay in one process and cannot be serialized. There is no CLI option.
Only default check options are supported; compiled operations, admission,
anchors and references are outside this feature.


## Reusing evaluation work across snapshots

`EvaluationSession(model, *, max_rows=100000, max_bytes=33554432)` takes a loaded
`Model`. Load every population with that same model. `session.check(population)`
and `session.transition(pre, steps, post=None)` return the ordinary API payloads;
`session.check_with_receipt(population)` returns the ordinary payload/receipt pair.
The normal stateless functions, CLI, batch and experiment defaults remain fresh.

The session rechecks current validation markers, model content including operations,
ordered facts, rosters, coverage and supported options. A no-op can reuse eligible
extension components and constraint findings. A change recomputes the dirty
component from current inputs, including whole recursive components; it preserves
current witnesses, lineage, unavailable/possible states, branch evidence and report
ordering. Admission and every required root/intermediate/post check still run.
Snapshot comparison remains proportional to input size. This is component reuse,
not a promise of work proportional only to added rows.

Reference, anchored, witness/observer, compiled/admission and unknown dependency
modes select fresh work as applicable. Custom family hooks with unclassified
external dependencies also run fresh. Unsupported keys or resource bounds never
substitute an empty relation for unavailable data. `check` accepts the normal
semantic keywords; `transition` accepts `unredacted`, `references` and `pre_receipt`.
Results are detached from stored findings. A receipt's mutable public report also
cannot change the private snapshot later consumed by a transition.

A session retains one committed generation, up to the configured projected bytes
and retained fact/witness rows. Oversized/unmeasurable units run fresh. The byte
projection bounds cache content, not Python RSS or caller-owned inputs. A completed
violation can publish valid units; errors/indeterminate checks discard staged cache
work. Exceptions/cancellation before publication preserve committed cache and
feedback sequence. One active call per session is permitted; overlapping calls
raise `ValueError`. Independent sessions may interleave. `reset()` clears retained
work; `close()` releases it and rejects future work. Sessions cannot be serialized.

`stats()` is diagnostic and stays outside reports/feedback. `lookups` counts each owned unit lookup once. `hits`, `misses` and
`bypasses` are overlapping event counters: a computed miss may also bypass storage
because of a bound. Their sum is not a lookup denominator; use `bypasses/lookups`
for that fraction. A zero denominator means no rate was measured. `session_calls`/`session_fresh_calls` count
completed or attempted facade evaluations under ownership; `extension_context_calls`
and `extension_context_fallbacks` count context requests/refusals; `constraint_calls`
and `constraint_fallbacks` count finding routes/fresh eligibility refusals. These
are different denominators:0 unit bypasses does not establish whole-call eligibility.
`entries`, `rows`, `bytes` describe retained content; `generation` counts published
cache generations. Reset preserves lifetime diagnostic counters and feedback numbering.

Use `observe(population, replacements)` and
`check_with_feedback(population, *, attempt)` for a host loop. The
[offline two-attempt example](../agents/dev-session.md#a-host-loop-in-one-python-process)
explains whole-relation replacement, bounded counts, explicit availability/overflow,
strict feedback versioning and retry order. This wire is separate from persistent
experiment sessions and never serializes cache handles.


Measured on the frozen public reporter replay (13 calls), receipts executed 4,878
rule bodies and sessions with receipts executed 179, with matching reports and
ordered logical calculation results. In the initial IE5 three-round interleaving on a
shared macOS/Python3.11.15 host, medians were 5.83 s with receipts and 6.79 s with
sessions plus receipts. The session was slower on this fixture despite less rule
work. Course/localized controls were also slower. These are workload-specific
observations, not a reason to change existing defaults or a prediction for the
unsupplied 547-program workload. Maintainer evidence records ranges, cold/no-op/
dirty cases, bounds and source identities in the incremental-evaluation milestone.


IE6 reduces repeated policy-size traversal with bounded immutable accounting
summaries and exact builtin fast paths. Live signature hashing, mutable/code guards,
private cloning and current-content admission remain in place. A separate balanced
same-host comparison (three samples per arm, one warmup per worker) measured:

| Workload | Pre-IE6 session + receipts | IE6 session + receipts | IE6 full + receipts |
|---|---:|---:|---:|
| Reporter | 9.59 s | 9.03 s | 8.50 s |
| Course | 2.41 s | 1.99 s | 0.86 s |
| Localized | 0.574 s | 0.541 s | 0.423 s |

Session medians improved by about 6%, 17% and 6% against the archived pre-IE6
implementation in that comparison; all remained slower than full evaluation with
receipts. These are shared-host observations with small samples and recorded ranges,
not guaranteed speedups. Compare arms within a run; the earlier IE5 numbers use a
separate measurement and must not be chained into a speedup claim. The missing
547-program workload still prevents downstream performance acceptance.
