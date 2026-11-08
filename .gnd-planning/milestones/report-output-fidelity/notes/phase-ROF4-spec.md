# Phase ROF4: accept both model identities at every matching site (issue 111)

## 1. Status

**r1 approved 2026-11-08** (owner: "Approve, author corpus", answering
"Approve ROF4 D1-D6 as proposed, so I author the pin corpus?"). D1-D6 ruled
as proposed. The corpus is authored and red (section 12). Next: the owner's
go-ahead to implement. No source code is written. `auto=false`.

## 2. Provenance

- Plan r3 (approved 2026-11-07, [plan-gate record](../001-plan.md)): §1 "111,
  consumers" (the site classification), §2 "compatibility and migration"
  items 1-10, §4 ROF4 (C1-C4), §6 risks, §9 ROF4 row, §10 D3 (no emission;
  re-ask after ROF4) and D7 (generated plans keep the legacy constant, ruled
  (a)).
- ROF3 record [004-phase-ROF3.md](../004-phase-ROF3.md): `model_identity`,
  `ModelIdentityError`, the normative subsection, `gnd validate --identity`;
  ROF3-O1 ruled (accept the refusal); ROF3-O2 (timing tests under load, not
  this milestone).
- The owner's go-ahead for this spec: "Write ROF4 spec" (2026-11-08),
  answering "Write the ROF4 spec now?".
- Base: `origin/main` at `6058c674` (ROF1-ROF3 merged), branch
  `claude/rof4-accept-identities`.
- Site probes below are at `6058c674`, read-only. No review has read these
  bytes. Marks: `(o)` an owner decision.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan ROF4-C1 | one helper `model_identity_matches(supplied, model)` that returns which identity matched or `None`; every "match a supplied identity" site calls it; exact-coherence and copy sites do not; a source scan pins the classification | M1, M2; T1, T9 |
| plan ROF4-C2 | per matching site: legacy pin accepted, canonical pin accepted, wrong pin refused naming the expected values | T2-T6; D2 (message wording) |
| plan ROF4-C2 | witness replay: whole-binding equality with only the model field widened; a wrong candidate digest still refuses | T5 |
| plan ROF4-C2 | measure: a corpus mixing both spellings of one model is accepted; the report keeps the legacy spelling | T6 |
| plan ROF4-C2 | reference-bearing model: only its version-1 identity | T7 |
| plan ROF4-C2 | generated Pyrel plan: per D7 (keeps the legacy constant; a canonical pin is refused by the plan) | T8; M4 limitation text |
| plan ROF4-C3 | the 15 shipped `src/gnd/examples/approvals/**` pins verify (executable); the 140 fixture files pass the full suite; the 12 `.gnd-planning` evidence files are byte-preserved (`git diff` empty) | T10; V5; V7 |
| plan ROF4-C4 | `docs/reference/formats.md`, `docs/guides/data-and-transitions.md`, the `steps.schema.json` description (both copies) and the `representation-format.md` digest table say "either identity" | M4; T11 |
| plan §2 item 4 | one shipped example pinned with the canonical identity, exercised by the package's own tests | M3; T10 |
| plan §2 item 5 | historical records are not edited | V7 |
| plan §2 item 6 | the legacy identity is not retired | out of scope |
| plan §2 item 7 | in-process markers (`Population._validated_model_digest`) keep the legacy function | M2 (not a site); T9 lists it |
| plan §2 item 8 | sites differ by contract; the witness replay widens only `model_digest`; measure normalizes before counting and emits the legacy spelling | M2; T5, T6, T9 |
| plan §2 item 10 | a model the canonical identity cannot represent matches by legacy only and is never reported as a mismatch for that reason | M1; T7 |
| plan rule 1 (frozen) | no existing report's bytes change; no recorded digest changes meaning; a verifier accepts more, never less | D2; T12; V5 |
| plan rule 2 (measure) | each site's reachability probed, not argued; regressions observed red first | section 6 probes; V2 red run |
| plan rule 3 (one home) | consumers call the helper, never `model_identity` directly or a second comparison | M1; T1 |
| plan rule 4 (one walk over N consumers) | the N sites are served by one helper, not N edits of their own | M1, M2; T1 |
| plan §6 risks | a recorded digest stops verifying; accept-both widens an exact binding; the walk refuses a model legacy accepted | T10, V5; T1, T5; T7 |
| plan §9 ROF4 row | new ROF4 tests + `tests/test_public_transition_contract.py tests/test_coverage_payload.py tests/test_witness_composition.py tests/test_public_v71_witness_corpus.py tests/test_public_measure_corpus.py` and the pyrel-plan suites | V2 |
| plan §8 | ROF4 changes security-relevant comparison code: the diff review is the owner's independent reviewer, not a self-review | D6 |
| plan §10 D3 | "re-ask after ROF4 has measured the cost" | the ROF4 record re-asks D3 with the measured cost (R1) |
| ROF3 record | `model_identity` is linear and about 4x the legacy digest (T8); no caller adopted it | M1 laziness; T13 |
| D7 (ruled (a)) | generated plans stay byte-identical | T8 (24 plan fixtures unchanged in V5) |

