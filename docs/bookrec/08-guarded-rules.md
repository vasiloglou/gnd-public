# 8. Add a rule and prove it judges something

BookRec's catalogue gains a horror shelf, and the product owner adds one line
to the brief: **never recommend a horror book to a minor**. You will write that
rule, watch it pass a recommendation it should have refused, and learn why from
the report. Then you will generate a failing and a passing example for every
rule, and compare the old and the new rules on the same output before the
change ships.

Each step answers one question about a guarded rule:

| Question | Command |
|---|---|
| Which rule is this verdict about, and what should I do? | `gnd check --rule-ids` |
| Did the rule judge anything in this population? | `gnd check --guarded-diagnostics` |
| What does a failing and a passing input look like? | `gnd synth --guarded-cases` |
| What changes for this output if the new rules ship? | `gnd check --baseline-model` |

!!! note "Where these commands ship"

    `--guarded-diagnostics`, `--baseline-model` and `--guarded-cases` are on
    `main` after 0.3.0 and are not in a published package yet. Install GND
    from a checkout of the repository to run this chapter. `--rule-ids`,
    `--baseline` and `--allow-vacuous` have shipped since 0.2.0, as the
    [release notes](../release-notes.md#rule-checks-for-projects-that-already-break-their-rules)
    record.

    Case generation needs the optional `synth` extra. From the checkout, run
    `uv sync --locked --extra synth`, then activate the environment before
    running the commands below.

No model account, native solver or network connection is needed. The chapter
does not need the PyRel environment of [chapter 7](07-native.md).

## Start from installed resources

Work in the same directory as before. This chapter makes its own copy of the
BookRec resources, so the models you evolved in [chapter 6](06-evolution.md)
stay as you left them.

<!-- gnd-run expect=0 output=stdout -->
```python
from importlib.resources import files
import shutil

shutil.copytree(str(files("gnd").joinpath("examples", "bookrec")), "bookrec-rules")
print("Copied the BookRec resources to bookrec-rules/")
```

```text
Copied the BookRec resources to bookrec-rules/
```

## A new shelf and a new rule

The catalogue team adds one book, and Ada tells BookRec she likes the new shelf:

| Change | Fact |
|---|---|
| New book `crypt` | primary genre `horror`, not adult-rated |
| Ada's preferences | `fantasy` and now `horror` |
| Today's candidate | recommends `crypt` to Ada and `night` to Ben |

Ada is a minor. The age rule from [chapter 1](01-model.md) does not stop this
candidate, because `crypt` carries no adult flag. The new brief line should.

The author writes it as a guarded rule: for each recommendation of a horror
book, the reader must not be a minor.

```yaml
id: no_horror_for_minors
type: guarded
modality: alethic
remedy: Replace the book with one outside the horror genre for this reader.
antecedent:
  - fact_type: recommendation
    bind: {user: "$u", book: "$b"}
  - fact_type: book_has_genre
    bind: {book: "$b", genre: "Horror"}
consequent:
  absence:
    fact_type: user_is_minor
    bind: {user: "$u"}
```

Two fields are new to this tutorial. `id` is the name the author gives the
rule; the three rules of chapter 1 already have one. `remedy` is the author's
advice, printed with the verdict when the rule fails. The value `"Horror"` is a
**literal**: the second antecedent atom matches only genre facts with exactly
that value.

The next block adds the rule to a draft copy of the model and writes today's
candidate. Both are new files; the shipped model and populations are not edited.

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

home = Path("bookrec-rules")
model = json.loads((home / "model.orm.yaml").read_text())
model["constraints"].append({
    "type": "guarded",
    "source": "explicit",
    "status": "confirmed",
    "modality": "alethic",
    "provenance": {"user_quote": "Never recommend a horror book to a minor."},
    "id": "no_horror_for_minors",
    "remedy": "Replace the book with one outside the horror genre for this reader.",
    "antecedent": [
        {"fact_type": "recommendation", "bind": {"user": "$u", "book": "$b"}},
        {"fact_type": "book_has_genre", "bind": {"book": "$b", "genre": "Horror"}},
    ],
    "consequent": {"absence": {"fact_type": "user_is_minor", "bind": {"user": "$u"}}},
})
(home / "draft.orm.yaml").write_text(json.dumps(model, indent=2) + "\n")

candidate = json.loads((home / "seed.population.json").read_text())
facts = candidate["facts"]
facts["book_has_genre"].append({"book": "crypt", "genre": "horror"})
facts["user_prefers_genre"].append({"user": "ada", "genre": "horror"})
facts["recommendation"] = [{"user": "ada", "book": "crypt"}, {"user": "ben", "book": "night"}]
(home / "horror-for-minor.population.json").write_text(json.dumps(candidate, indent=2) + "\n")
print("Wrote draft.orm.yaml (four guarded rules) and horror-for-minor.population.json")
```

```text
Wrote draft.orm.yaml (four guarded rules) and horror-for-minor.population.json
```

## A passing check that judged nothing

The draft is a valid model:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate bookrec-rules/draft.orm.yaml
```

```text
OK: bookrec-rules/draft.orm.yaml is a valid GND ORM model
```

Now check today's candidate, the one that offers Ada a horror book:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check bookrec-rules/draft.orm.yaml bookrec-rules/horror-for-minor.population.json
```

```text
BLOCKING (alethic)
  (none)
ADVISORY (deontic)
  (none)
pass=6 fail=0 warning=0 unchecked=0 vacuous=0
COVERAGE
  recommendation: declared, facts=2
  user_rated_book: declared, facts=2
  user_is_minor: declared, facts=1
  book_rated_adult: declared, facts=1
  book_has_genre: declared, facts=6
  user_prefers_genre: declared, facts=3
```

Six passes and exit 0. A publication boundary like the one in
[chapter 4](04-application.md) would publish this candidate. Yet the facts have
not changed: Ada is a minor and `crypt` is a horror book. A pass tells you no
binding broke the rule. It does not tell you the rule had any binding to judge.

## Ask each guard how many bindings it had

`--guarded-diagnostics` adds one line per guarded rule to the same check:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check bookrec-rules/draft.orm.yaml bookrec-rules/horror-for-minor.population.json --guarded-diagnostics
```

```text
BLOCKING (alethic)
  (none)
ADVISORY (deontic)
  (none)
pass=6 fail=0 warning=0 unchecked=0 vacuous=0
COVERAGE
  recommendation: declared, facts=2
  user_rated_book: declared, facts=2
  user_is_minor: declared, facts=1
  book_rated_adult: declared, facts=1
  book_has_genre: declared, facts=6
  user_prefers_genre: declared, facts=3
GUARDED constraint:unread_only: bindings=2
GUARDED constraint:age_appropriate: bindings=1
GUARDED constraint:preferred_genre: bindings=2
GUARDED constraint:no_horror_for_minors: bindings=0 (first empty antecedent atom 1)
```

A **binding** is one assignment of the rule's variables that satisfies the
whole antecedent. The older rules each judged one or two. The new rule judged
none, and the report says where the antecedent ran dry: atom 1, counting from
zero. Atom 0 is the recommendation, and it matched. Atom 1 asks for a book
whose genre is `Horror`. The catalogue writes `horror`. Literals are compared
exactly, so no recommended book matched and the rule had nothing left to judge.

The JSON report carries the same two facts on every guarded verdict. Its
report version is 16:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check bookrec-rules/draft.orm.yaml bookrec-rules/horror-for-minor.population.json --guarded-diagnostics --format json \
  | python -c "import json, sys; [print(v['address'], v['verdict'], v['guarded_antecedent']) for v in json.load(sys.stdin)['verdicts'] if 'guarded_antecedent' in v]"
```

```text
constraint:unread_only pass {'binding_count': 2, 'first_empty_atom_index': None}
constraint:age_appropriate pass {'binding_count': 1, 'first_empty_atom_index': None}
constraint:preferred_genre pass {'binding_count': 2, 'first_empty_atom_index': None}
constraint:no_horror_for_minors pass {'binding_count': 0, 'first_empty_atom_index': 1}
```

The verdict is still `pass` and the exit is still 0. The option adds evidence
to the report; it changes no verdict and no exit code. A gate that must refuse
an idle rule reads `binding_count` itself.

### An idle rule and an empty table are different outcomes

Zero bindings is not always a mistake. Compare three populations under one rule:

| The population holds | Verdict | Exit | Diagnostic line |
|---|---|---|---|
| no recommendation at all | `vacuous` | 2 | `bindings=0` |
| recommendations, none of a `Horror` book | `pass` | 0 | `bindings=0 (first empty antecedent atom 1)` |
| a recommendation the antecedent matches | `pass` or `fail` | 0 or 1 | `bindings=1` or more |

The first row is the case [chapter 2](02-facts.md) called vacuous evidence: a
fact type the rule reads is empty, the check says so, and it exits 2. Write a
day with no recommendations and see it:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

home = Path("bookrec-rules")
quiet = json.loads((home / "horror-for-minor.population.json").read_text())
quiet["facts"]["recommendation"] = []
(home / "no-recommendations.population.json").write_text(json.dumps(quiet, indent=2) + "\n")
print("Wrote no-recommendations.population.json")
```

```text
Wrote no-recommendations.population.json
```

<!-- gnd-run expect=2 output=stdout -->
```sh
gnd check bookrec-rules/draft.orm.yaml bookrec-rules/no-recommendations.population.json --guarded-diagnostics
```

```text
BLOCKING (alethic)
  [vacuous] constraint:unread_only (constraints[0]): Fact type(s) 'recommendation' contain no facts in this population — constraint is vacuous, not evaluated.
  [vacuous] constraint:age_appropriate (constraints[1]): Fact type(s) 'recommendation', 'user_is_minor' contain no facts in this population — constraint is vacuous, not evaluated.
  [vacuous] constraint:no_horror_for_minors (constraints[3]): Fact type(s) 'recommendation', 'book_has_genre' contain no facts in this population — constraint is vacuous, not evaluated.
    remedy: Replace the book with one outside the horror genre for this reader.
ADVISORY (deontic)
  [vacuous] constraint:preferred_genre (constraints[2]): Fact type(s) 'recommendation', 'book_has_genre' contain no facts in this population — constraint is vacuous, not evaluated.
pass=2 fail=0 warning=0 unchecked=0 vacuous=4
COVERAGE
  recommendation: declared, facts=0
  user_rated_book: declared, facts=2
  user_is_minor: declared, facts=1
  book_rated_adult: declared, facts=1
  book_has_genre: declared, facts=6
  user_prefers_genre: declared, facts=3
GUARDED constraint:unread_only: bindings=0
GUARDED constraint:age_appropriate: bindings=0
GUARDED constraint:preferred_genre: bindings=0
GUARDED constraint:no_horror_for_minors: bindings=0
```

The second row is the one this chapter is about. Every table the rule reads
has rows, the join between them is empty, and the check passes without a word
unless you ask for the diagnostic. The count tells you the rule was idle. You
decide whether that is expected. Here it is not: the candidate recommends a
horror book, so a horror rule with zero bindings is wrong.

## Let validation catch the typo

The diagnostic found the mistake after a candidate had already passed. The
model can catch it earlier if it knows which genres exist. Declare the
catalogue's genre list as a value constraint, still without fixing the literal:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

home = Path("bookrec-rules")
model = json.loads((home / "draft.orm.yaml").read_text())
model["constraints"].append({
    "type": "value",
    "object_type": "genre",
    "allowed": ["fantasy", "science", "horror"],
    "source": "explicit",
    "status": "confirmed",
    "modality": "alethic",
    "provenance": {"user_quote": "The catalogue has three genres: fantasy, science and horror."},
    "id": "known_genres",
})
(home / "declared.orm.yaml").write_text(json.dumps(model, indent=2) + "\n")
print("Wrote declared.orm.yaml: the draft plus the genre list")
```

```text
Wrote declared.orm.yaml: the draft plus the genre list
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate bookrec-rules/declared.orm.yaml
```

```text
WARNING at $.constraints[3].antecedent[1].bind[genre]: Literal lies outside the value domain declared by constraints[4]. [semantic:guarded-literal-outside-domain]
OK: bookrec-rules/declared.orm.yaml is a valid GND ORM model
```

Validation now names the exact place: the `genre` binding of antecedent atom 1
in `constraints[3]`, and the constraint that excludes it. It is a warning, so
the model still loads and the exit is still 0. A literal in a consequent is
checked the same way, which the binding count cannot do: a misspelt literal in
an `absence` consequent leaves the antecedent, and so the count, untouched.

Validation can only warn about a domain the model declares. Without
`known_genres` there is nothing to compare `Horror` against, and the binding
count is the evidence you have.

## Fix the literal and read the verdict

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

home = Path("bookrec-rules")
model = json.loads((home / "declared.orm.yaml").read_text())
rule = next(row for row in model["constraints"] if row.get("id") == "no_horror_for_minors")
rule["antecedent"][1]["bind"]["genre"] = "horror"
(home / "rules.orm.yaml").write_text(json.dumps(model, indent=2) + "\n")
print("Wrote rules.orm.yaml: genre literal is now", rule["antecedent"][1]["bind"]["genre"])
```

```text
Wrote rules.orm.yaml: genre literal is now horror
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate bookrec-rules/rules.orm.yaml
```

```text
OK: bookrec-rules/rules.orm.yaml is a valid GND ORM model
```

The same candidate **should now fail**:

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check bookrec-rules/rules.orm.yaml bookrec-rules/horror-for-minor.population.json --guarded-diagnostics
```

```text
BLOCKING (alethic)
  [fail] constraint:no_horror_for_minors (constraints[3]): Guarded absence consequent evaluated over bindings=1 — violated by bindings: {'$u': 'ada', '$b': 'crypt'}.
    remedy: Replace the book with one outside the horror genre for this reader.
ADVISORY (deontic)
  (none)
pass=6 fail=1 warning=0 unchecked=0 vacuous=0
COVERAGE
  recommendation: declared, facts=2
  user_rated_book: declared, facts=2
  user_is_minor: declared, facts=1
  book_rated_adult: declared, facts=1
  book_has_genre: declared, facts=6
  user_prefers_genre: declared, facts=3
GUARDED constraint:unread_only: bindings=2
GUARDED constraint:age_appropriate: bindings=1
GUARDED constraint:preferred_genre: bindings=2
GUARDED constraint:no_horror_for_minors: bindings=1
```

The rule has one binding and that binding breaks it: Ada and `crypt`. Two
things in the failing line come from `--rule-ids`, which
`--guarded-diagnostics` switches on:

- The verdict is named `constraint:no_horror_for_minors`, the id its author
  wrote, with the position `constraints[3]` in brackets. Chapters 2 and 5
  matched failures by position. A position moves when a rule is inserted above
  it; an id does not.
- The `remedy` line is the author's advice. A producer, human or agent, reads
  what to do next without opening the model.

The diagnostic keeps its value after the fix. The seed population of chapter 2
recommends no horror book, and the rule is idle there for a good reason:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check bookrec-rules/rules.orm.yaml bookrec-rules/seed.population.json --guarded-diagnostics | grep GUARDED
```

```text
GUARDED constraint:unread_only: bindings=2
GUARDED constraint:age_appropriate: bindings=1
GUARDED constraint:preferred_genre: bindings=2
GUARDED constraint:no_horror_for_minors: bindings=0 (first empty antecedent atom 1)
```

## Generate failing and active passing cases

You found the typo because you had a hand-written candidate that ought to
fail. For the other rules, and for the next rule someone adds, `gnd synth` can
build that pair for you:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd synth bookrec-rules/rules.orm.yaml --guarded-cases --out bookrec-rules/cases --seed 17
```

```text
OK: wrote bookrec-rules/cases/guarded-cases.json
```

For each supported guarded rule the command tries to construct two small populations: one where
the rule fails and one where it passes. Both are **active**: the antecedent
has at least one binding, so the passing case cannot be the idle pass you just
debugged. The checker must confirm the verdict and the binding count of each
case before anything is written. The manifest lists them:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

manifest = json.loads(Path("bookrec-rules/cases/guarded-cases.json").read_text())
print(manifest["schema_version"], "seed", manifest["seed"])
for rule in manifest["rules"]:
    for case in rule["cases"]:
        print(f'{rule["rule_id"]:<21} {case["kind"]:<8} verdict={case["verdict"]:<8}'
              f' bindings={case["binding_count"]} {case["population"]}')
```

```text
gnd-guarded-cases/1 seed 17
unread_only           failing  verdict=fail     bindings=1 cases/0000.fail.json
unread_only           passing  verdict=pass     bindings=1 cases/0000.pass.json
age_appropriate       failing  verdict=fail     bindings=1 cases/0001.fail.json
age_appropriate       passing  verdict=pass     bindings=1 cases/0001.pass.json
preferred_genre       failing  verdict=warning  bindings=1 cases/0002.fail.json
preferred_genre       passing  verdict=pass     bindings=1 cases/0002.pass.json
no_horror_for_minors  failing  verdict=fail     bindings=1 cases/0003.fail.json
no_horror_for_minors  passing  verdict=pass     bindings=1 cases/0003.pass.json
```

`preferred_genre` is the advisory rule of chapter 1, so its failing case is a
`warning`. Open the pair for the new rule:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

for name in ("0003.fail.json", "0003.pass.json"):
    facts = json.loads(Path("bookrec-rules/cases", "cases", name).read_text())["facts"]
    print(name, json.dumps(facts))
```

```text
0003.fail.json {"recommendation": [{"user": "maybe", "book": "old"}], "book_has_genre": [{"book": "old", "genre": "horror"}], "user_is_minor": [{"user": "maybe"}]}
0003.pass.json {"recommendation": [{"user": "maybe", "book": "old"}], "book_has_genre": [{"book": "old", "genre": "horror"}]}
```

The reader and book names are placeholder words the generator invents; with
`--seed 17` it invents the same ones each time. The two cases differ by one
fact: in the failing case the reader of the horror book is a minor, and in the
passing case that fact is gone. That one fact is the rule.

Each case also records `other_findings`: other rules that did not pass on that
small population, such as a preference warning for a reader with no declared
preferences. Read a case as an example of its own rule, not as a clean
population.

### What a generated case cannot tell you

Generated cases illustrate the rule **as written**. Run the generator on the
misspelt draft and it builds a failing case for the misspelt rule without
complaint:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd synth bookrec-rules/draft.orm.yaml --guarded-cases --out bookrec-rules/draft-cases --seed 17 > /dev/null
python -c "import json; print(json.load(open('bookrec-rules/draft-cases/cases/0003.fail.json'))['facts']['book_has_genre'])"
```

```text
[{'book': 'old', 'genre': 'Horror'}]
```

The case has a `Horror` book because the rule says `Horror`. Nothing in it
knows the catalogue writes `horror`. That knowledge is in your hand-written
candidate, `horror-for-minor.population.json`, so keep examples that come from
the intended policy beside the generated ones.

When the model declares the genre list, the generator has something to check
the literal against, and it refuses the rule instead:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd synth bookrec-rules/declared.orm.yaml --guarded-cases --out bookrec-rules/declared-cases --seed 17 > /dev/null
python -c "import json; [print(r['rule_id'], len(r['cases']), 'cases, reason:', r['reason']) for r in json.load(open('bookrec-rules/declared-cases/guarded-cases.json'))['rules']]"
```

```text
unread_only 2 cases, reason: None
age_appropriate 2 cases, reason: None
preferred_genre 2 cases, reason: None
no_horror_for_minors 0 cases, reason: antecedent-unreachable
```

`antecedent-unreachable` means a literal in the antecedent lies outside its
declared value domain, so no population the model allows can make the rule
fire. The command still exits 0: a manifest may hold rules it could not serve,
each with a reason. The other reasons are `missing-id` for a rule without an
`id`, `unsupported-shape`, `no-failing-case`, `no-passing-case` and
`search-limit`; the [synthetic data guide](../guides/synthetic-data.md#generate-examples-for-guarded-rules)
defines them.

### The other rules keep their ordinary corpus

BookRec's model also has rules that are not guarded: each book has exactly one
primary genre, and now the genre list. `gnd synth --class all` already
generates and labels cases for those. The guarded run writes that corpus
under `ordinary/`, together with a **scoped model**: your model without its
guarded rules.

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

ordinary = json.loads(Path("bookrec-rules/cases/guarded-cases.json").read_text())["ordinary"]
print("scoped model:", ordinary["model"])
print("guarded rules left out:", ", ".join(ordinary["omitted_guarded_refs"]))
for original, scoped in ordinary["constraint_refs"].items():
    print(f"  {original} -> {scoped}")
```

```text
scoped model: ordinary/scoped.orm.yaml
guarded rules left out: constraints[0], constraints[1], constraints[2], constraints[3]
  fact_types[book_has_genre].constraints[0] -> fact_types[book_has_genre].constraints[0]
  fact_types[book_has_genre].constraints[1] -> fact_types[book_has_genre].constraints[1]
  constraints[4] -> constraints[0]
```

The map shows where each ordinary rule sits in the scoped model. Measure the
checker against that corpus with the scoped model:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd measure bookrec-rules/cases/ordinary/scoped.orm.yaml --populations bookrec-rules/cases/ordinary/corpus
```

```text
MEASUREMENT bookrec-rules/cases/ordinary/scoped.orm.yaml [pool=faker] populations=20
COVERAGE 1.0000 (12/12 applicable (family, case_kind) cells; 3 not-applicable, 0 missing)
...
VIOLATING CASES: isolating=6 set-attributed=1 wrong_attribution=0
CHECKER DEFECTS: 0
```

The `...` stands for the per-rule rates, which the
[synthetic data guide](../guides/synthetic-data.md) explains. All 20 labelled
populations were scored and no checker defect was found. The corpus is
bound to the scoped model's digest. Measuring it with the full model is
refused, because the labels were not made for that model:

<!-- gnd-run expect=0 output=stdout -->
```python
import subprocess

run = subprocess.run(["gnd", "measure", "bookrec-rules/rules.orm.yaml",
                      "--populations", "bookrec-rules/cases/ordinary/corpus"],
                     capture_output=True, text=True, timeout=120)
print("exit", run.returncode)
print(run.stdout.strip().rsplit(" — ", 1)[-1])
```

```text
exit 3
a wrong-model sidecar.
```

## Compare two editions on the same output

The corrected rules are ready. Before they replace the shipped model, the
product owner asks what the change does to output BookRec already produces.
[Chapter 6](06-evolution.md) answered that question for one rule with two
separate checks and a comparison you wrote yourself. `--baseline-model` runs
both editions on the same population bytes and reports the difference by rule
id and by binding. The first model is the new edition, and the option names
the old one:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check bookrec-rules/rules.orm.yaml bookrec-rules/horror-for-minor.population.json --baseline-model bookrec-rules/model.orm.yaml
```

```text
RULE EDITIONS bookrec-rules/model.orm.yaml -> bookrec-rules/rules.orm.yaml
base check exit 0
head check exit 1
constraint:age_appropriate [paired] base=pass/alethic head=pass/alethic 0 base-only, 0 head-only, 0 standing
constraint:known_genres [added] head=pass/alethic 0 base-only, 0 head-only, 0 standing
constraint:no_horror_for_minors [added] head=fail/alethic 0 base-only, 1 head-only, 0 standing
  head-only {"$b":"crypt","$u":"ada"}
constraint:preferred_genre [paired] base=pass/deontic head=pass/deontic 0 base-only, 0 head-only, 0 standing
constraint:unread_only [paired] base=pass/alethic head=pass/alethic 0 base-only, 0 head-only, 0 standing
fact_types[book_has_genre].constraints[0] [unpaired] base=pass/alethic
fact_types[book_has_genre].constraints[1] [unpaired] base=pass/alethic
fact_types[book_has_genre].constraints[0] [unpaired] head=pass/alethic
fact_types[book_has_genre].constraints[1] [unpaired] head=pass/alethic
```

Read it top to bottom:

- The shipped edition accepts today's candidate (`base check exit 0`). The
  new edition refuses it (`head check exit 1`). The comparison itself exits 0:
  it completed, and it reports both sides without taking one.
- The three rules of chapter 1 are `paired` and unchanged.
- `known_genres` and `no_horror_for_minors` are `added`. The new rule has one
  `head-only` binding, Ada and `crypt`: a finding that exists only under the
  new edition.
- The two genre-shape rules are `unpaired`. They have no `id`, so the tool
  will not guess that `constraints[0]` of one edition is `constraints[0]` of
  the other. Give a rule an id when you want it tracked across editions.

Now repeat chapter 6's question. `strict.orm.yaml` makes the genre rule hard,
and `genre-warning.population.json` recommends a science book to Ada:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check bookrec-rules/strict.orm.yaml bookrec-rules/genre-warning.population.json --baseline-model bookrec-rules/model.orm.yaml \
  | grep -v unpaired
```

```text
RULE EDITIONS bookrec-rules/model.orm.yaml -> bookrec-rules/strict.orm.yaml
base check exit 0
head check exit 1
constraint:age_appropriate [paired] base=pass/alethic head=pass/alethic 0 base-only, 0 head-only, 0 standing
constraint:preferred_genre [paired] base=warning/deontic head=fail/alethic 0 base-only, 0 head-only, 1 standing
constraint:unread_only [paired] base=pass/alethic head=pass/alethic 0 base-only, 0 head-only, 0 standing
```

The finding is `standing`: the same binding offends under both editions. What
changed is its weight, from `warning/deontic` to `fail/alethic`. A list of
failing rules would show this as new; the comparison shows that the population
did not get worse, the rule got stricter.

The JSON result has the schema `gnd-rule-edition-comparison/1`. It binds the
population by SHA-256 and each edition by model digest, so a reviewer can tell
exactly which three files were compared:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check bookrec-rules/rules.orm.yaml bookrec-rules/horror-for-minor.population.json --baseline-model bookrec-rules/declared.orm.yaml --format json \
  | python -c "
import json, sys
result = json.load(sys.stdin)
print(result['schema_version'], 'base exit', result['base']['exit_code'], 'head exit', result['head']['exit_code'])
for rule in result['rules']:
    delta = rule['delta'] or {}
    if rule['pairing'] != 'unpaired':
        print(rule['address'], rule['pairing'], {key: len(rows) for key, rows in delta.items()})
row = next(rule for rule in result['rules'] if rule['address'] == 'constraint:no_horror_for_minors')
print('head only:', row['delta']['head_only'])
"
```

```text
gnd-rule-edition-comparison/1 base exit 0 head exit 1
constraint:age_appropriate paired {'base_only': 0, 'head_only': 0, 'standing': 0}
constraint:known_genres paired {'base_only': 0, 'head_only': 0, 'standing': 0}
constraint:no_horror_for_minors paired {'base_only': 0, 'head_only': 1, 'standing': 0}
constraint:preferred_genre paired {'base_only': 0, 'head_only': 0, 'standing': 0}
constraint:unread_only paired {'base_only': 0, 'head_only': 0, 'standing': 0}
head only: [{'$u': 'ada', '$b': 'crypt'}]
```

This run compares `declared.orm.yaml`, the misspelt edition, with the
corrected rules. Every rule with an id is `paired`, and one binding is
head-only. That is the typo fix, stated as a difference.

### Two editions or two populations

`--baseline-model` holds the population still and changes the rules.
`--baseline`, which shipped earlier, does the reverse: one model, and a second
population to compare with. Yesterday BookRec published the seed
recommendations. Judge today's candidate against them under the new rules:

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check bookrec-rules/rules.orm.yaml bookrec-rules/horror-for-minor.population.json --baseline bookrec-rules/seed.population.json
```

```text
BLOCKING (alethic)
  [fail, new] constraint:no_horror_for_minors (constraints[3]): Guarded absence consequent evaluated over bindings=1 — violated by bindings: {'$u': 'ada', '$b': 'crypt'}.
    remedy: Replace the book with one outside the horror genre for this reader.
ADVISORY (deontic)
  (none)
pass=6 fail=1 warning=0 unchecked=0 vacuous=0
COVERAGE
  recommendation: declared, facts=2
  user_rated_book: declared, facts=2
  user_is_minor: declared, facts=1
  book_rated_adult: declared, facts=1
  book_has_genre: declared, facts=6
  user_prefers_genre: declared, facts=3
BASELINE bookrec-rules/seed.population.json
  new=1 standing=0 resolved=0 positional_keyed=0 undecided=0
```

The failure is marked `new`: yesterday's output did not have it.
[Adopt rules on a project that already breaks them](../how-to/adopt-rules-with-a-baseline.md)
builds a CI gate on that marking. The two options answer different questions
and cannot be combined: `--baseline-model` refuses `--baseline` and the other
rule-id options with a usage error, exit 64.

| You hold fixed | You vary | Option | Findings are marked |
|---|---|---|---|
| the rules | the population | `--baseline POPULATION` | `new`, `standing`, resolved |
| the population | the rules | `--baseline-model MODEL` | `head-only`, `standing`, `base-only` |

## Limits

- **Diagnostics describe; they do not decide.** A rule with zero bindings over
  populated tables stays `pass`. No option turns it into a failure or into
  `vacuous`.
- **Plain snapshot checks only.** `--rule-ids`, `--guarded-diagnostics` and
  `--baseline-model` work on one population checked against a model without
  temporal terms, an active redaction policy or reference populations. Other
  models are refused before the population is read.
- **The literal warning needs a declared domain.** It fires when a value
  enumeration or range definitely excludes the literal. It is a warning, never
  an error.
- **Case generation serves a fragment.** It covers asserted scalar facts with
  atom, absence and scalar comparison consequents, and existential consequents
  without a `where` filter. A rule outside it gets the reason
  `unsupported-shape`, not a guessed case. Generated cases
  do not show that the rule matches the policy you meant.
- **Edition comparison needs one vocabulary.** Both models must use the same
  vocabulary, and the population must be valid under both; otherwise the
  comparison is refused with exit 3. Comparing across a renamed or removed
  fact type is not supported. When the variables of a guarded rule cannot be
  matched across editions without ambiguity, that rule's difference is
  withheld with a reason and the comparison exits 4.

The exact fields are in the [rule-check report reference](../reference/rule-check-report.md)
and the [synthetic data guide](../guides/synthetic-data.md).

## Agent handoff and exercise

To have an agent add a rule of your own, explicitly select `gnd-model-evolve`
and give it the evidence this chapter used:

> Add the rule "never recommend a horror book to a minor" to the BookRec model
> as a guarded constraint with an id and a remedy. Validate the candidate and
> show me every warning. Check `horror-for-minor.population.json` with
> `--guarded-diagnostics` and report each rule's binding count. Compare the
> candidate with the current model using `--baseline-model` and show me the
> added rules and head-only findings. Do not apply the change until I accept it.

That is a new session with its own outcome. Running this chapter's commands
does not mean an agent did the work.

**Exercise:** In a scratch copy of `rules.orm.yaml`, move the literal to the
consequent: keep only the recommendation and `user_is_minor` in the
antecedent, and require the `absence` of `book_has_genre` with genre `Horror`.
Predict the binding count for today's candidate, and predict what
`gnd validate` says. The count is 1, because the antecedent no longer contains
the typo, and the check passes wrongly. Validation still warns, at the
consequent's binding. That is why this chapter used both.

Next: [let the catalogue suggest rules](09-suggested-rules.md).
