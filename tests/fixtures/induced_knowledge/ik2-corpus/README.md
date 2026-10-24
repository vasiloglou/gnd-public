# IK2 approval corpus

This is the owner-approval instrument for IK2 (spec IK2-D1). It holds the
loader, bounds and admission cases of the
[IK2 spec](../../../../.gnd-planning/milestones/induced-knowledge/notes/phase-IK2-spec.md)
§8 (T2–T4). It was committed red, before any implementation file.

**This file tells each case's story without its answer.** The answers are in
[`expected.json`](expected.json), kept separate so that a blind reader can
predict an answer before seeing it. The inputs are in [`cases.json`](cases.json).
Both are written by
`.gnd-planning/milestones/induced-knowledge/evidence/IK2/build_ik2_corpus.py`,
whose expected answers are typed by hand from the approved spec, not computed
from code. The harness is `tests/test_induced_provenance.py`.

## How a case runs

- **Base model.** Every constraint case is appended to the first fact type
  (`work_item_has_title`) of the `evolution-safe-additive` before model in
  `tests/fixtures/phase4_reference/evolution.json`. Cases L34–L36 instead edit
  `tests/fixtures/models/v2_operations.orm.yaml`.
- **The minimal induction block** used unless a case changes it:
  - inducer `gnd-discover` `0.1.0`, method `gnd-discover`;
  - manifest digest `a`×64;
  - no examples or counterexamples;
  - support 2 of 3;
  - one evidence item `populations/p1.json` with digest `b`×64.
- **Loader and bounds cases (L, B)** run `gnd validate` on the model. The
  answer gives the exit code, and a rule id that must appear in the output.
- **YAML cases (L30–L33)** splice a YAML flow fragment into the JSON base, for
  values JSON cannot spell: `.nan`, `.inf`, an anchor, an unquoted date.
- **Admission cases (A)** call the D-12 gate directly on a before model and a
  candidate model; the answer is "admitted" or one of the named reasons R-I1 to
  R-I4. Cases marked "preview" also run `gnd evolve preview` on a one-operation
  fact-type modify; the answer gives the exit code and the refusal text.
- **Two cases also pass at B, by design.** L37 and A10 pin behaviour that IK2
  must not change.
- **T5 is separate.** The D-12 table of today's outcomes is not part of this
  corpus. It is `../ik2-d12-baseline.json`, captured at B by
  `.gnd-planning/milestones/induced-knowledge/evidence/IK2/capture_ik2_d12_baseline.py`.

## Loader cases (T2) and bounds (T3)

| Case | Story |
|---|---|
| L01 | minimal induced block, proposed and deontic |
| L02 | maximal block: examples, counterexamples, two evidence items, confidence |
| L03 | confirmed and alethic, with the review record named |
| L04 | proposed but claiming alethic modality |
| L05 | provenance present but without an induction block |
| L06 | induction block with an unknown key |
| L07 | an extra provenance key next to induction |
| L08 | induced source with no provenance at all |
| L09 | evidence ref is an absolute POSIX path |
| L10 | evidence ref is a Windows path |
| L11 | evidence ref climbs out of the manifest directory |
| L12 | evidence ref has a parent segment in the middle |
| L13 | evidence ref segment starts with a dot |
| L14 | evidence ref contains a space |
| L15 | evidence ref ends in a newline |
| L16 | example id is a raw two-word value |
| L17 | example id contains a path separator |
| L18 | example id is empty |
| L19 | example id ends in a newline |
| L20 | manifest digest in upper case |
| L21 | manifest digest one character short |
| L22 | evidence digest followed by a newline |
| L23 | support numerator larger than its denominator |
| L24 | more listed examples than the support numerator |
| L25 | more counterexamples than the support gap allows |
| L26 | one id listed as both an example and a counterexample |
| L27 | confirmed without a review record |
| L28 | confirmed with a whitespace-only review record |
| L29 | the same example id listed twice |
| L30 | YAML: confidence value is .nan |
| L31 | YAML: confidence value is .inf |
| L32 | YAML: support numerator is an anchored true |
| L33 | YAML: inducer version is an unquoted date |
| L34 | induced source on an operation |
| L35 | induced source on an operation precondition |
| L36 | induced source on an operation dynamic rule |
| L37 | an induction block under source explicit |
| L38 | confidence without its formula |
| B01 | inducer name of 1 character |
| B02 | inducer name of 64 characters |
| B03 | inducer name of 65 characters |
| B04 | empty inducer name |
| B05 | inducer version of 64 characters |
| B06 | inducer version of 65 characters |
| B07 | method of 64 characters |
| B08 | method of 65 characters |
| B09 | empty method |
| B10 | example id of 64 characters |
| B11 | example id of 65 characters |
| B12 | 256 examples |
| B13 | 257 examples |
| B14 | 32 counterexamples |
| B15 | 33 counterexamples |
| B16 | no evidence items |
| B17 | 32 evidence items |
| B18 | 33 evidence items |
| B19 | evidence ref of 256 characters |
| B20 | evidence ref of 257 characters |
| B21 | negative support numerator |
| B22 | numerator and denominator at 2^53 - 1 |
| B23 | numerator at 2^53 |
| B24 | denominator of 0 |
| B25 | denominator at 2^53 |
| B26 | confidence value 0 |
| B27 | confidence value 1 |
| B28 | confidence value -0.01 |
| B29 | confidence value 1.01 |
| B30 | empty confidence formula |
| B31 | confidence formula of 256 characters |
| B32 | confidence formula of 257 characters |
| B33 | review record of 256 characters |
| B34 | review record of 257 characters |

## Admission cases (T4)

"Proposed" means the rule is advisory (deontic) unless the story says
otherwise. A "review record" is `provenance.reviewed_in`.

| Case | Story | Preview |
|---|---|---|
| A01 | a new induced rule, proposed and advisory | yes |
| A02 | a new induced rule claiming alethic modality | yes |
| A03 | a new induced rule arriving already confirmed | yes |
| A04 | a new proposed induced rule that already names a review record | yes |
| A05 | an existing proposed induced rule confirmed by review, kept advisory | yes |
| A06 | an existing proposed induced rule confirmed by review and made alethic | yes |
| A07 | confirmation that also edits the rule's rationale | yes |
| A08 | an induction block under a new llm-inferred rule | yes |
| A09 | an induction block under a new user-supplied rule | yes |
| A10 | an already confirmed induced rule left unchanged | gate only |
| A11 | two confirmations claiming the same single proposed predecessor | gate only |
| A12 | the proposed predecessor kept unchanged next to a confirmed copy | gate only |
| A13 | confirmation with a whitespace-only review record | yes |
| A14 | a confirmed induced rule whose evidence changes, returned to proposed | yes |
| A15 | a confirmed induced rule whose evidence changes, still confirmed | yes |
| A16 | confirmation whose predecessor was llm-inferred, not induced | yes |
| A17 | a hostile induction value (a string) under source explicit | gate only |