## 4. The standing rules, bound to this phase

| Rule | Binding |
|---|---|
| 1 Totality | `model_identity_matches` answers every input: a match name or `None`, never an exception. A non-string `supplied`, a malformed string, a model whose canonical identity raises `ModelIdentityError`: `None` unless the legacy identity matches. T7. |
| 2 Algorithm bound | the legacy comparison runs first; the canonical identity is computed only when the legacy one did not match. A legacy pin costs what it costs today; T13 pins that `model_identity` is not called on that path. |
| 3 Validation order | each site keeps its order: the schema/shape check, then the identity comparison, then what followed it. Only the comparison's predicate changes. |
| 4 One walk | one helper in `values.py`; seven sites call it (M2). |
| 5 One home | the identity definition stays in the ROF3 subsection; the acceptance rule ("either identity") is stated once in `representation-format.md` (M4), and the other docs cite it. |
| 6 Measure | the site list was re-probed at `6058c674` (section 6); line numbers moved since the plan's `12daa5b7`, the classification did not. |
| plan 0.1 Frozen | every existing payload, report and message is byte-identical (D2 proposes keeping the refusal messages exactly as they are); generated plans are byte-identical (D7). The only changed bytes are documentation, one schema description string (two copies) and one new shipped example (section 11). |
| Failure classes | *A widened exact binding*: T1's source scan pins the exact-coherence and copy sites unchanged; T5 pins that the witness widening stops at one field. *A branch with no failing case*: every site has a wrong-pin case (T2-T6). *A refusal turned into a mismatch*: T7. |

## 5. Goal

A supplied model identity equal to either the model's legacy identity or its
canonical identity is accepted at each of the seven matching sites (section 6)
with the exit code and payload a legacy pin gets today (for example, `gnd
check --steps` exits 0 on a passing walk); a supplied identity equal to
neither is refused exactly as today (same rule id, same message bytes under
D2(a), same exit). The exact-coherence and copy sites, the in-process marker,
generated plans and every existing report are byte-identical. A reference-
bearing model has one identity (version 1), so its sites change nothing.

## 6. Design

**Probes (2026-11-08, at `6058c674`, read-only).** The plan's classification,
re-located:

