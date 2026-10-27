# Measuring host labels

`gnd measure --labels` measures the checker over populations **you labelled
yourself**, instead of over `gnd synth` output. Use it when you already know,
for real data, which rules each population should break, or which populations
are good and which are bad. **The labels are your claim.** GND checks that they
are well-formed and bound to the right model and files; it does not check that
they are true.

This page is the one home of the label manifest's contract. To see it end to
end, [find the rule your auditors are really using](../tutorials/learn-rules.md)
scores a written rule against an auditor's labels.

```
gnd measure MODEL --labels MANIFEST [--out OUT] [--format text|json]
```

`--labels` replaces `--populations`. Giving both, or neither, is exit 64.
`--promote` needs synth sidecars, so it is refused with `--labels` (exit 64).

## The manifest (`gnd-labels/1`)

A JSON file of at most 1 MiB, validated by the packaged closed schema
`labels.schema.json`. Population paths are relative to the manifest's folder.

```json
{"schema_version": "gnd-labels/1",
 "model_sha256": "<sha256 of the model file's bytes>",
 "mode": "expected-state",
 "populations": [
   {"id": "march", "path": "pops/march.yaml", "sha256": "<sha256 of that file>",
    "expectations": {
      "id:u_person_team": {"ground_truth": "violated", "expected_verdict": "fail"},
      "fact_types[person_has_skill].constraints[0]":
          {"ground_truth": "satisfied", "expected_verdict": "pass", "reason": "audited"}}}]}
```

- **Modes.** In `expected-state` mode, each population says, for **every** rule in
  the model, what is true and which verdict a correct checker should give. In
  `class` mode, each population carries `"class": "positive"` or `"negative"`,
  and a top-level `rules` object says which class each rule should fire on:
  `"rules": {"id:u_person_team": {"fires_on": "negative"}}`.
- **Naming a rule.** Use `id:<constraint id>` when the rule has an `id`. Use the
  checker's positional form, `fact_types[<fact type>].constraints[<i>]` or
  `constraints[<i>]`, only when it has none. An unknown id, a positional name for
  a rule that has an id, or a position past the end is refused, naming the ref.
- **Binding.** `model_sha256` must match the model file, and each population's
  `sha256` must match its bytes. A changed file is refused, never measured.

| Bound | Limit |
|---|---|
| manifest | 1 MiB |
| populations | 1 to 10,000 (in practice the 1 MiB cap allows about 8,000) |
| rules (class mode) | 1 to 1,024 |
| a rule name | 256 characters |
| `reason` | 256 characters |
| each population | the usual 10 MiB population cap |

## Expected-state mode: report schema 4

Each label is scored with the same cell table `gnd measure` uses for synth
corpora, so the `per_constraint` rows and `checker_defects` have the same shape
and meaning. Two differences, both because a host label has no sidecar:
- defect rows have no `sidecar` or `seed`;
- `wrong_attribution` is always `0` and `set_attributed_evidence` always `false`.

A label must be consistent with itself: `satisfied` with an expected `fail`, for
example, is refused. As on the synth path, a wrong verdict on an **alethic** rule
is a checker defect and exits 6; a wrong verdict on a deontic rule is measured
but is not a defect.

## Class mode: report schema 5

For each rule, six counts, each with its numerator and denominator. The cell
definitions live in the docstring of `gnd.measure.agreement`; in short:
- a rule **fired** on a population when its verdict is `warning` or `fail`, and
  was **silent** when it is `pass`;
- `fired_on_negative`, `fired_on_positive`, `silent_on_negative` and
  `silent_on_positive` count only populations of that class where the verdict
  was decided;
- `vacuous` and `unchecked` count over all populations, and are never part of
  another count.

The agreeing counts for a rule that fires on `negative` are `fired_on_negative`
and `silent_on_positive`. There is no accuracy or F1 figure. Disagreement is
evidence, not an error: class mode exits 0.

Both report variants carry a `labels` block (the manifest's path and digest,
the model digest, the mode, one row per population, and the work done) in place
of the synth-only seeds, pools and sidecars. The work is one unit per population
checked plus one per label scored, and never exceeds P × (1 + C) for P
populations and C model constraints. Reports carry no timestamp, so two runs give
the same bytes.

## Exits

| Exit | Meaning |
|---|---|
| 0 | done (class mode, whatever the agreement) |
| 3 | the manifest is not valid JSON or fails the schema; wrong model; an unknown or misused rule name; an unlabelled rule; a self-contradicting label; a population path that leaves the manifest's folder, is missing or has the wrong digest |
| 5 | a population fails to load |
| 6 | expected-state mode found a checker defect |
| 64 | `--labels` with `--populations`, neither, or `--labels` with `--promote` |
| 66 | the manifest or the model does not exist |
| 70 | an internal accounting fault |
| 74 | the manifest or a population is a symbolic link |
