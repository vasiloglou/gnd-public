# Reader 4: measurability, falsifiability and reproducibility

**Digests:** both subjects matched their expected values.
- `.gnd-planning/milestones/ilp-learners/evidence/plan-review-r1/ilp-learners-plan.md` = `6cb10d97…8e463`
- `.gnd-planning/milestones/ilp-learners/evidence/plan-review-r1/phase-IL1-spec.md` = `59629173…6b027`

**Verdict: request-changes.** Two findings block approval:
- **F1:** a T4 case is wrong.
- **F7:** no test can fail IL1-C4.

The rest are fixes that should land before the IL1 gate.

**Scope:** I checked that the completion predicates and IL1-C1..IL6-C3 can be falsified, that the IL1 tests and gate discharge them, that SWI escape syntax is handled correctly, how honestly live runs are recorded, and whether the IL6 comparison is well defined.

**Probe and side effect:**
- I ran `ilp_popper.parse_program` on the T4 inputs at HEAD 63f7f1f. The script is at `<scratchpad>/review/reader-4/probe.py`.
- My first `uv run` created `.venv/` in the worktree. Git ignores it (`.gitignore:1`) and no tracked file changed, but it is a new directory in the worktree.

## Findings

- **R4-F1** (blocking, high): the T4 "beyond Unicode" case is valid Unicode. A correct implementation will accept it.
  - **Cites:** spec:138 lists `'\4000000\'` as "beyond Unicode" and expects exit 3. Spec:93 requires "the same Unicode-scalar check" as the hex form (`ilp_popper.py:255`, `code > 0x10FFFF`).
  - **Problem:** octal 4000000 = 1048576 = U+100000, a valid scalar. Octal for U+10FFFF is 4177777. A faithful implementation therefore fails T4, or T4 forces a wrong bound.
  - **Reproduce:** `python3 -c "print(hex(int('4000000',8)), oct(0x10FFFF))"` prints `0x100000 0o4177777`.
  - **Repair:** use `'\4200000\'` (0x110000) as the beyond-Unicode case. Add the boundary pair `'\4177777\'` (accept) and `'\154000\'` (0xD800, refuse). The surrogate case is already correct.

