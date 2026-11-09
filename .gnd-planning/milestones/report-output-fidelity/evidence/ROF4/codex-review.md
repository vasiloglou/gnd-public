# Diff review of ROF4 (Codex), retained

- Instrument: one reviewer in a different tool (plan section 8: ROF4 changes security-relevant comparison code, so the diff review is the owner's independent reviewer). One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -o <scratch>/codex-final.md -`, prompt on stdin (`review-prompt.txt` beside this file), exit 0.
- Reviewed bytes: commit d44ba67a, `git diff 20cc7654 d44ba67a`.
- The reviewer could not run the suite; its conclusions are by reading (it says so).
- Retained: the reviewer's final answer, unedited. Its tool-call transcript (which contains the operator's absolute paths) is not retained.
- Disposition `block`, 7 findings. Triage: the ROF4 record, section "Review".

## Reviewer output (verbatim)

DISPOSITION: block

ID: P1  
SEVERITY: blocking  
LOCATION: src/gnd/values.py:320  
QUOTE: `if supplied == prefix + _model_digest(model):`  
PROBLEM: `isinstance(supplied, str)` admits string subclasses, and this comparison calls their `__eq__`. A subclass containing a wrong digest whose `__eq__` returns `True` is accepted as `legacy-repr`; one whose `__eq__` raises violates the helper’s totality promise. The canonical comparison has the same flaw.  
FIX: Require `type(supplied) is str` before either comparison.

ID: P2  
SEVERITY: blocking  
LOCATION: src/gnd/api.py:467  
QUOTE: `document = {**document, "model_digest": transition_module.transition_model_identity(model)}`  
PROBLEM: For the new canonical steps example, the emitted `transition.model_digest` becomes the legacy digest, although `report.schema.json:1508` defines that field as **“As SUPPLIED by the steps document.”** `verify_digests` also rewrites this value in later refusal payloads. The top-level report digest is already computed as legacy at `api.py:429`; changing the supplied field creates a false provenance claim.  
FIX: Remove both rewrites of the supplied digest. Keep the top-level report digest legacy and retain the actual steps pin in `transition.model_digest` and refusals.

ID: P3  
SEVERITY: hardening  
LOCATION: src/gnd/measure/report.py:221  
QUOTE: `legacy_digest = model_digest(model)`  
PROBLEM: An all-legacy measure corpus previously computed the model digest once in `_cmd_measure`. It now computes it there once and twice more here: this call and `model_identity_matches` inside the comprehension. Thus the stated legacy-path cost bound is false on a model-size-dependent operation. T13 watches only `model_identity`, so it cannot detect this.  
FIX: Carry S5’s admitted match and legacy digest into report construction so the all-legacy path does not rehash the model.

ID: P4  
SEVERITY: completeness  
LOCATION: tests/test_rof4_accept_identities.py:169  
QUOTE: `row.pop("sidecar_sha256")`  
PROBLEM: The canonical and legacy cases rewrite different sidecar file bytes, so their report payloads cannot be byte-identical: `corpus[].sidecar_sha256` must differ. Removing that field makes T6 pass even if the report publishes an incorrect sidecar hash.  
FIX: Assert each published hash against its sidecar file; compare the remaining payload fields separately and correct the byte-identity claim.

ID: P5  
SEVERITY: completeness  
LOCATION: tests/fixtures/rof4-accept-identities/expected/cases.json:27  
QUOTE: `"case": "S2-reference-legacy"`  
PROBLEM: Every S2 case uses a reference-bearing model, whose canonical-v1 and legacy values are identical. Reinstating S2’s old equality comparison would pass every S2 corpus case. The claimed distinct canonical acceptance at S2 is therefore untested and, for this model class, unobservable.  
FIX: State S2’s one-identity limit in the coverage claim; retain a source-level assertion that it delegates to the helper.

ID: P6  
SEVERITY: completeness  
LOCATION: tests/fixtures/rof4-accept-identities/expected/cases.json:78  
QUOTE: `"binding_edit": "extra-key", "expect": {"exit": 3, "reason": "input-invalid"}`  
PROBLEM: The extra-key and missing-key cases stop in `certificate_shape` before the new `binding.keys() != expected.keys()` comparison. They verify shape refusal, but cannot fail if that new key-set comparison is removed.  
FIX: Describe these as shape-order tests; test the binding comparison separately if its key-set clause is retained as a claimed guarantee.

ID: P7  
SEVERITY: hardening  
LOCATION: src/gnd/skills/gnd-orm-core/references/representation-format.md:925  
QUOTE: `` `model_digest` (`legacy-repr`) is still what reports, `validate --trace`, steps files and generated plans carry. ``  
PROBLEM: The commit ships `plan-draft-2.canonical.steps.json`, whose `model_digest` is canonical-v2. The normative subsection now contradicts its own new acceptance rule and example.  
FIX: Say that reports, trace output and generated plans carry legacy; steps files may carry either identity.

CONFIRMED: By reading only, I found that the listed exact-coherence, marker, copy and generated-plan comparisons remain unchanged; the witness schema rejects altered binding key sets before replay; the API copies a caller-provided steps mapping, so the rewrite does not mutate that caller’s object. I did not run the test suite.