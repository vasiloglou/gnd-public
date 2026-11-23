# Check facts extracted from documents

Use GND when a report, form, memo, or article needs to become structured facts
that can be checked against domain rules. Keep two questions visible:
“Do these facts satisfy the model?” and “Did the extraction faithfully capture
the document?” A checker pass answers the first question; extraction fidelity
needs its own evidence.

## Prepare the extraction vocabulary

With an authored, supported non-temporal model, this contextual command emits
the extraction bundle:

```sh
gnd extract model.orm.yaml --out artifacts
```

The bundle includes a shape-only JSON Schema projection, a constraint-blind
verbalization, an applicability description, and an index that binds their
digests and header template. It is produced offline. `gnd extract` does not
read the source document or call a model provider.

`gnd extract model.orm.yaml --out artifacts --guidelines` also writes
`<stem>.guidelines.md`: per fact type, its readings, the fact types played
by the same object types, and per role the object type's description,
reference mode and primitive. It stays constraint-blind; an external
uniqueness that identifies an entity appears only as that entity's
identification. A description is
the modeller's prose and can restate a rule, and the guideline repeats
descriptions, so read it as guidance about meaning, not as rules to enforce.

The extraction schema describes which facts and values can be represented.
It deliberately does not tell an extractor how to rewrite facts to satisfy
uniqueness, mandatory, or other domain rules. If a document describes an
invalid application state, the extraction should preserve that state so the
checker can reveal it.

