# COUNT membership for a named group

Copy this directory to a writable location and run the commands there with
an installed `gnd`. The example ships under `gnd/examples/literature/count_fixture`.

```sh
gnd check model.orm.yaml population.json
gnd witness-count model.orm.yaml population.json --request group.json --raw --out flow.cert.json
gnd replay-count model.orm.yaml population.json flow.cert.json --request group.json --raw
gnd witness-count model.orm.yaml population.json --request empty-group.json --raw --out empty.cert.json
gnd replay-count model.orm.yaml population.json empty.cert.json --request empty-group.json --raw
```

The `flow` group has two contributions. Alpha and beta both have the
label `included`. Their distinct member keys count separately. Two source
occurrences support beta's contribution, and the certificate selects its
first occurrence. The `empty` group has no contributions in the declared
covered relation. Its certificate replays successfully with an empty
roster. The aggregate checker yields rows for `flow` and `other` only.

The first member of the `flow` roster points to row index 2 of
`observation`, the alpha row. The supplied `member-targets.json` requests
that row for a separate positive witness.

```sh
gnd witness model.orm.yaml population.json --targets member-targets.json --raw --out alpha.cert.json
gnd replay model.orm.yaml population.json alpha.cert.json
```
