---
milestone: report-output-fidelity
station: phase-ROF3
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-ROF3
date: 2026-11-08
gate:
  command: ".venv/bin/python -m pytest -q -p no:cacheprovider -rf tests/test_rof3_model_identity.py tests/test_model_v2.py tests/test_reference_population_corpus.py tests/test_rf1_helper_pins.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf1_semantic_pins.py tests/test_public_transition_trace.py tests/test_v62_phase1_trace.py tests/test_guarded_corpus.py tests/test_marketplace_plugins.py tests/test_packaged_skills.py tests/test_model_validation.py tests/test_rof1_projected_text.py tests/test_rof2_projected_text.py tests/test_rf5_*.py tests/test_rf6_*.py tests/test_gnd_arch.py tests/test_rf1_layering.py tests/test_rf8_structure.py tests/test_rf7_structure.py tests/test_rf3_core.py tests/test_rf4_peripheral.py tests/test_v71_phase3_successors.py tests/test_transition_report.py tests/test_population_load.py"
  exit: 1
  output: "3 failed, 2970 passed, 1 skipped, 3 deselected in 969.18s (0:16:09)"
  note: >-
    The focused gate at 9ccb8290 ran beside two full-suite runs (about 13
    pytest processes); its three failures are wall-clock bounds of 10 s in
    checker timing tests (11.6 s and 13.3 s observed). Rerun alone at the same
    bytes: "3 passed in 22.67s". ROF3 does not touch the checker. Lint,
    layers, the component index and the sharded full suite are in the body.
evidence:
  - path: src/gnd/values.py
    sha256: 95a5d287e18d5a75ad39838c4220adf3b26c1b1cf321a4cabd3c7678dcc0cf36
  - path: src/gnd/output.py
    sha256: 9567ec0672c6fa606f931c4319486f8136fad8271f377cfdbffbb3a03cfe578d
  - path: src/gnd/commands/checking.py
    sha256: a037cd34bc602ba627e01cc2f8ff949071777cd567bc6779ff80cfd2c5e5b04b
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 4d6444bcc085838042705bd7bd87a27c3e152a7837bc8c366f58365827a20f0d
  - path: tests/test_rof3_model_identity.py
    sha256: 8fed0bfd1bd7920b676bfab54ffbc4a1105255e7996cb82945ca5d997097d86f
  - path: tests/fixtures/rof3-model-identity/README.md
    sha256: 24cfe2770ab0f5d656a796f102d777b37c529f1d4b13b67b5defb5b431d08c2a
  - path: tests/fixtures/rof3-model-identity/expected/vectors.json
    sha256: 74e3cc29432932a5cdbacc0f2e8c33b17d0735fa08005b438fa62466238e2ec9
  - path: tests/fixtures/model-identity-cli/expected.json
    sha256: 65a09a460b56b5266ddde3986e05c93709b029e37d9485d75ee358aeeec20b2c
  - path: .gnd-planning/milestones/report-output-fidelity/notes/phase-ROF3-spec.md
    sha256: 8b656919d59393fce0415383c4318deccda7a66c72559c2b808a8c18530e69f2
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF3/codex-review.md
    sha256: 9ab6513fc9324d8a2a5133a81084dc28b020e6e06a6e689e7029e95e33359ce1
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF3/full-suite-main-8f9781b9.txt
    sha256: 003b1b0ba830bbb2d9ee30efa288503110b7e3bec251f45f250ffcddfc5a076b
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF3/full-suite-rof3-9ccb8290.txt
    sha256: 1ae3a40f569de7a9a28a35039c62c79b849db3b8d10cce543cc187b916222417
---

# Claim

