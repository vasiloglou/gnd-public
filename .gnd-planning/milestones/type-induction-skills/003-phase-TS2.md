---
milestone: type-induction-skills
station: "phase-TS2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-TS2
date: 2026-11-05
gate:
  command: "uv run pytest -q tests/test_discover_type_evidence.py tests/test_discover_fact_type_family.py tests/test_discover.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py"
  exit: 0
  output: "581 passed in 138.24s (0:02:18)"
  note: >-
    The plan section 9 TS2 row: the TS1 gate plus the direct file
    tests/test_discover_type_judgements.py (73 passed, exit 0) and
    tests/test_schema_sync.py (4 passed). The first run of this line after
    the review fixes failed 2 RF6 inventory tests; the successor was
    regenerated and the line rerun green. Both runs are in
    evidence/TS2/gate.txt.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or the milestone close"
  reason: "the broad historical lanes are outside TS2's impact closure"
evidence:
  - path: .gnd-planning/milestones/type-induction-skills/notes/phase-TS2-spec.md
    sha256: acad5d56722d2535d0d4126994c06ea88786344983c2ca3455a1acd84433bcc9
  - path: .gnd-planning/milestones/type-induction-skills/notes/phase-TS2-claude-review.md
    sha256: 17c3e70e4ec724d0dd7fcc9af59d4356dfd48f87ab8136fdbaf7e94a8378e0ba
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS2/capture_fixture_parity.py
    sha256: 400d9e962b040921031df0bb5f1f397afb6510e1f6ae7ae726a6d1b457b25b4f
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS2/dynamic-query-successor.json
    sha256: 85478f5045d366e8c20a673cb23245699a10588e06b68d10b17586a3fcf17d60
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS2/fixture-parity-7b171bb2.json
    sha256: d54949aa902c5d9d0ba121188b6d826eef0e8a03690fcf2fe5051f41e45d2d49
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS2/fixture-parity-after.json
    sha256: d54949aa902c5d9d0ba121188b6d826eef0e8a03690fcf2fe5051f41e45d2d49
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS2/gate.txt
    sha256: e776991d3e7d4aa10c3ea3b3147398e6c619b4566f6a4963b1a713d65f190ac0
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS2/mutate.py
    sha256: 26d25423ac91a94e88a1761e3c88639ef0b84c1411ddf5320b7b51896b2604a7
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS2/mutations.txt
    sha256: e1facdc7bd1e4059dcf8ab94e501f90efa6bdbe6b3c4af6c71f8ca4e6f708984
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS2/parity-7b171bb2.json
    sha256: 4061906db53757824984dc82eefa43cb865b069cf2ac9e18adffa57cdc8bbe48
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS2/parity-after.json
    sha256: e22b30de1ba8d97ff76a54ec33151884368d54af4c575a1f61df3d19dd3bf09a
  - path: src/gnd/discover/type_judgements.py
    sha256: dd164fca5b9aad37143f2ff563172459f245f524c54a9ddc99f9286835781fd2
  - path: src/gnd/discover/types.py
    sha256: 9912c0b51cb621523130f500212a756a2e5f9642bf1fd18d8bfb3480b43d7bb9
  - path: src/gnd/discover/service.py
    sha256: 98c3851d16ab385427d1d232c085c1bf402943962ccafad6afb5b98d7703def4
  - path: src/gnd/discover/type_evidence.py
    sha256: c48084d39eb743c8f81b7c2276d8b8a3d9dbf9dfedc65f4d46a5eb1d87a09dea
  - path: src/gnd/commands/discover.py
    sha256: 88af8235acc534b6e9b174990199409db79b2cad0ddbfc5b4d6c780d8c32a553
  - path: src/gnd/type-judgements.schema.json
    sha256: 3a5bf109771342e1741b91eef1c9bc816185e7362b1e23cb7f590353ec4bb873
  - path: src/gnd/discover.schema.json
    sha256: 01788de8cce4b96a3ad4a4fb85a94206d7e840208d8f21ce86b2a3afb27bcaa5
  - path: tests/test_discover_type_judgements.py
    sha256: 15bea2c69111fed7da0e8c74a0010e95263283a28df541f2e8c364f13a932adc
  - path: docs/reference/discover.md
    sha256: abd10b019f70dead188ea06aa4e0839fe60de8a04728b10b614191e38f110d88
---

# TS2: judgements and rendering

**Claim.** `gnd discover MODEL POP --families fact-type --type-evidence-in E
--duplicate-judgements J [--shape-judgements S]` reads verdicts bound to the
raw-byte SHA-256 of `E`, recomputes `E` from the model, population and
settings and refuses any difference, checks coverage and every verdict
against the data (exit 3, nothing written), and renders them: `distinct` is
proposed whatever its signature matches, `duplicate` is reported against the
named fact type, `many-to-many` is proposed with a uniqueness spanning both
roles, and `skip` is counted. Judged proposals pass `gnd evolve preview
--policy additive`, apply, and validate (T21–T22). Without the new options,
the 20-case IK4 corpus gives `7b171bb2`'s exits and bytes except E6's stderr
usage text, and 36 runs of the TS1 fixture (three variants, three modes, with
and without values and `--type-evidence`) are byte-identical. Spec r1 was
approved `(a2)` 2026-11-05 on the prose instrument, D1–D10 as proposed;
implementation began on the owner's "go ahead" in this session.

