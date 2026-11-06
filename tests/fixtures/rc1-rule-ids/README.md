# RC1 corpus: declared rule identity in `gnd check` (report version 15)

This corpus is the approval instrument for phase RC1 of the
`rule-check-adoption` milestone (spec:
`.gnd-planning/milestones/rule-check-adoption/notes/phase-RC1-spec.md`, §11).
It is committed before any implementation and fails until RC1 lands.
`tests/test_rc1_rule_ids.py` runs every case from this directory, with the
paths written below, and compares the result with the answer key in
`expected/`. This README tells each case's story only; the expected bytes
and exit codes are in `expected/`, not here.

Every command runs with this directory as the working directory.

## The models

- `models/components.orm.yaml`: a component graph. Components use other
  components and sit in areas. Two rules, both with an author `id` and a
  `remedy` (what to do about a violation): `no_import_loops`, a ring rule
  saying the uses relation has no cycle, declared inside the fact type; and
  `no_legacy_area`, a top-level rule saying no component lives in the
  `legacy` area.
- `models/components-positional.orm.yaml`: the same two rules with no `id`
  and no `remedy`; the ring rule keeps a `rationale`.
- `models/exact-terms.orm.yaml`: a model with derived fact types computed
  by exact arithmetic (a residue `value mod divisor`), with no redaction.
- `models/exact-terms-redacted.orm.yaml`: the same model with one role
  marked `redact: true`.
- `models/temporal.orm.yaml`: a model with a `Duration` value type.
- `models/reference/model.orm.yaml`: a model that binds a fixed reference
  population (`models/reference/references/catalog.pop.json`).

## The cases

1. **declared-fail.** `gnd check models/components.orm.yaml
   populations/graph-fail.pop.yaml --rule-ids --format json`. Two
   components import each other, and the `cli` component is in the
   `legacy` area, so both rules fail. The report names each failing rule by
   the id its author wrote, says that the id was declared, and carries the
   author's remedy. Everything else in the report is what today's report
   says for the same input, apart from the report version and the model
   digest (the model now contains `remedy` text).
2. **positional-pass.** `gnd check models/components-positional.orm.yaml
   populations/graph-pass.pop.yaml --rule-ids --format json`. No cycle and
   no legacy component, so both rules pass. The rules have no ids, so each
   is addressed by its position and says so; neither has a remedy, and the
   `rationale` is not used in its place.
3. **derivation-plain.** `gnd check models/exact-terms.orm.yaml
   populations/term-ok.pop.yaml --rule-ids --format json`. Every derived
   fact is computed and claimed correctly. The derivation results appear
   exactly as today's report shows them.
4. **derivation-mod-zero.** `gnd check models/exact-terms.orm.yaml
   populations/term-input.pop.yaml --rule-ids --format json`. One ticket
   has divisor 0, so the residue cannot be computed: the derivations are
   unchecked with the reason `term:mod-zero`, and the run is indeterminate.
   The new report must describe that reason; today's report schema does not.
5. **text-declared-fail.** Case 1 without `--format json`: the text report
   names each failing rule by its id and its position, with the remedy on
   the next line.
6. **refuse-redaction**, 7. **refuse-temporal**, 8. **refuse-reference.**
   `gnd check <model> populations/absent.pop.yaml --rule-ids --format json`
   for the redacted, temporal and reference models. `--rule-ids` does not
   support these kinds of model, so the run is refused before the
   population is read; the population file does not exist, and that is
   not what the report complains about. The report keeps the version the
   model would get without the flag.
9. **conflict-populations.** `gnd check models/components.orm.yaml
   --populations populations --rule-ids --format json`. `--rule-ids`
   applies to one population only; the command is a usage error and prints
   no report.
