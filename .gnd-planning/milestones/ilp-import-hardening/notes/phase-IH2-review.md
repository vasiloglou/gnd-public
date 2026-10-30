# IH2 review (verbatim, sanitized)

> Retained by the author. One reviewer read the IH2 working-tree diff against
> `4389b61` (process-phase step 4); one reviewer is one reviewer. It returned
> this report as message text, because the harness refuses report files from
> subagents; the text is otherwise verbatim. **Edited:** the session scratch
> path is replaced by `<scratch>`. The repairs made after this review carry no
> review opinion.

## IH2 adversarial review: verdict

**Approve with one blocking finding.** The check behaves as designed for every shape the tests cover. It adds no regression and moves no golden or version, and the order is consistent across the tuple, the docs table and the pins. But the spec's central claim is false for one valid model shape, a diamond. In that model an own-reference subtype ends up in its supertype's family. The rule is then not refused and still reaches exit 70. This contradicts the phase Goal, Design 1 ("exactly the joins"), Design 3 ("exit 70 is unreachable through such a join") and the release note. It is pre-existing behaviour, not something the diff introduced, but IH2 claims to discharge IH0's "own-reference exit 70" suspicion, and that discharge does not hold.

No worktree file was edited. Scratch files are under `<scratch>/IH2/review/`:
- `drive.py`: the export and import run, as in `test_ih2_ownref._import`.
- `athead.py`: loads HEAD's `ilp_amie.py`.
- `mutplug.py` and `mutorder.py`: the mutants.

## Findings

### F1 (blocking): a multiple-inheritance diamond puts the own-reference subtype in its supertype's family, giving exit 70 at HEAD and in the worktree
- **Location:** `src/gnd/export/ilp_amie.py::family`. The union-find joins every parent of an inheriting subtype. The spec's Design 1 and 3 rely on the opposite. Also affected: the release note, and the docs sentence at `docs/reference/ilp-bridge.md:476-478` saying an own-reference subtype "starts a family of its own".
- **Model** (`diamond.orm.yaml` in scratch):
  - `staff`: String `staff_code`.
  - `manager`: `subtype_of [staff]`, `inherits_reference: false`, own reference `manager_no` Integer.
  - `director`: `subtype_of [manager, staff]`, `inherits_reference: true`.
  - Population: manager `1`, `2`; staff `"1"`, `"2"`; the same facts as R1. R1's rule.
  - `gnd validate` gives OK and `gnd check` exits 0.
- **Command:** `uv run --project <wt> python drive.py diamond.orm.yaml diamond.population.yaml "$R1"`
- **Observed:**
  - `facts.tsv` spells both types in one family, e.g. `manager:1 f_manages team:t1` and `manager:1 f_works_in team:t1`.
  - Exit 70: `internal: constraints[0] holds by GND's count but the checker says 'warning'`.
  - HEAD (via `athead.py`) gives the identical exit 70.
- **Expected:** `own-reference-join`, exit 3, per the Goal ("joins an own-reference subtype with its supertype … refused … before any count").
- **Cause:** `director` unions `manager` with `staff`, so the family-span check sees one family.
- **Same diamond with String `manager_no`:** exit 0, admitted, and the checker agrees. So only the mixed-primitive case misbehaves.
- **Options:**
  - Also refuse when a variable's types include a type that is not in the inheriting set but shares a family with a different reference value type.
  - Refuse when a family mixes reference types at export time.
  - Or narrow the spec, docs and release-note claims and carry the exit-70 suspicion forward as open.

### F2 (hardening): no test covers an own-reference join in the object position
- **Location:** `tests/test_ih2_ownref.py`. T1, T5 and R1 all use `?a` as the subject.
- **Mutant `subjonly`:** zip only the `subject` with `families[:1]`. `pytest tests/test_ih2_ownref.py tests/test_il_close.py` gives `54 passed`, so the mutant survives.
- **The real code is correct here.** I built `objpos.orm.yaml`, which is T1's model with the role order reversed, using rule `?b f_manages ?a => ?b f_works_in ?a`:
  - The worktree gives exit 3, `rule 0: own-reference-join: variable ?a joins the families manager and staff, …`.
  - The `subjonly` mutant gives exit 3 `support-mismatch`.
- Suggested: add this object-position case, and ideally the diamond from F1, as tests.

### F3 (completeness): the docs and release note overstate the coverage
- The release note says "refuses a mined rule that joins a subtype having its own reference scheme with its supertype". The docs table row and the changed docs sentence say much the same. Both are false for F1's diamond.
- Fix them together with F1.

## Checked and found true
- **Q1, the families claim, for the shapes in the fixtures:**
  - After 9b, a cross-family variable needs an own-reference edge on the subtype path. A sub-subtype that inherits from an own-reference type is grouped with that type's family, as designed.
  - The multi, cyclic, family (C1b, C1d, C1e, R2) and subtype (C1a) cases pass.
  - Value types are their own family, and unrelated types are refused by 9b first.
- **Q1, no regression:** a cross-family variable can never bind, because the two families give different prefixes. So no rule admitted today can now be refused. Such rules previously ended in `covers-nothing`, `support-mismatch` or `does-not-hold`.
- **Q2, the message is deterministic:** the first spanning variable in atom order (body, then head) is reported, with the families sorted. The observed message is `variable ?a joins the families manager and staff, which the count spells apart`.
- **Q3, the order agrees:**
  - `MAPPING_REFUSALS[-2:]` and the docs table row order agree.
  - The pins pass: `test_ilp_amie` T13 and `test_ih1_counting` T5.
  - Targeted run of `test_ih2_ownref`, `test_il_close`, `test_ih1_counting`, `test_ilp_amie` and `test_il6_walk`: 194 passed, 1 skipped.
- **Q4, no caller change or version move:**
  - The only callers are `ilp_service` (map, then count) and the tests. `tools/ilp_comparison.py` exits 0 (T4).
  - No golden, fixture or replay files are modified (git status shows only new IH2 files). `ADAPTER_VERSION` is still `"2"`.
  - The RF6 successor chains IH1 with a matching SHA (`3ffd3a42…`). `test_rf6_query_policy` and `test_rf2_pre_move_pins` give 21 passed.
  - ruff on the changed files is clean.
- **Q5, red at HEAD and the mutants:**
  - At HEAD, T1 gives `support-mismatch` and T5 hits the count. The `athead.py` harness reproduces `red.txt`'s T1 output.
  - Mutant "body atoms only": caught, by T1.
  - Mutant `>= 1`: caught, by T4.
  - Mutant "check disabled": caught.
  - Mutant "check moved before 9b": caught, by 4 failures (`ih1` T7, `ilp_amie` m5 and m8, among others).
- **Q6:** apart from F1/F3, the docs sentence and table row are accurate, and the release note's "before any count" and "exit still 3" are true.

## Suspected, not reproduced
- Whether the checker matches entity values across different primitives in other own-reference shapes, beyond the observed cases: Integer `1` vs String `"1"` gives a warning, and String vs String gives equal.
- Any other path besides F1 by which a family could mix reference value types, for example cycles mixed with own-reference edges. I did not construct one.