| # | Site (function) | Supplied value comes from | Today | Class |
|---|---|---|---|---|
| S1 | `transition.verify_digests` (`transition.py:252`) | a caller-authored `steps.json` | `!= transition_model_identity(model)`; refuses `transition:model-digest-mismatch` with "steps say X, model is Y" | **accept both** |
| S2 | `admission_validation.validate_reference_transport` (`:59`) | a reference wrapper GND wrote (session replay) | `!= reference_model_digest(model)`; "reference wrapper binding differs" | **accept both** |
| S3 | `admission_validation.validate_admission_payload` (`:130`) | an admission report GND wrote | `!= transition_model_identity(model)`; "model identity differs" | **accept both** |
| S4 | `coverage._report_binding` (`:689`) | a check/verify report GND wrote | `!= census_model_digest` (a string passed down from `build_coverage`, `:960`); `coverage:model-digest-mismatch` | **accept both** |
| S5 | `measure/service._cmd_measure` (`:170`) | a `gnd synth` sidecar | `!= validated_model_sha256(model)`, **bare hex, no `sha256:` prefix**; "C6 sidecar binding failed …" exit 3 | **accept both, bare spelling** |
| S6 | `witness/kernel.replay_witness` (`:313`) | a witness certificate's `binding` | whole dict `!= identity(model, candidate, refs)`; reason `binding-stale`, exit 3 | **accept both, `model_digest` field only** |
| S7 | `measure/report.build_measurement_report` (`:218`) | the sidecars S5 already admitted | counts distinct `sidecar.model_digest` strings; refuses more than one; emits that string (`:308`) | **normalize to legacy, then count** |
| X1 | `assurance/transport.py:115` | a receipt vs. the report it authenticates | exact | exact coherence, unchanged |
| X2 | `model/__init__.py:627` | an in-process bound context | exact | exact coherence, unchanged |
| C1 | `export/souffle_runtime.py:513`, `witness/io.py:282`, `export/lean.py:926`, `export/souffle.py:360`, `witness/producer.py:202` | — | copy or produce | unchanged |
| G1 | `export/pyrel_rules.py:1609`, `:2212` | a `steps.json`, inside generated code | `!= MODEL_DIGEST` (legacy constant) | D7: unchanged |
| P1 | `population.py:215-220, 260` | in-process marker | legacy | unchanged (plan §2 item 7) |

Probe of S1 today: `plan-draft-2.steps.json` (legacy pin
`sha256:278b20b2…`) exits 0; the same bytes with the approvals model's
version-2 identity (`sha256:1ef9d764…`, from `gnd validate --identity`)
print `ERROR at $.model_digest: model_digest does not match this model:
steps say sha256:1ef9d764…, model is sha256:278b20b2…
[transition:model-digest-mismatch]`. The legacy digest appears in 15 shipped
files: 14 `steps.json` and `recordings/TASK.md`.

Observations that shape the design:

- **S2-S7 read artifacts GND itself writes, and every one carries the legacy
  identity** (D3: no emission). A canonical value reaches them only through
  an artifact a caller rewrote or produced outside GND. The plan includes
  them by approved classification; the cost is a few lines each and a
  canonical walk only on the path that refuses today. S1 is the site with a
  caller-authored pin.
- For a **reference-bearing** model, `transition_model_identity`,
  `reference_model_digest` and `validated_model_sha256` already return the
  version-1 canonical identity (with and without the prefix), so the legacy
  and canonical identity are the same string; the helper accepts exactly that
  one value.
- No existing refusal message is pinned only in source: S1's message is in 3
  committed fixtures (`tests/fixtures/coverage/refused/evidence/transition-refused.json`
  and the ROF2 corpus's `transition-refused.json` and `.txt`, an approved
  answer); S5's is quoted in an RF5 predecessor file under `.gnd-planning`.
  Changing a message moves them (D2).
- The witness kernel's docstring: "Only intake/identity and the immutable
  wire contract are shared with production." The helper is identity, so the
  kernel may call it; the kernel's inference-import boundary test
  (`tests/test_public_v72_semantic_owners.py`) does not cover `values`.
- RF5 pins `replay_witness`'s body (one row in the compiled-snapshot
  `source-successors.json`); the other six functions have no RF5 row. The
  RF6 query policy and the component index move as in ROF3 (census before
  code).

**Reuse table** (searched 2026-11-08: `components_index.py search "model
identity match"`, `"digest comparison"`, plus `git grep` for every caller of
the four digest functions, section 6 table).

