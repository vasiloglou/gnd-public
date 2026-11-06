# TS5 adversarial review (commit dd0d61ef)

Verdict: no blocking findings. Three hardening findings and two completeness findings, all reproduced. The page's replay text, CLI output and skill-decision claims hold against the recordings, the skills and the CLI as it runs now.

## What I checked and reproduced

- **T1.** `uv run python tools/run_tutorials.py --group type-judgements` gives "16 tutorial blocks passed", exit 0. The runner compares each shown stdout block line by line, with `...` as a wildcard (`tools/run_tutorials.py:67-71,177`), so every printed output on the page is checked against a real run.
- **T3.** The six named test files: 151 passed.
- **CLI claims, page lines 236-243 and 247-250.** I ran these in a scratch copy:
  - `GND_DISCLOSURE=internal` gives "show_values differs".
  - `customer` gives "show_digests differs".
  - `--show-values` gives "show_values differs".
  - `--min-support 10` gives "min_support differs".
  - Dropping one population row gives "population_sha256 differs".
  - Editing the model gives "model_sha256 differs".
  - Changing one evidence group, or only reformatting the evidence JSON with a matching digest, gives "groups differ".
  - `distinct` on g0 gives "group g0 was already induced as item_has_attribute_induced_0".
  - Every one of these exits 3 and writes no `--out`. `--actor other` binds, which matches the spec's sweep.
- **Rendered values.**
  - The duplicates uniqueness is `roles ['entity']`, deontic.
  - The multi-valued uniqueness is `['entity','value']` with counterexample `ft0#132`.
  - Population row 132 repeats an earlier row (True), so "133rd row … states a pair some earlier row already stated" holds.
- **Replay quotes.**
  - Every `>` quote matches the assistant text in `TS3/recording-2/run-1/turn-0{1,2}.jsonl` and `TS4/recording/run-1/turn-0{1,2}.jsonl`.
  - The `/gnd:` turns and the answers match `results.json` `user_turns[0..1]`.
  - The narration is accurate:
    - "decided g0, g1 and g2 and asked about g3";
    - the TS4 agent ran `grep … item_has_attribute_induced_0 model.orm.yaml` before S1;
    - "Sonnet 5.5" matches `claude-sonnet-5-5` and 004/005 records;
    - "closed with … `skipped.judged_skip`".
- **Skill rules.** The page's R1–R4, S1–S4 and the precondition paraphrases agree with `gnd-judge-fact-types/SKILL.md:38-117` and `gnd-model-multivalued/SKILL.md:117-147`. They link the skills and do not copy the rules (standing rule 5).
- **TS-R5 and paths.**
  - I collected all 298 distinct population strings from both example populations.
  - None of length 3 or more appears in the page or the three SVGs (word-boundary match).
  - No `/Users`, `/private`, `/tmp` or `/home` appears in the page, the SVGs, the README or the dispositions.
- **SVG facts.** All counts and verdicts agree with the evidence and judgements. Each of g2's 12 multi-valued items holds exactly two values: 24 + 12 = 36 distinct pairs, plus 1 repeat, gives 37 rows.
- **Dispositions.**
  - The stated grep at `dd0d61ef^` lists 14 files.
  - A broader grep (`judgement|induced fact type|type induction|generic rows|generic fact type|induced_from|provenance.generic`) adds only pages that use "judgement" in an unrelated sense (clinic textual rule, gsd-mapping), and `discover.md`.
  - I checked every "unchanged" row:
    - `agents/index.md:42-43`
    - `disclosure.md:224-228`
    - `orm-core/SKILL.md:35-36,56-57`
    - `gnd-solve/SKILL.md:141-143`
    - `disclosure-mode.md:220-221`
  - All of them are still accurate. No page was missed.
- **discover.md (TS5-C3).** Both edited sentences agree with the reproduced behaviour.

## Findings

**F1 — hardening — `tests/test_type_judgements_example.py:54-67`**
- **Claim.** The commit says "a test pins every quoted replay line to the recordings".
- **Evidence.** `quoted_fragments()` reads only lines starting with `>` and splits them on `...`. I ran mutations of the page against the test's own function (`scratchpad/ts5-review/mut.py`):
  - Paraphrasing the `text` block at line 158 (which the page calls the "recorded second turn") to "Group g3 is distinct. Write it." is **NOT caught**. The same holds for lines 128, 355 and 392, which the page says are "exactly" the recorded turns.
  - Splicing a quote with an inserted `...` ("I haven't ... Group `g3` needs ... first") is **NOT caught**. Any concatenation of real fragments passes, even when it changes the meaning.
  - Swapping the TS3 opening quote for the TS4 opening quote is **NOT caught**. The corpus merges both recordings, so attribution to the wrong session passes.
  - Indenting a quote line is **NOT caught**.
  - A word changed inside a quote is caught.