For a version-5 model with pinned includes, use the authored root in both
`gnd extract` and `gnd verify`. Keep the flat model and flattening record
with the bundle for verification. Give the extraction agent the shape-only
schema and verbalization as usual. Verification checks the bundle against the
root and its pinned files. See the [flattening record contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#extraction-flattening-record)
for the two additional files.

## Ask an agent to extract, then verify its output

In an agent session with the GND skills installed, explicitly select the
extraction workflow. Example prompt; replace the named files with your own:

```text
Use gnd-extract with model.orm.yaml and artifacts/ to extract report.md into
extracted.population.json. Preserve the document's facts, including facts
that violate the model. Write the required digest-bound extraction sidecar,
then run the verifier and explain its findings.
```

The skill treats the document as quoted data. Instructions, links, and code
inside it are content to interpret, not commands to follow. The agent writes
the population and its adjacent extraction sidecar. The sidecar records the
model, document, projection, and population binding.

Given those completed artifacts, the contextual verification command is:

```sh
gnd verify model.orm.yaml extracted.population.json --artifacts artifacts --format json
```

Verification validates the handoff before checking the population. Missing,
malformed, or stale sidecars produce input refusal at band `3`. Read the
`extraction` block and the semantic verdicts independently. If your population
was authored directly and never extracted, explicitly use `--no-extraction`;
the report records that the extraction path was skipped.

## Reading a failed verification

Exit `1` means at least one alethic constraint or derivation failed. To see
which ones, and on which rows, run the same command with `--format json`;
the report's `outcome` is then `violated`. A model that includes another
file needs that file at the path its `includes` entry names, next to the
model.

1. The failing constraints are the entries of `verdicts` whose `verdict` is
   `fail` and whose `modality` is `alethic`.
2. Each one gives the constraint's address in `constraint_ref`:
   `fact_types[<fact type>].constraints[<n>]` for a constraint on a fact
   type, `constraints[<n>]` for one at the top level. The address is in the
   model `gnd verify` composed. For a model without includes that is the
   file you wrote. For a model with includes, the root's constraints and the
   included ones are composed into one list, so the position can differ from
   the file that declared the constraint. `gnd flatten MODEL --out DIR`
   writes a `gnd-flattening/1` record whose `origins` map each composed
   address to the file that declared it (`origin`), its address there
   (`original_address`) and its `id` (`element_id`); a fact type's composed
   position is the origin whose `element_id` is the fact type
   ([the record's format](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md)).
   `constraint_type` names the kind, `message` says what the constraint
   requires and what broke it, and `offending_facts` lists the witnesses of
   the violation. A witness's shape depends on the kind of constraint: the
   violating facts as objects of role values for the uniqueness failure
   below, for instance, or a bare instance for a mandatory constraint it
   does not meet. Read each witness with `message`, which says what it is.
3. The failing derivations are the entries of `derivations` whose `verdict`
   is `fail`. Each names itself in `derivation_ref` and lists what went
   wrong in `findings`. `derivations` is `null` for a model that declares
   none.
4. A `warning` verdict is a deontic violation. It is reported and does not
   change the exit.
5. A model can mark roles as sensitive. Then `message` holds a marker and
   `offending_facts` holds one marker row, in place of the values. Whether
   you can see the values (`--unredacted`, or `GND_DISCLOSURE=internal`) is
   set by the [disclosure mode](../reference/disclosure.md).
6. The text output (without `--format json`) prints the same constraints and
   messages, but not the rows.

The packaged literature reading example writes a population with two labels
for one subject, which breaks a uniqueness constraint. These steps list it:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
import shutil
import subprocess
import sys
from importlib.resources import files


def failed(report):
    """Steps 1 and 3: the failing constraints, then the failing derivations."""
    constraints = [v for v in report["verdicts"] if v["verdict"] == "fail" and v["modality"] == "alethic"]
    derivations = [d for d in report["derivations"] or [] if d["verdict"] == "fail"]
    return constraints, derivations


# The literature reading example writes a population that breaks one rule.
subprocess.run([sys.executable, "-m", "gnd.examples.literature.reading", "run", "--out", "run"],
               capture_output=True, check=True)
# The model includes a vocabulary file; both go in the same folder.
example = files("gnd").joinpath("examples", "literature")
for part, name in (("reading_fixture", "reading.orm.json"), ("depth_fixture", "vocabulary.orm.json")):
    shutil.copyfile(example.joinpath(part, name), f"run/{name}")

done = subprocess.run(["gnd", "verify", "run/reading.orm.json", "run/reported-conflict.population.json",
                       "--no-extraction", "--format", "json"], capture_output=True, text=True)
report = json.loads(done.stdout)
print("exit:", done.returncode, report["outcome"])
constraints, derivations = failed(report)
for verdict in constraints:
    print(verdict["constraint_ref"], verdict["constraint_type"])
    for witness in verdict["offending_facts"]:
        print("  ", witness)
for derivation in derivations:
    print(derivation["derivation_ref"])
    for finding in derivation["findings"]:
        print("  ", finding)
```

```text
exit: 1 violated
fact_types[subject_label].constraints[0] uniqueness
   {'subject': 'alanine-in-vacuum', 'label': 'Alanine dipeptide observation'}
   {'subject': 'alanine-in-vacuum', 'label': 'Conflicting reported label'}
```

The flattening record of this model maps
`fact_types[subject_label].constraints[0]` to the included vocabulary's
`subject_has_one_label`. Which side is wrong, the data or the
constraint, is yours to judge: the report shows the rule and the rows. A
passing report is still not proof that the extraction is faithful; see the
[extraction contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-extract/references/extraction-contract.md#5-failure-semantics).

## Bind important values to source spans

An `anchored` constraint checks whether populated role values have witnesses
in a bound source document. The anchor sidecar names a fact occurrence, role,
source span, and the necessary digests. Contextual snapshot command:

```sh
gnd check model.orm.yaml extracted.population.json --anchors extracted.population.anchors.json --document report.md --format json
```

A malformed binding is refused. An absent or unsuitable witness can be a
failure or an unchecked result depending on the situation and modality. The
matcher uses documented lexical normalization and explicit numeric/date
recognizers; it does not infer arbitrary paraphrase equivalence. Source
anchoring provides specific occurrence evidence, not a blanket truth claim.
The sidecar format, including version 2's several anchors per role, is in
the [anchor sidecar reference](../reference/anchors.md).

## Test a round trip without hiding failures

For an extraction evaluation, explicitly select `gnd-render-doc` to turn a
known population into prose. That workflow preserves all applicable source
facts, plants three kinds of distractors, and writes a document manifest.
`gnd doccheck` checks that rendering contract. Then separately select
`gnd-extract` to read the document back, and measure the retained round-trip
cases with `gnd fidelity`.

These outputs remain different evidence: rendering completeness, extracted
population checking, and measured fidelity. Saved extraction outputs or
synthetic receipts are not evidence that a provider ran now.

See the [extraction contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-extract/references/extraction-contract.md)
and [rendering contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-render-doc/references/rendering-contract.md)
for exact sidecars, manifests, distractors, and failure semantics.

## Separate extraction and checking models

Pin the same shared vocabulary in an extraction root and a checking root.
The extraction root projects the document shape. The checking root can add
constraints that are only meant for the composed result, including guarded
calendar comparisons. Keep the two authored roots independently identified
even when their candidate vocabulary is identical.

Run `gnd extract` on the extraction root and give the extractor its indexed
bundle. For an include root, the bundle contains the flattened model and its
origin record. Run `gnd verify` against the same authored root and bundle
before transferring a population to the checking root. Fixed catalogs keep
their model declarations and their raw-byte digests across the two roots.

The [literature example](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/literature/README.md#extraction-to-checking-interop)
records the transfer in a `literature-rebind/1` record for each source. It
binds both roots, the include and catalog digests, the extraction index,
the document, the original extraction and its sidecars, and the checking
population and anchors. The checking population updates the model header.
The anchors bind the updated population bytes to the original source spans.
The example re-derives the rebinds before composing the sources under the
checking root. Check and replay use the composition record from that root.

`gnd fidelity` can measure the original extraction against the same
include root when it has the authenticated indexed bundle. In the example,
the original document evidence and extraction handoff live alongside the
checking-bound artifacts in each source directory.
