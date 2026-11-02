<!-- DC2 draft, 2026-11-01. The edits NM4 makes to existing pages, each shown as
the new text with the passage it replaces. Outputs come from running the block
above them against 420114e and are re-checked by the tutorial runner. Not
committed to docs/ or src/gnd/skills/. -->

# Changes to existing pages

Each section names a page, says what the new text replaces, and gives the new
text. Pages with no change are listed at the end with the reason.

## `docs/reference/why-not.md`

*Replaces the first sentence of "Values in the answer" ("The Python API returns
raw values, like `api.witness`."), which is false under `customer`.*

> ## Values in the answer
>
> With no [disclosure mode](disclosure.md) set, the Python API returns raw
> values, like `api.witness`, and the CLI prints a redacted view: `samples`,
> constant roles and an unavailable term's binding read `"redacted"`, and the
> answer carries `"view": "redacted"`. An atom blocker keeps
> `near_miss_count` and `near_miss_truncated` and shows `near_misses` as
> `"redacted"`. Pass `--raw` to print the values, with `"view": "raw"`.
>
> Under `GND_DISCLOSURE=internal` both print the raw view. Under `customer`
> both return the redacted view and `--raw` is refused with exit 3. The
> near-miss counters stay visible in every mode; [who customer mode
> protects](disclosure.md#who-customer-mode-protects) says what they reveal.

## `docs/reference/cli.md`

*New paragraph after the page's opening paragraph.*

> The root option `--disclosure internal|customer` goes before the subcommand
> (`gnd --disclosure customer check …`) and sets the
> [disclosure mode](disclosure.md) for that invocation; `GND_DISCLOSURE` sets it
> for a process. It is accepted only at the root.

*Replaces "Check-family reports normally apply declared redaction;
`--unredacted` requests the value-bearing view."*

> Check-family reports normally apply declared redaction; `--unredacted` requests
> the value-bearing view. The disclosure mode can grant or refuse that request;
> see [what customer mode refuses](disclosure.md#what-customer-mode-refuses).

*The witness and why-not rows of "Proofs, exports, and skill installation".*

> | `gnd witness MODEL POPULATION --targets REQUEST` | Redacted finite-witness result (raw under `internal`) |
> | `gnd witness MODEL POPULATION --targets REQUEST --raw --out CERTIFICATE` | Explicit new raw certificate; refused under `customer` |
> | `gnd why-not MODEL POPULATION --fact-type ID` | Where each clause of a derivation stops, values redacted (raw under `internal`) |
> | `gnd why-not MODEL POPULATION --fact-type ID --row REQUEST` | Where a derivation stops for one claimed row, with values spelled differently counted; values redacted |

*Appended to "General command refusals may use `64` for usage …".*

> A request for values refused by the disclosure mode exits `3` with nothing on
> stdout. A misspelled or repeated `--disclosure` is a usage error, `64`.

## `docs/reference/python-api.md`

*Replaces, in the `witness` section, "The Python result contains raw values in
the certificate; the CLI's default witness view removes them."*

> With no disclosure mode set, the Python result contains raw values in the
> certificate; the CLI's default witness view removes them. Under
> `GND_DISCLOSURE=customer` the result is the default view with no
> `certificate` (see [disclosure](disclosure.md)).

*Replaces, in the `why_not` section, "The Python result carries raw values; the
CLI's default view removes them."*

> With no disclosure mode set, the Python result carries raw values; the CLI's
> default view removes them. Under `customer` the function returns the redacted
> view.

*Replaces the bullet "Model-based redaction applies by default … `unredacted=True`
is an explicit request to retain source values."*

> - Model-based redaction applies by default to checking, verbalization, and
>   diff reports. `unredacted=True` is an explicit request to retain source
>   values. Under the [disclosure mode](disclosure.md) `internal` it is granted
>   without asking; under `customer` it raises `DisclosureRefused`.

*New section before "Integrate reports deliberately". It runs after the page's
existing blocks; here it repeats the page's setup so it runs on its own.*

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from shutil import copytree

copytree(str(files("gnd") / "examples" / "dispatch"), "api-dispatch")
```

> ## Under a disclosure mode
>
> The functions read `GND_DISCLOSURE` when they are called. Under `customer`
> the witness has no certificate, why-not returns the redacted view, and a
> request for values raises `DisclosureRefused`:

<!-- gnd-run expect=0 output=stdout -->
```python
import json, os
from pathlib import Path
from gnd import api

targets = {"version": 1, "targets": [{
    "fact_type": "dispatch_reachable",
    "tuple": [{"primitive": "String", "value": "WH-A"},
              {"primitive": "String", "value": "DEST-D"}],
}]}
Path("targets.json").write_text(json.dumps(targets))
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

## `docs/reference/capabilities.md`

*The why-not row's boundary, and one new row after it.*

> | Explain a missing derived fact | `why-not`; `api.why_not` | Declared-order steps and the first empty one; counts values spelled differently; no aggregates or prose rules; values redacted by default | [Why-not](why-not.md) |
> | Serve internal or customer readers | `GND_DISCLOSURE`, `--disclosure` | Customer mode refuses requests for values; a guard, not a lock, for code inside the process; some outputs are the same in every mode | [Disclosure](disclosure.md) |

## `docs/reference/formats.md`

*Two new rows in the canonical-references table.*

> | Why-not answers | [Why-not reference](why-not.md), [why-not schema](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/why-not.schema.json) (`gnd-why-not/2`) |
> | Which outputs carry values in each mode | [Disclosure](disclosure.md) |

## `docs/reference/discover.md` and `docs/reference/ilp-bridge.md`

*One sentence each, after the passage on redacted roles.*

> `discover`: Its output is the same in every [disclosure mode](disclosure.md):
> it never proposes values for a redacted role, so there is nothing to withhold.

> `ilp-bridge`: The export is the same in every [disclosure mode](disclosure.md):
> it refuses declared roles and writes undeclared values, because handing values
> to a learner you chose is its job. Do not run it for a customer.

## `docs/guides/exports.md` and `docs/agents/export-and-review.md`

*One sentence each, after the explanation of the redacted view.*

> Under `GND_DISCLOSURE=customer`, `--raw` is refused with exit 3, so a service
> facing customers cannot publish a raw certificate or bundle; see
> [disclosure](../reference/disclosure.md).

## `docs/release-notes.md`

*New entry above the near-miss entry.*

> ## Unreleased: disclosure mode (2026-11-01)
>
> One GND installation can now serve readers behind your interface and
> customers ([issue #70](https://github.com/vasiloglou/gnd-public/issues/70)).
> Set `GND_DISCLOSURE` or the root option `--disclosure` to `internal` or
> `customer`; unset changes nothing.
>
> - `internal` acts as if every value option were passed.
> - `customer` withholds declared roles and every witness, replay, why-not, Lean
>   and Soufflé value, in the CLI and the Python API. A request for values exits
>   3 or raises `gnd.api.DisclosureRefused`.
> - Contract change under `customer` only: `api.why_not` returns the redacted
>   view, and `api.witness` and `api.replay` return the default view without a
>   certificate.
> - Child processes receive `GND_DISCLOSURE=customer` only under `customer`.
>
> See [disclosure](reference/disclosure.md).

## Packaged skills

*`src/gnd/skills/gnd-orm-core/references/representation-format.md`, appended
to the fact-type `redact` entry.*

> Under `GND_DISCLOSURE=customer` the selected roles stay redacted and
> `--unredacted` is refused; under `internal` they are shown.

*`src/gnd/skills/gnd-export/SKILL.md`, step 2 after "it explains, it proves
nothing", and step 3.*

> Its atom blockers count rows spelled differently (`near_miss_count`); read
> the pairs with `--raw` before changing a spelling.
>
> 3. On explicit raw export selection, run the same command with
>    `--raw --out NEW_CERTIFICATE`. Under `GND_DISCLOSURE=customer` this is
>    refused with exit 3; do not retry it in another mode for that reader.

*`src/gnd/skills/gnd-export/references/export-contract.md`, after "`--raw`
explicitly exposes the certificate."*

> Under `GND_DISCLOSURE=customer` every `--raw` is refused with exit 3 and
> nothing is written; under `internal` the raw view is the default.

*`src/gnd/skills/gnd-dev-session/references/judgment-contract.md`, after
"--unredacted only for an explicit raw operator view".*

> Under `GND_DISCLOSURE=customer`, `--unredacted` is refused with exit 3.

*`src/gnd/skills/gnd-dev-session/references/session-v7-contract.md`, after the
feedback redaction paragraph.*

> Feedback redaction is the same in every disclosure mode; `internal` does not
> lift it.

The packaged-skill pins are updated with these edits.

## Pages with no change

| Page | Why it stays |
|---|---|
| `docs/runtimes/lean.md`, `docs/runtimes/souffle.md` | Tutorials run with the mode unset (the runner drops `GND_DISCLOSURE`); their `--raw` is the documented unset behaviour. |
| `docs/bookrec/*`, `docs/expense/*` | Same: tutorials run unset, and their redaction passages describe the unset default. |
| `docs/development/architecture-audit.md` | "redaction" names a module in a historical inventory. |
| `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json` | The `redact` property has no description that states behaviour. |
| `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md` | "redact" refers to user-authored prose in records, not population values. |
| `src/gnd/skills/gnd-dev-session/SKILL.md` | Its "redaction" is of adapter credentials, not population values. |
| `docs/how-to/repair-a-missing-claim.md` | Changed in NM3; it runs unset and links the why-not reference. |
