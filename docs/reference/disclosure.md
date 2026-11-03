# Choose what GND discloses

GND reads your populations, so many of its outputs can quote population values:
a why-not sample, a witness certificate, a sensitive role in a check report.
Whether that is acceptable depends on who reads the output.

- **Behind your own interface**, the reader is you or your service. Values help:
  they say which fact to add or fix.
- **In front of customers**, the reader may be anyone whose requests your
  service forwards. Values should stay inside.

One setting, the *disclosure mode*, says which of these situations GND is in.
To try it on an example, see
[Run GND behind your interface or in front of customers](../how-to/disclosure-mode.md).

## The three states

| Mode | Declared sensitive roles in check reports | Witness, replay, why-not, Lean and Soufflé outputs | Requests for values |
|---|---|---|---|
| unset | redacted unless `--unredacted` | value-free unless `--raw` or `raw=True`; `api.witness`, `api.replay` and `api.why_not` return raw values | allowed |
| `internal` | shown | raw, in the CLI and the Python API | allowed (already granted) |
| `customer` | redacted | value-free, in the CLI and the Python API | refused, exit 3 or `DisclosureRefused` |

**Unset** is the default and changes nothing: every output and every option
behaves as it did before the mode existed.

**`internal`** acts as if every value option were passed: `--unredacted` on
the check family, `--raw` on `witness`, `witness-view`, `replay`,
`why-not` and the Lean and Soufflé exports, and the matching Python keywords.

**`customer`** withholds two kinds of value:

- in check-family reports, the roles your model declares sensitive with
  `redact: true` (see [declare what is sensitive](#declare-what-is-sensitive));
- in witness, replay, why-not, Lean and Soufflé outputs, every population
  value. The Python functions return what the CLI prints by default:
  `api.why_not` returns the redacted view, and `api.witness` and
  `api.replay` return the default view with no raw certificate.

It does **not** withhold values in check-family messages for roles you have not
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

The value is exactly `internal` or `customer`. The mode governs the commands
in the table below that withhold or refuse values, and the commands that start
processes. For those, GND resolves it in this order:

1. If `GND_DISCLOSURE` holds anything else (`Customer`, a trailing space,
   the empty string), the command refuses with exit 3, even when
   `--disclosure` is given. A mistyped lock never opens.
2. If `GND_DISCLOSURE=customer`, `--disclosure internal` is refused with
   exit 3. The option can tighten the mode, never loosen it.
3. Otherwise `--disclosure`, if given, applies to that invocation; else the
   environment; else the mode is unset.

The commands listed under
[outputs that are the same in every mode](#outputs-that-are-the-same-in-every-mode)
and the commands that emit no values ignore the variable and the option's
value.

The option itself is checked like any other argument. A value other than the
two names, or a second `--disclosure`, is a usage error, exit 64:

<!-- gnd-run expect=0 output=stdout -->
```sh
set +e
gnd --disclosure Customer validate model.orm.yaml 2>&1 | tail -1 | sed 's/ (choose.*//'; echo "exit ${PIPESTATUS[0]}"
gnd --disclosure customer --disclosure customer validate model.orm.yaml 2>&1 | tail -1; echo "exit ${PIPESTATUS[0]}"
```

```text
gnd: error: argument --disclosure: invalid choice: 'Customer'
exit 64
gnd: error: --disclosure may be given at most once
exit 64
```

The Python API has no per-call keyword. It reads the environment, and, when it
runs inside a `gnd` command, that command's mode. `customer` from either
wins.

## What customer mode refuses

Every request for values is refused, not quietly downgraded, so nobody mistakes
a redacted answer for the raw one.

| Request under `customer` | Command line | Python |
|---|---|---|
| `--unredacted` on a check-family command; `unredacted=True` | exit 3 | `DisclosureRefused` |
| `--raw` on `witness`, `witness-view`, `replay`, `why-not`, `export lean`, `export souffle*`; `raw=True` | exit 3 | `DisclosureRefused` |
| `gnd --disclosure internal …` with `GND_DISCLOSURE=customer` | exit 3 | — |
| a malformed `GND_DISCLOSURE` | exit 3 | `DisclosureRefused` |

A refused command prints nothing on stdout and one line on stderr that names the
option or the variable, never a value. `DisclosureRefused` is exported from
`gnd.api` and is a `ValueError`. The
[how-to](../how-to/disclosure-mode.md#requests-for-values-are-refused-not-downgraded)
shows each refusal.

## Outputs that are the same in every mode

These outputs do not follow the mode, and none of them takes a value option.
Do not route them to a customer.

| Output | What it emits | Why it is unchanged |
|---|---|---|
| `gnd exp run` session feedback, attempts and results; `EvaluationSession.check_with_feedback` | declared redaction, always applied | The session contract fixes it, and feedback goes to agents that may be external providers, so `internal` must not lift it. |
| `EvaluationSession.observe` | the caller's own population | It returns what the caller passed in. |
| `gnd discover` | candidate constraints; never value candidates for redacted roles | Its proposals name positions, not values. |
| `gnd export ilp` | undeclared values in its learner input; refuses declared roles | Its job is to hand values to a learner you chose. |
| `gnd fidelity` | the extracted facts it measures | Its input is your own extraction case. |
| `gnd doccheck` | the population values a rendered document misses | Its input is your own rendering case. |

## Child processes

Under `customer`, GND passes `GND_DISCLOSURE=customer` to the processes it
starts: the agents of `gnd exp run`, the stations of `gnd solve` and the
reviewers of `gnd review panel`. Under `internal` or unset it passes
nothing, so a child never gets more disclosure than it would have on its own.

Passing the mode on sets a default for the child, not a lock: an agent controls
its own environment.

## Who customer mode protects

Customer mode protects the end users of an operator-controlled wrapper: a
service that turns a customer's request into GND command-line arguments or
`gnd.api` keywords. Such a caller cannot get values out by asking for them.

For code that runs inside the GND process it is a guard, not a lock: that code
can change the environment or call internal functions. Do not run untrusted
code in the process.

Do not forward arguments that name a program to run: `--executable` on
`export souffle-run`, `export souffle-witness` and `export lean-compile`, and
`--test-argv` and `--adapter-policy` on `exp run` and `solve`. A caller who
chooses the program runs code of their own, and no mode holds after that.

Some signals remain by design, because the mode is applied after the verdict.
A caller who supplies a claimed row learns whether it matches exactly from the
status, the exit code and the per-step counts of `why-not`, `witness` and
`replay`. The near-miss counters add one more: whether the population holds a
value spelled like theirs up to case, spacing and punctuation (see
[values spelled differently](why-not.md#values-spelled-differently)). Here the
claim names the work "Field Notes", which the population spells
"FIELD NOTES":

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/quoted_claims', 'quoted_claims', dirs_exist_ok=True)"
```

<!-- gnd-run expect=0 output=stdout -->
```sh
GND_DISCLOSURE=customer gnd why-not quoted_claims/model.orm.json quoted_claims/spelling-gap.pop.json \
  --fact-type certified --row quoted_claims/claim.json \
  | python -c "import json, sys; b = json.load(sys.stdin)['clauses'][0]['blocker']; print(b['near_miss_count'], b['near_misses'])"
```

```text
1 redacted
```

The count says one row of `authored` matches after normalization; the values
stay withheld.

## Declare what is sensitive

Check-family redaction follows the model. Mark a whole fact type or one role,
as described in the
[representation format](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md):

```yaml
fact_types:
  - id: has_email
    reading: "{Customer} has email {EmailAddress}"
    roles:
      - { object_type: customer_code, role_name: customer }
      - { object_type: email_address, role_name: email, redact: true }
```

The packaged `disclosure` example declares this role; the
[how-to](../how-to/disclosure-mode.md) runs it in each mode.

## Every command and function

Every command, every public `gnd.api` function and every report kind is in
exactly one row. A test keeps this table equal to the code.

<!-- disclosure-table:start -->
| Surfaces | What they disclose |
|---|---|
| Command: `gnd check`, `gnd validate`, `gnd diff`, `gnd verbalize population`, `gnd measure`, `gnd verify`, `gnd judgments check` | declared roles: shown under `internal`, redacted under `customer`; `--unredacted` or `unredacted=True`, where taken, refused under `customer` |
| `gnd.api`: `validate`, `check`, `diff`, `verbalize`, `transition`, `check_with_receipt`, `judgments`, `EvaluationSession.check`, `EvaluationSession.check_with_receipt`, `EvaluationSession.transition` | declared roles: shown under `internal`, redacted under `customer`; `--unredacted` or `unredacted=True`, where taken, refused under `customer` |
| Output kind: `validate`, `check`, `admission`, `verify`, `transition`, `plan`, `batch`, `measure`, `population-verbalization`, `diff` | declared roles: shown under `internal`, redacted under `customer`; `--unredacted` or `unredacted=True`, where taken, refused under `customer` |
| Command: `gnd witness`, `gnd witness-view`, `gnd replay`, `gnd why-not`, `gnd export lean`, `gnd export souffle`, `gnd export souffle-run`, `gnd export souffle-witness` | every value: raw under `internal`, value-free under `customer`; `--raw` or `raw=True`, where taken, refused under `customer` |
| `gnd.api`: `witness`, `replay`, `why_not`, `export_lean`, `export_souffle`, `run_souffle`, `souffle_witness` | every value: raw under `internal`, value-free under `customer`; `--raw` or `raw=True`, where taken, refused under `customer` |
| `gnd.export.service`: `export_lean`, `export_souffle`, `run_souffle`, `souffle_witness` | every value: raw under `internal`, value-free under `customer`; `--raw` or `raw=True`, where taken, refused under `customer` |
| Command: `gnd exp run` (starts processes), `gnd discover`, `gnd export ilp`, `gnd fidelity`, `gnd doccheck` | the same in every mode (see [outputs the same in every mode](#outputs-that-are-the-same-in-every-mode)) |
| `gnd.api`: `EvaluationSession.check_with_feedback`, `EvaluationSession.observe` | the same in every mode (see [outputs the same in every mode](#outputs-that-are-the-same-in-every-mode)) |
| Output kind: `session-feedback`, `session-attempt`, `session-result` | the same in every mode (see [outputs the same in every mode](#outputs-that-are-the-same-in-every-mode)) |
| Command: `gnd solve` (starts processes), `gnd review panel` (starts processes), `gnd review panel-light` (starts processes), `gnd codegen`, `gnd conformance`, `gnd coverage`, `gnd doctor`, `gnd evolve apply`, `gnd evolve finalize`, `gnd evolve preview`, `gnd exp author-expectation`, `gnd exp close`, `gnd exp init`, `gnd exp validate`, `gnd export lean-compile`, `gnd export lean-verify`, `gnd export pyrel`, `gnd export souffle-verify`, `gnd extract`, `gnd import ilp-rules`, `gnd import mined-rules`, `gnd import rai-orm`, `gnd install`, `gnd recovery inventory`, `gnd recovery verify`, `gnd review finalize`, `gnd synth`, `gnd uninstall` | emits no population values |
| `gnd.api`: `CheckReceipt`, `ReceiptRefused`, `DisclosureRefused`, `EvaluationSession`, `verify_lean`, `verify_souffle`, `compile_lean`, `EvaluationSession.reset`, `EvaluationSession.close`, `EvaluationSession.stats` | emits no population values |
| `gnd.export.service`: `verify_lean`, `verify_souffle`, `compile_lean` | emits no population values |
<!-- disclosure-table:end -->

Names bound in `gnd.api` that are library types or helpers (`Model`,
`load_population`, …) emit nothing and are not listed.
