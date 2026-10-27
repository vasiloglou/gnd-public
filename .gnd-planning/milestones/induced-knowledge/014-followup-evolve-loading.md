---
milestone: induced-knowledge
station: followup-evolve-loading
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: IK-evolve
date: 2026-10-27
gate:
  command: "uv run pytest -q -p no:randomly <spec §8 selection plus tests/test_*evolution*.py: 56 files>"
  exit: 0
  output: "3164 passed, 39 deselected in 278.00s (0:04:37)"
  note: >-
    The expanded command line is the first line of
    evidence/evolve-loading/final-gate.txt. Spec finding F8 added the evolution
    suites, which §8's evolve glob missed.
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
  - path: .gnd-planning/milestones/induced-knowledge/notes/followup-evolve-loading-agent-review.md
    sha256: 3bef3a8afe9211cf978aef437c3a7288e93a41da937c75fbce5c53d6c9715d8f
---

# Follow-up — evolve loading

**Claim.** `gnd evolve preview`, `apply` and `finalize` load every model
through one helper that parses as `gnd validate` parses. A model or candidate
holding a value outside the JSON data model exits 3, and the message names the
value's path and kind. It never exits 70. A `.json`-named model is parsed as
strict JSON. Reference-free YAML previews are byte-identical to before (T6).
Reference exits stay 66, 74 and 3.

**Authority:**
- the close row in [012-milestone-close.md](012-milestone-close.md) "Open
  questions carried forward" (C-D2, CD3, CD5);
- spec r1 ([notes/followup-evolve-loading-spec.md](notes/followup-evolve-loading-spec.md)),
  approved 2026-10-27 with D1-A..D5-A (spec §12). The owner's words, relayed by
  the starting session: "ok go on then with the recs"; confirmed directly the
  same day: "Approve D1 to D5 as proposed."

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

**Seen, deferred:**
- **The cross-module load-then-bind helper** (`api.py` judgments,
  `export/lean_io.py`, `export/pyrel_rules.py`, discover's
  `_bind_references`). Each has its own root option and wrap rule and none is
  broken (D3-A). Re-carried as **IK4-Q2-R1** to the refactoring milestone that
  owns RF5.
- **Each evolve load parses its bytes twice** (inside `load_model_bytes`, then
  `parse_model_document`), plus one guard pass. Returning the document from the
  loader would remove one parse, but changes `gnd.model`'s public surface.
  Carried with IK4-Q2-R1.

## Boundary — what this follow-up does NOT establish

- **Models with YAML-only values still cannot be evolved.** They are refused
  by name; the author quotes the value (D1-A). `gnd validate` accepts them.
- **Evolve still rewrites a model as the candidate's text,** so comments and
  tags are not kept. A tagged model is refused before that can happen.
- **Discover's `.inf` traceback** is in its output writer, not the parser, and
  is not fixed (D4-A).
- **`gnd recovery verify`** shares `render_model_verbalization`. A date-bearing
  model there was not reproduced or fixed.
- **Changed refusal precedence at apply** (spec F4): a preview failing both a
  load and the replay reports the load. Both exit 3.
- **Changed predecessor tests** (spec F5): `test_r1_…` was removed for J1;
  `test_ik4_q2_q2_…` and the `test_model_v2.py` source scan followed the
  rulings.

## Open questions

| ID | Question | Proposed | Owner |
|---|---|---|---|
| IK4-Q2-R1 (re-carried) | One load-then-bind helper across `api.py`, the two exporters and discover; and returning the document from the loader to drop evolve's second parse | the refactoring milestone that owns RF5 | owner |
| IKE-Q1 | `gnd discover` on a model holding `.inf` or `.nan` crashes in its candidate writer (exit 1) | a discover issue | owner |
| IKE-Q2 | `gnd recovery verify` over a model holding a YAML-only value may hit the same verbalization `json.dumps` (not reproduced) | reproduce, then a recovery issue | owner |

The close row's five items are discharged here: IK4-Q3, IK4-Q2-Q1, R4 and the
tag case are fixed, and IK4-Q2-R1 is executed inside evolve and re-carried for
the rest.

## Refuted premises

- **"A tagged current model exits 3" (spec §2, §8).** It exits 70 on the base:
  "current model is not" matched no CLI marker (spec F1). Repaired by the
  marker (review H1).
- **"§8's verification selection covers evolve's consumers."** The
  `*evolve*` glob missed `tests/test_*evolution*.py` (spec F8). Repaired in the
  final gate.

## Size

`git diff --stat 63f7f1f -- src tests`: 9 files changed, 580 insertions(+), 78 deletions(-). `src/gnd/evolve/service.py`
accounts for 148 insertions and 50 deletions. The estimate was about 90 source lines and 220 test
lines; the source landed at about twice that, mostly the value walk and the
review fixes.
