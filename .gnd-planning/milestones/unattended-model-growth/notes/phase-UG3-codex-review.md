# UG3 phase diff: Codex CLI review (one reviewer)

2026-11-09. Instrument: one reviewer in a different tool, the instrument UG1 and UG2 used:
`codex exec --sandbox read-only -c model_reasoning_effort=xhigh` (model `gpt-6.1-sol`, the
configured default), prompt on stdin, repository read-only. This is **one reviewer, not a
panel**. Subject: `git diff e881e521..2dea8a81` (part A `747c1ba5`, part B `2dea8a81`).

**This file was edited from the reviewer's output in one way:** the operator's absolute
worktree path was replaced by `<repo>/` (the review-and-record sanitization rule). Nothing
else in the "Reviewer output" section is changed.

**What the reviewer could not do.** Under the read-only sandbox it could not create temporary
files, so it ran 11 tests that need no writes and reproduced the rest in memory, with the
file-loading seam replaced for CLI cases. It did not run apply or finalize.

## Dispositions

Every finding was reproduced by the author before it was believed, and each fix has a
regression test shown failing on `2dea8a81` (in a throwaway worktree at that commit with the
new test files copied in). Triage follows `review-convergence.md`: blocking and hardening
findings on this phase's own deliverable are fixed in-phase.

