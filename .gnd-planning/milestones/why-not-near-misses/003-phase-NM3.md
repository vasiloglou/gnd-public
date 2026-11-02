---
milestone: why-not-near-misses
station: phase-NM3
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-NM3
date: 2026-11-01
gate:
  command: "uv run pytest -q tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_public_why_not.py tests/test_why_not_anonymity.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_disclosure_mode.py tests/test_public_api.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_why_not_near_misses_public.py tests/test_why_not_repair_loop.py tests/test_public_built_inventory.py tests/test_conformance_payload.py"
  exit: 0
  output: "1014 passed, 16 deselected in 250.80s (0:04:10)"
  note: >-
    The plan section 9 NM3 row with the schema-inventory consumers the spec's
    Verification selection names. The docs gates, the installed-docs check,
    the post-review reruns and ruff are in the body; evidence/NM3/final-gate.txt
    holds each command and exit.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection at milestone close (plan section 9)"
  reason: "every changed path is covered by the selected consumer suites; the broad lane is outside NM3's impact closure"
evidence:
  - path: .gnd-planning/milestones/why-not-near-misses/notes/phase-NM3-spec.md
    sha256: 990074e417b0496961112bd9fc133cac377d2eb49b19bee6065ae9ee47a31e8c
  - path: .gnd-planning/milestones/why-not-near-misses/notes/phase-NM3-claude-review.md
    sha256: eb1c9638ba509d8f96a620409ba182a55edd82076fee1133d080b60cd4780b41
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM3/final-gate.txt
    sha256: bb4b30a23be87c31234f2619cf4c1991fafcc64ebcdcd18e000141afa1027f71
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM3/corpus-red.txt
    sha256: 2abdb752f0298b23e6c87f450839658712d39ace72cde7ef1ea8dc21fa2874c1
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM3/build_goldens.py
    sha256: 2f16a540a4d3dadba9965efeca341661d01525f0afe2851a1b1ab9896cb6cc82
  - path: src/gnd/witness/service.py
    sha256: b952b03e08df545d72c4de1c53828c1a0752647a5eebb1a770a1f46d19796d6b
  - path: src/gnd/witness/view.py
    sha256: e7361b120d32ae86155418d5954fb400d0981bb9e90eaf9bbee24678f4ad3d9f
  - path: src/gnd/why-not.schema.json
    sha256: 6a43565feb923eac97e89ad44a9c62268d92dca1ab454544b84517c189393756
  - path: src/gnd/api.py
    sha256: 9231ad93016ea96df4cc2dbd38c29f0a2f76d9f92e82e7abdc7095554e4f8c9a
  - path: src/gnd/disclosure.py
    sha256: 5dd9eb0d8ad4e6562c95c021739b399793659265d4324f28d0d74a45a9a584c5
  - path: src/gnd/examples/quoted_claims/spelling-gap.pop.json
    sha256: cdd55a51ae86a2c0a52811da589ef43cb78ac0b7721adef19e74c3d968d4f153
  - path: tests/test_why_not_near_misses_public.py
    sha256: 54249ec28144a4eb6ae3eca95081a94d4618403b5e786a31b78f84ecc9d7d94d
  - path: tests/test_why_not_repair_loop.py
    sha256: 0f7c457b90c6edb26e4e0bd6f9f69f15c7a54c0744013f9a3ce0b13dcb250fd7
  - path: tests/test_why_not_oracle.py
    sha256: e792c409d80056dcfd312cbfb069b980f71044f9e29d7c2b78e4bcd745c29f7f
  - path: tests/test_public_api.py
    sha256: 0ab1802ed4d4ab949b873841662abdd71f5f14e02d4866996367f887e7ad5828
  - path: tests/fixtures/why_not/cases.json
    sha256: a2f60f499fd2920d95a072100d8239c607be50aa5b366f24be71cd91927f6366
---

# Phase NM3 -- near-misses on the public why-not surface

Spec: [phase-NM3-spec.md](notes/phase-NM3-spec.md), r1, approved by the owner
on 2026-11-01 `(s3)` (SHA-256 `f836f123…e988` at approval). The rulings were
D1 (a), D2 (a), D3 (a), D4 (a) and D5 (a), with no spec review panel. As D1 (a)
requires, the 47 goldens, the g20 case and the tests were written before any
source change. The red run (75 failed, 115 passed) is
[corpus-red.txt](evidence/NM3/corpus-red.txt).

## What shipped

- **`gnd.witness.service`**: `why_not_result` asks the kernel for near-misses
  and stamps `schema_version: "gnd-why-not/2"`.
- **`gnd.witness.view`**: the redacted why-not view keeps `near_miss_count` and
  `near_miss_truncated` on atom blockers and replaces `near_misses` with
  `"redacted"`, at every descent depth. Non-atom blockers gain nothing.
- **`why-not.schema.json`** (D5 (a), replaced in place): `/2` title and const,
  `$defs/near_miss`, the three required atom-blocker fields, the exact count
  tie (D2 (a), six clauses) and `"redacted"` pinned in `redacted_clause`.
