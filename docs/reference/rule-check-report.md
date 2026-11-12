# Rule-check report (version 15)

`gnd check MODEL POPULATION` with `--rule-ids`, `--baseline BASE` or
`--allow-vacuous` writes report version 15. It is the version-7 snapshot
report with a rule's own identity in every verdict and room for a baseline.
Without those flags nothing changes: the check writes the version its model
gets today. The how-to [Adopt rules on a project that already breaks
them](../how-to/adopt-rules-with-a-baseline.md) works through every field on
a small example. The closed schema is the `rule_ids_report` branch of
[`report.schema.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/report.schema.json).

## Flags

| Flag | Does | Implies |
|---|---|---|
| `--rule-ids` | report version 15 | — |
| `--baseline BASE` | judges the population BASE under the same model and marks each violation new or standing | `--rule-ids` |
| `--allow-vacuous` | exits 0 when vacuous rules are the only shortfall | `--rule-ids` |

All three apply to one plain snapshot check. With `--populations`, the
transition arm (`--pre`, `--steps`, `--post`), `--anchors`, `--document`,
`--composition`, `--sources`, `--admission` or `--compiled-operations`, the
command exits 64 before reading the model.

## Refusals

Version 15 describes a plain version-7 model only. Each refusal exits 3,
before either population is read, and reports at the version the model gets
without the flags:

| Rule id | Model |
|---|---|
| `check:rule-ids-unsupported` | uses temporal terms (version 11), has an active redaction policy (version 9), or declares reference populations (wrapped as version 12) |
| `check:baseline-unsupported` | has structured derivations, under `--baseline` only; `--rule-ids` alone accepts it |

An ill-formed base exits 3 with the base's own issues, each path prefixed
`baseline:`; the base's warnings are prefixed the same way.

## Fields added to each verdict

| Field | Value |
|---|---|
| `address` | `constraint:<id>` when the rule declares an `id`, else its position, `fact_types[<fact type>].constraints[<n>]` or `constraints[<n>]` |
| `addressing` | `declared-id` or `positional` |
| `remedy` | the rule's `remedy` text, or `null`; `rationale` is never copied in its place |
| `novelty` | under `--baseline`, for a failing or warning verdict: `new` when any of its offending rows is new (or, with no rows, when the rule did not fail in the base), else `standing`; otherwise `null` |
| `row_novelty` | under `--baseline`, a list aligned one to one with `offending_facts`, each `new` or `standing` (`[]` for a failure without rows); otherwise `null` |

Every version-7 verdict field is unchanged, with one exception for `acyclic`
rules.

**Acyclic rules list every loop edge.** A failing `acyclic` rule (and the
loop part of `acyclic-intransitive`) lists one `[from, to]` row for every
edge inside a strongly connected group, instead of version 7's single cycle,
and its message names the groups: `2 strongly connected groups (sizes 2, 2)
hold 4 edges`. Adding a separate loop does not change the values of an
existing loop's rows (their position in the list may shift), which is what
makes them usable as baseline keys: matching ignores row order.

Derivation findings keep the version-7 shape.

## Fields added to the report

| Field | Value |
|---|---|
| `baseline` | `null` without `--baseline`; otherwise the block below |
| `allow_vacuous` | `true` when `--allow-vacuous` was given |

The `baseline` block:

| Field | Counts |
|---|---|
| `population`, `population_sha256` | the base path as given and the sha256 of the exact bytes read |
| `new` | head offending rows (or row-less failures) not in the base |
| `standing` | those also in the base |
| `resolved` | base ones not in the head |
| `positional_keyed` | head keys that use a positional address; they move when a rule is inserted above, and the text output warns when there are any |
| `undecided` | distinct rules unchecked in the head or the base, of either modality; a rule unchecked in both counts once |

A key is a rule's address plus the canonical JSON of one offending row, with
numbers compared by value (`1` and `1.0` are one key). Warnings (advisory
rules) are marked and counted like failures but, as without a baseline,
never decide the exit code.

## Exit codes

Once the model and the populations have loaded (a load failure or refusal
returns 3 first), the precedence is 1 > 4 > 2 > 0, as for every check.

| Exit | Without `--baseline` | With `--baseline` |
|---|---|---|
| 1 | a must-hold rule fails | a must-hold rule fails with a new row |
| 4 | a must-hold rule is unchecked | a must-hold rule is unchecked in the head or the base |
| 2 | a rule is vacuous (either modality) | a rule is vacuous in the head (either modality) |
| 0 | none of the above | none of the above |

`--allow-vacuous` turns a 2 into 0, and nothing else. `outcome` and
`acceptance_ready` follow the exit code. When `--baseline` is given, or when
`--allow-vacuous` accepted a vacuous run, the `assurance` block is the
uncertified one for that exit code (`assurance_level: none`): the certified
path attests the plain check's decision, which these runs do not report.

## Text output

With any of the three flags, each verdict line names the rule by its
declared address, with its position in brackets, and prints `remedy:` on the
next line when the rule has one. Under `--baseline` the outcome reads
`[fail, new]` or `[fail, standing]`, and a closing `BASELINE` block prints
the base path and the counts. Under `--allow-vacuous`, a last line counts the
vacuous rules the option covers; it is printed whenever the option is on and
a rule is vacuous, including in a run that fails for another reason, so the
exit code is the verdict.

## Other consumers

`gnd coverage` does not accept version-15 reports; it refuses them with its
existing version message.

## Related formats

- `remedy` is a constraint field: see the [constraint
  reference](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/constraint-reference.md).
- `source: tool-output` and `producer` are population header fields: see the
  [population format](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/population-format.md).

## Guarded antecedent diagnostics

`gnd check MODEL POPULATION --guarded-diagnostics` uses the plain
rule-check scope above and implies `--rule-ids`. It can be combined with
`--baseline` and `--allow-vacuous`. The JSON report uses version 16. Its
guarded verdicts include:

```json
{"guarded_antecedent": {"binding_count": 0, "first_empty_atom_index": 1}}
```

`binding_count` counts the distinct bindings from the completed antecedent
join. It is null when the join is unavailable, including an empty relation
whose coverage was omitted. A covered empty relation gives zero. When all
antecedent relations have available rows and the join produces no binding,
`first_empty_atom_index` identifies the first prefix with no matches in
declared atom order, starting at zero. Otherwise the index is null. A
complete antecedent can have a known count even if the consequent is
undecided. These fields leave verdicts and exit bands as reported by the
same check without this option. Text output lists the same observations.

For authoring-time findings on literal values, see the ORM
[constraint reference](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/constraint-reference.md).

## Comparing two rule editions

Run `gnd check HEAD POPULATION --baseline-model BASE --format json` to compare
the findings of two models against the same captured population bytes.
Both models must use the same vocabulary and be eligible for the plain
rule-ID check. The population must be valid under both editions. If the
editions declare different model IDs, omit the optional population
`model_id` header to use the population with both.

The `gnd-rule-edition-comparison/1` result includes the population SHA-256,
each side's model digest and check band, and the rule rows. Rules pair by
declared address. The pairing is `paired`, `added`, `removed`, or
`unpaired` for an anonymous rule. Each side carries its own positional
reference, family, verdict and modality. An available `delta` holds
`base_only`, `head_only` and `standing` offending bindings. A rowless
failure is represented by null. Standing entries retain both original
bindings. For guarded rules, shared unambiguous antecedent roles align
variables across editions. The shared projection must cover every variable
of at least one edition and keep distinct bindings separate. An ambiguous
mapping or a collision withholds that rule's delta and supplies a reason.

Exit 0 means the comparison completed, even if either side failed its
ordinary check. Exit 3 identifies invalid input or incompatible vocabulary.
Exit 4 means the comparison was incomplete. An unchecked rule, an
ambiguous alignment, or a projection collision is identified on its row. A side check at
exit 4 also leaves the overall comparison incomplete.
Exhausting the comparison's 1,000,000-unit work budget yields an empty rule
list and `comparison-work-limit`. The text form lists the directional
bindings and the side check bands. This option is exclusive with
`--baseline`, other rule-ID output flags, and other check arms.