At 9ccb8290 (main 8f9781b9 merged in), `gnd.values.model_identity(model)`
returns a canonical model identity a caller can recompute from the bytes
alone: version 2 for a model without reference populations, the existing
version 1 for a reference-bearing model, or a typed refusal
(`model:identity-unrepresentable`). `gnd validate MODEL --identity` prints the
digest and the document (exit 0), refuses an unrepresentable model (exit 3)
and is a usage error with `--trace`, `--document` or `--format json` (exit
64). The definition has one home, a new subsection of the gnd-orm-core
representation format, with test vectors. The legacy `model_digest`, every
report, `validate --trace` and `validate --format json` are unchanged; the
CLI help and usage line of `gnd validate` gained the option. No site accepts
the new identity yet (ROF4). The full default suite at 9ccb8290 has no failure
that main lacks.

## What shipped

- `src/gnd/values.py`: `IDENTITY_VERSION`, `ModelIdentityError`,
  `_identity_parts` (the one place that decides representability),
  `model_identity_document`, `model_identity_bytes`, `model_identity`;
  `_reference_identity_document`, now the one home of the version-1 envelope,
  shared with `reference_model_digest` (bytes unchanged for every loadable
  model; declarations now go through the canonical walk).
- `src/gnd/output.py` `_print_model_identity`; `src/gnd/commands/checking.py`
  the `--identity` option, its usage check and its dispatch.
- `src/gnd/skills/gnd-orm-core/references/representation-format.md` "Model
  identity (canonical, versions 1 and 2)" (the normative text and three
  vectors) and a sentence after "Three digests, three bases";
  `docs/reference/formats.md` cites it.
- Corpus `tests/fixtures/rof3-model-identity/` (004d24fa, approved with
  "Approve, implement"): ten models; runner `tests/test_rof3_model_identity.py`,
  80 tests.
- CLI successor fixture `tests/fixtures/model-identity-cli/expected.json`
  wired into `tests/test_rf1_cli_pins.py` (no frozen golden edited); RF5 row
  for `_cmd_validate`; query-policy and dynamic-query successors under
  `evidence/ROF3/`; index entries `model.scalar_identity`,
  `cli.checking_command`, `infra.text_output`.

## Gate output (verbatim)

Focused gate, at 9ccb8290 (concurrent with the full suites):

    3 failed, 2970 passed, 1 skipped, 3 deselected in 969.18s (0:16:09)

The three, rerun alone at 9ccb8290:

    3 passed in 22.67s

Focused gate at 3b0dbcc1 + spec edits, first run: one failure whose name the
saved output did not keep; the clean rerun at the same source: `2947 passed,
1 skipped, 3 deselected in 483.32s (0:08:03)`.

Corpus and ROF3 tests at each stage (`tests/test_rof3_model_identity.py`):

    004d24fa (corpus, base code):   21 failed, 11 passed   [32 tests]
    3b0dbcc1 (implementation):      55 passed
    3b0dbcc1 + review tests:        P1, P2, P3, P4 failed; P5 and P8 vectors passed (the code matched; the text did not)
    9ccb8290:                       80 passed

Lint: `ruff check` over the touched source and test files: `All checks passed!`

Layers and structure: in the gate above (`test_gnd_arch`, `test_rf1_layering`,
`test_rf8_structure`, `test_rf7_structure`, `test_rf3_core`,
`test_rf4_peripheral`).

V6: `python3 scripts/components_index.py changed --base origin/main --strict`:
`changed against origin/main (8f9781b): 72 file(s) differ; 0 to fix, 0 warning(s), 2 to reread`.
The two rereads (`subsystem.check`, `infra.output`) are still accurate: they
gain a member function and a re-export, not a capability.

V5, default lane, six round-robin shards run locally:

    main 8f9781b9 (concurrent with other runs):  107 failed or errored ids
    rof3 9ccb8290 (clean, alone):                 83 failed ids; head minus main = none

The 83 are 77 in `tests/test_public_tests_mode_corpus.py` plus
`test_rf1_session_pins` [3] fresh and resume, two `test_public_book_runtime`
tests, `test_doctor_uninstall` and `test_development_scaffold::test_reference_closure_and_declared_bootstrap`;
all six also fail on main, and were not examined. An earlier head run at
20c49621 is not used: the review repairs were edited into the tree while it
ran.

