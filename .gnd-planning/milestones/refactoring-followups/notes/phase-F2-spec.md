# F2 · Strengthen the RF1 characterization fixtures

Delegated spec gate, 2026-11-25, under the named auto=true invocation.

## Provenance and obligations

Plan r2 §§0, 3, 4, 9 and 10, issue #306, RF1 review 05 and 10, RF1-OQ7, RF3-OQ3 and Q3. C21/C23 require common token replacement and independently bound fixture bytes. C32 requires observed evaluator-call controls in both families. C24 distinguishes a digest validator from a hasher.

## Design and standing rules

In tests/support/rf1_pins.py share the exact longest-token-first replacement loop across normalize_text, normalize_json_text and scrub. Preserve pre-escape ordering for JSON observations, domain-specific substitutions, boundary types and all old fixture outputs. In test_rf1_session_pins.py verify the declared adapter-policy bytes against independent environment-normalized expectations before they participate in digest substitution. Interpreter and prompt strings remain independently constructed from explicit inputs; pin the prompt template independently of production. Limit substitutions to fixture-owned paths and identifiers. Preserve historical answer files. Check the independent expected surfaces against each inventory phase, including owed rows. Publish Q3 corrections here: extract.anchors._digest and judgments.digest validate hexadecimal strings; measure.promote._digest reads and hashes file bytes.

D1 shares the two identical guards after deliberately calling patched checker.check through each fixture. Retain historical imports. One policy walk owns the targets. Totality applies to JSON fixture observations within their existing typed domain. No new production or untrusted input reader, timing-dependent algorithm, or product refusal is introduced. Normalization order is contractual and gets an overlapping-token test. These are test-support semantics and their normative home is rf1_pins. Round-trip legal escaped paths to verify representation decisions.

## Verification, estimate and boundaries

Run focused RF1 normalizer, session fixture and both no-evaluator controls, and compare the historical inventory against separately named plan obligations. An altered adapter policy, missing owed surface or escaping regression must be detectable. Default-lane pytest and touched-file ruff exit 0. Estimate 80–140 support/test lines. Approval instrument is this spec and focused fixtures. Claude Code independently reviews the diff. F2 owns test support only.
