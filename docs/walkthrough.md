# Solve a public model

Use `gnd solve MODEL --workspace DIR` to run a gated station walk. The CLI help lists station selection and timeout options. Each station keeps its own result; the walk log records station order, authorization, captured output and evidence paths.

| Command | Exit | Meaning |
|---|---|---|
| solve | 0 | all selected stations completed with accepted exits |
| | 17 | a gated station walk halted before completing its selection |

A halted walk retains the station's exit and halt reason in its log. Inspect those details before starting another walk.
