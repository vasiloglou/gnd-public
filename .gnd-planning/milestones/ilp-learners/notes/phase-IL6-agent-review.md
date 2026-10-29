# IL6 adversarial review — `git diff 860e651..HEAD` on `claude/il6`

Reviewer: single adversarial reviewer. Nothing tracked was modified. Scratch files are under
`<scratch>/review/`.

Baseline: `.venv/bin/python -m pytest -q tests/test_il6_walk.py tests/test_il6_skill_census.py tests/test_ilp_amie.py`
gives 135 passed, 1 deselected. `.venv/bin/python tools/ilp_comparison.py` exits 0. Neighbouring tests
(`test_ik6_skill_census`, `test_packaged_skills`, `test_ik6_walk`, `test_ilp_learners`, `test_ik_close`) give 147 passed, 1 skipped.

No blocking defect in code, goldens, shipped bytes or run handling. Six findings: four about false
or stale text, two about weak tests.

---

## R1 — Public docs say every learner/adapter "was run once"; Popper ran 3 times and AMIE twice under two settings

- **Files:**
  - `docs/how-to/compare-ilp-learners.md:255`: "Every learner was run once, under one setting, on one small example."
  - `docs/reference/capabilities.md:36`: "each adapter was run once against one real learner version"
  - `docs/release-notes.md:8-9`: "each was run once against a real learner version"
  - `docs/reference/ilp-bridge.md:579-580`: "Each rendering was run once against one learner version and one setting"
- **Defect:** The committed evidence contradicts all four. Popper had three invocations, and the same page says so at lines 65-78. The AMIE rendering ran under two settings (invocation 2 adds `-enstd -minc 1`). The `neutral` adapter never ran against any learner of its own: the LLM run only bound its export.
- **Reproduction:**
  ```
  $ grep -n "run once\|one setting" docs/how-to/compare-ilp-learners.md docs/reference/capabilities.md docs/reference/ilp-bridge.md
  docs/reference/ilp-bridge.md:580:  once against one learner version and one setting, as the
  docs/how-to/compare-ilp-learners.md:255:- Every learner was run once, under one setting, on one small example. The
  docs/reference/capabilities.md:36: ... each adapter was run once against one real learner version ...
  $ ls -d .gnd-planning/milestones/ilp-learners/evidence/IL1/live/invocation-* .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-*
  .../IL1/live/invocation-1  .../IL1/live/invocation-2  .../IL1/live/invocation-3
  .../IL4/live/invocation-1  .../IL4/live/invocation-2
  ```
  Recorded argv: invocation 1 is `-maxad 3 -mins 1`; invocation 2 is `-maxad 3 -mins 1 -enstd -minc 1`. The generated table on the same bridge page lists Popper invocations 1, 2 and 3 and AMIE invocations 1 and 2.
- **Severity:** hardening. These are false public claims, each a one-line fix. Suggested wording: "each run of record is a single run; owner-ruled extra runs are marked".

## R2 — The walk says AMIE's run of record "used its defaults"; it ran with `-mins 1`

- **File:** `docs/how-to/compare-ilp-learners.md:217`
- **Defect:** IL4-D11 (o), the recorded argv and `run_amie.py`'s own comment all say "`-mins 1`, defaults otherwise". Minimum support was set deliberately away from AMIE's default, so "used its defaults" is false.
- **Reproduction:**
  ```
  $ python3 -c "import json;print(json.load(open('.gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/outcome.json'))['argv'])"
  ['/opt/homebrew/bin/java', '-Xmx2G', '-jar', '<scratch>/amie4.0.0.jar', '-maxad', '3', '-mins', '1', 'amie/facts.tsv']
  $ grep -n "minimum threshold" .gnd-planning/milestones/ilp-learners/evidence/IL4/live/invocation-1/raw-stdout.txt
  2:Using Support as pruning metric with minimum threshold 1.0
  $ grep -n "SETTINGS = \|IL4-D11" .gnd-planning/milestones/ilp-learners/evidence/IL4/run_amie.py
  ... #: Each invocation's AMIE settings. 1, IL4-D11 (o): no -const, -mins 1, defaults otherwise.
  ```
- **Severity:** hardening. Suggested wording: "with minimum support 1 and otherwise its defaults".

