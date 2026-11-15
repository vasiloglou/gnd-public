# Plan review disposition

The owner asked on 2026-11-14 to "plan the milestones for #193 and then do a
review". That selects the project's plan-review instrument, the maintained
standard GND review panel (D9). Round 1 reviewed plan r1 at commit
`b75c910e`, SHA-256
`f27c10dc08020a9f6d7f28a4691a649dc0ba21c2b55bee6b64307b8fc453bfe3`.

## Round 1

**The run.**

- **Command:** `uv run python tools/run_gnd_review_panel.py
  li-plan-review-request.json --out li-plan-panel-r1 --reviewer-timeout 600
  --overall-timeout 900`, which exited 0.
- **Run:** the run digest is
  `b65da3701e69946512d41b68626b58bad7de2bcab3db5bc6713761a3a0538653`, and the
  reviewed artifact was unchanged during the run.

**The seats.** Six seats were attempted and five responses validated:

| Seat | Result |
|---|---|
| Claude, Codex, Qwen, Kimi, GLM | Each returned `revise`, and each response passed validation |
| Kimi | All three concerns retained. One preamble line was ignored |
| GLM | Two of its four concerns are unanchored, so its quotes were not found in the plan |
| Gemini | Malformed output, no response |

The panel met its runtime quorum of three and the project's four-reviewer
bar.

**Finalization.** `gnd review finalize` exited 0 with synthesis SHA-256
`f34dc7b7310ffcc85e29aa24961bfe0a416a768f4d8a395015711cbb9b75d055`. The
synthesis has 9 agreed groups, 18 divergent views and 13 prioritized fixes.

**Evidence.**

- The rendered [report](../evidence/plan-review/r1.md).
- Its [synthesis](../evidence/plan-review/r1-synthesis.json).
- The [request](../evidence/plan-review/r1-request.json). Its plan path is
  repository-relative.
- The raw 652 KB run directory is kept outside the repository, as in
  earlier milestones that committed only the rendered report. It can be
  added on request.

### Agreed groups

| Group (supporters) | Disposition in r2 |
|---|---|
| `joins`: identity joins of equal unchanged values bypass decisions. Decision coverage is undefined (Claude, Codex, Qwen) | **Accepted.** §2 LI2 now keys decisions at composition's grain (source, object type, source value), defines a coverage set that includes equal spellings, adds `different` closure and separating renamings, and states the refusal. R1 uses a two-document identical-spelling whale. R4 covers partial and transitive cases |
| `counts`: public corpus denominators unstated (Claude, Codex, Qwen, GLM) | **Accepted.** C1 declares floors per category. §4.1 marks the 16/50/24/180 figures as host-owned under D1 |
| `trace`: no per-criterion trace. Precision, recall and abstention unowned (Claude, Qwen, GLM) | **Accepted.** §4.1 adds the per-criterion trace table. C5 owns precision, recall and abstention |
| `n2`: N2 is unfalsifiable (Claude, Qwen, Kimi) | **Accepted.** A score field, a threshold `T` declared before the run, homonym suppression on a shared introducing work, and a single-branch N2 |
| `n3`: N3 sample unspecified (Claude, Qwen) | **Accepted.** Sample size of at least 100, selection, labeller and per-kind denominators are declared before the measurement |
| `cites`: wrong module citations (Kimi, GLM) | **Accepted.** §3 cites `src/gnd/judgments.py`, `src/gnd/commands/judgments.py` and `gnd.witness.why_not` |
| `li4`: no producer of the admitted population. Retention untested (Claude, Qwen) | **Accepted.** The LI4 admission step binds the three input digests. A5 tests receipt sensitivity, refusal and retention |
| `li0home`: a third home for default omission (Claude, Qwen) | **Accepted.** §2 names the existing hooks. LI0 spec D1 is re-argued, and §5 documentation is conditional on the measured choice |
| `rulings`: D7 shown as ruled. No ruling step (Claude, Qwen) | **Accepted.** D7 is marked proposed. §8 lists the rulings each spec gate needs |

### Divergent views

| Concern | Disposition |
|---|---|
| Claude · LI1 C2 makes the dependencies cyclic | **Accepted.** C2 keeps only the mutations 0.3.1 commands can detect. R6, A1 and L5 own the rest |
| Claude · report stages and failure signal unspecified | **Accepted.** §2 names the seven stages and the harness exits. C2 pins each mutation to a stage |
| Claude · R2 replacement breaks anchors | **Accepted.** `Mention` entities keep the anchored surface text. R2 asserts that an `anchored` constraint passes |
| Claude · N1 kinds and the near-miss key | **Accepted.** N1 pins kinds. §3 states that LI3 has its own normalization |
| Claude · LI5 relation policies untested | **Accepted.** There is a path-policy table and one exclusion fixture per non-ancestral relation. "Composition policy" is renamed "path policy" |
| Claude · held-out cases unowned | **Accepted.** C6 commits the held-out subset and its digest before LI5 |
| Claude · LI0 dependency understated | **Accepted.** §3 requires fixtures to declare `model_id` and version 2 or later unless the phase depends on LI0. R5 asserts the reason |
| Codex · lineage decision trace | **Accepted.** Lineage fact types carry assertion roles, and the record names decisions per fact. L5 tests removal |
| Qwen · LI0 does not address the version-enum refusal | **Refuted by measurement.** The `version` 2–5 rule is conditional on `operations` being present (`orm-meta.schema.json` `allOf`). Dropping the empty list and the null `model_id`, then reloading, gives an equal `Model` for both version-1 fixtures (§9) |
| Qwen · family candidates untested | **Accepted.** `family` is defined with a declared `k`, and N1 includes a family case |
| Qwen · unresolved admission contradiction | **Accepted.** An unresolved decision never joins two keys, and its mentions stay distinct and sense-less. LI5 queries the composed admitted population |
| Qwen · cross-domain chain against the partition | **Accepted.** §3 states that L2 uses ordinary composition of public sources, with no includes and no reference populations |
| Qwen · why-not without `model_id` not measured | **Accepted.** Measured on 2026-11-15: exit 3 at versions 1 and 2 (§9) |
| Qwen · byte identity has no oracle | **Accepted.** W3 and R5 compare against golden digests committed from the baseline |
| Qwen · replay "unaffected" cites §9 | **Accepted.** §3 cites `service.replay_result` and the export `admit` paths |
| Qwen · whale label ambiguous | **Accepted.** The whale is scored in development (C6). The flat-model witness of L4 is a separate fixture outside the scored corpus |
| Qwen · part 10 has no owner | **Accepted.** §1.1 names literature-depth as owner of the deferred row, pending its P3 ruling |
| GLM · A3 not falsifiable | **Accepted.** `polarity` and `attribution` fields. A3 requires four distinct pairs and no `own-finding` admission |

## Round budget and stop rule

The budget is two plan rounds for this revision sequence (D9). It was
declared in r1's own bytes (§8) before round 1.

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| 1 | 6 attempted, 5 valid | Claude 17, Codex 3, Qwen 17, Kimi 3, GLM 4 | 0 / 44 | 22 / 44 | high | 5 revise |

**Round 2** would review r2. Its stop test:

- stop if more than half of its findings attack text marked `(p2)`;
- or if the counts per seat are flat or rising while the severity ceiling
  falls;
- in any case, stop after round 2 and record whether the bar was met.

r2 carries no review opinion. Round 2 runs only on the owner's request,
because it is a second paid six-seat run.