## Criteria

| Criterion | Result |
|---|---|
| ROF3-C1 | `model_identity` and the document, defined in the normative home; T1 re-implements the definition in the test file and agrees on every tracked loadable model; the ten vectors match byte for byte |
| ROF3-C2 | refusals: a non-string key, a set / Decimal / bytes, a lone surrogate, a malformed or non-string-keyed reference declaration, nesting past the interpreter; each is `ModelIdentityError`, the legacy digest stays total; absent and empty `reference_populations` agree |
| ROF3-C3 | the identity of a 9.7 MB model takes under 4 s (measured 0.43-0.65 s, about 4x the legacy digest); the legacy digest of every corpus model equals its pin (D6) |
| ROF3-C4 | `gnd validate --identity` prints the digest and the document; a subprocess recomputes the digest with `hashlib` from line 2; also under `PYTHONIOENCODING=ascii` |
| plan §2 | version 2 only without reference populations, version 1 only with them; operations-only twins: plain identity unchanged, reference identity moves |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over
`git diff 004d24fa 3b0dbcc1`, disposition `block`, 8 findings:
[codex-review.md](evidence/ROF3/codex-review.md). P1 (version-1 declarations
bypassed the walk), P2 (a `TypeError` leaked), P3 (the producer depended on
the terminal encoding) and P4 (the document function returned a document the
bytes refused) were reproduced red and fixed. P5 (datetime spelling and a
false quoting claim) was fixed in the normative text, P6 by correcting the
spec's compatibility claim (usage errors repeat the usage line), P8 by
hand-written byte vectors; P7 was applied for T7 and argued for T8 and T12
(spec I7). The reviewer could not run the suite. The repairs were not
re-reviewed.

## Refactoring review

Executed: the version-1 envelope moved out of `reference_model_digest` into
`_reference_identity_document`, now shared with the new identity, so the
envelope has one home (bytes unchanged; its counted query read moved with
it). Representability is decided in one function, `_identity_parts`. Seen and
not done: `transition.transition_model_identity` and
`values.reference_model_digest` both still return the legacy spelling for
plain models under names that now read as if they were the identity; renaming
them is ROF4's work, where the comparison sites change, or later.

## Size

Estimate: about 155 source and doc lines and 230 test lines. Measured
(`git diff --numstat 004d24fa 9ccb8290`, ROF3 files only; the merge of main
is excluded): source and docs +226 / -5 (`values.py` 90, the normative text
77, `output.py` 33, `checking.py` 20, `_output.py` 3, `formats.md` 3), under
1.5x; tests +357 / -2 (`test_rof3_model_identity.py` 338, the CLI pins 17,
the successor chain 2), 1.55x the test estimate, mostly the review
regressions and the hand-written vectors.

## Boundary: what this phase does NOT establish

- No site accepts the canonical identity yet: steps files, sidecars,
  witnesses, measure corpora and generated plans still match the legacy
  digest only (ROF4; D7 for plans).
- Reports still carry only the legacy digest; issue 111 stays open (plan
  D3, ROF5 not scheduled).
- The identity covers the loaded model: a caller who starts from the YAML
  text needs GND's defaults, or the `--identity` output, to rebuild the
  document.
- T8 bounds the time near the input cap; it does not measure the cost a
  caller will pay at a verifier site (ROF4 decides those sites).
- The independence of T1 and `derive_vectors.py` is limited: they use the
  same Python JSON encoder; the hand-written P8 vectors are the check that
  does not.

## Open questions

| Row | Question | Owner / target |
|---|---|---|
| ROF3-O1 | `reference_model_digest` now refuses (with the walk's `TransitionLoadError`) a reference declaration mutated after loading to carry a non-string key, where it used to coerce it; no loadable model reaches this. Accept, or keep the old coercion for the legacy function only? | owner; before ROF4 |
| ROF3-O2 | The checker timing tests (10 s bounds) fail under parallel load on this machine; the gate and the main-branch run were taken under such load | not this milestone |