## R3 — Census row for `gnd-solve/SKILL.md` has a false "why", and the packaged route it excuses is stale

- **Files:** `.gnd-planning/milestones/ilp-learners/skill-census.md:79`; `src/gnd/skills/gnd-solve/SKILL.md:141-144`
- **Defect:** The row says "its station 7 route names the proposal sources as examples and stays true … (an open question records whether this route should name it too)". It is wrong in three ways:
  1. The proposal-source text is in **Station 6** (line 133, "Station 6 — evolve the model"). Station 7 is review.
  2. The text does not give the sources "as examples". It lists exactly two, `gnd discover` and `gnd import ilp-rules`, and ends "review either here". Now that `gnd import mined-rules` exists, "either" is stale.
  3. No open question about this exists anywhere in the milestone.

  The IK census row for the same file (`induced-knowledge/skill-census.md:77`) treated this same route as a pin site that IK4 and IK5 edited.
- **Reproduction:**
  ```
  $ grep -n "### Station 6\|### Station 7\|review either" src/gnd/skills/gnd-solve/SKILL.md
  133:### Station 6 — evolve the model
  144:advisory constraints; review either here like any other.
  151:### Station 7 — review
  $ grep -rn "gnd-solve" .gnd-planning/milestones/ilp-learners | grep -v "skill:" | grep -v skill-census.md
  (no output: no open question records it)
  $ grep -n "gnd-solve" .gnd-planning/milestones/induced-knowledge/skill-census.md
  77:| src/gnd/skills/gnd-solve/SKILL.md | IK4, IK5 | station 8 names discover (IK4) and import ilp-rules (IK5) as proposal sources |
  ```
- **Severity:** completeness. Two fixes are possible. One is to edit the Station 6 sentence to name `gnd import mined-rules`, which makes the census cell `IL6`. The other is to correct the row to "Station 6" and actually record the open question.

## R4 — `test_t4_a_changed_golden_row_fails` cannot fail for any defect in the generator

- **File:** `tests/test_il6_walk.py:185-191`
- **Defect:** The test mutates the golden and asserts `build(ROOT) != mutated`. Whenever T4 (`build == golden`) passes, this holds by construction. When the tool is broken, `build` differs from everything and the test still passes. It has no detection power for the generator, or for the golden being derived from the wrong source.
- **Reproduction:** Replace the tool's `build` with a stub that returns `{"broken": True}` (plugin at `scratchpad/review/conftest_broken.py`):
  ```
  $ PYTHONPATH=<scratch>/review .venv/bin/python -m pytest -q -p conftest_broken tests/test_il6_walk.py -k "changed_golden_row or reproduces_the_golden"
  FAILED tests/test_il6_walk.py::test_t4_the_tool_reproduces_the_golden - Asser...
  1 failed, 4 passed
  ```
  All four mutation cases pass against the broken tool.
- **Severity:** hardening. Replace it with mutations of the evidence that the tool reads. For example, copy the evidence tree to `tmp_path`, edit `IL2/live/invocation-1/import-stderr.txt` to `clause 1: …` or delete `IL1/live/invocation-3/proposal.json`, and assert that `build(tmp_root)` differs from the golden in the expected field. This also proves the "first refusal" and "admitted" columns come from those files.

## R5 — Milestone README still shows the IL6 spec as an undecided draft

- **File:** `.gnd-planning/milestones/ilp-learners/README.md:52` and `:80`
- **Defect:** The README calls the spec "IL6 spec (r1, draft, awaiting the owner gate)" with "Next action: the owner rules on the IL6 spec (r1)". The spec at HEAD records "**r1 approved, 2026-10-28** (§12)", and implementation and docs have been committed.
- **Reproduction:**
  ```
  $ grep -n "awaiting the owner gate\|Next action" .gnd-planning/milestones/ilp-learners/README.md
  52:- [IL6 spec (r1, draft, awaiting the owner gate)](notes/phase-IL6-spec.md)
  80:**Next action:** the owner rules on the IL6 spec (r1), IL6-D1 to IL6-D11.
  $ grep -n "^\*\*r1" .gnd-planning/milestones/ilp-learners/notes/phase-IL6-spec.md
  5:**r1 approved, 2026-10-28** (§12). `auto=false`. Implementation follows
  ```