## What shipped

- **`src/gnd/discover/type_judgements.py` (new):** `read` (capped read,
  the shared bounded JSON intake, the closed schema; messages name a
  location, never a value), `check_binding`, `bind` (coverage, vocabulary,
  `of` among the listed candidates, D4 over the whole model and the listed
  candidates, D5), and `scan_free_text` (an Aho–Corasick matcher over
  boundary-tagged tokens; the D10 model-text exemption).
- **`src/gnd/discover/types.py`:** `propose` takes `verdicts` and
  `judgement`. A judged group is rendered by its verdict, not by the
  signature match; `many-to-many` spans both roles with pairs/rows support
  and exact repeats as counterexamples; judged fact types carry
  `provenance.judgement` and, except under `customer` (D3),
  `provenance.induced_from`. The kind vocabulary is public (D9):
  `primitive_kind`, `PRIMITIVE_FOR_KIND`, `cell_text`.
- **`src/gnd/discover/service.py`:** the three options, the §6.1 order
  (usage 64; inputs 66; outputs 74, 11; judgements and their digest before
  the model is read, 3), the deterministic run and its evidence compared
  byte for byte, `bind`, the scan, a second `propose` with the verdicts,
  and the written-bytes trim (`_trimmed_proposal`, factored out and used
  for both runs).
- **`src/gnd/commands/discover.py`:** `--type-evidence-in`,
  `--duplicate-judgements`, `--shape-judgements`; the family-flags message
  names them.
- **Schemas:** `src/gnd/type-judgements.schema.json` (new, closed, in both
  runtime schema inventories); `discover.schema.json` gains optional
  `judged`, `shape`, `skipped.judged_skip` and `judgements`.
- **Docs:** a "Type judgements" section in `docs/reference/discover.md`,
  one sentence in `docs/reference/disclosure.md`, one release-note line.
- **Pins:** RF1 `discover` help, exit and tree-subtree goldens, the manifest
  and its digest; the RF6 dynamic-read successor
  `evidence/TS2/dynamic-query-successor.json` (the live query policy is
  unchanged); `tools/gnd_layers.json` maps `gnd.discover.type_judgements`
  to lane `discover`; TS1's usage-message assertion follows the extended
  message (spec §12 I6).

## Gate output (verbatim)

From `evidence/TS2/gate.txt`:

```
$ uv run pytest -q tests/test_discover_type_judgements.py
.                                                                        [100%]
73 passed in 85.66s (0:01:25)
exit 0
$ uv run pytest -q tests/test_discover_type_evidence.py tests/test_discover_fact_type_family.py tests/test_discover.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py
FAILED tests/test_rf6_query_policy.py::test_dynamic_duplicate_inventory_row_is_refused
2 failed, 579 passed in 153.70s (0:02:33)
exit 1
$ uv run pytest -q tests/test_schema_sync.py
....                                                                     [100%]
4 passed in 0.07s
exit 0
$ uv run pytest -q -m distribution tests/test_public_built_inventory.py::test_wheel_carries_every_vendored_runtime_schema
.                                                                        [100%]
1 passed in 0.88s
exit 0
$ uv run ruff check src/gnd/discover src/gnd/commands/discover.py tests/test_discover_type_judgements.py tests/test_discover_type_evidence.py
All checks passed!
exit 0
$ uv run zensical build --strict
No issues found
Build finished in 0.61s
exit 0
$ uv run python tools/check_docs.py site
14307 local links/assets/anchors checked
exit 0
parity parity-7b171bb2.json vs parity-after.json: 20 cases, differing: {'E6': ['stderr_sha256']}
parity fixture-parity-7b171bb2.json vs fixture-parity-after.json: 36 cases, differing: {}

Rerun after the RF6 dynamic-read successor was regenerated for the review fixes (the run above failed 2 RF6 inventory tests):
$ uv run pytest -q tests/test_discover_type_evidence.py tests/test_discover_fact_type_family.py tests/test_discover.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py
.....                                                                    [100%]
581 passed in 138.24s (0:02:18)
exit 0
```

The first TS1-gate run above is red (2 RF6 inventory tests); it was run
after the review fixes and before their dynamic reads were recorded. The
rerun is the gate result.

## Measured criteria

- **T28 time bound** (standing rule 2): 20,000 groups judged, 380-character
  rationales, in 13.3 s against a stated ceiling of 120 s (one machine).