- **R4-F2** (hardening, high): the spec places the octal fix in the wrong function, and four of the seven T4 cases pass already at HEAD.
  - **Cites:** spec:44, 90-95 and the ~10-line size estimate put the change only in `_unquote`.
  - **Problem 1 (wrong locus):** the tokenizer's quoted alternative (`ilp_popper.py:34`, `\\x…\\|\\.`) consumes the closing `\'` through `\\.`. So every closed octal form fails before `_unquote` runs. The probe gives `unparsable: line 1, column 27: unexpected "'"` for `'\001\'`, `'\101\'` and `'\7\'`. If the octal alternative is not ordered before `\\.`, token boundaries can also shift inside a line.
  - **Problem 2 (cases that cannot fail):** all four negative T4 cases (8 digits, unclosed, beyond Unicode, surrogate) already exit 3 at HEAD, through "unexpected" or "unknown escape". Only the three positive cases can distinguish the fix from the current code.
  - **Problem 3 (case label):** `'\101'` is accepted by SWI itself, where the closing `\` is optional. Refusing it is a deliberate GND strictness, not a "malformed" input.
  - **Repair:**
    - Name `_TOKEN` as a changed loader.
    - Add a token-boundary case, e.g. `wrong(A):- f(A,B,'\001\'),g(A,B,'x').` must yield two constants.
    - Assert the octal-specific refusal message, not just `unparsable`.
    - Label `'\101'` as intended strictness.

- **R4-F3** (hardening, medium): the escape corpus covers only octal. SWI's other control escapes are unreadable.
  - **Cites:** `_ESCAPES` (`ilp_popper.py:36`) handles only `\\ \' \n \t` plus `\x…\`. IL1-C3 (plan:231-233) promises the escape forms SWI writes.
  - **Problem:** SWI's quoted-atom writer also emits `\a \b \v \f \r` for those control codes. If Popper prints through SWI, a constant containing CR becomes a refusal at the live run, not at a unit test.
  - **Reproduce:** this is from my knowledge of SWI's writer, so check it against the SWI version pinned at IL1-D3: `writeq('\r')`, then `writeq('\001\')`.
  - **Repair:** have T4 enumerate every escape form the pinned SWI writes, recorded from that SWI version at the gate. That makes "one test per escape form" a closed, checkable list.

- **R4-F4** (hardening, high): the spec contradicts itself on target order, and the RF1 goldens decide the contradiction.
  - **Cites:**
    - spec:73 says `LEARNERS … sorted by target`.
    - spec:85-87 says the `--help` goldens are unchanged "because the sets are unchanged".
    - `commands/export.py:108` and `commands/checking.py:452` declare `("popper","neutral")`.
    - `tests/fixtures/rf1-pins/goldens/cli-help/gnd_export_ilp.json` and the `gnd_import_ilp-rules.py31{1,3,4}.json` help and exit goldens pin `{popper,neutral}`.
  - **Problem:** sorting gives `{neutral,popper}`, so T1b fails.
  - **Repair:** fix `EXPORT_TARGETS` and `IMPORT_TARGETS` to declaration order `("popper","neutral")`, and say that new targets are appended. Note that each later phase moves the RF1 goldens.

- **R4-F5** (hardening, medium): T2, T3 and T7 cannot fail if the registry is never wired in, and the gate command is not fixed.
  - **T3:** `gnd export ilp … --target bogus` already exits 64 at HEAD (I ran it), and corpus case B3 already gives `learner-mismatch`. A registry that is declared but ignored still passes.
  - **T2:** the "no `"popper"` literal" scan is the source-string pattern that `standing-rules.md` §"A declared branch…" says "is not a case".
  - **T7:** passes at HEAD and checks only `pyproject.toml`. Plan:322 promises wheel metadata too.
  - **Gate command:** spec:143-144 leaves placeholders (`<IK6 walk and RF1 CLI golden files> <layer and RF5 controls>`), but `verification-selection.md:47` requires the exact command and exit.
  - **Repair:**
    - Assert by parser introspection that argparse `choices` are the registry tuples.
    - Monkeypatch a fake registry entry and show it reaches `render`, the `method` token and the `learner-mismatch` text.
    - Have T7 also read the built wheel's `Requires-Dist`.
    - Write the gate as a literal file list in the spec.

- **R4-F6** (hardening, medium): T5 passes at HEAD and misses the carried obligation.
  - **Cites:** IK5 case I2 (`tests/fixtures/induced_knowledge/ik5-corpus/i2.popper.pl:2`, `wrong(A):- f_order_amount(A,B,C),f_order_flagged(A,B).`) already imports a two-fact-type join with exit 0.
  - **Problem:** the carried "IK6 join space" row (`010-phase-IK6.md:164-165`; `012-milestone-close.md:151`) is about the stand-in learner's join branch (`src/gnd/examples/refunds/stand_in_learner.py:70-78`). That branch yields 0 joins on refunds and has no case. T5 (spec:139) tests the bridge, which is already covered.
  - **Repair:** either give the stand-in's join branch a case, which needs a fixture model where it yields a join, or restate IL1-C5 as closed by I2 plus a refunds characterization case and say the stand-in branch stays uncovered.

- **R4-F7** (blocking, medium): no test can fail IL1-C4 or completion predicate 1, and they have no outcome for "no output".
  - **Cites:**
    - Plan:38-40 accepts "imports with exit 0 or refuses with a named reason". Standing rule 1 guarantees exactly that for every input, so the predicate is met by any run that has a record.
    - T6 is "evidence only" (spec:140, 117-118), and rule 6 says the run "decides nothing about a gate" (spec:49).
    - There is no outcome for: Popper finding no solution, the 600 s wall-clock kill (IL1-D4), or a failed install.
    - Popper's own search timeout should be set below the 600 s wall clock, and IL1-D3/D4 should record its default from the pinned version. Otherwise the kill can arrive first and leave no program to import.
  - **Repair:**
    - Before the run, fix a closed outcome list: rendering-rejected, no-solution, learner-timeout, wall-clock-kill, unparsable, a named refusal, admitted.
    - Set Popper's own timeout explicitly, below the wall clock.
    - Add a default-gate replay test over the committed raw program, run record and export digest. It re-runs `gnd import ilp-rules` and asserts the recorded exit and the stderr or report digest, making the record a claim that can fail.
    - Add a record-completeness check: required fields present and digests recompute.

- **R4-F8** (hardening, high): "a failure is a result, fix it in the adapter" conflicts with byte-identical goldens and with "one run".
  - **Conflict with goldens:** spec:113-116 and plan:237-239 allow a rendering fix after the live run. But IL1-C1 (plan:226-227) and IL-R7 (plan:82) require the IK5 Popper goldens to stay byte-identical, including `tests/fixtures/induced_knowledge/ik5-corpus/expected-export/popper/popper/bias.pl`, which carries `_SETTINGS` (`ilp_popper.py:27`). Any rendering fix fails C1.
  - **Conflict with "one run":** a re-run after a fix exceeds D2's "one recorded run each" (plan:385). Nothing requires keeping the attempts that were not chosen.
  - **Repair:**
    - Every live invocation is numbered and retained.
    - The first run after the gate is the run of record.
    - A rendering or settings fix is an IL-R7/IK-R12 amendment that names the golden change.
    - A second run needs the owner's ruling and is reported alongside the first, not instead of it.

- **R4-F9** (hardening, medium): bounds-before-results covers only process limits, and the run records do not say what is reproducible.
  - **Bounds:**
    - Plan:328 fixes only process limits per spec.
    - The settings that decide what each learner can find are unbound before results (IK-R12): the IL2 ILASP mode-bias limits, IL3 learner hyperparameters, IL4 AMIE pruning thresholds and threads, and IL5 sampling parameters and answer-size cap.
  - **Reproducibility:** only the LLM run is described as not repeatable (plan:192-193).
  - **Whose numbers:** the spec's run record carries coverage computed by the evidence script in SWI (spec:104-106), and IL3-C3's per-conjunct coverage would be too. So `coverage-mismatch` tests script semantics against GND, not the learner against GND, and the record should say so.
  - **Repair:**
    - Each spec fixes a learner-settings table at the gate, recorded with the full argv.
    - Each record states:
      - the provenance of each number (from the learner, or computed by the script);
      - the seed and thread settings;
      - "single run, reproducibility not measured" (or the measured result);
      - for IL5, the prompt digest, the resolved model id and the sampling parameters.

- **R4-F10** (completeness, high): IL4's `support-mismatch` cannot be decided, because "support" is undefined across the two sides.
  - **GND side:** IK2 `support` is a `{numerator, denominator}` pair over example ids (`ilp_service.py:400`; `orm-meta.schema.json:2786-2805`, `denominator` minimum 1). `confidence` carries a free `formula` (lines 2831-2848).
  - **Miner side:** AMIE reports an absolute count of head pairs plus confidences.
  - **Also undefined:** what the IK-R11 opaque ids are when the "examples" are pairs of raw values, and what happens to a rule with zero body matches (denominator 0).
  - **Cites:** plan:174-177 and IL4-C3 (plan:273-274) leave all of this to the IL4 spec, but the predicate depends on it.
  - **Repair:** fix in the plan:
    - GND support = |{(x,y): body ∧ head}|, compared by integer equality with the miner's positive-example count.
    - Provenance = {numerator: support, denominator: body pairs}.
    - The exact confidence formula string.
    - PCA confidence: either not compared, or compared with a stated rule.
    - Counterexamples as digests of opaque pairs.

- **R4-F11** (completeness, high): the IL6 comparison table and IL5-C3 have no defined meaning per clause, and AMIE has no defined row.
  - **Per-clause counts:** import is all-or-nothing and stops at the first refusal (`ilp_service.py:15-16`, 384-394). One import cannot yield "clauses proposed, admitted and refused, with refusal names" (plan:59-60, 285-286). "Admitted" is 0 whenever any clause refuses, and later clauses are never evaluated.
  - **AMIE:** predicate 6 says "per adapter", but IL6-C1 covers only "every labelled adapter" (plan:290-292).
  - **Missing output:** nothing defines the row for an adapter whose live run produced no output.
  - **Input:** IL2-C4, IL3-C4, IL4-C4 and IL5-C3 do not require the live run to be over the refunds export. IL6-C1 assumes it is, and IL3's feature export has a different digest.
  - **Repair:**
    - Fix the columns: proposed count; import exit; first refusal name and clause index; clauses not evaluated. Alternatively, define per-clause probe imports with a GND-derived run record, labelled as GND-derived.
    - Give AMIE a separate unlabelled row: mined, admitted, `support-mismatch`.
    - Add a "no output" outcome.
    - Bind each live run to a named refunds export digest.

- **R4-F12** (completeness, medium): new targets are wire changes, but the plan lists only CLI goldens.
  - **Cites:** `src/gnd/ilp-import.schema.json:30-34` and `src/gnd/ilp.schema.json:254-258` enumerate `target` as exactly `popper`, `neutral`. Plan §5 (plan:312-313) says IL2–IL5 add a `--target` value with CLI goldens only. IL-R7 (plan:82) requires a named change and a version bump for any wire change.
  - **Repair:** have the plan state, per adapter phase, the schema enum change and its version decision under IL-R7, with a golden that fails if the change is not made.