| Capability | Found | Decision |
|---|---|---|
| the canonical identity | `values.model_identity` (ROF3) | **reuse** |
| the legacy identity | `values._model_digest`, `transition.transition_model_identity` | **reuse** |
| a "match against either" predicate | nothing | **new**, `values.model_identity_matches` (one home, plan rule 3) |

**M1. `src/gnd/values.py`, about 45 lines.**

```python
IdentityMatch = Literal["legacy-repr", "canonical-v1", "canonical-v2"]

def model_identity_matches(
    supplied: object, model: Model, *, prefixed: bool = True
) -> IdentityMatch | None:
    """Which identity of ``model`` ``supplied`` names, or None.

    prefixed=True compares "sha256:<hex>" spellings (steps, reports,
    certificates); prefixed=False compares bare hex (measure sidecars).
    Order: the legacy identity first (no canonical walk on that path); then,
    for a model without reference populations, the version-2 identity. A
    reference-bearing model's legacy value IS its version-1 identity, so it
    has exactly one accepted value and a match is "canonical-v1".
    ModelIdentityError while computing version 2 means "not this identity":
    the result is None, never an exception.
    """

def accepted_model_identities(model: Model, *, prefixed: bool = True) -> tuple[str, ...]:
    """The accepted values, legacy first; omits version 2 when it is
    unrepresentable. For messages and tests only (D2 (b) would use it)."""
```

A non-`str` `supplied` returns `None` without computing anything.

**M2. The seven sites, about 45 lines in all.** Each replaces only its
comparison predicate:

- S1: `if model_identity_matches(supplied["model_digest"], model) is None:`
  then the existing `_refuse(…)`, message per D2.
- S2: `model_identity_matches(payload["model_digest"], model) is None or
  payload["reference_binding"] != binding`.
- S3: `if model_identity_matches(inner["model_digest"], model) is None:`.
- S4: `_report_binding` receives the model (a keyword, `census_model`), not
  only the digest string; `read_evidence_document` passes it through. The
  string `census_model_digest` stays for the message and for
  `build_coverage`'s output (`:1073`, legacy, unchanged).
- S5: `model_identity_matches(sidecar.model_digest, model, prefixed=False)`.
- S6: compare the binding without `model_digest` to `identity(…)` without
  `model_digest` (whole-dict equality otherwise unchanged, key set
  included), and the `model_digest` field through the helper.
- S7: each sidecar's digest is mapped to the model's legacy bare digest when
  the helper accepts it, otherwise kept as written; then the existing
  distinct count and refusal run; the emitted `model_digest` is the legacy
  bare digest (unchanged bytes for every existing corpus).

**M3. One shipped example, about 40 lines of JSON and 2 README lines.**
`src/gnd/examples/approvals/plan-draft-2.canonical.steps.json`: the bytes of
`plan-draft-2.steps.json` with `model_digest` replaced by the approvals
model's version-2 identity, and one README row and command line: `gnd check
model.orm.yaml --pre state.pop.yaml --steps plan-draft-2.canonical.steps.json
# exit 0`. The 15 existing shipped pins are not edited.

**M4. Documentation, about 15 lines.**

- `representation-format.md`: the "Three digests, three bases" table's
  `model_digest` row and the sentence after it say that a supplied
  `model_digest` may be either the legacy value or the canonical model
  identity, and that a generated Pyrel plan accepts only the legacy value
  (D7). This is the acceptance rule's one home.
- `steps.schema.json` `model_digest` description (both copies, held identical
  by `tests/test_schema_sync.py`): "either … or …", citing the subsection.
- `docs/reference/formats.md`, `docs/guides/data-and-transitions.md`: one
  sentence each, citing the subsection; the guide adds `gnd validate MODEL
  --identity` as the second source of a pin.
- `docs/agents/plans.md` (the generated-plan page): one sentence stating the
  D7 limitation.

Estimated: about 90 source lines (M1 45, M2 45), 15 doc lines, the example,
and about 300 test lines plus the corpus. The plan's estimate was 150 source
and 300 test lines.

