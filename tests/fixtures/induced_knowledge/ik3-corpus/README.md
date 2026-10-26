# IK3 approval corpus -- measuring host-labelled populations

Owner ruling IK3-D1 (corpus-first): these cases and their hand-written answers
are the approval instrument for `gnd measure MODEL --labels MANIFEST`. Inputs
are listed in [cases.json](cases.json), answers in [expected.json](expected.json),
and the harness is `tests/test_measure_labels.py`. The manifests were written by
`.gnd-planning/milestones/induced-knowledge/evidence/IK3/build_ik3_corpus.py`,
which fills in real file digests; the answers in it are written by hand from spec
r1 (§5, §6, §8). The existing `gnd check` was used only to confirm the verdict
each population draws.

## The model and its five populations

[labels.orm.yaml](labels.orm.yaml) is a small staff model with three rules:

| Rule | Kind | Modality | Ref in the manifest |
|---|---|---|---|
| a person is in at most one team | uniqueness | alethic | `id:u_person_team` |
| every person has a grade | mandatory | deontic | `id:m_person_grade` |
| a person has at most two skills | frequency | deontic | `fact_types[person_has_skill].constraints[0]` (no id) |

The report keys rows by the checker's positional refs, so the uniqueness rule
appears as `fact_types[person_in_team].constraints[0]` and the mandatory rule as
`fact_types[person_has_grade].constraints[0]`.

| Population | What is in it | uniqueness | mandatory | frequency |
|---|---|---|---|---|
| `pops/ok.yaml` | three people, two teams, grades, skills | pass | pass | pass |
| `pops/dup.yaml` | person 1 is also in team B | **fail** | pass | pass |
| `pops/nograde.yaml` | person 3 has no grade | pass | **warning** | pass |
| `pops/noskill.yaml` | nobody has a skill | pass | pass | **vacuous** |
| `pops/opaque.yaml` | one skill row's person is hidden | pass | **unchecked** | **unchecked** |
| `pops/broken.yaml` | names a fact type the model lacks | does not load | | |

## Expected-state mode (report schema 4)

Each population says, for every rule, what is true and what a correct checker
should say. Measure scores the checker's verdict against that label with the
same table the synth path uses.

- **E1 -- all labels right.** Three populations; every rule's label matches. Every
  rule gets `correct 3`, no defects, exit 0.
- **E2 -- one wrong label.** The duplicate-team population is labelled as
  satisfying the alethic uniqueness rule. The checker says fail, so the
  uniqueness rule gets `correct 2, false_fail 1`, the report lists one
  false-fail defect, and the exit is 6. (An alethic rule is needed here: a
  deontic disagreement is measured, not a checker defect -- finding C-F4.)
- **E3 -- nothing to check, or cannot check.** The no-skills population is
  labelled `no-subjects / vacuous` for frequency; the hidden-person population
  is labelled `satisfied / unchecked` for mandatory and frequency. All `correct`.
- **E4 -- a label that contradicts itself** (`satisfied` but expect `fail`): exit 3.
- **E5 -- a rule left unlabelled** (ruling D4: every rule, every population): exit 3.
- **E6 -- a positional ref to a rule that has an id:** exit 3.
- **E7 -- an id no rule carries:** exit 3, naming the id.
- **E8 -- a manifest written for another model** (wrong `model_sha256`): exit 3.
- **E9 -- a population whose bytes changed** since the manifest was written: exit 3.
- **E10 / E20 -- a population path outside the manifest's folder** (`../`, or absolute): exit 3.
- **E11 -- a population that will not load:** exit 5.
- **E12 -- a population path that is a symbolic link:** exit 74; it is not followed.
- **E13 / E14 -- both `--labels` and `--populations`, or neither:** exit 64.
- **E15 -- the manifest is missing:** exit 66.
- **E16 -- not JSON** (a NaN and a repeated key): exit 3.
- **E17 -- over 1 MiB:** exit 3.
- **E18 -- nested deeper than 64 levels:** exit 3.
- **E19 -- an unknown field:** exit 3.
- **E21 -- a positional ref past the end of its fact type's rules:** exit 3.
- **E22 -- a reason over 256 characters:** exit 3.
- **E23 -- a class on an expected-state population** (mode/field mismatch): exit 3.
- **E24 -- no populations:** exit 3.

