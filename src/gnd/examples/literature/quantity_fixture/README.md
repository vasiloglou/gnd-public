# Exact time-step example

From an installed GND environment, copy this packaged fixture to an
empty working directory. Run the checked anchor, witness and replay.

```sh
gnd check time.orm.yaml time.population.json --document source.txt --anchors time.anchors.json --format json
gnd witness time.orm.yaml time.population.json --targets time.targets.json --raw --out time.witness.json
gnd replay time.orm.yaml time.population.json time.witness.json --raw
```

The source states the same time step in three units. The sidecar selects
the second matching occurrence, `0.002 ps`, and binds the entire span.
The energy value and the sub-femtosecond duration have different meanings.
The `time-fs` constraint enforces this distinction for the coefficient.
The model's other two constraints fix the display scale and unit.

The replayed tuple `[2, 3, "ps"]` encodes an exact coefficient and scale.
For display, `Decimal(2).scaleb(-3)` gives `0.002` in ps. The checker
establishes the source anchor. The replay checks the tuple against the
bound population. Native Float and non-integral Number still receive
`fragment-unsupported` in the witness fragment.
