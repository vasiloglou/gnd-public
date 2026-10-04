# 1. Give a recommender rules it can be checked against

BookRec suggests books. A familiar feature becomes a useful GND example when we
ask what a suggestion must never do: recommend a book a reader has already
rated, or recommend an adult-rated book to a minor. A third request—prefer the
reader's favorite genres—starts as advice. You will build a small Python CLI,
check its actual output, repair a mistake, and change one business rule.

The application is deliberately local: two invented readers and five invented
books, with JSON files in place of a database. You need Python 3.11 or newer and
GND installed in the environment that runs `python` and `gnd`. No model account,
API key, native solver or network connection is needed after installation.

## What you will make

By chapter 4 you will run a recommender that writes a result only after GND
accepts it. By chapter 6 you will distinguish a valid partial recommendation
list from a list that contains **every eligible book**. Those are different
requirements, and GND can check both when you state them explicitly.

| Piece | Your responsibility | GND's contribution |
|---|---|---|
| Business brief | Decide what the app must and should do | A model vocabulary and explicit constraint provenance |
| Recommender | Write the algorithm and choose its ranking | A check of the facts the algorithm produces |
| Project | Implement CLI, storage and integrations | Generated model artifacts and conformance checks |
| Rule change | Approve the intended new behavior | Preview, model publication and retained change evidence |

The alphabetical ordering used here makes examples reproducible. A successful
check says nothing about whether that ordering is a useful recommendation.

## Start from installed resources

Create a fresh directory and keep it as your working directory for all six
chapters. The command below copies resources from your installed `gnd` package;
it works outside a Git checkout. It deliberately refuses an existing
`bookrec-demo` directory so a rerun cannot overwrite your work.

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from pathlib import Path
import shutil

source = files("gnd").joinpath("examples", "bookrec")
shutil.copytree(str(source), "bookrec-demo")
assert Path("bookrec-demo/model.orm.yaml").is_file()
print("Copied BookRec models, populations and application checkpoint.")
```

## Turn the brief into a model

Our supplied model is a reviewed teaching checkpoint. Its rules are:

1. Never recommend an already-rated book.
2. Never recommend an adult-rated book to a minor.
3. A recommendation should match a preferred genre.
4. Each book has exactly one primary genre.

`model.orm.yaml` uses JSON spelling, which is valid YAML. Open it in any editor.
`object_types` names users, books and genres. `fact_types` describes relationships,
including `recommendation(user, book)` and `user_rated_book(user, book)`.
`constraints` says which combinations of those facts are allowed.

The first rule is a guarded constraint. For each recommended user/book pair,
it requires the absence of that same pair in `user_rated_book`. The second
joins a recommendation with a minor flag before checking the adult flag. This
is how a rule applies to the particular reader and book rather than to an
entire table indiscriminately. Here is the central part of that first rule
(an excerpt to read, not a separate runnable model):

```yaml
id: unread_only
type: guarded
modality: alethic
antecedent:
  - fact_type: recommendation
    bind: {user: "$u", book: "$b"}
consequent:
  absence:
    fact_type: user_rated_book
    bind: {user: "$u", book: "$b"}
```

`$u` and `$b` are bindings shared by the antecedent and consequent. If the
recommendation is Ada/`read`, the checker searches for exactly Ada/`read` in
the rating facts. The complete checkpoint also includes the required source,
status and provenance fields.

<!-- gnd-run expect=0 -->
```sh
gnd validate bookrec-demo/model.orm.yaml --format json
```

Expected: exit 0 and no validation errors. Validation checks the *model's
structure*. It has not checked recommendations yet; that requires facts.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path

model = json.loads(Path("bookrec-demo/model.orm.yaml").read_text())
assert [rule["modality"] for rule in model["constraints"]] == [
    "alethic", "alethic", "deontic"
]
print("Two hard rules; one advisory genre rule.")
```

**Alethic** is the model's term for a hard constraint; a violation rejects the
output. **Deontic** marks a policy expectation that can produce a warning.
`source`, `status` and `provenance` record where each rule came from. The genre
rule's rationale explicitly explains why “should” remains advisory. These
labels make the intended interpretation inspectable; they do not prove the
brief is complete.

## Build it with an agent

To author your own version instead of using the checkpoint, explicitly select
`gnd-model-from-text` and give the agent this prompt:

> Use gnd-model-from-text to model this BookRec brief in MVP-fast mode. Ask me
> about ambiguous rules. Preserve “must never” versus “should.” Show me example
> facts and the model's verbalization, then validate it. Do not generate a
> project or run another skill until I select that handoff.

This is optional authoring work. The runnable tutorial continues with the
supplied files so a provider's response cannot change its expected results.

**Exercise:** In the model, find why “exactly one primary genre” requires both
uniqueness and mandatory participation. Predict what would happen to a book
with two genres, and to a book appearing elsewhere with no genre.

Next: [supply facts and observe failures](02-facts.md).