### Normative order and home

The identity: ROF3's subsection. The acceptance rule: the
`representation-format.md` digest table (M4). Its implementation:
`values.model_identity_matches`. Nothing else decides acceptance.

## 7. Decisions

| D | Question | Readings and cost |
|---|---|---|
| D1 | Approval instrument | **corpus of pins** (proposed): for the approvals model (plain) and a reference-bearing model, a directory of supplied artifacts per site (a `steps.json`, a sidecar, a witness certificate, an admission payload, a coverage source) in three spellings (legacy, canonical, wrong), with the expected exit and refusal text split out in `expected/`; the owner approves by reading which are accepted. Alternative: prose only. An exit-code contract is a shape the protocol defaults to corpus-first. **Ruled 2026-11-08: as proposed.** |
| D2 | The refusal message on a wrong pin | (a) **unchanged bytes** (proposed): S1 still says "steps say X, model is Y" with Y the legacy value; plan rule 1 holds and no fixture moves. The departure: C2's "a message naming the expected values" is met only for the legacy value; a caller pinning the canonical identity reads it from `gnd validate --identity`. (b) **name both**: "… model is Y (or its canonical identity Z)" for S1, S4, S5; moves 3 fixtures (one an approved ROF2 corpus answer, which returns it to the owner) and the bytes of every existing refusal payload of those kinds, which rule 1 forbids. Exit codes are the same either way. **Ruled 2026-11-08: as proposed.** |
| D3 | The helper's return value | (a) **a name** (`"legacy-repr"`, `"canonical-v1"`, `"canonical-v2"`) (proposed): the plan's "returns which version matched"; no caller prints it in this phase (D2 (a)), tests read it. (b) a bool: simpler, loses "which matched". No exit-code difference. **Ruled 2026-11-08: as proposed.** |
| D4 | The shipped example | (a) **`plan-draft-2.canonical.steps.json`** (proposed): a passing walk, exit 0, the smallest change to the example set. (b) a canonical twin of `approve-41.steps.json` (exit 1, the frame catch): shows acceptance less plainly, since the walk then fails for another reason. **Ruled 2026-11-08: as proposed.** |
| D5 | Widening S2-S7, whose inputs GND writes with the legacy identity | (a) **widen all seven, as plan §1 classifies** (proposed): one rule for every matching site, and ROF5 (if D3 is re-ruled "emit") then needs no verifier change. (b) widen S1 only: smaller diff; a hand-edited canonical value in a report, sidecar or certificate is refused, which plan C1 says it must not be. Flagged because the cost of (a) buys nothing observable until a canonical value is emitted. **Ruled 2026-11-08: as proposed.** |
| D6 | Review | none over the spec bytes (proposed, as ROF1-ROF3); the diff gets the owner's independent reviewer (Codex), as plan §8 asks for ROF4. **Ruled 2026-11-08: as proposed.** |

## 8. Tests

`tests/test_rof4_accept_identities.py` unless named. "Legacy", "canonical"
and "wrong" are the three spellings of the supplied identity.

