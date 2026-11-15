---
milestone: literature-identity
station: "phase-LI0"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LI0
date: 2026-11-15
gates:
  - command: "uv run pytest -q tests/test_li0_witness_wire.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_witness_composition.py tests/test_public_why_not.py tests/test_public_replay_admission.py tests/test_public_optional_value_witness.py tests/test_public_v71_witness_corpus.py tests/test_why_not_kernel.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
  - command: "uv run ruff check"
    exit: 0
  - command: "python3 scripts/components_index.py changed --base ecd12986 --strict"
    exit: 0
evidence:
  - path: src/gnd/witness/io.py
    sha256: f61093c2f89fd1bada58d6223e802a9524b6b87d744a8f1eadf081796c5e514d
  - path: src/gnd/witness/producer.py
    sha256: 05d8f0ed67ec618017e9dd3cb57b42cc528c5e31b8cafd925ee744353ea4ba30
  - path: src/gnd/witness/service.py
    sha256: 0b187b0c884d015e9afadc74c1f7c3f246a3f5fd68ca35c2b8188b13adbef795
  - path: tests/test_li0_witness_wire.py
    sha256: a034fee28e16c72868294551eedde22660b1b15eaad09ba60a6c198b0b73bff3
  - path: tests/fixtures/li0/golden.json
    sha256: 2917808e40c884a3b392e0f82af3ff3df4e12028b2a5ce7fd263e884e686ee5e
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI0-spec.md
    sha256: 594df385e3cf4677fa80cd65000efa7d682cd12256e5f38ec1a192468b858a38
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI0-codex-review.md
    sha256: 97359e467385ad413f90414536e690f73981c4184b3d2ae5ce69a39f70e84173
---

# Claim

`gnd witness` and `gnd why-not` exit 0, and `gnd replay` exits 0 on the
resulting witnesses, for a valid version-1 model and for models without
`model_id` at versions 1 and 2. They previously exited 3. The certificate golden and all
228 model-identity goldens generated at `ecd12986` are unchanged. All five
ledger gates exited 0.

## Gate output (verbatim)

    == direct (head 1beae563)
    17 passed in 17.47s
    exit 0
    == consumers (head dc4ce588; src unchanged since)
    474 passed, 11 deselected in 211.65s (0:03:31)
    exit 0
    == guards (head 1beae563)
    679 passed, 2 deselected in 87.25s (0:01:27)
    exit 0
    == ruff (head 1beae563)
    All checks passed!
    exit 0
    == components (head 1beae563)
    changed against ecd12986 (ecd1298): 32 file(s) differ; 0 to fix, 0 warning(s), 3 to reread
    exit 0

    == red-first (176355e8, src identical to ecd12986)
    12 failed, 4 passed in 13.92s

## Verification-selection ledger

| Obligation | Disposition | Result |
|---|---|---|
| W1–W3, T1–T11 and the D1 pin | run | 17 passed, exit 0 |
| Witness, replay and why-not consumers | run at `dc4ce588`; inherited for `1beae563` | 474 passed, exit 0. `git diff --quiet dc4ce588 -- src` held, because the later commit changed tests only |
| Structure guards | run | 679 passed, exit 0 |
| Lint | run | exit 0 |
| Component index | run | exit 0. The three `reread:` entries were re-read and remain accurate (spec finding 5) |
| Soufflé and Lean exports | inherit | No export module changed. Both parse raw bytes |
| Evidence, census, native and provider lanes | cadence | Milestone-close lane. Not run |

## Review

- **Reviewer.** One reviewer, Codex `gpt-6-sol` at xhigh, read-only, prompt
  on stdin. **One reviewer is one reviewer.**
- **What it could not do.** It could not run pytest in its sandbox. Its
  checks were in-memory runs and reading.
- **Findings.** No behavioral counterexample. Four points about the test
  evidence, triaged in the [review note](notes/phase-LI0-codex-review.md):
  - **R3 (blocking).** Fixed. The hardened T8 fails under the reviewer's
    mutation.
  - **R2 (hardening).** Fixed with a pin.
  - **R1.** No change: the passing tests are controls by design.
  - **R4.** Carried below.

## Refactoring review

**None executed.** That is argued from what the phase touched:

- **Size.** The phase added one 8-line function beside `population_wire`,
  its existing sibling projection, and changed two call sites to use it.
- **The two omission homes.** `Model`'s hooks and `model_wire` now both
  remove empty defaults. That split is deliberate (D1): moving the omission
  into `Model` would move 54 of 228 pinned identities, as the liveness
  experiment measured. So the split is a design boundary, not duplication.

**Seen but deferred.** `gnd.documents.Model` omits its empty defaults by two
mechanisms in one class:

- a `model_dump` override for `reference_populations`;
- a `model_serializer` for `includes` and `fact_type_constraints`.

This is an open question below. It is not in this phase.

## Boundary -- what this result did NOT establish

- **T7 is narrower than the spec wrote** (spec finding 1). The certificate
  golden covers the LI0 version-2 fixture only. The composition and v7.1
  corpus certificates are covered by their own suites. The argument that
  their bytes cannot move rests on the binding being built from the original
  model, and no new byte golden stands behind it.
- **Baseline consumer lane.** The 474-test lane run before the change
  overlapped test authoring, so it is not a clean pre-change measurement
  (spec finding 6). The red-first evidence is the `176355e8` run.
- **YAML provenance dates.** The JSON hop still turns YAML-authored
  provenance dates into strings inside witness intake, as before. This phase
  records that and does not change it.
- **Out of scope.** Include-bearing models in witness, temporal models and
  external consumers are outside this phase.
- **Further authority.** No merge, publication, release or certification is
  authorized. One reviewer is one reviewer.

## Open questions

- **Model serializer tangle.** `Model` uses two serializer mechanisms for one
  omission policy (`model_dump` override and `model_serializer`). Merging
  them must preserve every identity in `tests/fixtures/li0/golden.json`.
  Target: a code-refactoring successor milestone. Owner: unassigned.
