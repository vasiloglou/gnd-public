# From several documents to one checked answer

A program that reads contracts extracts each one on its own: one document,
one population, one anchor sidecar that says where in the text each value was
found. Some questions need two documents at once. Which city is each
contract's party based in, when one contract names the party and another
says where it is based? In this how-to, GND composes two extractions into one
population, checks the result against both documents, and traces the answer
back to a passage in each.

Three rules hold the whole way through. GND never decides on its own that two
values mean the same thing; a manifest says so, and nothing else changes.
Every anchored value is checked against the document it came from, under the
name that document uses. The record of where each composed fact came from carries ids
and indexes, never a value, so it can travel where the contracts cannot.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Two contracts and what each contributes">

![Two documents side by side. Agreement C-1 names Acme Corp. as the supplier and says the supplier is based in Lyon; its extraction holds C-1 has party Acme Corp., with two anchors on the party because the name appears twice, and Acme Corp. is based in Lyon. Addendum C-2 is signed by ACME CORP. and says ACME CORP. is based in Lyon; its extraction holds C-2 has party ACME CORP. and ACME CORP. is based in Lyon. Each population has its own anchor sidecar binding it to its own document. Below, the question: which city is each contract's party based in?](../assets/applications/compose-documents.svg)
</div>

*Source: `contracts/composition/contract-a` and `contract-b` of the shipped example.*

!!! info "Files on GitHub"

    - [`composition/model.orm.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/composition/model.orm.yaml): contracts, parties and cities, an `anchored` party and city, a uniqueness and the derived "Contract is in City"
    - [`composition/composition/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/composition/composition): the composition directory, with `manifest.json` and one folder per contract holding `document.txt`, `population.json` and `population.json.anchors.json`
    - [`composition/composition-conflict/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/composition/composition-conflict): the same, except that the addendum says Zurich
    - [`composition/targets.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/composition/targets.json): the derived fact to trace
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/compose-documents.md)

Copy the example into a working folder:

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/composition', 'contracts', dirs_exist_ok=True)"
```

## The model

Three value types, Contract, Party and City, and three fact types. "Contract
has party Party" carries an `anchored` constraint on the party: every party
must be found in the document its fact was extracted from. "Party is based in
City" anchors the city the same way and adds a uniqueness: a party has one
seat. The third fact type is derived, and it is the question:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "from gnd import api; [print(r['fact_type'], '->', r['text']) for r in api.verbalize_rules('contracts/model.orm.yaml')['rules']]"
```

```text
contract_is_in_city -> when contract_has_party(contract = $c, party = $p) and party_is_based_in_city(party = $p, city = $x), derive (contract = $c, city = $x)
```

The rule joins on the party. It only answers when both premises name the party
the same way, which is the whole difficulty of reading two documents.

## Two documents, two extractions

The agreement:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat contracts/composition/contract-a/document.txt
```

```text
Agreement C-1

Agreement C-1 is entered into by Acme Corp. as the supplier.
The supplier, Acme Corp., is based in Lyon.
```

The addendum, which writes the same company in capitals:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat contracts/composition/contract-b/document.txt
```

```text
Addendum C-2

Addendum C-2 is signed by ACME CORP. as the supplier.
ACME CORP. is based in Lyon.
```

