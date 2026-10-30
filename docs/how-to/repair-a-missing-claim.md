# Repair a claim that does not derive

Use this when a rule should derive a row and does not, and you want to know
which fact is missing. `gnd why-not` names the first step of the rule that
left no bindings, and the values that reached it. You add that fact and ask
again, until the row derives and `gnd witness` proves it.

!!! info "Files on GitHub"

    - [`quoted_claims/model.orm.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/quoted_claims/model.orm.json): the model
    - [`quoted_claims/gap.pop.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/quoted_claims/gap.pop.json): the population, with two facts missing
    - [`quoted_claims/claim.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/quoted_claims/claim.json): the claimed row
    - [`quoted_claims/extracted.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/quoted_claims/extracted.json): a value a source document supplies
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/repair-a-missing-claim.md)

## The claim

An answer says Ada Byrne said quotation `q-17`. The model certifies a quotation
as said by a person when three facts hold: the quotation appears in a work,
the person wrote that work, and an editor reviewed it.

```text
certified(q, p) <- quote(q, w), authored(w, p), reviewed(w, r)
```

The population records where each quotation appears, and nothing else. Copy
the example:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/quoted_claims', 'quoted_claims', dirs_exist_ok=True)"
gnd validate quoted_claims/model.orm.json
```

```text
OK: quoted_claims/model.orm.json is a valid GND ORM model
```

`gnd check` passes: the population covers the claim's fact type, asserts
none of its rows, and none derive. That is consistent, and it does not tell you why the
claim is missing.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check quoted_claims/model.orm.json quoted_claims/gap.pop.json --format json \
  | python -c "import json, sys; r = json.load(sys.stdin); print(r['exit_code'], [d['verdict'] for d in r['derivations']])"
```

```text
0 ['pass']
```

## Ask why the claim is not derived

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd why-not quoted_claims/model.orm.json quoted_claims/gap.pop.json \
  --fact-type certified --row quoted_claims/claim.json | python -m json.tool
```

```text
{
    "clauses": [
        {
            "blocker": {
                "asserted_not_read": false,
                "derivation": "base",
                "fact_type": "authored",
                "ground": true,
                "index": 1,
                "kind": "atom",
                "roles": {
                    "person": {
                        "bound": true,
                        "variable": "$p"
                    },
                    "work": {
                        "bound": true,
                        "variable": "$w"
                    }
                },
                "sample_count": 1,
                "samples": "redacted"
            },
            "clause_index": 0,
            "descent": null,
            "descent_stopped": "not-derived",
            "steps": [
                {
                    "count": 1,
                    "fact_type": "quote",
                    "index": 0,
                    "kind": "atom"
                },
                {
                    "count": 0,
                    "fact_type": "authored",
                    "index": 1,
                    "kind": "atom"
                }
            ],
            "steps_after_blocker": "not-evaluated"
        }
    ],
    "exit_code": 0,
    "fact_type": "certified",
    "mode": "row",
    "order": "declared",
    "reason": null,
    "schema_version": "gnd-why-not/1",
    "status": "blocked",
    "unavailable": null,
    "view": "redacted",
    "work": {
        "binding_cells": 3,
        "joins": 1,
        "pre_joins": 2,
        "probes": 4
    }
}
```

The rule's first step found one binding, and the second, `authored`, found
none. Both of its roles are bound, so the missing fact is fully determined.
The default view hides the values. Ask for them with `--raw`:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd why-not quoted_claims/model.orm.json quoted_claims/gap.pop.json \
  --fact-type certified --row quoted_claims/claim.json --raw \
  | python -c "import json, sys; b = json.load(sys.stdin)['clauses'][0]['blocker']; print(b['fact_type'], b['samples'])"
```

```text
authored [{'person': 'Ada Byrne', 'work': 'Field Notes'}]
```

## Add the first fact and ask again

The missing fact is `authored(Field Notes, Ada Byrne)`. Add it and ask again:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "
import json
p = json.load(open('quoted_claims/gap.pop.json'))
p['facts']['authored'].append({'work': 'Field Notes', 'person': 'Ada Byrne'})
json.dump(p, open('quoted_claims/once.pop.json', 'w'))
"
gnd why-not quoted_claims/model.orm.json quoted_claims/once.pop.json \
  --fact-type certified --row quoted_claims/claim.json --raw \
  | python -c "import json, sys; b = json.load(sys.stdin)['clauses'][0]['blocker']; print(b['fact_type'], b['roles'], b['samples'])"
```

```text
reviewed {'reviewer': {'bound': False, 'variable': '$r'}, 'work': {'bound': True, 'variable': '$w'}} [{'work': 'Field Notes'}]
```

Now the rule stops one step later, at `reviewed`. Its `work` role is bound,
but no binding reaches `reviewer`: the payload cannot say who reviewed the
work. That value has to come from a source, here `extracted.json`.

## Add the second fact and prove the claim

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "
import json
p = json.load(open('quoted_claims/once.pop.json'))
reviewer = json.load(open('quoted_claims/extracted.json'))['reviewed']['reviewer']
p['facts']['reviewed'].append({'work': 'Field Notes', 'reviewer': reviewer})
json.dump(p, open('quoted_claims/twice.pop.json', 'w'))
"
gnd why-not quoted_claims/model.orm.json quoted_claims/twice.pop.json \
  --fact-type certified --row quoted_claims/claim.json \
  | python -c "import json, sys; print(json.load(sys.stdin)['status'])"
gnd witness quoted_claims/model.orm.json quoted_claims/twice.pop.json \
  --targets quoted_claims/claim.json \
  | python -c "import json, sys; print(json.load(sys.stdin)['results'][0]['status'])"
```

```text
derived
proved
```

## Keep the population consistent

The row now derives, but the population still covers that fact type and asserts
no rows, so `gnd check` would report the derived extension incomplete. Assert
the derived row, and the check passes again:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "
import json
p = json.load(open('quoted_claims/twice.pop.json'))
p['facts']['certified'] = [{'quote': 'q-17', 'person': 'Ada Byrne'}]
json.dump(p, open('quoted_claims/repaired.pop.json', 'w'))
"
gnd check quoted_claims/model.orm.json quoted_claims/repaired.pop.json --format json \
  | python -c "import json, sys; r = json.load(sys.stdin); print(r['exit_code'], [d['verdict'] for d in r['derivations']])"
```

```text
0 ['pass']
```

## What the answer does not tell you

- Why-not says which fact is missing, not whether it is true. Add a fact only
  when a source supports it.
- A step with an unbound role needs a value from somewhere else, as
  `reviewer` did here.
- Each answer covers the rule as written, in declared order. The
  [why-not reference](../reference/why-not.md) defines the steps, the exit
  codes and the limits.
