---
milestone: induced-knowledge
station: followup-evolve-loading
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: IK-evolve
date: 2026-10-27
gate:
  command: "uv run pytest -q -p no:randomly <r1's 56 files plus every test file naming a changed r2 home: 235 files>"
  exit: 0
  output: "9656 passed, 463 deselected, 1 warning in 1018.05s (0:16:58)"
  note: >-
    The r2 gate, on the final bytes. The expanded command line is the first line
    of evidence/evolve-loading/final-gate-r2.txt. The warning is a pydantic
    serializer warning in tests/test_exp_session_store.py, which r2 does not
    touch. The r1 gate (56 files: 3164 passed, 39 deselected, exit 0) is
    evidence/evolve-loading/final-gate.txt.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside this follow-up's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/induced-knowledge/evidence/evolve-loading/tests-red.txt
    sha256: de46da029698708b03907382b7294ea66eabea5b2179aa9a5df28deba22c6c20
  - path: .gnd-planning/milestones/induced-knowledge/evidence/evolve-loading/regressions-red.txt
    sha256: 1a54f573e20522b86566f3ac389790f6c8023fc7f48fc3867ccefd3a3ca7b25d
  - path: .gnd-planning/milestones/induced-knowledge/evidence/evolve-loading/final-gate.txt
    sha256: 65b2fde0d9d0037fc5252e8d31bc86d1b3bea8f43ad2f536f56d8501ee05bbc4
  - path: .gnd-planning/milestones/induced-knowledge/evidence/evolve-loading/dynamic-query-successor.json
    sha256: 2c58d5c0166576fd6a095eeb831ca0b5351465a1e761daf0ad60d68697e6f4f6
  - path: .gnd-planning/milestones/induced-knowledge/evidence/evolve-loading/r2-tests-red.txt
    sha256: 99873679af7a26ac7a1050a10bdc30bd3ae57e5734a594f1e699e024a8d33ab3
  - path: .gnd-planning/milestones/induced-knowledge/evidence/evolve-loading/r2-regressions-red.txt
    sha256: 0cf52862a805febfc78c2f9b4bff62d21ff54ca0fdf5319c70d3c7f5ece06015
  - path: .gnd-planning/milestones/induced-knowledge/evidence/evolve-loading/final-gate-r2.txt
    sha256: 5329ed99135fee2938e8b423502914b199990ae823a9718a9993d7fb0f3941e5
  - path: tests/fixtures/induced_knowledge/reference-homes-before-r2.json
    sha256: 99c39b8f995d4f6ab80150d8546a5e76464fe012b015b8c2fbeaab528f944dc4
  - path: .gnd-planning/milestones/induced-knowledge/notes/followup-evolve-loading-agent-review.md
    sha256: 3bef3a8afe9211cf978aef437c3a7288e93a41da937c75fbce5c53d6c9715d8f
---

# Follow-up — evolve loading

**Claim.** `gnd evolve preview`, `apply` and `finalize` load every model
through one helper that parses as `gnd validate` parses. A model or candidate
holding a value outside the JSON data model exits 3, and the message names the
value's path and kind. It never exits 70. A `.json`-named model is parsed as
strict JSON. Reference-free YAML previews are byte-identical to before (T6).
Reference exits stay 66, 74 and 3. After amendment r2, eight of the nine
load-then-bind homes bind through one `gnd.model` helper with every outcome
unchanged; discover exits 0 on non-finite floats; and recovery verify refuses
a YAML-only value by name at 3.

**Authority:**
- the close row in [012-milestone-close.md](012-milestone-close.md) "Open
  questions carried forward" (C-D2, CD3, CD5);
- spec r1 ([notes/followup-evolve-loading-spec.md](notes/followup-evolve-loading-spec.md)),
  approved 2026-10-27 with D1-A..D5-A (spec §12). The owner's words, relayed by
  the starting session: "ok go on then with the recs"; confirmed directly the
  same day: "Approve D1 to D5 as proposed.";
- amendment r2 (spec "Amendment r2"), for three more rows the owner asked for,
  approved 2026-10-27: "Approve D6 to D8 as proposed (D6-A, D7-A, D8-A)." D6-A
  reverses D3-A.

## What shipped

- **One loader** in `src/gnd/evolve/service.py`, `_load_model_document`. It
  returns the model and its document for all seven loads: preview current and
  candidate; apply current, candidate and staged; finalize staged before and
  candidate. The second safe-YAML parse after each load is gone (IK4-Q2-R1).
- **The validator's parser.** `gnd.model.parse_model_document` is the parse
  half of `load_model_bytes`, moved verbatim; `load_model_bytes` calls it.
  Evolve's documents and `_parse_model_text` (discover, ILP export, apply's
  gate) use it. So the close row's tagged description extra no longer reads as
  "not valid YAML", and discover reads it (was a traceback, exit 1).
