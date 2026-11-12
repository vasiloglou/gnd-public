# 9. Let the catalogue suggest rules

In [chapter 8](08-guarded-rules.md) a person wrote the rule and the tools
showed whether it judged anything. This chapter goes the other way. The
catalogue team starts exporting which book continues which, and the reviewer
asks what rules that data already follows. Two commands answer:

| Question | Command |
|---|---|
| Which rules do a relation and a classification already obey? | `gnd discover --families guarded-join` |
| Can a rule from an outside miner name a constant, such as `horror`? | `gnd import mined-rules --target amie` |

Both write an ordinary evolve proposal. Nothing joins the model until you
preview and apply it, as in [chapter 6](06-evolution.md).

!!! note "Where these commands ship"

    The `guarded-join` family and constants in mined rules are on `main` after
    0.3.0 and are not in a published package yet. Install GND from a checkout
    of the repository to run this chapter.

Continue in the directory of chapter 8; this chapter starts from its
`bookrec-rules/rules.orm.yaml`. No miner, model account or network connection
is needed.

## A series export

The export covers three series of eight books. Each book after the first
continues the one before it, and each has one genre. One row is wrong:
`orbit-8`, the last book of a science series, is filed under `fantasy`.

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

home = Path("bookrec-rules")
model = json.loads((home / "rules.orm.yaml").read_text())
model["fact_types"].append({
    "id": "book_continues_book",
    "reading": "{Book} continues {Book}",
    "roles": [{"object_type": "book", "role_name": "sequel"},
              {"object_type": "book", "role_name": "earlier"}],
})
(home / "catalogue.orm.yaml").write_text(json.dumps(model, indent=2) + "\n")

genres, links = [], []
for series, genre in {"tide": "fantasy", "orbit": "science", "crypt": "horror"}.items():
    for volume in range(1, 9):
        genres.append({"book": f"{series}-{volume}", "genre": genre})
        if volume > 1:
            links.append({"sequel": f"{series}-{volume}", "earlier": f"{series}-{volume - 1}"})
next(row for row in genres if row["book"] == "orbit-8")["genre"] = "fantasy"
export = {
    "population": {
        "model": "catalogue.orm.yaml",
        "model_id": model["model_id"],
        "source": "tool-output",
        "producer": "catalogue-export 2.1.0 @ shelf-2026-11",
        "covers": ["book_has_genre", "book_continues_book"],
    },
    "facts": {"book_has_genre": genres, "book_continues_book": links},
}
(home / "catalogue.population.json").write_text(json.dumps(export, indent=2) + "\n")
print(f"Wrote catalogue.orm.yaml and catalogue.population.json: {len(genres)} genres, {len(links)} sequel links")
```

```text
Wrote catalogue.orm.yaml and catalogue.population.json: 24 genres, 21 sequel links
```

The header says a program produced these facts: `source: tool-output` with a
`producer` naming the program and its revision. GND records the label and does
not run or verify the program. The export holds no recommendation, so the four
recommendation rules have nothing to judge. `--allow-vacuous` accepts that as
the only shortfall:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate bookrec-rules/catalogue.orm.yaml
gnd check bookrec-rules/catalogue.orm.yaml bookrec-rules/catalogue.population.json --allow-vacuous | grep "pass="
```

```text
OK: bookrec-rules/catalogue.orm.yaml is a valid GND ORM model
pass=3 fail=0 warning=0 unchecked=0 vacuous=4
```

