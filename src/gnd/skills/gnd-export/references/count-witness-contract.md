# Bounded COUNT membership certificate

`gnd witness-count MODEL POPULATION --request REQUEST --raw --out CERTIFICATE`
creates a certificate for one named group. Run
`gnd replay-count MODEL POPULATION CERTIFICATE --request REQUEST` to verify
it against the caller's expected inputs. These commands follow the
[disclosure policy](https://vasiloglou.github.io/gnd-public/reference/disclosure/).
`--out` requires raw output and creates a new file.

## Rule and snapshot scope

The model declares one derived COUNT clause with a single asserted body
fact type. The body binds each role to a distinct variable. The head
projects at least one group variable and one fresh Integer count
variable. `over` and `of` name body variables, and the roles use String,
Boolean or Integer. The clause admits direct variable projection and
has no filters, negation, arithmetic or recursion. The inputs are a
single include-free and reference-free model and its candidate population.
The population must list the entire body relation in `population.covers`.
An opaque value in that relation prevents certification.

Completeness is relative to the declared coverage of the bound population.
For an empty selected group, the certificate succeeds with an empty roster
and count zero. The ordinary checker continues to derive aggregate rows
only for groups with contributing bindings.

## Closed version 1 JSON

A request has exactly `version`, `fact_type` and `group`. The version is
the integer `1`. The fact type identifies the derived COUNT rule. The
group maps each non-count head role name to a typed cell. A cell has
exactly `primitive` and `value`. The value is a JSON string, boolean or
integer matching the cell's declared primitive and the model role.

```json
{"version":1,"fact_type":"method_count","group":{"group":{"primitive":"String","value":"flow"}}}
```

A certificate has exactly `version` (integer `1`), `kind`
(`count-membership`), `binding`, `request`, `count`, `status` and
`members`. The binding contains `model_sha256`, `population_sha256`
and `request_sha256`, each the lowercase SHA-256 of the corresponding
file's exact bytes. Replay uses the caller's request file and compares the
parsed request to the embedded one as well as checking all three digests.

`members` lists distinct contributions in lexicographic order of the
canonical JSON bytes of `[over, of]`. Each entry has exactly `over`
(ordered typed cells in aggregate declaration order), `of` (one typed
cell), and `fact_index` (the lowest zero-based position in the body
relation's population row array that produces this contribution). Count
is the number of members. A nonempty roster has status `complete`. An
empty roster has status `empty-group`.

Replay reconstructs the entire roster from the caller's model, request
and candidate rows. It checks the supplied count, status, order,
contributions and representative positions against that reconstruction.
To get an ordinary positive witness for a member, use `fact_index` to
look up the body row and pass its typed tuple in role order to
`gnd witness`. The [worked example](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/literature/count_fixture)
shows both group outcomes and the individual member witness.

## Verdicts and limits

| Exit | Reason | Meaning |
|---|---|---|
| 0 | JSON null | The exact group membership was established. |
| 1 | `proof-invalid` | A well-formed certificate disagrees with the reconstructed result. |
| 2 | `fragment-unsupported`, `coverage-undeclared`, `opaque-value` | The rule or body relation cannot establish complete membership under this contract. |
| 3 | `input-invalid`, `binding-stale` | An input is unreadable or malformed, or the certificate mismatches the caller's expected inputs. |
| 4 | `work-limit` | Input snapshot bytes, work, or generated output exceeded a limit. |

Replay validates certificate shape first, then reads the external request
and bounded snapshot bytes. An oversized snapshot refuses before digest
comparison. Replay checks bindings before model evaluation and checks
declared coverage before deciding membership. Request and certificate
input byte, depth and scalar limits apply at intake. After checking
bindings, the commands guard YAML snapshot depth before the normal
loaders construct nodes. The JSON snapshot readers apply their existing
depth guard. Inputs are regular files. Unresolved includes fail model
intake.

The limits are 10 MiB per request, certificate, model or population file,
64 container levels, 4,096 UTF-8 bytes per wire string and 128 digits
per wire integer. The scan checks a ceiling of 100,000 body rows and
100,000 cells, accounting for the body width, group projection and
contribution width for every row. At most 10,000 distinct contributions
may be emitted. Generated certificate size includes the canonical final
newline. Refusal yields no certificate.
