# Run GND behind your interface or in front of customers

Use this when one GND installation serves two kinds of reader. Your own team,
behind your interface, wants the population values that explain a failure.
A customer, reached through your service, must not see them. One setting, the
*disclosure mode*, tells GND which reader it is serving. The full rules are in
the [disclosure reference](../reference/disclosure.md).

!!! info "Files on GitHub"

    - [`disclosure/model.orm.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/disclosure/model.orm.yaml): a support desk's contacts, with the email role declared sensitive
    - [`disclosure/population.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/disclosure/population.json): one customer with two email addresses
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/disclosure-mode.md)

## The example

A support desk records each customer's email address. The model says a
customer has at most one, and marks the address as sensitive:

```yaml
roles:
  - { object_type: customer_code, role_name: customer }
  - { object_type: email_address, role_name: email, redact: true }
```

The population gives customer `c-1` two addresses, so the check fails. Copy
the example:

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/disclosure', 'disclosure', dirs_exist_ok=True)"
```

The blocks below print two fields of the check report: the violation
message and the offending facts. Save the filter once:

<!-- gnd-run expect=0 -->
```sh
cat > show.py <<'PY'
import json, sys
verdict = json.load(sys.stdin)["verdicts"][0]
print(verdict["message"])
print(verdict["offending_facts"])
PY
```

## With no mode set: as before

Without a mode, GND behaves as it always has: the declared role is redacted
unless you ask for it with `--unredacted`.

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check disclosure/model.orm.yaml disclosure/population.json --format json | python show.py
```

```text
[REDACTED INSTANCE DETAIL]
[{'redacted': True, 'roles': ['has_email.email']}]
```

The check still fails. The report says which constraint failed
and which role was withheld, but not the addresses.

## Behind your interface: `internal`

Set the mode on the root command, before the subcommand, or in the
environment of the process that runs GND:

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd --disclosure internal check disclosure/model.orm.yaml disclosure/population.json --format json | python show.py
```

```text
Each customer plays 'has_email' with at most one combination of the other roles — violated: customer 'c-1' has 2 facts.
[{'customer': 'c-1', 'email': 'ann@example.com'}, {'customer': 'c-1', 'email': 'ann.lee@example.com'}]
```

`internal` acts as if every raw option were passed. Your team sees the two
addresses and can decide which one to keep.

## In front of customers: `customer`

Set the mode in the environment of the service that faces customers, so no
request can loosen it. In a real deployment you export it once in that service's
environment; here it is set for one command:

<!-- gnd-run expect=1 output=stdout -->
```sh
GND_DISCLOSURE=customer gnd check disclosure/model.orm.yaml disclosure/population.json --format json | python show.py
```

```text
[REDACTED INSTANCE DETAIL]
[{'redacted': True, 'roles': ['has_email.email']}]
```

The verdict is the same; only the values are withheld.

### Requests for values are refused, not downgraded

A customer's request might be turned into `--unredacted` by your service.
Under `customer` GND refuses it and prints nothing on stdout, so
nobody mistakes a redacted answer for the raw one:

<!-- gnd-run expect=3 output=stderr -->
```sh
GND_DISCLOSURE=customer gnd check disclosure/model.orm.yaml disclosure/population.json --unredacted
```

```text
gnd: error: --unredacted is refused in customer disclosure mode
```

The root option can tighten the mode but never loosen it:

<!-- gnd-run expect=3 output=stderr -->
```sh
GND_DISCLOSURE=customer gnd --disclosure internal check disclosure/model.orm.yaml disclosure/population.json
```

```text
gnd: error: --disclosure internal is refused when GND_DISCLOSURE=customer
```

A mistyped value is refused too, so a misspelled lock never opens:

<!-- gnd-run expect=3 output=stderr -->
```sh
GND_DISCLOSURE=Customer gnd check disclosure/model.orm.yaml disclosure/population.json
```

```text
gnd: error: GND_DISCLOSURE must be 'internal' or 'customer'
```

## Why-not and witness answers

The mode also covers the commands that explain a derivation: `witness`,
`witness-view`, `replay`, `why-not`, and the Lean and Soufflé exports. This
uses the `quoted_claims` example from
[Repair a claim that does not derive](repair-a-missing-claim.md). In its
`spelling-gap.pop.json` the claimed quotation is missing because the work the
claim calls "Field Notes" is recorded as "FIELD NOTES".

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/quoted_claims', 'quoted_claims', dirs_exist_ok=True)"
cat > blocker.py <<'PY'
import json, sys
answer = json.load(sys.stdin)
blocker = answer["clauses"][0]["blocker"]
print(answer["view"], blocker["fact_type"], blocker["near_miss_count"])
print(blocker["near_misses"])
PY
```

Behind your interface, the answer shows the row spelled differently:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd --disclosure internal why-not quoted_claims/model.orm.json quoted_claims/spelling-gap.pop.json \
  --fact-type certified --row quoted_claims/claim.json | python blocker.py
```

```text
raw authored 1
[{'candidate': {'person': 'Ada Byrne', 'work': 'FIELD NOTES'}, 'roles': ['work'], 'sample': {'person': 'Ada Byrne', 'work': 'Field Notes'}}]
```

In front of customers, the same answer names the blocking step and keeps the
count, but not the values:

<!-- gnd-run expect=0 output=stdout -->
```sh
GND_DISCLOSURE=customer gnd why-not quoted_claims/model.orm.json quoted_claims/spelling-gap.pop.json \
  --fact-type certified --row quoted_claims/claim.json | python blocker.py
```

```text
redacted authored 1
redacted
```

and `--raw` is refused:

<!-- gnd-run expect=3 output=stderr -->
```sh
GND_DISCLOSURE=customer gnd why-not quoted_claims/model.orm.json quoted_claims/spelling-gap.pop.json \
  --fact-type certified --row quoted_claims/claim.json --raw
```

```text
gnd: error: --raw is refused in customer disclosure mode
```

## From Python

The Python API reads the same environment variable. A request for values under
`customer` raises `DisclosureRefused`, a `ValueError`:

<!-- gnd-run expect=0 output=stdout -->
```python
import os
os.environ["GND_DISCLOSURE"] = "customer"
from gnd import api
try:
    api.check("disclosure/model.orm.yaml", "disclosure/population.json", unredacted=True)
except ValueError as error:
    print(type(error).__name__, error)
```

```text
DisclosureRefused unredacted=True is refused in customer disclosure mode
```

## What the mode does not change

- `gnd exp run` session feedback, `gnd discover` (apart from its
  `--show-values` option, which the mode governs), `gnd export ilp`,
  `gnd fidelity` and `gnd doccheck` behave the same in every mode. Do not
  route their output to a customer.
- Values in check messages for roles you have not declared with `redact: true`
  are not withheld. Declare every sensitive role.
- Under `customer`, the processes GND starts (the agents of `gnd exp run`, the
  stations of `gnd solve`) receive `GND_DISCLOSURE=customer`. Under `internal`
  or no mode they receive nothing extra.