## Class mode (report schema 5)

Each population is only `positive` or `negative`, and each rule says which class
it should fire on. A rule "fires" when the checker says warning or fail. The
four agreement cells count only decided populations of that class; vacuous and
unchecked are counted separately over all populations.

- **C1 -- five populations, three rules, each meant to fire on negatives.**
  Positive: ok, noskill. Negative: dup, nograde, opaque.

  | Rule | fired on negative | fired on positive | silent on negative | silent on positive | vacuous | unchecked |
  |---|---|---|---|---|---|---|
  | uniqueness | 1/3 | 0/2 | 2/3 | 2/2 | 0/5 | 0/5 |
  | mandatory | 1/2 | 0/2 | 1/2 | 2/2 | 0/5 | 1/5 |
  | frequency | 0/2 | 0/1 | 2/2 | 1/1 | 1/5 | 1/5 |

  Mandatory's negative denominator is 2 because its opaque cell is unchecked.
  Frequency loses the opaque negative (unchecked) and the noskill positive
  (vacuous).
- **C2 -- the control.** One positive (ok) and one negative (dup). Uniqueness
  fires exactly on the negative: `fired_on_negative 1/1`, `silent_on_positive 1/1`.
  Mandatory, the wrong rule for this split, never fires: `fired_on_negative 0/1`.
- **C3 -- an unknown id in `rules`:** exit 3.
- **C4 -- a class manifest with no rules:** exit 3.
- **C5 -- 1,025 rules, one over the bound** (made by the harness): exit 3.

## Harness-built cases

- **N1 -- near the cap.** 8,000 class-mode populations (all `ok.yaml`,
  alternating classes) in a compact manifest under 1 MiB. Every rule is silent
  everywhere: `silent_on_negative 4000/4000`, `silent_on_positive 4000/4000`.
  Work must be at most P x (1 + C) = 8000 x 4 = 32,000.
- **X1 -- parity with the synth path.** The committed movie/faker synth corpus
  is copied, its sidecar expectations are converted into a manifest, and the
  report's `per_constraint` must equal the committed synth report's, except the
  two synth-only fields (C-F2). That corpus has no defects, so defect parity is
  carried by E2.
- **D1 -- determinism.** C1 run twice gives byte-identical reports.

## Corpus findings (for the owner)

- **C-F1 -- v4 defect rows.** The current defect schema requires `sidecar` and
  `seed`, which a host-labelled population does not have. Proposed: v4 defect
  rows omit both; everything else in the row is unchanged. E2's answer is
  written that way.
- **C-F2 -- synth-only row fields.** `wrong_attribution` and
  `set_attributed_evidence` come from synth sidecars. Proposed: labels mode
  reports `0` and `false`, and X1's parity ignores those two fields. This
  narrows spec T3's "byte for byte".
- **C-F3 -- the 10,000-population bound cannot be reached.** Every entry
  carries a 64-character digest, so even the shortest 10,001 entries take
  1,199,012 bytes, over the 1 MiB cap. The count bound is dominated by the size
  cap and no CLI case can fail it, which the shipment rule forbids. Proposed:
  keep `maxItems: 10000` in the schema as defence in depth, test it by
  validating a manifest against the schema directly (not through the CLI), and
  record that the size cap is the effective bound. N1 uses 8,000 entries
  (1,047,047 bytes), and spec T7's "10,000 populations" reads as "the most a
  1 MiB manifest holds". The other bounds are reachable: E24 (no populations)
  and C5 (1,025 rules).
- **C-F4 -- exit 6 needs an alethic rule.** Deontic disagreements are measured,
  not defects, so the corpus's uniqueness rule is alethic to make E2 possible.
- **C-F6 -- which ref a class row carries.** Spec §6 gives `rules[]` rows a
  `ref` but does not say whether it is the manifest's form (`id:...`) or the
  checker's positional ref. Proposed: the positional ref, the same key as
  `per_constraint`, so both report variants line up. C1, C2 and N1 are written
  that way.
- **C-F5 -- a misleading checker message (pre-existing, out of scope).** On
  `opaque.yaml` the mandatory rule is `unchecked` with reason `role-unresolved`
  and a message saying role `person` does not exist. The verdict is what the
  corpus needs; the message is wrong and is carried as an open question for a
  checker follow-up.