Without the option the same check exits 2, as in
[chapter 8](08-guarded-rules.md#an-idle-rule-and-an-empty-table-are-different-outcomes).

## Find every link in a sequel loop

A series should have a reading order. Give the sequel relation an acyclic
rule, then check a copy of the export with one reversed link in each of two
series. The verdict names both groups and reports all four links, including
the two original links that now complete a loop.

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path
import subprocess

home = Path("bookrec-rules")
model = json.loads((home / "catalogue.orm.yaml").read_text())
population = json.loads((home / "catalogue.population.json").read_text())
series = next(fact for fact in model["fact_types"] if fact["id"] == "book_continues_book")
series["constraints"] = [{
    "id": "series_order", "type": "ring", "variant": "acyclic",
    "source": "user-supplied", "status": "confirmed", "modality": "alethic",
    "remedy": "Check which book came first.",
    "provenance": {"user_quote": "A book cannot continue itself, directly or through a series."},
}]
for name in ("orbit", "tide"):
    population["facts"]["book_continues_book"].append(
        {"sequel": f"{name}-1", "earlier": f"{name}-2"}
    )
model_path = home / "loops.orm.json"
population_path = home / "loops.population.json"
model_path.write_text(json.dumps(model))
population_path.write_text(json.dumps(population))
run = subprocess.run(
    ["gnd", "check", str(model_path), str(population_path), "--rule-ids", "--format", "json"],
    capture_output=True, text=True, timeout=60,
)
assert run.returncode == 1, run.stderr
verdict = next(row for row in json.loads(run.stdout)["verdicts"]
               if row["address"] == "constraint:series_order")
assert "2 strongly connected groups" in verdict["message"]
assert verdict["offending_facts"] == [
    ["orbit-1", "orbit-2"], ["orbit-2", "orbit-1"],
    ["tide-1", "tide-2"], ["tide-2", "tide-1"],
]
for sequel, earlier in verdict["offending_facts"]:
    print(f"{sequel} continues {earlier}")
```

```text
orbit-1 continues orbit-2
orbit-2 continues orbit-1
tide-1 continues tide-2
tide-2 continues tide-1
```

## Ask the data for joined rules

Name the relation and the classifier, each with its two roles in order.
`guarded-join` is opt-in: the default families never propose guarded rules.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd discover bookrec-rules/catalogue.orm.yaml bookrec-rules/catalogue.population.json \
  --families guarded-join \
  --joined-relation book_continues_book:sequel:earlier \
  --joined-classifier book_has_genre:book:genre \
  --actor catalogue-reviewer --requested-at 2026-11-11T00:00:00Z \
  --out bookrec-rules/joined.proposal.json --report bookrec-rules/joined.report.json
```

```text
GND DISCOVER
MODEL bookrec-rules/catalogue.orm.yaml
POPULATION bookrec-rules/catalogue.population.json
EMITTED 5
  constraints[5] guarded-join support=8
  constraints[6] guarded-join support=7
  constraints[7] guarded-join support=7
  constraints[8] guarded-join support=6
  constraints[9] guarded-join support=6
NEAR MISSES 1
  guarded-join violations=1/21
REJECTED vacuous=0 unchecked=0 fail=0 warning=5
SUPPRESSED
GUARDED JOIN compared=9
WORK total=0
PROPOSAL bookrec-rules/joined.proposal.json
```

Five rules were emitted and one came close. The report says what they are:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

home = Path("bookrec-rules")
report = json.loads((home / "joined.report.json").read_text())
links = json.loads((home / "catalogue.population.json").read_text())["facts"]["book_continues_book"]

def genre_of(atom):
    return atom["bind"]["genre"]

for row in report["emitted"]:
    rule, support = row["constraint"], row["support"]
    print(f'{rule["id"]}: a {genre_of(rule["antecedent"][1])} book never continues'
          f' a {genre_of(rule["consequent"]["absence"])} book'
          f' ({support["numerator"]}/{support["denominator"]})')
for miss in report["near_misses"]:
    print(f'near miss {miss["constraint"]["id"]}: a sequel has the genre of the book it continues,'
          f' broken by {miss["violations"]} of {miss["subjects"]} links')
    for fact_id in miss["counterexamples"]:
        print("  counterexample", fact_id, links[int(fact_id.split("#")[1])])
```

```text
gj_01dc5d4dd89d3397ce70abf9: a fantasy book never continues a horror book (8/8)
gj_6eb7d5accf6cd2486ce37b83: a horror book never continues a fantasy book (7/7)
gj_70b945bb1b07c2e41d3ce3e4: a horror book never continues a science book (7/7)
gj_2eef81a7b996742b086e01f3: a science book never continues a fantasy book (6/6)
gj_7b4fc8d9744e8604a618393e: a science book never continues a horror book (6/6)
near miss gj_a142606e604de5a6f24627d2: a sequel has the genre of the book it continues, broken by 1 of 21 links
  counterexample ft6#13 {'sequel': 'orbit-8', 'earlier': 'orbit-7'}
```

Read the two shapes:

- **A forbidden pair** says no sequel of one genre continues a book of
  another. Its support is the number of sequel links that leave the first
  genre. Six ordered pairs of different genres exist; five were emitted. The
  sixth, a fantasy book continuing a science book, is in the data: that is
  `orbit-8`.
- **The same-class rule** is the one the reviewer had in mind: a sequel has
  the genre of the book it continues. It fails on one link of 21, so it is a
  **near miss**: reported with its counterexample, and left out of the
  proposal. The counterexample is the fact id of the offending link, row 13 of
  `book_continues_book` in population order.

The near miss is the useful result here. It points at one row to correct in
the catalogue, or one exception to accept. Every emitted rule is `induced`,
`proposed` and `deontic`: a suggestion that warns, never a blocking rule. The
checker confirmed each one on this population before the proposal was written.

To ask the same-class question about some targets only, add a marker. This
run restricts it to links whose earlier book is `horror`:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd discover bookrec-rules/catalogue.orm.yaml bookrec-rules/catalogue.population.json \
  --families guarded-join \
  --joined-relation book_continues_book:sequel:earlier \
  --joined-classifier book_has_genre:book:genre \
  --joined-marker 'book_has_genre:book:genre="horror"' \
  --actor catalogue-reviewer --requested-at 2026-11-11T00:00:00Z \
  --out bookrec-rules/marked.proposal.json --report bookrec-rules/marked.report.json | grep -E "EMITTED|support|NEAR"
```

```text
EMITTED 6
  constraints[5] guarded-join support=8
  constraints[6] guarded-join support=7
  constraints[7] guarded-join support=7
  constraints[8] guarded-join support=6
  constraints[9] guarded-join support=6
  constraints[10] guarded-join support=7
NEAR MISSES 0
```

The five forbidden pairs return, and a sixth rule joins them: a book that
continues a horror book is a horror book, with support 7. No link breaks it,
so it is emitted instead of being a near miss. The
[discovery reference](../reference/discover.md#discover-guarded-joins)
defines support, the marker, the pair cap and the refusals.

## Import a mined rule that names a genre

An outside rule miner can find that last rule too. Export the catalogue as typed
triples for an AMIE-style miner:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd export ilp bookrec-rules/catalogue.orm.yaml --population bookrec-rules/catalogue.population.json \
  --target amie --out bookrec-rules/amie-export | head -1
head -3 bookrec-rules/amie-export/amie/facts.tsv
```

```text
EXPORTED 45 facts in 2 relations to bookrec-rules/amie-export (amie); skipped 5 fact types
book:crypt-1	f_book_has_genre	genre:horror
book:crypt-2	f_book_continues_book	book:crypt-1
book:crypt-2	f_book_has_genre	genre:horror
```

Every value is spelled with its object type: `book:crypt-1`, `genre:horror`.
A rule may use such a spelling as a **typed constant** in any position.

This tutorial does not run a miner. The next block writes the lines a miner
would print, as a stand-in, with the run record that binds them to the
population and the exported facts by SHA-256. Three rules, one per file:

<!-- gnd-run expect=0 output=stdout -->
```python
import hashlib
import json
from pathlib import Path

home = Path("bookrec-rules")
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()

def stand_in(name, genre, support):
    rule = (f"?a  f_book_continues_book  ?b  ?b  f_book_has_genre  genre:{genre}"
            f"   => ?a  f_book_has_genre  genre:{genre}")
    rules = home / f"{name}.rules.tsv"
    rules.write_text("\t".join([rule, "0.875", "1", "1", str(support), "7", "7", "?a"]) + "\n")
    (home / f"{name}.run.json").write_text(json.dumps({
        "schema_version": "gnd-mined-run/1",
        "learner": {"name": "amie", "version": "tutorial-stand-in"},
        "rules_sha256": sha(rules),
        "population_sha256": sha(home / "catalogue.population.json"),
        "facts_sha256": sha(home / "amie-export/amie/facts.tsv"),
    }, indent=2) + "\n")
    print(f"{name}.rules.tsv: {rule}")

stand_in("horror", "horror", 7)
stand_in("misspelt", "Horror", 7)
stand_in("science", "science", 6)
```

```text
horror.rules.tsv: ?a  f_book_continues_book  ?b  ?b  f_book_has_genre  genre:horror   => ?a  f_book_has_genre  genre:horror
misspelt.rules.tsv: ?a  f_book_continues_book  ?b  ?b  f_book_has_genre  genre:Horror   => ?a  f_book_has_genre  genre:Horror
science.rules.tsv: ?a  f_book_continues_book  ?b  ?b  f_book_has_genre  genre:science   => ?a  f_book_has_genre  genre:science
```

Import the first:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd import mined-rules bookrec-rules/catalogue.orm.yaml bookrec-rules/horror.rules.tsv \
  --population bookrec-rules/catalogue.population.json --reported bookrec-rules/horror.run.json \
  --target amie --out bookrec-rules/horror.proposal.json \
  --actor catalogue-reviewer --requested-at 2026-11-11T00:00:00Z
```

```text
IMPORTED 1 mined rules -> bookrec-rules/horror.proposal.json
  rule 0 constraints[5]: holds on 7 of 7 head pairs
```

GND does not take the miner's word for the support. It counts the rule itself
over the population and admits it only when the count equals the reported
figure and the rule holds on every pair. The other two files are refused,
each with exit 3 and no proposal:

<!-- gnd-run expect=0 output=stdout -->
```python
import subprocess

for name in ("misspelt", "science"):
    run = subprocess.run(
        ["gnd", "import", "mined-rules", "bookrec-rules/catalogue.orm.yaml", f"bookrec-rules/{name}.rules.tsv",
         "--population", "bookrec-rules/catalogue.population.json", "--reported", f"bookrec-rules/{name}.run.json",
         "--target", "amie", "--out", f"bookrec-rules/{name}.proposal.json",
         "--actor", "catalogue-reviewer", "--requested-at", "2026-11-11T00:00:00Z"],
        capture_output=True, text=True, timeout=120)
    print(name, "exit", run.returncode, "-", (run.stdout + run.stderr).strip())
```

```text
misspelt exit 3 - rule 0: covers-nothing: no binding satisfies the body, so the rule has no support
science exit 3 - rule 0: does-not-hold: 6 of 7 head pairs hold; only rules that hold are admitted (D11 (o))
```

- `genre:Horror` is the typo of chapter 8 in a mined rule. A constant is
  matched exactly, no fact has that genre, and the rule is refused
  `covers-nothing` instead of being admitted as a rule that judges nothing.
- The science rule is the near miss again: `orbit-8` continues a science book
  and is filed under fantasy. Only rules that hold are admitted.

## Preview and apply under the additive policy

The admitted proposal adds a rule about `book_has_genre`, a fact type that
already has data. The additive policy admits that only with proof that the
data satisfies the rule, given by `--check-population`:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve preview bookrec-rules/catalogue.orm.yaml bookrec-rules/horror.proposal.json \
  --workspace bookrec-rules --records bookrec-rules/mined-records --out bookrec-rules/mined.preview.json \
  --policy additive --check-population bookrec-rules/catalogue.population.json | grep -E "breaking|affected|policy"
```

```text
  breaking: false
  affected: model.constraints[guarded:new:0]
  policy: additive
```

Apply repeats the reviewed options. Then the catalogue model has a sixth
rule, and it judges something:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve apply bookrec-rules/catalogue.orm.yaml bookrec-rules/horror.proposal.json \
  --preview bookrec-rules/mined.preview.json --workspace bookrec-rules --records bookrec-rules/mined-records \
  --policy additive --check-population bookrec-rules/catalogue.population.json > /dev/null
python -c "
import json
rule = json.load(open('bookrec-rules/catalogue.orm.yaml'))['constraints'][-1]
print(rule['source'], rule['status'], rule['modality'], rule['provenance']['induction']['method'], rule['provenance']['induction']['support'])"
gnd check bookrec-rules/catalogue.orm.yaml bookrec-rules/catalogue.population.json --guarded-diagnostics --allow-vacuous | grep -E 'constraints\[5\]: bindings|pass='
```

```text
induced proposed deontic ilp-amie {'numerator': 7, 'denominator': 7}
pass=4 fail=0 warning=0 unchecked=0 vacuous=4
GUARDED constraints[5]: bindings=7
```

The mined rule has seven bindings, the seven links into the horror series.
A mined rule carries no author id, so the report addresses it by position,
`constraints[5]`. It stays `proposed` and `deontic` until a person confirms it.

## Where each request is shown

The commands of chapters 8 and 9 came from numbered requests by one reporter.
This table maps each request to a worked example. BookRec is used where a
chapter runs it; otherwise the link goes to the page that already does, in
the expense context where one exists.

### Rule-check requests

| Request | What it asked for | Worked example |
|---|---|---|
| GR-D1 (issue 92) | rule id and author's `remedy` in each verdict | [Chapter 8: fix the literal and read the verdict](08-guarded-rules.md#fix-the-literal-and-read-the-verdict) |
| GR-D2 (issue 93) | judge a change against a baseline population | [Chapter 8: two editions or two populations](08-guarded-rules.md#two-editions-or-two-populations); CI gate in [Adopt rules with a baseline](../how-to/adopt-rules-with-a-baseline.md#compare-with-main) |
| GR-D3 (issue 94) | every loop edge of an `acyclic` violation | [Find every link in a sequel loop](#find-every-link-in-a-sequel-loop) |
| GR-D4 (issue 95) | shared definitions, project-owned policies | [Two-team expense tutorial](../tutorials/shared-expense-policies.md) and [its commands](../how-to/shared-expense-policies-commands.md) |
| GR-D5 (issue 96) | accept rules with nothing to judge | [`--allow-vacuous` on the series export](#a-series-export); [Adopt rules with a baseline](../how-to/adopt-rules-with-a-baseline.md#accept-a-rule-that-has-nothing-to-judge-yet) |
| GR-D6 (issue 97) | label facts a program produced | [`source: tool-output` and `producer` on the series export](#a-series-export) |
| GR-D7 (issue 118) | a release that carries the rule checks | [Release notes, 0.2.0](../release-notes.md#rule-checks-for-projects-that-already-break-their-rules) |
| GR-D8 (issue 179) | a failing and an active passing case per guarded rule | [Chapter 8: generate a failing and a passing case](08-guarded-rules.md#generate-failing-and-active-passing-cases) |
| GR-D9 (issue 180) | two rule editions on one population | [Chapter 8: compare two editions](08-guarded-rules.md#compare-two-editions-on-the-same-output) |
| GR-D10 (issue 181) | guarded rules from joined facts | [Ask the data for joined rules](#ask-the-data-for-joined-rules) |
| GR-D11 (issue 182) | typed constants in mined rules | [Import a mined rule that names a genre](#import-a-mined-rule-that-names-a-genre) |
| GR-D12 (issue 183) | say when a guarded rule matched nothing; warn on an out-of-domain literal | [Chapter 8: binding counts](08-guarded-rules.md#ask-each-guard-how-many-bindings-it-had) and [the validation warning](08-guarded-rules.md#let-validation-catch-the-typo) |

GR-D1 to GR-D7 are in published releases. GR-D8 to GR-D12 are on `main` after
0.3.0.

### Earlier requests, shipped

| Request | What shipped | Worked example |
|---|---|---|
| GR-T7 (issue 66) | `gnd why-not`: why a derived fact is missing | [Repair a claim that does not derive](../how-to/repair-a-missing-claim.md), on a refunds claim; BookRec's derived eligibility list is in [chapter 7](07-native.md#go-further-the-complete-list) |
| GR-T8 (issue 70) | near-miss values in why-not; disclosure mode | [When the values are spelled differently](../how-to/repair-a-missing-claim.md#when-the-values-are-spelled-differently); [Run GND for internal or customer readers](../how-to/disclosure-mode.md) |
| GR-T9 (issue 72) | rule read-back | [Grow a model: read the derivation rules back](../how-to/grow-a-model.md#read-the-derivation-rules-back) |
| GR-T10 (issue 73) | several anchors per role, composition, witness lineage | [From several documents to one checked answer](../how-to/compose-documents.md) |
| GR-T11 (issue 74) | unattended model-from-text; unchecked spans counted | [Grow a model: when nobody reviews the model](../how-to/grow-a-model.md#when-nobody-reviews-the-model) |
| GR-T12 (issue 75) | additive evolve policy | [Preview and apply under the additive policy](#preview-and-apply-under-the-additive-policy); [Grow a model, round 1](../how-to/grow-a-model.md#round-1-a-returns-note-arrives) |
| GR-T13 (issue 76) | duplicate-shape report | [Shape report](../reference/evolve-policy.md#shape-report) |
| GR-T14 (issue 77) | fact-type proposals from generic rows | [Judge induced fact types with two skills](../how-to/judge-induced-fact-types.md) |
| GR-T15 (issue 78) | extraction guidelines | [Grow a model: give the extractor guidelines](../how-to/grow-a-model.md#give-the-extractor-guidelines) |
| GR-T17 (issue 104) | constraints admitted on clean data; unattended growth procedure | [`--check-population` in this chapter](#preview-and-apply-under-the-additive-policy); [Admitting a constraint on clean data](../reference/evolve-policy.md#admitting-a-constraint-on-clean-data) |

For a reviewed change to a populated model without the additive policy, the
expense tutorial's [chapter 3](../expense/03-evolution.md) adds currencies
through the same preview and apply.

## Limits

- **Support is a claim about one population.** It is bound to the population's
  digest. Re-run discovery, or check the applied model, when the data changes.
- **Suggestions are not policy.** Five forbidden pairs fit this export. Whether
  a fantasy series may ever continue as horror is the product owner's call.
- **The classifier must be total and single-valued.** Each book on a link
  needs exactly one genre, or the family refuses and says why in
  `joined_rules`.
- **The stand-in is not a miner.** The rule lines here were written by hand.
  The [ILP bridge reference](../reference/ilp-bridge.md#amie-style-miner)
  describes the run of record with AMIE and every refusal.
- **Admission is all-or-nothing.** One refused rule in a file refuses the file.

**Exercise:** Correct `orbit-8` to `science` in a copy of the export and run
the first discovery again. Predict the number of emitted rules. It is seven:
the sixth forbidden pair now holds, and the same-class rule is emitted with
support 21 of 21 instead of being a near miss.
