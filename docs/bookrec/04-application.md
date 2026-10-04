# 4. Run the application and publish checked output

The BookRec library makes a proposal. GND checks that proposal against the
selected rules. Only then does the CLI move the candidate to its output path.
This chapter makes that control flow visible with both the CLI and Python.

The important branch in the supplied `publish` function is small:

```python
# Excerpt: candidate and output are paths prepared by publish().
report = api.check(model, candidate, unredacted=True)
if report["exit_code"] == 0 and report["acceptance_ready"]:
    candidate.replace(output)
```

The surrounding function writes a temporary JSON file, refuses an existing
output path, prints the report, and removes rejected temporary files. The
recommender never gets to declare its own result accepted.

Continue from [chapter 3](03-project.md). All examples use the invented catalogue,
so the CLI prints unredacted checker details for learning purposes.

## Ask for Ada's recommendations

<!-- gnd-run expect=0 -->
```sh
(cd bookrec-project && python -m bookrec.cli recommend --model model.orm.yaml --input seed.population.json --output recommendations.json --user ada --limit 2)
```

Expected: exit 0, a checker report with one genre warning, and a new
`bookrec-project/recommendations.json`. The algorithm chooses unread,
age-appropriate books in alphabetical order. Ada gets `cosmos` and `map`;
Ben's existing `night` recommendation stays in the population. Ada's science
recommendation is legal under the current advisory genre policy.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
from gnd import api

path = Path("bookrec-project/recommendations.json")
output = json.loads(path.read_text())
ada = [row["book"] for row in output["facts"]["recommendation"] if row["user"] == "ada"]
assert ada == ["cosmos", "map"]
assert {"user": "ben", "book": "night"} in output["facts"]["recommendation"]
report = api.check("bookrec-project/model.orm.yaml", path)
assert report["acceptance_ready"] and report["counts"]["warning"] == 1
assert not list(path.parent.glob(".bookrec-*.json"))
print("Published:", ada, "with one advisory warning.")
```

The library's filters make this particular proposal reasonable. GND is the
independent acceptance boundary: if an implementation bug emits forbidden
facts, the checker can reject them without trusting the library's filtering.

## Exercise an application refusal

The CLI only knows readers with supplied preference facts. An unknown reader
is refused before a candidate is published.

<!-- gnd-run expect=3 -->
```sh
(cd bookrec-project && python -m bookrec.cli recommend --model model.orm.yaml --input seed.population.json --output ghost.json --user ghost)
```

<!-- gnd-run expect=0 -->
```python
from pathlib import Path

assert not Path("bookrec-project/ghost.json").exists()
print("Unknown reader produced no output file.")
```

Exit 3 here is an application-level unknown-user refusal. The checker also uses
3 for malformed inputs, so retain the command and diagnostic context when
interpreting a number. An application's exit meanings belong to its declared
interface, not to a guess based on the integer alone.

## Call the library from Python

The library returns ordinary dictionaries. It does not publish files or hide a
network call. This example selects preferred genres and passes the resulting
facts to the same checked-publication function used by the CLI.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path("bookrec-project").resolve()))
from bookrec.library import recommend
from bookrec.cli import publish

seed = json.loads(Path("bookrec-project/seed.population.json").read_text())
proposal = recommend(seed, user="ada", limit=2, preferred_only=True)
assert [r["book"] for r in proposal["facts"]["recommendation"] if r["user"] == "ada"] == [
    "map", "river"
]
assert publish("bookrec-project/model.orm.yaml", proposal,
               "bookrec-project/preferred.json") == 0
assert seed["facts"]["recommendation"] == [
    {"user": "ada", "book": "map"}, {"user": "ben", "book": "night"}
]
print("Library preserved input and published preferred recommendations.")
```

In your own app, call [the stable Python API](../reference/python-api.md) at the
boundary where candidate data would enter storage or another system. A checker
report is an input to your publication policy. This example requires both exit
0 and `acceptance_ready: true` and refuses to overwrite existing output files.
It is a small local-file example; database transactions, concurrency and service
request handling remain ordinary application engineering.

## Ask an agent to improve the algorithm

> Implement a better ranking in BookRec's authored extension. Preserve the
> model and the checked-publication boundary. Demonstrate the before and after
> recommendation facts and checker reports. Run gnd-conformance only when I
> explicitly select that skill; do not turn a warning into a hard rule yourself.

The prompt deliberately distinguishes application tuning from changing the
requirements. If your question needs a recorded development experiment,
explicitly select `gnd-dev-session`, define its acceptance contract and coverage
floors, and retain its outcome separately from ordinary checker reports. This
chapter's direct calls are not a claim that an experiment session was run.

**Exercise:** Change `limit=2` to `limit=1` with a new output filename. Predict
which book Ada receives and whether the genre warning remains. Then try
`preferred_only=True`; the first book becomes `map`.

Next: [repair a failing candidate and inspect code drift](05-repair.md).