| T | Case | Expected |
|---|---|---|
| T1 | source scan over `src/gnd` | S1-S6 call `model_identity_matches(`; S7 calls it and emits the legacy digest; X1, X2, C1, G1, P1 do not call it and keep their comparison text; no other function both computes a model digest and compares it (a pinned table of functions, by AST) |
| T2 | S1: `gnd check --pre --steps` on the approvals model with each spelling | legacy and canonical: exit 0, the `--format json` payloads byte-identical to each other (the payload carries the computed legacy digest, not the supplied one); wrong: exit 3, `transition:model-digest-mismatch`, message bytes per D2 |
| T3 | S2, S3: session-replay admission over a recorded payload, model_digest in each spelling | legacy, canonical: admitted; wrong: `AdmissionValidationError` with today's message |
| T4 | S4: `gnd coverage` with a check report source whose `model_digest` is each spelling | legacy, canonical: model-bound, exit as today; wrong: `coverage:model-digest-mismatch` |
| T5 | S6: `replay_witness` with the certificate's `binding.model_digest` in each spelling; and canonical model digest with a wrong `candidate_digest`; and with a missing or extra binding key | legacy, canonical: replay result as today; wrong model: `binding-stale`; canonical model + wrong candidate: `binding-stale`; key set changed: refused as today |
| T6 | S5, S7: `gnd measure` over a corpus whose sidecars carry legacy, canonical (bare) and mixed spellings; and one wrong; and one `sha256:`-prefixed canonical value | legacy, canonical, mixed: exit 0, payload byte-identical to the all-legacy run (`model_digest` legacy); wrong: exit 3, today's C6 message; prefixed in a bare site: exit 3 |
| T7 | reference-bearing model (ROF3 corpus `reference`) at S1 and the helper; the ROF3 `surrogate` model at the helper | reference: its one value matches as `canonical-v1`; a version-2-style value computed for the model with its references dropped is refused; surrogate: legacy matches, any other value is `None`, no exception |
| T8 | a generated Pyrel plan (`tests/test_pyrel_rules_plans.py` successor) run on `plan-draft-2.canonical.steps.json` | refused `transition:model-digest-mismatch` (D7), while `gnd check` exits 0 on the same file; the plan's bytes are unchanged |
| T9 | helper unit cases | non-string, empty, uppercase hex, prefix/bare mismatch, each spelling: the right name or `None`; never raises |
| T10 | shipped pins: the 14 `steps.json` files under `src/gnd/examples/approvals/` that pin the legacy digest (the plan's 15 files are these and `recordings/TASK.md`, which quotes it), and the new example, checked against the approvals model | none is refused `transition:model-digest-mismatch`; each exits as at the base (`plan-draft-2` 0, `plan-draft-1` 1, `approve-41` with its post 1, the recordings as at the base); the new example exits 0; `TASK.md` is byte-preserved |
| T11 | docs | the `representation-format.md` table row, both schema copies (identical), `formats.md`, the guide and `plans.md` carry the sentence once |
| T12 | frozen bytes | the existing refusal fixtures (S1's three, `public-binding-reports/answers.json`, `test_measure_offline.py`'s C6 case) pass unchanged; every generated-plan fixture unchanged |
| T13 | laziness | with `values.model_identity` patched to raise, every legacy-spelling case of T2-T6 still accepts |

Every declared branch has a case that can fail it: accept legacy, accept
canonical, refuse wrong at each of S1-S6 (T2-T6); S7 normalization (T6);
one-field widening (T5); reference-bearing single value (T7); unrepresentable
canonical (T7); D7 divergence (T8); laziness (T13); classification (T1).

## 9. Out of scope for this phase

Emitting the canonical identity in any report (ROF5, D3 "not now"; the record
re-asks); changing generated Pyrel plans (D7); retiring the legacy identity;
the exact-coherence, copy and in-process sites; raw-file digests (`batch.py`,
conformance currency, codegen manifest); issue 112.

## 10. Size

Estimate: about 90 source lines, 15 doc lines, one example file, about 300
test lines plus the corpus. Stop at 1.5x (135 source lines).

## 11. Approval instrument

Proposed (D1): `tests/fixtures/rof4-accept-identities/`, entry point
`README.md` (the stories: which site, which artifact, which spelling), answers
in `expected/` (per case: accepted or refused, exit, refusal text), runner
`tests/test_rof4_accept_identities.py`, red first (every canonical-spelling
case refused today). The supplied artifacts are copies of committed ones with
only `model_digest` rewritten; the canonical values come from `gnd validate
--identity`, recorded in `expected/`.

**Changed bytes, listed before code (rule 1):** the five doc files of M4; the
`steps.schema.json` description in its two copies (and any pin of their
bytes, found by the census); the new example file and the approvals README;
the RF5 row for `replay_witness`; RF6 query and dynamic-query successors if
the helper adds counted model reads; the component index entries for
`values`, `transition`, `admission_validation`, `coverage`, `measure` and
`witness`. Under D2 (a), no refusal message, report, payload or generated
plan moves. A stub-and-diff census (as ROF2) confirms this list before code.

## 12. The corpus as authored (2026-11-08)

`tests/fixtures/rof4-accept-identities/`: four copied models (approvals, the
ROF3 `reference-operations` model, the `public-binding-reports`
`nonstructured` model, the shipped `release_governance/dependencies` model),
one artifact per site pinned with the legacy identity, 30 cases in
`expected/cases.json` and the identities in `expected/identities.json`.
Choices made while authoring, within the approved design:

- S4 uses the committed `current-v5-valid` check report, not a fresh
  approvals report: `gnd coverage` on a fresh `gnd check --format json`
  report of the approvals model crashes today (`TypeError` in
  `_index_snapshot`, `derivations: null`). Not this phase; a follow-up.
- S1 on the reference model runs with `--format json`: the text form of
  `gnd check --pre --steps` on a reference-bearing model crashes today
  (`KeyError: 'transition'` in `_cmd_transition`). Not this phase; a
  follow-up.
- S6 uses the `dependencies` model: the approvals model has no derivation to
  witness. A changed binding key set is refused by the certificate shape
  (`input-invalid`) before the binding comparison, today and after.
- S5/S7 commit a `gnd synth --seed 7 --seeds 2` corpus of the approvals model
  (about 8 KB).
- T8 is marked `pyrel_oracle` (it needs the DuckDB runtime, absent on this
  machine); `test_t12_the_generated_plan_keeps_the_legacy_constant` checks the
  generated constant in the default lane.
- T13 patches `values.model_identity` to count and refuse; it also asserts
  the canonical case reaches the patch, so the test cannot pass vacuously.
- T11 looks for the words "either identity" in the six documents, and in the
  `model_digest` row of the representation-format digest table.

Red run at `c08ac5f7` plus the corpus: 22 failed, 55 passed, 1 deselected
(T8). The 22: the canonical case at S1, S3, S4, S5, S6 and the S7 mixed
corpus (each refused exactly as a wrong pin is today); the four helper tests
(the helper does not exist); two T1 scans; T13; the two tests of the new
example; seven T11 documentation tests. Every legacy, wrong, reference and
frozen-bytes case passes now.

## Verification ledger

| # | Obligation | Disposition | Command or evidence |
|---|---|---|---|
| V1 | base record | run before any edit | full default suite at `6058c674` (sharded, clean tree); the failure set is the base |
| V2 | focused gate | run | `.venv/bin/python -m pytest -q tests/test_rof4_accept_identities.py tests/test_public_transition_contract.py tests/test_coverage_payload.py tests/test_witness_composition.py tests/test_public_v71_witness_corpus.py tests/test_public_measure_corpus.py tests/test_measure_offline.py tests/test_pyrel_rules_plans.py tests/test_public_binding_reports.py tests/test_schema_sync.py tests/test_packaged_skills.py tests/test_rof3_model_identity.py tests/test_rof2_projected_text.py` plus the RF5/RF6 guard suites and `tests/test_public_v72_semantic_owners.py` |
| V3 | lint | run | `ruff check` on touched files |
| V4 | layers and homes | run | `tools/gnd_layers.json` import check (the witness and measure homes now import `values.model_identity_matches`) and the RF structure suites |
| V5 | full default suite vs base | run (sharded, clean tree, no edits during the run) | failure set ⊆ V1's; covers the 140 fixture files and the 24 plan fixtures (C3) |
| V6 | component index | at record time | `scripts/components_index.py changed --base 6058c674 --strict` |
| V7 | historical evidence | at record time | `git diff --stat 6058c674 -- .gnd-planning/milestones/*/evidence` shows only this milestone's new ROF4 evidence |
| R1 | D3 re-ask | in the record | the measured cost of emission (report versions per ladder, fixtures that would move) and the question to the owner |
