# Local milestone-close review — seat four

2026-10-13. Scope: public regression recipe, redaction/assurance, artifact hashes,
phase-record contract and question sweep. Runtime candidate `6cff353` and docs
candidate `47e9071`; current working-tree close materials inspected separately.
Only this opinion file was written. No broad suite, paid tools, certification,
publication or production mutation.

## Opinion and actionable disposition

No reproduced runtime blocker within this seat's scope. Closure remains
conditional on the CS2-C3 counterexample evidence identified by seats one/three
and its supplementary close-record binding. The existing issue suite establishes
literal transition-only exclusion but does not alone demonstrate the three
promised snapshot-pass/failed-walk contrasts (retained temporal precondition,
intermediate state, frame). **P2 / completion evidence:** preserve that finding
until the supplemental tests and exact gate result are retained. I have not
claimed those tests passed before their evidence exists.

The new `evidence/CS2/obligation-inventory.txt` makes the exclusion inventory
inspectable: 23 compiled locators and one retained `start.pre_concept_exists`
entry, refused because `var_bound` has multiple asserters. Its heading explicitly
requires activation. Bind this supplemental artifact in the close record rather
than rewriting immutable earlier phase evidence.

## Attempts to refute the remaining claims

- Verified all 30 path/SHA-256 pairs listed in `002-phase-CS1.md` (12),
  `003-phase-CS2.md` (12), and `004-milestone-close.md` (6). Every listed file
  existed and matched its recorded digest at this review. Future close-material
  edits require refreshing only current close bindings, not old phase records.
- Both retained focused output files show 215 passing tests and the exact
  durations repeated by the close record. This inspection confirms the stored
  output claim; it is not a new two-interpreter execution by this reviewer.
- `notes/app-regression-recipe.md` distinguishes the candidate runtime/docs
  commits from eventual merged app adoption, specifies expected exits 1 and 2,
  and requires the named compiler locator with zero derivation failures. Its
  Python model/population placeholders and batch placeholders intentionally
  target the downstream owner's inputs. No external M3 acceptance is claimed.
- `evidence/CS2/agreement.json` names both population cases, inventory count 23,
  exact counts/failure references and the observable-field limitation. The dated
  plan amendment explicitly narrows the original per-row batch claim; neither
  artifact asserts that batch exposes passing/warning identities.
- Public API documentation at `docs/reference/python-api.md:319` explains
  activation, unknowns, unavailable assurance and admission refusal. The guide
  at `docs/guides/data-and-transitions.md:119` explains the caller's standing
  implication assertion and links the canonical contract. The close question
  sweep carries app adoption and future admission support to explicit owners.
- Reran both retained review-four public probes. Compiled failure witnesses
  remained masked with explicitly unredacted controls; anchor routing retained
  the failure; mutated operation names used fresh redacted locators while
  historical side tables remained unchanged. Assurance remained `none`.

## Selected fresh gate

```text
.venv/bin/python -m pytest -q tests/test_compiled_snapshot_obligations.py --tb=short
30 passed in 3.22s
```

The result supports the recipe's issue regression and existing opt-in controls.
It does not establish newly pending CS2-C3 supplemental cases. No additional
actionable defect was reproduced. This bounded local opinion is an advisory
development close reading, not proof or owner merge acceptance.

## Final follow-up — supplementary completion evidence

The P2 completion-evidence finding above is **discharged** on the current close
materials. Inspected `tests/test_compiled_snapshot_boundaries.py` and executed:

```text
.venv/bin/python -m pytest -q tests/test_compiled_snapshot_boundaries.py --tb=short
3 passed in 0.16s
```

The three public-interface cases distinguish a retained literal precondition,
undeclared frame change, and transient intermediate-state exclusion failure.
Each checks snapshot band 0 with zero failures/unchecked rows and walk band 1
with the specific failing walk family. Frame and intermediate cases also verify
the relevant endpoint snapshots pass. This supports the promised boundary
without claiming full-walk equivalence.

Verified all ten current artifact/hash pairs in `004-milestone-close.md`,
including the counterexample test file, retained 23-compiled/one-retained trace
inventory and both supplemental focused-gate outputs. Those output files retain
**218 passed in 26.96s** and **218 passed in 25.89s**, matching the current close
record. This reviewer independently ran the three new tests; the two-interpreter
full focused results were inspected as retained evidence, not rerun by this seat.
Earlier phase records remain historical and the close supplies the additional
completion evidence. No residual actionable finding within this bounded scope;
the initial conditional opinion is now satisfied.
