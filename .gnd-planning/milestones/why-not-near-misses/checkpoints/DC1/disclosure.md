<!-- DC1 draft, 2026-11-01. Illustrative: written from the approved plan r3
before any code exists. Not committed to docs/. Outputs on this page are
illustrative, not real runs; DC2 replaces them with executed `gnd-run` blocks. -->

# Choose what GND discloses

GND reads your populations, so many of its outputs can quote population values:
a why-not sample, a witness certificate, a sensitive role in a check report.
Whether that is acceptable depends on who reads the output.

- **Behind your own interface**, the reader is you or your service. Values help:
  they say which fact to add or fix.
- **Facing a customer**, the reader may be anyone your service forwards
  requests for. Values should stay inside.

One setting, the *disclosure mode*, says which of these situations GND is in.

## The three states

| Mode | Declared sensitive roles in check reports | Witness, replay, why-not, Lean and Soufflé outputs | Requests for raw values |
|---|---|---|---|
| unset | redacted (as today) | value-free by default; raw on request (as today) | allowed (as today) |
| `internal` | shown | raw, in the CLI and the Python API | allowed |
| `customer` | redacted | value-free, in the CLI and the Python API | refused, exit 3 |

**Unset** is the default and changes nothing: every output and every flag
behaves as it did before the mode existed.

**`internal`** acts as if every raw option were passed: `--unredacted` on the
check family, `--raw` on `witness`, `witness-view`, `replay`, `why-not`, `lean`,
`souffle`, `souffle-run` and `souffle-witness`, and the matching Python
keywords.

**`customer`** withholds two kinds of value:

- in check-family reports, the roles your model declares sensitive with
  `redact: true` (see [declaring sensitive roles](#declare-what-is-sensitive));
- in witness-lane, Lean and Soufflé outputs, every population value. The Python
  functions return what the CLI prints by default: `api.why_not` returns the
  redacted view, and `api.witness` and `api.replay` return the default view
  with no raw certificate.

It does **not** redact values in check-family messages for roles you have not
declared. Declare them.

## Set the mode

Set the environment variable of the process that runs GND:

```sh
export GND_DISCLOSURE=customer
```

or pass the root option, before the subcommand:

```sh
gnd --disclosure internal why-not model.orm.yaml population.json --fact-type cited_by
```

The value is exactly `internal` or `customer`. GND resolves the mode in this
order:

1. If `GND_DISCLOSURE` is set to anything else (including `Customer`, a trailing
   space or the empty string), a command that can emit values refuses with exit
   3, even when `--disclosure` is given. A mistyped lock never opens.
2. If `GND_DISCLOSURE=customer`, `--disclosure` may only say `customer`;
   `--disclosure internal` is refused with exit 3. The option can tighten the
   mode, never loosen it.
3. Otherwise `--disclosure`, if given, applies to that invocation; else the
   environment; else the mode is unset.

The Python API has no per-call keyword. It reads the environment, and when it
runs inside a `gnd` command, that command's mode; `customer` from either wins.

## What customer mode refuses

Every request for values is refused, not quietly downgraded, so a caller never
mistakes a redacted answer for the raw one.

| Request | Under `customer` |
|---|---|
| `--unredacted` on a check-family command, `unredacted=True` in Python | exit 3 / `ValueError` |
| `--raw` on `witness`, `witness-view`, `replay`, `why-not`, `lean`, `souffle*`; `raw=True` in Python | exit 3 / `ValueError` |
| `gnd --disclosure internal …` with `GND_DISCLOSURE=customer` | exit 3 |
| a malformed `GND_DISCLOSURE` | exit 3 |
| a misspelled or repeated `--disclosure` value | exit 64 (usage) |

The refusal names the option or the variable, never a value.

```json
{"status": "refused", "reason": "disclosure-refused",
 "detail": "raw output is refused in customer disclosure mode"}
```

*Illustrative; the exact payload per command is fixed in the NM2 spec.*

## Outputs that are the same in every mode

These outputs do not follow the mode. None of them accepts a raw option.

| Output | What it emits | Why it is unchanged |
|---|---|---|
| Session feedback, attempts and results (`gnd exp run`) | declared redaction, always applied | The contract fixes `applied`; feedback goes to agents that may be external providers, so `internal` must not lift it. |
| `gnd discover` | candidate constraints; never value candidates for redacted roles | Owner ruling of 2026-10-25. |
| `gnd export ilp` | undeclared values in its prompt; refuses declared roles | Its job is to hand values to a learner you chose. |
| `gnd fidelity` | quotes the extracted fact it measures | Its input is your own extraction case. |

Do not route these outputs to a customer.

## Child processes

Under `customer`, GND passes `GND_DISCLOSURE=customer` to the processes it
starts: the agents of `gnd exp run` and the stations of `gnd solve`. Under
`internal` or unset it passes nothing, so a child never gets more disclosure
than it would have had on its own.

Passing the mode on sets a default for the child, not a lock: an agent controls
its own environment.

## Who customer mode protects

Customer mode protects the end users of an operator-controlled wrapper: a
service that takes a customer's request and turns it into GND command-line
arguments or `gnd.api` keywords. Such a caller cannot get values out by asking
for them.

It is a guard, not a lock, for code that runs inside the GND process: that code
can change the environment or call internal functions. Do not run untrusted
code in the process.

One signal remains by design. A why-not answer in customer mode still shows
`near_miss_count`. A caller who supplies a `--row` learns whether the
population holds a value spelled like theirs up to case, spacing and
punctuation (see [near-misses](why-not.md#values-spelled-differently)).

## Declare what is sensitive

Check-family redaction follows the model. Mark a whole fact type or one role:

```yaml
fact_types:
  - id: has_email
    reading: "{Customer} has email {EmailAddress}"
    roles:
      - object_type: customer
        role_name: customer
      - object_type: email_address
        role_name: email
        redact: true
```

The packaged `disclosure` example declares one sensitive role; the
[disclosure how-to](../how-to/disclosure-mode.md) runs it in both modes.

## Every command and function

<!-- DC1: in the shipped page this table is generated from the NM2 coverage
test, which classifies every command and every public Python function. -->

| Surface | Class | `internal` | `customer` |
|---|---|---|---|
| `gnd check`, `measure`, `verify`, `judgments` and their API functions | site (declared redaction) | shown | redacted; `--unredacted` refused |
| `gnd witness`, `witness-view`, `replay`, `why-not`; `api.witness`, `api.replay`, `api.why_not` | site (view redaction) | raw | value-free; `--raw` refused |
| `gnd export lean`, `souffle`, `souffle-run`, `souffle-witness` and their API functions | site (view redaction) | raw | value-free; `--raw` refused |
| `gnd exp run` sessions, `discover`, `export ilp`, `fidelity` | emits values in every mode | as today | as today |
| `gnd validate`, `codegen`, … | value-free | — | — |

*Abbreviated for DC1.*