Each document was extracted on its own: a population of the facts the
document states, and beside it an anchor sidecar. No `gnd` command writes the
sidecar; the extractor does, whether that is you, an agent, or your own
tooling, and `gnd.anchors.write_anchor_sidecar` publishes one that the
parser accepts. This example's sidecars come from
[`tools/build_composition_example.py`](https://github.com/vasiloglou/gnd-public/blob/main/tools/build_composition_example.py),
which computes every digest and range from the files.

An anchor binds one role value of one fact to a range of the
document's text; the value's chosen occurrence must lie inside that range.
That is all an anchor claims. It does not say the passage entails the fact,
and GND does not say so either.

The agreement names Acme Corp. twice, so its sidecar (version 2, which allows
[several anchors per fact role](../reference/anchors.md#versions-1-and-2))
carries two anchors on the party of "C-1 has party Acme Corp.", one per
sentence, and one anchor on the city:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; d=open('contracts/composition/contract-a/document.txt').read(); [print(a['role'], a['occurrence'], repr(d[a['span']['start']:a['span']['end']])) for a in json.load(open('contracts/composition/contract-a/population.json.anchors.json'))['anchors']]"
```

```text
party 0 'Agreement C-1 is entered into by Acme Corp. as the supplier.'
party 1 'The supplier, Acme Corp., is based in Lyon.'
city 0 'The supplier, Acme Corp., is based in Lyon.'
```

Every anchor on a role must hold for the role to pass. Two anchors are two
claims about the document, and one wrong claim fails the fact even when the
other is right.

The sidecar also carries three digests (fingerprints of exact
content): of the population's bytes, of the document's bytes, and of the
model's vocabulary, meaning its object types, fact types and roles but not its
constraints, rules or descriptions. If the population, the document or that
vocabulary changes, the sidecar no longer binds and GND refuses it before
looking at a single value. The composition record, below, binds the whole
model file.

Each extraction also claims the answer its own document supports: the
agreement's population lists "C-1 is in Lyon" and the addendum's lists "C-2 is
in Lyon". The checker will compare those claims with what the rule derives
from the composed facts.

## Say what is the same, in the manifest

**You type.** With Claude Code, the ask is one paragraph:

```text
Compose contracts/composition under contracts/model.orm.yaml. The addendum
writes the supplier as "ACME CORP."; that is "Acme Corp." from the agreement.
Check the composition against both documents and tell me which city each
contract's party is based in, with the passage each answer rests on.
```

**Claude Code does.** It writes the manifest, then runs the four commands
below. The manifest lists the sources in reading order, the renamings, and the
deduplication rule:

<!-- gnd-run expect=0 output=stdout -->
```sh
cat contracts/composition/manifest.json
```

```text
{
  "schema": "gnd-composition-manifest/1",
  "sources": [
    "contract-a",
    "contract-b"
  ],
  "renamings": [
    {
      "source": "contract-b",
      "fact_type": "contract_has_party",
      "role": "party",
      "from": "ACME CORP.",
      "to": "Acme Corp."
    },
    {
      "source": "contract-b",
      "fact_type": "party_is_based_in_city",
      "role": "party",
      "from": "ACME CORP.",
      "to": "Acme Corp."
    }
  ],
  "deduplications": "identical-rows",
  "scope_tags": [
    {
      "source": "contract-a",
      "tag": "agreement"
    },
    {
      "source": "contract-b",
      "tag": "addendum"
    }
  ]
}
```

A renaming names one source, one fact type, one role, and the exact value to
rewrite. It is the only way composition changes a value. GND will not match
"ACME CORP." to "Acme Corp." by case, by edit distance or by any other guess,
because a program that guesses once will guess wrong once, silently, in a
population that then looks checked.

A renaming that matches no row is refused,
so a manifest cannot carry a stale rule. The scope tags label each source in
the record and change nothing in the population.

## Compose

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd compose contracts/model.orm.yaml contracts/composition --out composed.population.json --record composition.json
```

```text
Composed 5 fact(s) from 2 source(s).
```

For each source in manifest order, GND validates the population against the
model, binds the sidecar to the population and the document, and applies the
renamings. Then it appends the rows fact type by fact type. The two "is based
in Lyon" rows are identical once the addendum's party is renamed, so they
become one composed fact with two source facts.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Composition: two populations and a manifest become one population and a record">

![On the left, two populations: the agreement's facts and the addendum's facts, the addendum's party written ACME CORP. In the middle, the manifest: rename ACME CORP. to Acme Corp. in contract-b, once per fact type (renamings 0 and 1), deduplicate identical rows. On the right, the composed population: C-1 has party Acme Corp., C-2 has party Acme Corp. with the renaming highlighted, and one fact Acme Corp. is based in Lyon highlighted as deduplicated from both sources. Beside it the record: for every composed fact, its source ids and indexes and the renamings applied, and no values.](../assets/applications/compose-composition.svg)
</div>

*Source: the manifest above and the record printed below.*

**You get.** Two files. `composed.population.json` is an ordinary population,
written as canonical JSON so that composing the same inputs again gives the
same bytes. `composition.json` is the record: for every composed fact, the
source facts it came from and the manifest renamings applied to it, by index.
The helper below prints one line per composed fact:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; [print(f['fact_type'], f['index'], [s['source'] + '#' + str(s['fact_index']) for s in f['sources']], 'renamings', f['renamings']) for f in json.load(open('composition.json'))['facts']]"
```

```text
contract_has_party 0 ['contract-a#0'] renamings []
contract_has_party 1 ['contract-b#0'] renamings [0]
contract_is_in_city 0 ['contract-a#0'] renamings []
contract_is_in_city 1 ['contract-b#0'] renamings []
party_is_based_in_city 0 ['contract-a#0', 'contract-b#0'] renamings [1]
```

The record holds no role value: not "Acme Corp.", not "Lyon", not the
contract codes. It holds digests of the model, the manifest, every source's
three files and the composed population, plus ids and indexes. A record can be
handed to an auditor, logged, or compared across runs without disclosing what
the contracts say. The values stay in the populations: `gnd compose` writes
them in every mode, and [disclosure mode](../reference/disclosure.md) governs
only what a check, witness view or other report prints about them.

## Check the composition against both documents

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check contracts/model.orm.yaml composed.population.json --composition composition.json --sources contracts/composition
```

```text
BLOCKING (alethic)
  (none)
ADVISORY (deontic)
  (none)
DERIVATIONS (alethic)
  [pass] derivation:contract_is_in_city: The derivation claim for 'contract_is_in_city' matches its extension.
pass=4 fail=0 warning=0 unchecked=0 vacuous=0
COVERAGE
  contract_has_party: declared, facts=2
  party_is_based_in_city: declared, facts=1
  contract_is_in_city: declared, facts=2
```

**GND says.** *Clean.* Before it checks anything, the checker does two
things the record makes possible. It compares the model's and the composed
population's digests with the record, so a population edited after
composition is refused. Then it composes again from the sources directory,
binding every sidecar again, and compares the result byte for byte with the
record: manifest digest, every source digest, scope tags and lineage. The
checker runs over exactly the bytes it just re-derived, not over bytes it was
told came from the sources.

Only then do the constraints run, and the `anchored` ones run per source. The
composed population says contract C-2 has party "Acme Corp.", but the
addendum's document never contains those words:

<!-- gnd-run expect=1 output=stdout -->
```sh
grep -c "Acme Corp." contracts/composition/contract-b/document.txt
```

```text
0
```

So GND does not look for the composed value in the addendum. It takes the
source fact as it was before renaming, "C-2 has party ACME CORP.", and matches
it against the addendum's own sidecar and document. A renaming is a decision
about meaning, taken in the manifest; the evidence for the value is in the
document that used the old spelling, and that is where it is checked. A
composed fact passes when every one of its source facts passes.

The derivation line says the claims and the rule agree: joining the two
contracts' parties with the one seat gives "C-1 is in Lyon" and "C-2 is in
Lyon", exactly what the two extractions claimed.

## When the documents disagree

`contracts/composition-conflict` is the same pair of contracts, except that
the addendum now says the supplier is based in Zurich:

<!-- gnd-run expect=0 output=stdout -->
```sh
grep "based in" contracts/composition-conflict/contract-b/document.txt
```

```text
ACME CORP. is based in Zurich.
```

Composition still succeeds. It does not check constraints, and it does not
pick a city. Both rows compose, one from each contract:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd compose contracts/model.orm.yaml contracts/composition-conflict --out conflict.population.json --record conflict.json
```

```text
Composed 6 fact(s) from 2 source(s).
```

The check is where the disagreement surfaces:

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check contracts/model.orm.yaml conflict.population.json --composition conflict.json --sources contracts/composition-conflict
```

```text
BLOCKING (alethic)
  [fail] fact_types[party_is_based_in_city].constraints[1]: Each party plays 'party_is_based_in_city' with at most one combination of the other roles — violated: party 'Acme Corp.' has 2 facts.
ADVISORY (deontic)
  (none)
DERIVATIONS (alethic)
  [fail] derivation:contract_is_in_city: The derivation claim for 'contract_is_in_city' differs from its extension.
    [derived-extension-incomplete] The derived extension of 'contract_is_in_city' is incomplete — missing {"contract":"C-1","city":"Zurich"}.
pass=2 fail=2 warning=0 unchecked=0 vacuous=0
COVERAGE
  contract_has_party: declared, facts=2
  party_is_based_in_city: declared, facts=2
  contract_is_in_city: declared, facts=2
lineage party_is_based_in_city#0: contract-a:party_is_based_in_city#0
lineage party_is_based_in_city#1: contract-b:party_is_based_in_city#0
```

**GND says.** *Two failures, and where each side came from.* The
uniqueness fails because the composed population now holds two seats for one
party. The two `lineage` lines name the offending facts' sources: row 0 is
the agreement's fact, row 1 is the addendum's. A person can open the two
passages and decide; GND cannot, and does not try. Every anchor still passes,
because each document really does say what its extraction recorded. Nothing
was extracted wrongly. The two documents disagree.

The derivation failure shows why a conflict is never quietly tolerated. With
two seats for Acme Corp., the rule derives a second city for each contract:
"C-1 is in Zurich", though the agreement never mentions Zurich, and "C-2 is
in Lyon" beside "C-2 is in Zurich".

The derived extension is every row the rule
produces; the check names only the first one the extractions did not state; the others are missing in the same way.
Whichever seat is wrong, it changes the answer for a contract its document
does not even name. The `lineage` lines are in the JSON report too, as the
entries of `composition.lineage`, one per offending fact.

## Trace the answer to both documents

Back to the clean composition. "C-2 is in Lyon" rests on a premise from each
document: the addendum names the party, and both say where it is based.
`gnd witness` writes a finite proof of a derived fact; with `--composition`
it is a version-2 witness. Its base nodes are the stated facts the proof
starts from, and each one names the source facts the record lists for it:

<!-- gnd-run expect=0 -->
```sh
gnd witness contracts/model.orm.yaml composed.population.json --targets contracts/targets.json --composition composition.json --raw --out witness.json >/dev/null
```

The witness proves the target from two base facts, each with its sources:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import json; [print(n['fact_type'], [s['source'] + ':' + s['fact_type'] + '#' + str(s['fact_index']) for s in n['sources']]) for n in json.load(open('witness.json'))['nodes'] if n['kind'] == 'base']"
```

```text
party_is_based_in_city ['contract-a:party_is_based_in_city#0', 'contract-b:party_is_based_in_city#0']
contract_has_party ['contract-b:contract_has_party#0']
```

Each source fact has anchors in its own sidecar, and those anchors locate
spans in its own document. Following them is a few lines of Python: for each
base node, open the source's population to find the row, find the anchors in
the source's sidecar whose fact key is that row, and slice the document.

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

witness = json.loads(Path("witness.json").read_text())
for node in witness["nodes"]:
    if node["kind"] != "base":
        continue
    for entry in node["sources"]:
        folder = Path("contracts/composition") / entry["source"]
        row = json.loads((folder / "population.json").read_text())["facts"][entry["fact_type"]][entry["fact_index"]]
        sidecar = json.loads((folder / "population.json.anchors.json").read_text())
        text = (folder / "document.txt").read_text()
        for anchor in sidecar["anchors"]:
            if anchor["fact_key"]["roles"] == row:
                span = anchor["span"]
                print(entry["source"], anchor["role"] + ":", repr(text[span["start"]:span["end"]]))
```

```text
contract-a city: 'The supplier, Acme Corp., is based in Lyon.'
contract-b city: 'ACME CORP. is based in Lyon.'
contract-b party: 'Addendum C-2 is signed by ACME CORP. as the supplier.'
```

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="The trace from the derived answer to a span in each document">

![At the top, the derived answer: C-2 is in Lyon, proved by the rule. Below it two base facts. C-2 has party Acme Corp., from contract-b, points at the sentence "Addendum C-2 is signed by ACME CORP. as the supplier." in the addendum. Acme Corp. is based in Lyon, from contract-a and contract-b, points at "The supplier, Acme Corp., is based in Lyon." in the agreement and at "ACME CORP. is based in Lyon." in the addendum. The addendum's spans are found under the name that document uses.](../assets/applications/compose-trace.svg)
</div>

*Source: `witness.json` and the three spans printed above.*

Notice that the addendum's row says "ACME CORP." and its sidecar is matched
on that row, not on the composed "Acme Corp.". The trace crosses the renaming
in the right direction: from the composed answer, through the record, to the
spelling each document actually uses.

A witness can be replayed later against the same population and record.
`gnd replay` checks the digests the witness binds, then that every base node's sources
are what the record says, then the proof itself:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd replay contracts/model.orm.yaml composed.population.json witness.json --composition composition.json
```

```text
{"exit_code": 0, "kind": "derivation-witness-view", "reason": null, "replayable": false, "results": [{"reason": null, "request_index": 0, "root": 2, "status": "proved"}], "work": {"binding_cells": 3, "edges": 2, "nodes": 3, "proof_depth": 2}}
```

A version-2 witness without its record is refused rather than replayed as if
the lineage did not matter:

<!-- gnd-run expect=3 output=stdout -->
```sh
gnd replay contracts/model.orm.yaml composed.population.json witness.json
```

```text
{"exit_code": 3, "kind": "derivation-witness-view", "reason": "composition-required", "replayable": false, "results": [], "work": {}}
```

`"status": "proved"` is the verdict. `"replayable": false` describes this
printed summary, not the witness: a summary is never fed back to replay, the
`witness.json` file is.

Replay checks the witness against the record; only `gnd check --composition
--sources` re-derives the record from the sources. Run the check before
trusting a record, and replay after.

## What this proves, and what it does not

The composition and its check establish that the composed population is
exactly what the manifest says about those source files, that every anchored
value is found in its own document where its sidecar says, and that the
constraints and the derived claims hold over the result. The witness
establishes that "C-2 is in Lyon" follows from two base facts by the model's
rule, and names the passages those facts were read from.

None of it establishes that the contracts are right. An anchor binds a value
to a range of text, nothing more; a document can state a false seat, and an
extraction can read a true document wrongly in a way the anchors do not catch.
The renaming is a human decision recorded in a manifest, not a finding.

What GND adds is that every step is explicit, re-derivable, and refused when its
inputs change, so that the decisions a person did make, the renaming and the
choice of sources, are stated where anyone can check them.

## Recap

| Step | Command | What GND holds you to |
|---|---|---|
| Say what is the same | `manifest.json` | a renaming is explicit and must match a row |
| Compose | `gnd compose` | one population, one value-free record, same bytes every time |
| Check | `gnd check --composition --sources` | re-derived from the sources; each value checked in its own document |
| Disagree | the same check | the violation, with the source of every offending fact |
| Trace | `gnd witness --composition` | each premise's source facts, hence a span in each document |
| Replay | `gnd replay --composition` | the proof and the lineage, against the same record |

## Next steps

- The directory layout, the manifest, the record and every exit are in the
  [composition reference](../reference/composition.md); the sidecar format and
  the every-anchor rule are in [anchor sidecars](../reference/anchors.md).
- The witness format, including the version-2 `sources` and
  `composition_sha256` fields, is in the
  [witness contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-export/references/witness-contract.md).
- When a composed population lands many facts in a generic "item has attribute
  with value" fact type, declared generic in its `provenance`,
  `gnd discover --families fact-type` proposes proper
  fact types for recurring attributes, as a reviewed additive proposal:
  [proposing fact types from generic rows](../reference/discover.md#proposing-fact-types-from-generic-rows).
  Whether an attribute repeats a fact type you already have, or holds
  several values per item, is judged by two skills:
  [judge induced fact types with two skills](judge-induced-fact-types.md).
- The extraction half, one document at a time, is the `gnd-extract` skill in
  the [agent skill guide](../agents/index.md); a model that grows as documents
  arrive is [grow a model by additions](grow-a-model.md).
