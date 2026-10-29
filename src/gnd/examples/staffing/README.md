# Synthetic staffing example

A small unlabelled population for the rule-miner adapter of the ILP bridge,
used by the documentation page "Compare the rule learners on real runs". Copy
this directory from the installed `gnd` package; no learner install is needed.

All data is synthetic. The people, teams and sites are invented.

| Resource | Purpose |
|---|---|
| `model.orm.yaml` | People, teams and sites: who works in which team, where each team sits, where each person is based and parks |
| `population.yaml` | One population of those facts |
| `learners/amie/` | AMIE 4.0.0's run of record over `gnd export ilp --target amie`: the rules it printed and its run record |
| `learners/amie-2/` | A second, owner-approved run with standard confidence 1 (`-enstd -minc 1`) |

The rule files are AMIE's output byte for byte. `gnd import mined-rules`
reads them; the first run's set is refused because a rule does not hold, and
the second run's is admitted.
