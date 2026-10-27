# Reader 1 -- semantics and admission safety

Retained text of the reader's returned report. Local edits: scratch paths read
`<scratch>`, and quoted Markdown link syntax is escaped as `]\(` so the
repository's reference check does not read it as a live link.

Reviewed plan SHA-256 526ab075473ab60cf2e8090fe7c0f177aa54e4a82b7fce83af1cb50d1919c411 and spec SHA-256 0510b5275622f8b38aff8865500d40601c9ea4e3ce3b2e58ed2fcf5b9363515a: both match.

**Verdict: request-changes**

Scope: I read both subjects in full. I also read docs/reference/{ilp-bridge,discover,measure-labels}.md, docs/tutorials/learn-rules.md, the refunds example (README, stand_in_learner.py, labels.json), gnd-model-evolve SKILL.md:270-290, provenance-and-modality.md (the induced rows), tests/test_solve_successors.py:24 and test_packaged_skills.py:198-199, and the `--help` of all four commands. I ran these probes on copies of the example in `<scratch>/reader1/`: measure, discover twice, export ilp, the stand-in learner with and without `--also-claim north`, and three imports. I wrote nothing in the repository. I did not check the Popper `magic_value_type` claim: the plan claims nothing about Popper learning constants.

## Findings

- **R1-F1** (blocking, high): **The refusals allow an agent-written rule to be admitted under the learner's name.** No refusal stops the skill from editing a learner's clauses or run record. R-a covers only "a model" and "a proposal". R-c and R-d cover only the `covered` sets.
  - Where: plan 141, 152-159 and 266; spec 85, 91-99 and 101-106.
  - Reproduced:
    1. Ran `stand_in_learner.py`.
    2. Edited `"const": 500` to `600` in learned.clauses.json and recomputed `clauses_sha256` in learned.run.json. The covered set did not change (harbor, market, airport, station).
    3. `gnd import ilp-rules … --target neutral` exited **0**, printing "IMPORTED 1 learned clauses".
    4. The proposal's rule is `<= 600`, with rationale "learned by refunds-stand-in-learner 1" and `provenance.induction.inducer = refunds-stand-in-learner/1`. ilp-bridge.md:165 says `inducer` is the run record's learner, so GND records a rule the agent wrote as the learner's.
  - Why it is likely: after any fragment refusal (exit 3, ilp-bridge.md:129-140), the natural user follow-up is "fix the clause".
  - The plan also never says who writes a Popper run record. Popper prints counts, not sets (ilp-bridge.md:96), so the skill would author the record's learner field and both digests.
  - Fix: add a refusal along the lines of "It never writes or edits a learner's clauses or run record." Give it one stated exception: for Popper, the run record is assembled from Popper's printed program, the user's selected independent evaluation and the two digests, and the skill says it assembled it. Add the sentence to T8.

- **R1-F2** (blocking, medium): **No refusal stops the skill from writing, editing or re-digesting a label manifest.** The labels are the host's claim (measure-labels.md:6-8), and IS-R2's "GND's numbers" depend on them being the host's.
  - Where: plan 144 and 331 (D3 vendors the schema precisely so the agent can "reach the label-manifest format"); spec 82-83.
  - Reproduced: changing one byte of a model copy makes `gnd measure --labels` exit 3. The message prints both digests: "written for model sha256 8e03…, not this model (8ee1…)". Rewriting `model_sha256` is then trivial.
  - The same happens after any evolve apply. A "score the new rule" request also needs a new `fires_on` entry, because an unlabelled rule is exit 3 (measure-labels.md:102). Here the agent would be inventing an auditor verdict.
  - Fix: add a refusal along the lines of "It never writes, edits or re-binds a label manifest; labels come from the user." Make the exit-3 reaction say a stale manifest goes back to the user. State that D3's vendored schema is for reading only.

- **R1-F3** (blocking, low): **T8 cannot pass as written.** It requires R-a..R-g to appear "once in the packaged tree and only in gnd-induce/SKILL.md" (spec 191). R-g, "This skill never touches git." (spec 99), already appears verbatim at src/gnd/skills/gnd-export/SKILL.md:27, found with `grep -rn "never touches git" src/gnd/skills`. Fix: reword R-g so it is unique, or exempt it from the only-here clause and pin it through `RECORD_ROUTES` (spec 137).

- **R1-F4** (hardening, medium): **`gnd measure` overwrites an existing `--out` with no warning.** The reactions assume an existing output gives exit 11 (plan 145-146 and 148-150; spec 86), but measure has no exit 11 (`gnd measure --help`; measure-labels.md:99-108).
  - Reproduced: I wrote "old" to m.json and ran `gnd measure … --out m.json`. It exited 0 and replaced the file.
  - Fix: in Score, the skill confirms the output path does not exist before running measure. Say that exit 11 applies only to discover, export and import.

- **R1-F5** (hardening, medium): **R-c is weaker than D5 and leaves a circular route open.** D5 is positive: covered sets come only from the learner or from an independent evaluation the user selects (plan 333). R-c only bans "GND's own import result" (spec 95). That leaves `gnd check` or `gnd measure` over a scratch model holding the rewritten rule, which is the same checker and so circular.
  - The coverage-mismatch refusal also prints the difference ("GND covers [] that the learner did not report, and the learner reports ['north'] …"), so GND's set is easy to read off. R-d covers only the retry.
  - Fix: reword R-c as "from the learner's output or the user's selected non-GND evaluation, never from any gnd command's output", and keep R-d.

- **R1-F6** (hardening, low): **R-f clashes with the reporting rules.** R-f forbids host values or paths in "a report" (spec 98). But IS-R2 and the reactions require output "verbatim" (plan 68 and 148). GND's text output contains absolute host paths: the discover MODEL, POPULATION and PROPOSAL lines, measure's "json written to …", and the measure exit-3 message. The discover read-back (spec 84) also has to state host values.
  - Separately, GND itself writes host values into value-family proposals (discover.md:32: "the values themselves enter the model").
  - Fix: limit R-f to written and public artifacts, say chat read-back may show values, and point out value candidates as carrying host data when handing off.

- **R1-F7** (completeness, low): **The handoff has no case for discover with nothing emitted.** `gnd discover` exits 0 even when it writes no `--out` (discover.md:88 and 107). The hand-off says to name each proposal file "only after exit 0" (spec 87; plan 142). Fix: "on exit 0 with EMITTED 0 there is no proposal; report the counts and hand off nothing."

What held up:
- IS-R1 and D6 keep the skill from admitting anything; admission goes through gnd-model-evolve (SKILL.md:278-282).
- R-d plus the exit-3 stop does prevent the reproduced over-claim being retried.
- IS-R2's per-rule numerator/denominator rule matches measure's printed cells (e.g. `fired_on_negative=2/4`).
- No edited sibling is in `FROZEN_SKILLS`.