- **`gnd.api`** (D4 (a)): `DisclosureRefused` is exported and last in
  `__all__`; `disclosure.SURFACES` lists it as value-free.
- **Example**: `quoted_claims/spelling-gap.pop.json`, where the claim's work
  "Field Notes" is recorded as "FIELD NOTES". Byte copies of it, the model and
  the claim are in `tests/fixtures/why_not/spelling/` (T2 pins equality).
- **Fixtures**: 45 regenerated goldens plus the two g20 goldens; one RF5
  answer string.
- **Docs**: the normative section "Values spelled differently" in
  `docs/reference/why-not.md`, with blocker example fields and sentences in
  "Values in the answer", "Limits" and the schema line; the section "When the
  values are spelled differently" in `docs/how-to/repair-a-missing-claim.md`
  with every output regenerated; a release-note entry carrying the spec's
  migration line.

Size: 15 source lines and 226 schema lines (estimate about 90; F1); 285 test
lines added across the four test files; the docs as estimated.

## Gate output

See [final-gate.txt](evidence/NM3/final-gate.txt) for every command. Summary:

| Command | Result |
|---|---|
| the gate command above | 1014 passed, 16 deselected, exit 0 |
| `tests/test_documentation_tutorials.py tests/test_plan_app_docs.py` | 141 passed, exit 0 |
| `tools/run_tutorials.py` | 239 blocks passed, exit 0 |
| `tools/check_installed_docs.py --out <scratch>` | both wheel origins passed, exit 0 |
| after the review fixes: the two NM3 test files | 72 passed, exit 0 |
| after the review fixes: `zensical build --strict`, `check_docs.py site` | no issues; 12269 links checked; exit 0 |
| `ruff check` over the touched Python | all checks passed |

The RF6 query-policy suite passed unchanged, so no census successor row was
needed (spec "Successor evidence").

## Implementation findings

| ID | Finding |
|---|---|
| F1 | The schema took 226 lines, not about 90. The count tie and the atom rule are written once per `allOf` branch, and `redacted_clause` repeats the blocker shape. Same rules as the spec. |
| F2 | The spec's installed-docs command omits the required `--out`. The gate used `--out <scratch>/installed-docs` (review R2). |
| F3 | The first T7 draft could pass vacuously, because a negative's base could already be invalid under the old schema. Each negative now validates its unmutated base first. |
| F4 | The g20 example model differs from the WN2 `claims/` fixture model. The spelling copies (already in the spec) are what make the `<fx>` substitution work. |

## Adversarial review

One reviewer is one reviewer. A Claude subagent with read-only access and test
runs, given the diff and the spec but not the implementer's conclusions,
produced [phase-NM3-claude-review.md](notes/phase-NM3-claude-review.md). It
found no material defect and no redaction leak, and it independently checked
the docs claims against the kernel. Four low findings came back:

- R1: T8's untouched-rows check could not fail. Fixed: it now compares against
  copies taken before the edit. The fixed test passes.
- R2: the installed-docs command. Recorded as F2.
- R3: the migration-line wording. Fixed with the spec's words.
- R4: stale README status. Fixed.

Two info items: R5 is NM4's by H1, and R6 needs no change.

## Refactoring review

**None needed**, argued from what NM3 touched:

- **Schema repetition.** The count tie is spelled out per length (F1).
  JSON Schema has no arithmetic over array length, so the six clauses cannot be
  folded into one without dropping D2 (a).
- **The view.** It is one added key in a field allowlist and one conditional
  replacement, beside the existing `samples` replacement. A shared "redact these
  keys" helper would cover two lines.
- **Fixture copies.** The spelling copies duplicate three example files on
  purpose, and T2 keeps them identical. Moving the runner to read the packaged
  example directly would change WN2's `<fx>` contract for one case.

## Boundary -- what this phase does NOT establish

- **Matching is unchanged.** Near-misses are a report, not a fuzzy join.
- **Default limits.** The truncation flag is argued false at default limits,
  not measured over a large population. The 200,000-inspection ceiling has no
  real-population test.
- **Other blockers.** There are no near-misses on negated atoms, comparisons or
  heads (NM-D6).
- **Disclosure docs.** `disclosure.md`, the disclosure how-to and the pages
  that still say the API returns raw values are NM4's (H1, review R5).
- **Not run.** The broad default suite did not run.
- **One reviewer.** The review was one reviewer.

## Open questions

| ID | Question | Owner |
|---|---|---|
| NM3-Q1 | The spec's Verification-selection installed-docs command needs `--out` (F2). Correct the plan's §9 wording at close? | milestone close |

Carried: NM2-Q1 (doccheck every-mode, before NM4), NM2-Q2 (fidelity in three
modes, close), NM2-Q3 (RF1 golden recapture, later).

## Refuted premises

- **H1–H3** (spec, "Corrections to the plan").
- **The spec's installed-docs command** (F2).