- **One value walk**, `_json_document`. Strict mode refuses dates, timestamps,
  binary, sets, non-finite floats, non-core tags (including a scalar tag on a
  collection) and non-string keys, at the first one in document order:
  `"{label} validation failed: {path} holds a {kind}, which evolve's JSON
  evidence cannot represent; quote it or remove it"` (IK4-Q3, D1-A). Keep mode
  returns them as the safe reader did, so discover's dated candidates are
  unchanged.
- **Strict JSON** for a `.json` model name: the `.json` → `.yaml` rename is
  gone (IK4-Q2-Q1, D2-A).
- **One wrap** of a binder `ReferenceInputError` (R4).
- **The YAML guard** runs only on documents the YAML reader built, and its
  refusals and every model's YAML refusal land at 3 (review B2, H1). One CLI
  marker added: "is not valid YAML".
- **Contract:** `evolution-contract.md` §3 gains the loading paragraph.
- **RF controls:** an RF6b definition successor for `load_model_bytes`, an RF5
  body successor for `_evolve_service_exit` (chained over IK2's), and an RF6
  dynamic-census delta after the close's. Scripts are in
  `evidence/evolve-loading/`.

## Gate output (verbatim)

```
3164 passed, 39 deselected in 278.00s (0:04:37)
exit 0
```

The tests were committed red first (`f2507ca`,
`evidence/evolve-loading/tests-red.txt`): 21 failed, and E3 and J2 passed by
design (they pin premises).

## Criteria

| Obligation | Test | Result |
|---|---|---|
| O1 a dated discover proposal: named 3, never 70 | E1, RV1 | 3 (base 70); zoned timestamps keep discover at 0 |
| O1 every kind named | E2 (8 kinds), RV4, the walk's key test | 3, kind and path named |
| O2 strict JSON for `.json` | J1, J2, J3 | 3, 0/0, 3 (base 0, 0/0, 0) |
| O3 one loader at every site | H1 | 9 loads through preview and apply; no other parse of a loaded model |
| O4 one wrap | W1 | the cause is the binder's own error |
| O5 the tagged extra | E3, E3b, D5 | validate 0; preview 3 named (base 70); discover 0 (base 1) |
| O6 reference exits | T1..T7, R2, R3 | unchanged |
| O7 byte-identical previews | T6 | the golden still matches |
| never 70 on valid JSON | RV2, RV3 | 0 where the base path gave 70; every parse refusal maps to 3 |
| O8 RF controls | `tests/test_rf*.py`, `tests/test_gnd_arch.py` | in the gate |

## Adversarial review

One local reviewer agent read the diff with the spec. **One reviewer is one
reviewer.** It found two blocking regressions, both reproduced and fixed:
- **B1:** a zoned timestamp crashed discover (base 0).
- **B2:** the YAML guard made valid JSON exit 70.

It also found hardening gaps, all fixed: guard messages with no marker, other
labels' YAML refusals at 70, and a scalar tag on a collection passing. Its
completeness sweep found no parse difference for JSON-domain documents across
about thirty YAML forms, and no exit change from apply's reordering. RV1..RV4
fail on the reviewed code (`evidence/evolve-loading/regressions-red.txt`, both
RV2 cases at 70). Report and disposition:
[followup-evolve-loading-agent-review.md](notes/followup-evolve-loading-agent-review.md).

## Refactoring review

**Refactors executed:**
- `parse_model_document`, extracted from `load_model_bytes` (behaviour
  preserved: RF6b digest successor, the loader suites green, P1);
- evolve's seven load-then-parse pairs became one loader.

**Executed in r2** (superseding r1's deferral of the cross-module helper,
D6-A): `bind_declared_references` and `load_model_bytes_bound` in `gnd.model`,
adopted by eight of nine homes (see Amendment r2 below).

**Seen, deferred:**
- **`exp.session_replay._model`** keeps its own bind: it is an RF8-frozen body
  with no successor mechanism (spec F11).
- **Each evolve load parses its bytes twice** (inside `load_model_bytes`, then
  `parse_model_document`), plus one guard pass. Returning the document from the
  loader would remove one parse, but changes `gnd.model`'s public surface.
  Not proposed in r2 either.

## Boundary — what this follow-up does NOT establish

- **Models with YAML-only values still cannot be evolved.** They are refused
  by name; the author quotes the value (D1-A). `gnd validate` accepts them.
- **Evolve still rewrites a model as the candidate's text,** so comments and
  tags are not kept. A tagged model is refused before that can happen.
- **Two homes still leak a raw `ArtifactError`** on a missing or linked
  reference: `gnd discover` (a traceback) and the `judgments` API. D6-A forbids
  exit changes, so H3 pins them (IKE-Q3).
- **Recovery verify still loads through a temporary copy,** so a
  reference-bearing recovered model cannot bind there.
- **No end-to-end case for `gnd import ilp-rules` over a non-finite float;**
  RV8 pins the shared writer.
- **Changed refusal precedence at apply** (spec F4): a preview failing both a
  load and the replay reports the load. Both exit 3.
- **Changed predecessor tests** (spec F5): `test_r1_…` was removed for J1;
  `test_ik4_q2_q2_…` and the `test_model_v2.py` source scan followed the
  rulings.

## Open questions

| ID | Question | Proposed | Owner |
|---|---|---|---|
| IKE-Q3 | `gnd discover` and the `judgments` API let a raw `ArtifactError` escape on a missing or linked reference file (pinned by H3) | a discover/judgments issue; the fix changes exits | owner |
| IKE-Q4 | Evolve parses each model twice; returning the document from the loader needs `load_model_bytes` split as public API | the refactoring milestone that owns RF5 | owner |

The close row's five items are discharged: IK4-Q3, IK4-Q2-Q1, R4 and the tag
case in r1; IK4-Q2-R1 in r1 (evolve) and r2 (the other homes). IKE-Q1 and
IKE-Q2, raised by r1, are fixed in r2.

## Refuted premises

- **"A tagged current model exits 3" (spec §2, §8).** It exits 70 on the base:
  "current model is not" matched no CLI marker (spec F1). Repaired by the
  marker (review H1).
- **"§8's verification selection covers evolve's consumers."** The
  `*evolve*` glob missed `tests/test_*evolution*.py` (spec F8). Repaired in the
  final gate.

- **"Recovery over a dated model hits the same crash" (IKE-Q2).** It exits 3
  with an unnamed message, not 70 (spec r2.1).
- **"The r2 guards change nothing for models that render today" (spec r2.2,
  F13).** The strict walk refused ordered maps, pairs and tagged collections
  that `json.dumps` writes (review round 2, B1). Repaired by the walk's
  `encodable` mode.

## Amendment r2 — what shipped

- **Shared binding (IK4-Q2-R1, D6-A).** `gnd.model.bind_declared_references`
  (None when nothing is declared; the binder's errors unwrapped; `attach`
  optional) and `load_model_bytes_bound` (load, then that). Lean and souffle
  call the second. Evolve, judgments, discover, witness, pyrel and
  session_contract call the first at their existing bind point, so no refusal
  moves (spec F10). Session_replay keeps its own (F11). H3 pins 28 outcomes,
  measured before r2, unchanged; H2 shows every adopted home binding through
  the helper.
- **The value walk** moved verbatim to `gnd.model._documents.json_document`,
  and gained an `encodable` mode that refuses exactly what `json.dumps` cannot
  write.
- **Discover over non-finite floats (IKE-Q1, D7-A).** The candidate writer
  falls back to block YAML on `ValueError` as well. Discover exits 0; evolve
  refuses the proposal at 3, naming the value. `gnd import ilp-rules` shares
  the writer and also exits 0 now (was a traceback).
- **Recovery over YAML-only values (IKE-Q2, D8-A).** After the origin check,
  `gnd recovery verify` refuses such a model by name: `invalid-model-value:
  source.created holds a date, …`, exit 3. `render_model_verbalization` raises
  `VerbalizationError` naming path and kind instead of leaking `TypeError`.
- **RF:** an RF4 body successor for `gnd.api:_witness_inputs`; the new home is
  registered in the layer map, the RF6 package scope and the bind-consumer
  scan.

**Red first:** `d594717` (`evidence/evolve-loading/r2-tests-red.txt`): 13
failed, and H3's 28 passed by design.

**Review, round 2.** One reviewer: one blocking finding (B1 above), one
hardening (the origin check's precedence) and two completeness gaps (a
`!!str` scalar leaking `TypeError`; the ILP import's moved exit). Each was
reproduced first and fixed or pinned (RV5..RV8;
`evidence/evolve-loading/r2-regressions-red.txt`, 5 failed on the reviewed
code). It found no changed home outcome, and no verbalization difference over
171 valid models.

## Size

`git diff --stat 63f7f1f -- src tests` after r2: 23 files changed, 1068 insertions(+), 123 deletions(-). After r1 alone: 9 files changed, 580 insertions(+), 78 deletions(-). `src/gnd/evolve/service.py`
accounts for 148 insertions and 50 deletions. The estimate was about 90 source lines and 220 test
lines; the source landed at about twice that, mostly the value walk and the
review fixes.