- **Matcher:** 2,000 adversarial patterns over a 1 MB model and 5,000
  rationales of 2,000 tokens: 8.7 s after the F3 fix (1.4 s before it, for
  the reviewer's probe on the untagged matcher). A 60,000-case comparison
  against a literal implementation of §6.5: 0 misses, 4 over-refusals, all
  whitespace runs (I12).
- **Mutations** (`evidence/TS2/mutations.txt`, script `mutate.py`): 31
  mutations of the new refusal, scan and rendering branches, over the final
  source; all 31 killed.

## Adversarial review

One reviewer is one reviewer: a general-purpose subagent with shell access
that ran reproductions and the gate against the uncommitted tree. Retained
in `notes/phase-TS2-claude-review.md` (scratch path redacted, declared
there). It reproduced no blocking defect. All five findings were reproduced
here before fixing; each fix has a regression test shown failing first.
Triage:
- **Hardening, fixed:**
  - F1, D4 bypassed past candidate truncation: `test_f1_…`, I10.
  - F2, `judge.skill` unscanned but copied into the model: `test_f2_…`, I11.
  - F3, punctuation matched beside letters: `test_f3_…`, I12.
  - F4, a judged clash repeating an existing reading: `test_f4_…`, I13.
- **Completeness, fixed:** F5, untested branches. `test_f5_…` covers M1,
  M2, M12 and M19, the 70 and 74 exits, and non-JSON evidence (I14). The
  mutation run then killed all of them.

**What the reviewer confirmed:**
- Nothing is written after any refusal, and no TS2 path tracebacks.
- No message echoes a rationale, `of`, a value or a digest.
- No-option parity holds over 39 runs of its own against `git archive
  7b171bb2`.
- Many-to-many holds at the induction bounds (256 examples, 32
  counterexamples) and with a redacted value role.
- The g<n> positions agree with the records, and `drop_last` after
  judgement stays consistent.

**Own coverage audit against §8:**
- T1–T30 each have a case.
- T25 is the RF1 pin run.
- T26 is absent-key tests plus the recorded byte parity.
- T27 is the IK4 parity run.
- T30 runs inside the helpers.

## Refactoring review

- **Executed (D9):** the kind vocabulary got public names in
  `gnd.discover.types` (`primitive_kind`, `PRIMITIVE_FOR_KIND`), and
  `type_evidence` now calls the public one; `_primitive_of` stays private,
  since it reads the family's internal group record. `_cmd_discover`'s
  written-bytes trim became `_trimmed_proposal`, and the evidence build
  became `_evidence`, each used by both the deterministic and the judged
  run. Behaviour-preserving: the parity runs and the TS1 gate are
  unchanged after both.
- **Seen, deferred:** `bounded_json`'s refusal messages say "proposal"
  whatever they read; the reader rewrites the word. A neutral message in
  `gnd.json_input` is maintenance, outside the discover lane.

## Boundary — what this phase does NOT establish

- **The CLI checks verdicts; it does not check that they are right.** A
  judge that calls a true duplicate `distinct` gets a proposal; review at
  `gnd evolve preview` remains the control (plan §6).
- **The free-text scan is exact text only.** A paraphrase, a spelling
  change or an encoding escapes it, and numbers equal to a hidden value
  are refused even when they mean something else (I3). The skills' own rule
  is the main control.
- **The binding cannot see trim inputs the evidence does not record.** A
  written-bytes trim exactly at the size boundary depends on `--actor`,
  `--requested-at` and the population file name (reviewer); a different
  value there could make a valid judgements file stale.
- **Under `customer` no origin is recorded (D3),** so a later customer run
  cannot apply D4 to that fact type.
- **No skill exists yet.** The judgements files in the tests are written by
  hand; TS3 and TS4 add the skills.
- **One reviewer is one reviewer.** No panel reviewed the spec or the diff.
- **Not run:** the broad historical lanes (`evidence or census`) and the full
  default lane.

## Open questions

- **Carried from TS1:** the CT4 DateTime value-type defect (D9 leaves it to
  maintenance, since fixing it changes default output); the malformed-YAML
  traceback; plan repairs P2, the TS-R7 "growth zero" wording and the
  packaging test name.
- **New, pre-existing (reviewer):** a UTF-16 model gives a
  `UnicodeDecodeError` traceback from `load_model_bytes` at `7b171bb2`.
  Target: maintenance.
- **Plan repairs at the close:** P1 (judgement provenance on the fact type,
  not the constraint), P2 (no `functional` verdict), and §2.2's group key
  (`g<n>`, as TS1 ruled).
- **TS3, TS4:** vendoring the two schemas into `gnd-orm-core/references`
  (D7).

## Refuted premises

- **P1 (plan TS-R4, §2.2):** "`provenance.judgement` on the constraint".
  An induced constraint's provenance is closed to `induction`,
  `reviewed_in` and `spans`. Repaired within TS2-C7: both records are on
  the fact type. Found at spec time; proved by T21–T22.
- **P2 (plan §2.2, TS2-C4):** a `functional` shapes verdict. Every group a
  shapes file judges is `multi_valued`, so it could never be accepted. D2
  removed it; T17 refuses it.
- **§6.3's D4 over listed candidates** was too narrow (review F1, I10).
- **§6.5's matcher as first built** did not implement the character rule
  it stated (review F3, I12).
