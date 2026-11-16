# Scientific competency examples

Run the three worked examples from an installed GND environment.

```sh
python -m gnd.examples.literature.depth --out ./depth-run
```

Read `depth-run/report.json` for the supported answers, explicit unknowns,
and comparison results. The case directories contain the authored root,
the shared vocabulary, the extraction bundle, the population and the
extraction sidecar. The run uses saved extractor responses. GND generates
the bundle and runs verification and checking on all three populations.
The report includes raw digests for these handoffs.

## Questions and evidence

Each question names the predicates it needs. Every supported answer cites
one reviewed span tying its facts to a source version and locator.
An answer whose required facts are absent is unknown within the cited
scope. Some answers have additional limitations described in the source
note, such as the unreported ensemble of the particular molecular run.
The fixture uses original descriptions of the source material, with
local character offsets into those descriptions. The frozen support roster
records the author's source-to-fact review. GND verification establishes
evidence binding and model checking establishes the declared structural
constraints. The reported equation is a representation of a source claim.

- **Physical dynamics.** Equation and regime, boundary treatment,
  discretization, and whether the selected setup reports a measured
  conservation residual. [Clawpack dam-break example](https://www.clawpack.org/gallery/pyclaw/gallery/dam_break.html) and [shallow-water solver derivation](https://www.clawpack.org/riemann_book/html/Shallow_water_approximate.html)
- **Molecular and statistical physics.** System and force field,
  sampling objective, numerical conditions, and whether the result
  transfers to a different solvent environment. [OPES-eABF study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12243082/)
- **Algorithms.** Operator and objective, algorithm components, qualified
  complexity, and whether a requested device benchmark is available.
  [Randomized matrix decompositions, revised preprint](https://arxiv.org/abs/0909.4061v2)

Subject IDs are separate from display labels. The uniqueness constraint
gives each ID at most one display label within a snapshot. The fault
fixture assigns a second label and exercises the checker. Scientific
specialization, component membership and methodological influence are
represented by separate predicates.

## Experiment comparisons

The comparisons use a separate synthetic population. They first report
known differences in dataset version, split, metric, units or effective
experiment conditions. With no known differences, an absent context
field or score makes the comparison unknown. Comparable scores require
all these fields. Baseline, configuration and uncertainty are optional
facts. Record configuration differences that matter to a comparison as
conditions.

## Quantity probes

The example measures what the existing numeric anchors and witness
route do on small controls. The dimension probe uses the same magnitude
in time and energy units. The percentage-point control keeps score
units and absolute-change wording separate. A decimal value that passes
checking is also submitted as an exact witness target. The report
records the actual outcome of each probe.