- **Severity:** completeness. The phase record step may fix this anyway; it is stale at HEAD.

## R6 — Weaker-than-spec checks in T6, T2 and the hold count (three small items)

- **R6a, `tests/test_il6_walk.py:248-255`.** Spec T6 asks for "one section per adapter naming its refusals". The test only checks that every refusal name appears somewhere in `ilp-bridge.md`, so a refusal documented under the wrong adapter's section would pass. To reproduce: the assertion is `[name for name in names if f"`{name}`" not in bridge] == []`, with no section split.
- **R6b, `tests/test_il6_walk.py:106-117`.** Nothing asserts that the two refused imports wrote no proposal, yet the page says "In both cases GND wrote nothing" (line 263). T2 only hashes the files listed in `WRITTEN`. A real walk run (`scratchpad/review/w2`) shows no `ilasp.proposal.json` or `amie.proposal.json`, so the claim is true today but unpinned.
- **R6c, `tools/ilp_comparison.py:139-141`.** `hold()` silently `continue`s on `ilp.IlpError`, so a mined rule GND cannot map would be counted as "not holding" without any signal. It is not triggered by the committed evidence. The independent recount (`scratchpad/review/hold_detail.py`) gives invocation 1: 19/20, 19/20, 20/20, 5/5, 19/20, 20/36, 5/6, 19/35, so 2 hold. Invocation 2 gives 5/5 and 20/20, so 2 hold. Both match the golden, with no IlpError.
- **Severity:** hardening, low.

---

## Checked, no defect found

- **Spec:** read in full (§1–§12 and the implementability notes).
- **Table generator** (`tools/ilp_comparison.py`):
  - Every column comes from the run's own files: `outcome.json` for termination, import, exit and run of record; the target's reader over the retained learner output for "proposed"; `import-stderr.txt` for the first refusal; `proposal.json` operations for "admitted"; `ilp_amie.count` for "hold".
  - The golden is independent of the tool. It was added only in `e679e40` (19:24:16 −0400), 24 s before the AMIE invocation 2 run (AMIE stamp 23:24:40Z), and no later commit touches it. Corpus-first holds.
  - The rows match spec §6's expected rows exactly.
  - Popper invocations 1 and 2 have 0-byte `program.pl`, so the "—" there is correct.
- **AMIE invocation 2 outcome versus the prediction fixed before the run:** `completed` / `admitted`; 2 rules, which are invocation 1's rules 3 (5/5) and 2 (20/20); `body_size_agrees` is true for both. `run_of_record` is false and `argv` equals `recorded_argv(2)`, as T9 checks.
- **`run_amie.py`:** an un-ruled invocation is refused before any work (`invocation N has no owner-ruled settings`), and an existing invocation directory is refused. Invocation 1's argv is unchanged (`-maxad 3 -mins 1`). `--probe` stays on settings 1.
- **Shipped files:** all 14 are byte-equal to their evidence or fixture sources (T3 passes). No extra files ship under `learners/` or `staffing/`.
- **Privacy:** grep for the home-directory prefixes, the owner's user name, surname and email tokens, `/private/` and `/var/folders` over invocation-2 evidence, `run_amie.py`, shipped examples, the page and the census. The only hits are the public GitHub repository URLs in the page, which match the 38 other docs pages that use them. Evidence keeps `<scratch>` and `<working-directory>` placeholders; `/opt/homebrew/bin/java` matches invocation 1.
- **Walk:**
  - Every `expect=` equals the recorded `import_exit`.
  - Shown outputs are real: changing "19 of 20" to "18 of 20" in a scratch copy makes the runner fail with "stderr output differs from the page".
  - A full real run passes (12 blocks).
  - Page facts match the evidence: Popper 18.0 s crash and 1.16 s on run 3; ILASP 123.685 s; LLM `ge_t_amount 640`; RIPPER 450 covering `south` at 4/5; AMIE rule 0 at 19/20; 2 of 8 hold.
- **`cli.md`, `ilp-bridge.md` "Comparing the learners", and the `gnd-export` and `gnd-model-evolve` pin-site edits:** consistent with the registry and evidence (T6 and T7 pass).
- **Census test:** the seeded faults fail by name, and the changed cells equal git.