- **Fix.**
  - Assert each `text` block that follows "You type" or "You answer" equals `user_turns[i]` of the named recording.
  - Check the quotes of each section against that section's recording only.
  - Allow an elision only where it is marked as one: `> …` as its own token, and fragments in recording order.

**F2 — hardening — `tests/test_type_judgements_example.py:70-71`**
- **Claim.** `test_a_paraphrased_quote_is_found` shows the test detects a paraphrase.
- **Evidence.** It asserts that a constant string is absent from the recordings. It never touches the page or `quoted_fragments()`, so it cannot fail for any change to the page. In F1's mutation the user-turn paraphrase passed while this test stayed green.
- **Fix.** Run the real check over a mutated copy of the page, for example by setting `PAGE` to a `tmp_path` copy with one quoted word changed, and expect the assertion to fire.

**F3 — hardening — `docs/how-to/judge-induced-fact-types.md:503-506`**
- **Claim.** The recorder's "one false alarm … is noted in the recording."
- **Evidence.**
  - `evidence/TS4/recording/results.json` has only the keys gate, skill, fixture, user_turns, recorded and run. It carries `"no_population_access": false` with no note.
  - `manifest.json` has no note either.
  - The explanation lives in `005-phase-TS4.md:90,159` ("a recorder false positive (R1)") and in `tests/test_model_multivalued_skill.py:168-171`.
  - The page also does not say which of the two recordings had the false alarm. TS3 recording-2 has it true.
- **Why it matters.** Under the owner's rule, each failure a replay shows must be explained, with how GND caught it. A reader who opens the recording finds an unexplained `false`.
- **Fix.** Name the TS4 multi-valued recording and state that `results.json` keeps `no_population_access: false`. Point to the phase record and to the test that accepts exactly that one check. Say it was caught because the corrected check over the kept, redacted streams passes.

**F4 — completeness — `docs/how-to/judge-induced-fact-types.md:164`**
- **Claim.** It quotes "I wrote the judgements file to `...duplicates.judgements.json`."
- **Evidence.** `TS3/recording-2/run-1/turn-02.jsonl` reads ``to `<workspace>/duplicates.judgements.json` ``. The page swaps the redaction token for `...` inside a code span. That is not a marked elision, and the test accepts it only because it splits on `...` (F1).
- **Fix.** Quote ``` `<workspace>/duplicates.judgements.json` ``` verbatim, and say in one clause that `<workspace>` is the recorder's redaction.

**F5 — completeness — `.gnd-planning/milestones/type-induction-skills/notes/TS5-dispositions.md:3-7`**
- **Claim.** The scope is the grep's 14 files "plus `docs/reference/capabilities.md` and `docs/how-to/compose-documents.md`, which name the family in other words".
- **Evidence.**
  - `git show dd0d61ef^:docs/how-to/compose-documents.md | grep -cE "<the stated pattern>"` returns 1, so compose-documents is already one of the 14.
  - `git grep -l` at `dd0d61ef^` counts 14 files.
  - The table's 16 rows are therefore 14 + capabilities + the refuted `type-judgements.md`. The prose double-counts.
- **Fix.** "plus `docs/reference/capabilities.md`, which names the family in other words, and the plan's proposed `type-judgements.md`."

## Spec obligations

| Item | Status |
|---|---|
| T1 | Discharged. |
| T3 | Discharged. |
| T4 | Discharged by my scan. The test covers no value-absence; T4 rests on the runner plus this scan. |
| TS5-C1 | Discharged, apart from F5's wording. |
| TS5-C2 | Discharged as two folders under D2/P5. The page states this at lines 40-47. |
| TS5-C3 | Discharged. |
| T2 / TS5-C4 | **Not reproduced by me.** `zensical build --strict` writes `site/` in the worktree, which this read-only review must not modify. The phase record should cite its own T2 run. |
| T5 | This review. It is discharged once F1–F5 are dispositioned. |

No downstream names appear in the new files. I found nothing undischarged beyond what is listed here.
