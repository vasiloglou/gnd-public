# GND 0.5.0

`gnd export ossie` now writes the tables beside the ontology: a semantic
model and a mapping, five files in all, or your own delivered tables with
`--physical-binding`. `--ontology-only` keeps the three-file run.

Also in this release: PyRel rules programs for models with external
uniqueness, anchored rules, `Number` values and role-scoped value rules;
include roots in `gnd judgments check`, the new `gnd flatten` and the PyRel
export; unattended growth from a reviewed vocabulary; the literature
examples over a host's own model and documents; and COUNT certificates with
`gnd witness-count` and `gnd replay-count`.

Two things a script may notice: a default `gnd export ossie` run writes two
more files and can stop on the size bound for them, and the PyRel rules
programs refuse some inputs that 0.4.0's programs accepted. See the
[full release notes](https://github.com/vasiloglou/gnd-public/blob/main/docs/release-notes.md).

The attached wheel and sdist were built from
`85d076ba384e67b1f992cfd6b9a596ca01b3d4e7`.
