# 2. Make a mistake visible

A model states rules; a **population** supplies facts. BookRec's population is a
JSON document with a small header and a `facts` mapping. Each fact type maps to
rows whose keys are the model's role names. The checker compares these facts
with the selected model. For example, these two rows describe a recommendation
and a prior interaction for the same pair (an excerpt, not a complete population):

```json
{
  "facts": {
    "recommendation": [{"user": "ada", "book": "read"}],
    "user_rated_book": [{"user": "ada", "book": "read"}]
  }
}
```

The checker can join the shared `user` and `book` roles to expose the conflict.
The complete files additionally carry their model identity, coverage declarations
and the other fact types needed by the rules.

Continue in the directory created in [chapter 1](01-model.md). The catalogue is
small enough to work through by hand:

| Book identifier | Primary genre | Adult-rated? |
|---|---|---|
| cosmos | science | No |
| map | fantasy | No |
| night | fantasy | Yes |
| read | fantasy | No |
| river | fantasy | No |

Ada is a minor; Ben is an adult. Both prefer fantasy and have already rated
`read`. A rating is a positive interaction here, not a star score. In this
bounded catalogue an absent minor/adult flag means that flag is absent from
the supplied facts; this is not an age-verification system.

## Check a successful result

The seed recommends `map` to Ada and `night` to Ben. Both recommendations are
unread, age-appropriate, and in a preferred genre.

<!-- gnd-run expect=0 -->
```sh
gnd check bookrec-demo/model.orm.yaml bookrec-demo/seed.population.json --format json
```

Expected: exit 0, `acceptance_ready: true`, five passing verdicts. The five
come from two genre-shape constraints plus the three recommendation rules.

<!-- gnd-run expect=0 -->
```python
from gnd import api

result = api.check("bookrec-demo/model.orm.yaml", "bookrec-demo/seed.population.json")
assert result["exit_code"] == 0 and result["acceptance_ready"]
assert result["counts"]["pass"] == 5
print(result["counts"])
```

`api.check` returns a report dictionary rather than raising an exception for a
rule violation. Its `exit_code` corresponds to the CLI exit. The synthetic
examples below request unredacted details so you can see the offending pair;
choose disclosure deliberately when checking real user data.

## Reject two concrete errors

First, a candidate recommends `read` to Ada. The source already says Ada rated
it. Running this command **should fail**:

<!-- gnd-run expect=1 -->
```sh
gnd check bookrec-demo/model.orm.yaml bookrec-demo/already-read.population.json --format json --unredacted
```

Expected: exit 1 and a failed guarded constraint at `constraints[0]`. The
report identifies the Ada/`read` binding that violates the absence requirement.

The next candidate recommends `night` to Ada. The title is unread, but the
minor and adult-rated facts make the second rule reject it.

<!-- gnd-run expect=1 -->
```sh
gnd check bookrec-demo/model.orm.yaml bookrec-demo/adult-for-minor.population.json --format json --unredacted
```

<!-- gnd-run expect=0 -->
```python
from gnd import api

for name, constraint in [("already-read", "constraints[0]"),
                         ("adult-for-minor", "constraints[1]")]:
    result = api.check("bookrec-demo/model.orm.yaml",
                       f"bookrec-demo/{name}.population.json", unredacted=True)
    failed = [row for row in result["verdicts"] if row["verdict"] == "fail"]
    assert result["exit_code"] == 1 and len(failed) == 1
    assert failed[0]["constraint_ref"] == constraint
    assert failed[0]["offending_facts"]
    print(name, failed[0]["message"])
```

## Keep a warning distinct from rejection

`cosmos` is unread and age-appropriate for Ada, but its science genre is outside
her preference. The current brief says recommendations **should** match a
preferred genre. That produces a warning while accepting the population.

<!-- gnd-run expect=0 -->
```sh
gnd check bookrec-demo/model.orm.yaml bookrec-demo/genre-warning.population.json --format json --unredacted
```

<!-- gnd-run expect=0 -->
```python
from gnd import api

result = api.check("bookrec-demo/model.orm.yaml",
                   "bookrec-demo/genre-warning.population.json", unredacted=True)
assert result["exit_code"] == 0 and result["acceptance_ready"]
assert result["counts"]["warning"] == 1 and result["counts"]["fail"] == 0
warning = next(row for row in result["verdicts"] if row["verdict"] == "warning")
assert warning["modality"] == "deontic"
print(warning["message"])
```

A report can contain more than success or rejection. Exit 2 means inadequate
or vacuous evidence, 3 means malformed input, and 4 means indeterminate
checking. Production code should require explicit acceptance, rather than
assume every outcome other than exit 1 is safe to publish.

## Agent handoff and exercise

> Use gnd-orm-core as the format reference. Explain the failing bindings in
> these two check reports and propose corrected recommendation facts. Keep
> catalogue, reader preferences and model rules unchanged. Do not invoke a
> model-evolution or application-generation skill.

**Exercise:** Predict the result of recommending `night` to Ben and `cosmos` to
Ada together. The answer is an accepted result with one warning; the adult flag
is only prohibited when joined with a minor reader.

Next: [generate the project boundary](03-project.md).
