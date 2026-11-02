"""Apply the DC2 changes.md edits to the existing pages (NM4 spec, Design, as amended by D5). Each old passage must match once."""
import pathlib

EDITS = {
"docs/reference/why-not.md": [(
"""The Python API returns raw values, like `api.witness`. The CLI prints a
redacted view by default: `samples`, constant roles and an unavailable term's
binding read `"redacted"`, and the answer carries `"view": "redacted"`. An
atom blocker keeps `near_miss_count` and `near_miss_truncated` and shows
`near_misses` as `"redacted"`. Pass
`--raw` to print the values, with `"view": "raw"`. Use the raw view only where
those values are appropriate for the reader.
""",
"""With no [disclosure mode](disclosure.md) set, the Python API returns raw
values, like `api.witness`, and the CLI prints a redacted view: `samples`,
constant roles and an unavailable term's binding read `"redacted"`, and the
answer carries `"view": "redacted"`. An atom blocker keeps
`near_miss_count` and `near_miss_truncated` and shows `near_misses` as
`"redacted"`. Pass `--raw` to print the values, with `"view": "raw"`.

Under `GND_DISCLOSURE=internal` both print the raw view. Under `customer`
both return the redacted view and `--raw` is refused with exit 3. The
near-miss counters stay visible in every mode; [who customer mode
protects](disclosure.md#who-customer-mode-protects) says what they reveal.
""")],
"docs/reference/cli.md": [
("""[expenses](../expense/01-model.md), or the [quickstart](../quickstart.md).
""",
"""[expenses](../expense/01-model.md), or the [quickstart](../quickstart.md).

The root option `--disclosure internal|customer` goes before the subcommand
(`gnd --disclosure customer check …`) and sets the
[disclosure mode](disclosure.md) for that invocation; `GND_DISCLOSURE` sets it
for a process. It is accepted only at the root.
"""),
("""Check-family reports normally apply declared redaction; `--unredacted` requests
the value-bearing view. `validate --trace`""",
"""Check-family reports normally apply declared redaction; `--unredacted` requests
the value-bearing view. The disclosure mode can grant or refuse that request;
see [what customer mode refuses](disclosure.md#what-customer-mode-refuses).
`validate --trace`"""),
("""| `gnd witness MODEL POPULATION --targets REQUEST` | Redacted finite-witness result |
| `gnd witness MODEL POPULATION --targets REQUEST --raw --out CERTIFICATE` | Explicit new raw certificate |
""",
"""| `gnd witness MODEL POPULATION --targets REQUEST` | Redacted finite-witness result (raw under `internal`) |
| `gnd witness MODEL POPULATION --targets REQUEST --raw --out CERTIFICATE` | Explicit new raw certificate; refused under `customer` |
"""),
("""| `gnd why-not MODEL POPULATION --fact-type ID` | Where each clause of a derivation stops, values redacted |
| `gnd why-not MODEL POPULATION --fact-type ID --row REQUEST` | Where a derivation stops for one claimed row, values redacted |
""",
"""| `gnd why-not MODEL POPULATION --fact-type ID` | Where each clause of a derivation stops, values redacted (raw under `internal`) |
| `gnd why-not MODEL POPULATION --fact-type ID --row REQUEST` | Where a derivation stops for one claimed row, with values spelled differently counted; values redacted |
"""),
("""rather than assigning one universal meaning to every nonzero exit.
""",
"""rather than assigning one universal meaning to every nonzero exit.
A request for values refused by the disclosure mode exits `3` with nothing on
stdout. A misspelled or repeated `--disclosure` is a usage error, `64`.
"""),
],
"docs/reference/python-api.md": [
("""The Python result contains raw values
in the certificate; the CLI's default witness view removes them.""",
"""With no disclosure mode set, the Python result contains raw values
in the certificate; the CLI's default witness view removes them. Under
`GND_DISCLOSURE=customer` the result is the default view with no
`certificate` (see [disclosure](disclosure.md))."""),
("""The Python
result carries raw values; the CLI's default view removes them.""",
"""With no disclosure
mode set, the Python result carries raw values; the CLI's default view removes
them. Under `customer` the function returns the redacted view."""),
("""- Model-based redaction applies by default to checking, verbalization, and
  diff reports. `unredacted=True` is an explicit request to retain source values.
""",
"""- Model-based redaction applies by default to checking, verbalization, and
  diff reports. `unredacted=True` is an explicit request to retain source
  values. Under the [disclosure mode](disclosure.md) `internal` it is granted
  without asking; under `customer` it raises `DisclosureRefused`.
"""),
("""## Integrate reports deliberately
""",
"""## Under a disclosure mode

The functions read `GND_DISCLOSURE` when they are called. Under `customer`
the witness has no certificate, why-not returns the redacted view, and a
request for values raises `DisclosureRefused`:

<!-- gnd-run expect=0 output=stdout -->
```python
import os
from gnd import api

os.environ["GND_DISCLOSURE"] = "customer"
proof = api.witness("api-dispatch/model.orm.json", "api-dispatch/repaired.pop.json", "targets.json")
print(proof["exit_code"], "certificate" in proof)
answer = api.why_not("api-dispatch/model.orm.json", "api-dispatch/seed.pop.json", "dispatch_reachable")
print(answer["status"], answer["view"])
try:
    api.check("api-dispatch/model.orm.json", "api-dispatch/seed.pop.json", unredacted=True)
except api.DisclosureRefused as error:
    print(error)
```

```text
0 False
derived redacted
unredacted=True is refused in customer disclosure mode
```

## Integrate reports deliberately
"""),
],
"docs/reference/capabilities.md": [(
"""| Explain a missing derived fact | `why-not`; `api.why_not` | Declared-order steps and the first empty one; no aggregates or prose rules; values redacted by default | [Why-not](why-not.md) |
""",
"""| Explain a missing derived fact | `why-not`; `api.why_not` | Declared-order steps and the first empty one; counts values spelled differently; no aggregates or prose rules; values redacted by default | [Why-not](why-not.md) |
| Serve internal or customer readers | `GND_DISCLOSURE`, `--disclosure` | Customer mode refuses requests for values; a guard, not a lock, for code inside the process; some outputs are the same in every mode | [Disclosure](disclosure.md) |
""")],
"docs/reference/formats.md": [(
"""[export contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-export/references/export-contract.md) |
""",
"""[export contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-export/references/export-contract.md) |
| Why-not answers | [Why-not reference](why-not.md), [why-not schema](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/why-not.schema.json) (`gnd-why-not/2`) |
| Which outputs carry values in each mode | [Disclosure](disclosure.md) |
""")],
"docs/reference/discover.md": [(
"""carry what a redacted role holds.
""",
"""carry what a redacted role holds. Its output is the same in every
[disclosure mode](disclosure.md): it never proposes values for a redacted role,
so there is nothing to withhold.
""")],
"docs/reference/ilp-bridge.md": [(
"""- `references`: a model with declared reference populations.
""",
"""- `references`: a model with declared reference populations.

The export is the same in every [disclosure mode](disclosure.md): it refuses
declared roles and writes undeclared values, because handing values to a
learner you chose is its job. Do not run it for a customer.
""")],
"docs/guides/exports.md": [(
"""view, including an expanded view, is not replayable input.
""",
"""view, including an expanded view, is not replayable input.
Under `GND_DISCLOSURE=customer`, `--raw` is refused with exit 3, so a service
facing customers cannot publish a raw certificate or bundle; see
[disclosure](../reference/disclosure.md).
""")],
"docs/agents/export-and-review.md": [(
"""See [exports and witnesses](../guides/exports.md) and the
[Python API](../reference/python-api.md) (`api.witness`, `api.replay`).
""",
"""Under `GND_DISCLOSURE=customer`, `--raw` is refused with exit 3, so a service
facing customers cannot publish a raw certificate or bundle; see
[disclosure](../reference/disclosure.md).

See [exports and witnesses](../guides/exports.md) and the
[Python API](../reference/python-api.md) (`api.witness`, `api.replay`).
""")],
"docs/release-notes.md": [(
"""## Unreleased: near-miss values in why-not (2026-11-01)
""",
"""## Unreleased: disclosure mode (2026-11-01)

One GND installation can now serve readers behind your interface and
customers ([issue #70](https://github.com/vasiloglou/gnd-public/issues/70)).
Set `GND_DISCLOSURE` or the root option `--disclosure` to `internal` or
`customer`; unset changes nothing.

- `internal` acts as if every value option were passed.
- `customer` withholds declared roles and every witness, replay, why-not, Lean
  and Soufflé value, in the CLI and the Python API. A request for values exits
  3 or raises `gnd.api.DisclosureRefused`.
- Contract change under `customer` only: `api.why_not` returns the redacted
  view, and `api.witness` and `api.replay` return the default view without a
  certificate.
- Child processes receive `GND_DISCLOSURE=customer` only under `customer`.

See [disclosure](reference/disclosure.md).

## Unreleased: near-miss values in why-not (2026-11-01)
""")],
"docs/bookrec/02-facts.md": [(
"""choose disclosure deliberately""",
"""choose [disclosure](../reference/disclosure.md) deliberately""")],
"src/gnd/skills/gnd-orm-core/references/representation-format.md": [(
"""- **`redact`**: optional boolean on a fact type. `true` selects every declared
  role of that fact type for report redaction; absent and `false` select none.
""",
"""- **`redact`**: optional boolean on a fact type. `true` selects every declared
  role of that fact type for report redaction; absent and `false` select none.
  Under `GND_DISCLOSURE=customer` the selected roles stay redacted and
  `--unredacted` is refused; under `internal` they are shown.
""")],
"src/gnd/skills/gnd-export/SKILL.md": [
("""   It names the first rule step that left no bindings; it explains, it proves
   nothing.
""",
"""   It names the first rule step that left no bindings; it explains, it proves
   nothing. Its atom blockers count rows spelled differently (`near_miss_count`);
   read the pairs with `--raw` before changing a spelling.
"""),
("""   `--raw --out NEW_CERTIFICATE`. The destination is create-once; raw certificates
   contain source values. Never overwrite an existing destination.
""",
"""   `--raw --out NEW_CERTIFICATE`. The destination is create-once; raw certificates
   contain source values. Never overwrite an existing destination. Under
   `GND_DISCLOSURE=customer` this is refused with exit 3; do not retry it in
   another mode for that reader.
"""),
],
}

if __name__ == "__main__":
    import sys
    only = set(sys.argv[1:])
    for path, edits in EDITS.items():
        if only and path not in only:
            continue
        p = pathlib.Path(path); text = p.read_text()
        for old, new in edits:
            assert text.count(old) == 1, (path, old[:60], text.count(old))
            text = text.replace(old, new)
        p.write_text(text)
    print(sum(map(len, EDITS.values())), "edits across", len(EDITS), "files")