| # | Reviewer class | Reproduced | Disposition | Regression test (failed on 2dea8a81) |
|---|---|---|---|---|
| 1 | blocking | yes: `--require-documents` with no document on a redacted unattended model exits 3 with a version 9 payload without `redaction`. The same rebuild already served MG5's `--document` refusal (an undeclared document on the same model), so the defect predates UG3; UG3 added a route to it | fixed: the walk's issues and warnings are built, projected and reference-wrapped by one API helper (`gnd.api._run_validate_with_documents`) that mirrors `_run_validate`; the post-hoc payload edit (`_with_warning`) is gone. Document read failures (66, 74, oversize 3) keep their MG5 error payload; see open question UG3-Q1 | `test_r1_a_redacted_model_keeps_its_projected_report` (strict and MG5 routes; the warning route passes on 2dea8a81 as a control). The reference-wrapped variant was not reproduced with a fixture; it runs through the same helper |
| 2 | blocking | yes: `TypeError: 'int' object is not iterable` for `provenance: {spans: 3}` on a plain model, with the flag alone; the same crash with `--document` predates UG3 | fixed: the flag alone walks only a model in the mode, and the span iterator is total over any shape (`_listed`) | `test_r2_the_flag_is_a_no_op_on_a_model_with_unchecked_span_metadata` |
| 3 | blocking | yes: v1 and v2 records with a source-document operation were accepted by `EvolutionRecord.model_validate` (the reviewer's recipe on the public legacy record) | fixed: one helper, `_refuse_source_documents_before_v3`, used by the proposal and the record validators | `test_r3_an_old_record_cannot_carry_the_locator` (dict and JSON readers, v1 and v2, with controls) |
| 4 | hardening | yes: `TypeError: cannot use 'list' as a dict key` | fixed: the digest's type is checked before the lookup | `test_r4_a_digest_of_the_wrong_type_counts_as_unchecked` |
| 5 | hardening | yes: with the annex declared twice, a modify of the first entry applied and one of the second was refused by `before` | fixed: a modify or delete needs exactly one entry with the digest; two are refused as ambiguous (`stable locator` family, 3). Contract updated. Whether U1 should refuse a duplicate declaration outright is open question UG3-Q2 | `test_r5_a_digest_declared_twice_is_an_ambiguous_target` |
| 6 | hardening | yes by reading: each add scanned the growing list (the reviewer measured 2, 65, 5,150 inspections for 1, 10, 100 adds) | fixed: the replay reads the declared digests once and keeps the set current; an add never rescans | `test_b16_a_run_of_adds_is_linear` (on 2dea8a81 it fails because the counted seams do not exist; the quadratic count is the reviewer's measurement) |

None rejected. The fixes were not re-reviewed; the gate in the records runs over them.

## Reviewer output (verbatim, path sanitized)

Found **3 blocking defects and 3 hardening issues**. No nits.

1. **Blocking — strict refusals emit invalid projected/wrapped JSON.** [checking.py:85](<repo>/src/gnd/commands/checking.py:85)

   Reproduction: take the corpus `rounds.orm.yaml`, set `redact: true` on its first fact type, and validate with `--require-documents --format json`, supplying no documents. It exits 3, but rebuilds a mechanical payload with `schema_version: 9` while dropping its redaction metadata. `report.schema.json` rejects it. A reference-bearing unattended model similarly emits version 12 without `report` or `reference_binding`.

   Minimal fix: incorporate document issues before projection and reference wrapping, preserving the selected report structure.

2. **Blocking — the strict flag crashes on valid models outside unattended mode.** [checking.py:124](<repo>/src/gnd/commands/checking.py:124)

   Reproduction: take corpus `plain.orm.yaml` and give its first object type `provenance: {spans: 3}`. This metadata is accepted outside unattended mode: ordinary validation exits 0. Adding only `--require-documents` invokes the span walker and raises `TypeError: 'int' object is not iterable`, instead of preserving bytes and exit.

   Minimal fix: trigger a require-only document walk only when `source.mode == "unattended"`.

3. **Blocking — the shared locator union widens frozen record graphs.** [models.py:295](<repo>/src/gnd/evolve/models.py:295), [models.py:645](<repo>/src/gnd/evolve/models.py:645)

   Reproduction: load `legacy-record.json` from `public-legacy-readers/closure.json.gz`; replace `operations` with the valid round-document add, clear linked conformance, set its derived outcome to 0/false, and recompute `record_identity_sha256`. With outer version **1 or 2**, both `EvolutionRecord.model_validate` and `model_validate_json` accept the `source-document` operation.

   The new version guard protects proposals only; records also use `EvolutionOperation`.

   Minimal fix: enforce the locator’s version restriction in record validation as well, with dict and JSON regression cases for both versions.

4. **Hardening — malformed digest shapes crash the new coverage API.** [_unattended.py:281](<repo>/src/gnd/model/_unattended.py:281)

   Reproduction: call `unattended_span_coverage` with one otherwise well-formed span whose `document_sha256` is `[]` or `{}`, and a supplied document. Dictionary membership raises `TypeError` before `_span_issue` validates the shape. The promised result is one unchecked span.

   Minimal fix: validate the span shape before using its digest as a dictionary key. This is a function-boundary defect; unattended CLI validation rejects that malformed model earlier.

5. **Hardening — duplicate digests make modification targets ambiguous.** [service.py:944](<repo>/src/gnd/evolve/service.py:944)

   Reproduction: append a second annex declaration with the same digest and label `second-annex.txt`. The before model validates. A modify with `before.label: annex.txt` changes the first match; one with `before.label: second-annex.txt` is refused with “declared before value does not match,” despite that exact entry existing. Target selection silently depends on list position.

   Minimal fix: require exactly one digest match for modify/delete and refuse ambiguity through the existing `stable locator` exit-3 family.

6. **Hardening — add replay is quadratic, and B16 misses it.** [service.py:934](<repo>/src/gnd/evolve/service.py:934), [test_evolve_source_document.py:433](<repo>/tests/test_evolve_source_document.py:433)

   Each add scans the growing declaration list. Instrumenting entry visits from the two-document corpus produced **2, 65, and 5,150 inspections** for 1, 10, and 100 adds: `2N + N(N−1)/2`. B16 passes because it counts helper calls, not work inside them.

   Minimal fix: maintain a digest lookup across adds and assert entry visits in the complexity test.

No files changed. **11 tests requiring no filesystem writes passed**, alongside read-only probes of the A corpus, B parsing/preview cases, and both parity baselines. Synthetic CLI reproductions used real in-memory validation results with the file-loading seam replaced. The full suite and apply/finalize were not run because the sandbox forbids temporary-file writes.

Claims checked and found true:

- A corpus counts, issue ordering, both warning text routes, and recorded parity.
- Identity combinations exit 64; missing/directory documents retain 66/74; undecodable documents retain 3.
- Public proposal readers reject the tested bad shapes, rename, and v1/v2 locators.
- Unique-target before comparisons, missing/non-list declaration refusals, reordered-candidate refusal, and declaration-only blast radius work.
- B9’s six golden comparisons pass; the v0.2.0 proposal reader rejects the new locator.
