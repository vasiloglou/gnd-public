# IK4 approval corpus

This is the owner-approval instrument for IK4 (spec IK4-D1), the `gnd discover`
command of the
[IK4 spec](../../../../.gnd-planning/milestones/induced-knowledge/notes/phase-IK4-spec.md).
It was committed red, before any implementation file.

**This file tells each case's story without its answer.**
- The answers (every expected candidate, support count, suppression count and
  exit) are in [`expected.json`](expected.json).
- The inputs are in [`cases.json`](cases.json) and the model and population
  files beside them.
- Every answer was written by hand from the approved spec. The existing
  `gnd check` was used only to confirm the pass/fail verdicts the spec defers to.
- The harness is `tests/test_discover.py`.

## The fixtures

**`staff.orm.yaml`** has four fact types with no declared constraints:
- People are in teams.
- People have grades.
- Teams are led by people.
- People have skills.

**`staff.population.yaml`** has six people (1–6) and two teams (A, B):
- three people in each team;
- five people with a grade (person 6 has none);
- A led by 1, B led by 4;
- four skill rows (person 1 has two skills).

**Other populations and models:**
- `staff-declared.*`: the same, plus a numbering fact type (person ↔ person id)
  and a ternary rating fact type. It also declares one constraint for each
  suppression rule.
- `near-miss-2.population.yaml` and `near-miss-3.population.yaml`: 40 people in
  team A, two or three of whom are also in team B.
- `empty.population.yaml`: nothing at all.
- `other-model.population.yaml`: names a different model id.
- `bad name.population.yaml`: a valid population whose file name contains a
  space.
- **Generated in the test:** an over-cap population (about 14 MB), and a
  near-cap one (68,000 people, about 9.7 MiB). Their recipes are in
  `cases.json`.

## Cases

**Each family alone, on the base population:**

| Case | Story |
|---|---|
| K01 | Uniqueness only. Some roles are unique per row, some repeat. Each fact type's two-role key is trivially unique. |
| K02 | Mandatory only. Some roles are played by every member of their object type, some are not. Two value types appear in only one role each. |
| K03 | Value only. Every role has few distinct values, including the entity roles, whose values are reference ids. |
| K04 | Value with `--max-values 2`: only roles with at most two distinct values qualify. |
| K05 | Frequency only. Some roles occur once per value, which is uniqueness, not frequency. Others occur up to twice, and one exactly three times. |
| K06 | Subset, equality and exclusion over the seven pairs of same-typed roles in different fact types. The two Team roles hold exactly the same teams. |
| K07 | The same with `--max-pairs 1`: only the first pair is compared. |
| K08 | All seven families together, at the default bounds. The proposal is also previewed by `gnd evolve`, and the run is repeated to check determinism. |

**Suppression:**

| Case | Story |
|---|---|
| K09 | The declared model already says several things: a uniqueness (alethic), a team-leader frequency of at most one, the grade domain, the equality of the two Team roles, the person ↔ number reference fact, and a uniqueness on the ternary's first role. Discovery must not re-suggest what these state or entail, and must count each by rule. |

**Near-misses and empty input:**

| Case | Story |
|---|---|
| K10 | 40 people, 2 of them in two teams: "each person is in one team" is broken by 2 of 40. |
| K11 | The same with 3 of 40. |
| K13 | No data at all. |

**Refusals:**

| Case | Story |
|---|---|
| E1 | An unknown flag. |
| E2 | The population file does not exist. |
| E3 | The population names a different model id. |
| E4 | The population is over the 10 MiB cap. |
| E5 | The `--out` path is an existing symbolic link. |
| E6 | `--actor` is missing. |
| E7 | The population's file name cannot be an induction evidence ref, because it contains a space. |

**Work bound:**

| Case | Story |
|---|---|
| N1 | The near-cap population, at the default bounds: discovery's work counter against the ceiling stated in the answer key. |

## Corpus findings: where writing the answers had to pin the spec down

Each is a reading the answers adopt. The owner approves or amends it with the
corpus.

- **C-F1 (exit codes; differs from spec §5 and T10).** GND's one global argument
  parser exits **64** for usage errors, such as an unknown or missing flag, for
  every command. The spec's "invalid arguments exit 3" cannot hold for flags.
  E1 and E6 answer 64, and 3 is kept for invalid inputs.
- **C-F2.** The candidate-against-candidate counter for a frequency whose largest
  group is 1 (spec §6 rule 2, unnamed there) is named `redundant-frequency`.
- **C-F3.** `--max-pairs` counts **unordered** role pairs. Each pair yields two
  subset candidates (both directions), one equality and one exclusion.
- **C-F4.** A candidate matching several catalogue rows is counted under the first
  row in the spec's table order. For example, a two-role key that is both
  spanning and a superkey counts as `spanning-uniqueness`.
- **C-F5.** Pairs are enumerated by object type in model declaration order, not
  sorted by id, then by `(fact type, role)` in declaration order. Within a pair,
  subset X⊆Y comes before Y⊆X.
- **C-F6.** GND's loaders accept symbolic links for inputs. The spec's exit 74
  therefore applies to the files discover writes: E5 makes `--out` a link.
- **C-F7 (owner attention: noise).** A value type that appears in only one role
  is trivially mandatory there. K02 emits two such candidates, because the spec
  emits every passing candidate with support > 0.
- **C-F8 (owner attention: noise).** Value candidates on entity roles list
  reference ids (K03, `[1, 2, 3, 4, 5, 6]`), because the spec makes every role
  with at most 20 distinct values a candidate.
- **C-F9.** A near-miss counterexample id is the first fact of a violating
  subject, in order of first appearance.
- **C-F10.** Spec §6's report shape gives near-miss rows no host. A row carries
  `host` (the fact type id, or `null` at top level) beside `family` and
  `constraint`, so a reader can tell where the almost-rule lives.

## Red run at the base commit

18 cases fail, because `gnd discover` does not exist. Three tests pass at B:
- the answer-key coverage check;
- E1 and E6, which expect exit 64, the same exit the parser gives today for an
  unknown command. They discriminate only once the command exists, and are
  kept because the answer is right either way.
