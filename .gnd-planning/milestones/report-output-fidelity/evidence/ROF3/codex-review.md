# Diff review of ROF3 (Codex), retained

- Instrument: one reviewer in a different tool (plan section 8). One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -o <scratch>/codex-final.md -`, prompt on stdin (`review-prompt.txt`), exit 0.
- Reviewed bytes: commit 3b0dbcc1, `git diff 004d24fa 3b0dbcc1`.
- The reviewer could not run the suite; its conclusions are by reading (it says so per finding).
- Retained: the reviewer's final answer, unedited. Its tool-call transcript (which contains the operator's absolute paths) is not retained.
- Disposition `block`, 8 findings. Triage: spec section "Implementation findings", I7.

## Reviewer output (verbatim)

DISPOSITION: block

ID: P1  
SEVERITY: blocking  
LOCATION: src/gnd/values.py:205  
QUOTE: `dict(d, fact_types=sorted(d["fact_types"]))`  
PROBLEM: Version 1 declarations bypass `_canonical`. After loading the reference corpus model, add `model.reference_populations[0]["extra"] = {7: "seven"}`. The JSON writer converts that nested integer key to `"7"` and returns a digest. The normative text requires refusal of nonstring keys; this also lets distinct keys acquire the same identity. This conclusion is by reading only.  
FIX: Canonicalize the declarations through the shared walk before serialization, while preserving the version 1 bytes for valid declarations.

ID: P2  
SEVERITY: blocking  
LOCATION: src/gnd/values.py:205  
QUOTE: `fact_types=sorted(d["fact_types"])`  
PROBLEM: A loaded reference model whose mutable declaration is changed to `fact_types = [1, "dispatch_catalog_allows"]` raises `TypeError` during sorting. `model_identity_document` catches only `TransitionLoadError` and `RecursionError`; `model_identity_bytes`, `model_identity`, and `_print_model_identity` therefore leak the exception. The promised `ModelIdentityError` is missing. This conclusion is by reading only.  
FIX: Validate declaration shape before sorting and convert its failures to `ModelIdentityError`.

ID: P3  
SEVERITY: blocking  
LOCATION: src/gnd/output.py:72  
QUOTE: `print(data.decode("utf-8").removesuffix("\n"))`  
PROBLEM: The producer sends canonical UTF-8 through the terminal’s text encoding. For the corpus’s Greek-text model with `PYTHONIOENCODING=ascii`, the header prints, then the document raises `UnicodeEncodeError` instead of producing the two lines or an identity refusal. This conclusion is by reading only.  
FIX: Write the already encoded canonical bytes to `sys.stdout.buffer`.

ID: P4  
SEVERITY: hardening  
LOCATION: src/gnd/values.py:253  
QUOTE: `return {"identity_version": IDENTITY_VERSION, "model": _canonical(dumped, "$")}`  
PROBLEM: `model_identity_document` returns a document for the corpus’s loaded lone-surrogate model, although that document cannot be written in the required UTF-8 form. Only `model_identity_bytes` refuses it. The document function’s stated refusal contract is false. This conclusion is by reading only.  
FIX: Check byte representability before returning a document, sharing that check with `model_identity_bytes`.

ID: P5  
SEVERITY: hardening  
LOCATION: src/gnd/skills/gnd-orm-core/references/representation-format.md:904  
QUOTE: `A date, time or datetime value ... is written as its ISO 8601 text ... Quoting it in the model gives the same identity.`  
PROBLEM: “ISO 8601 text” does not determine timezone spelling or fractional-second precision. The implementation uses `isoformat()`: a UTC datetime becomes `2025-01-01T00:00:00+00:00`, while a quoted `2025-01-01T00:00:00Z` remains `...Z`; their identities differ despite the quoted-form claim. This conclusion is by reading only.  
FIX: Specify the exact language-neutral datetime spelling, including offsets and precision, and add a timezone vector.

ID: P6  
SEVERITY: hardening  
LOCATION: tests/fixtures/model-identity-cli/expected.json:24  
QUOTE: `"stderr": "usage: gnd validate [-h] [--trace] [--identity] ..."`  
PROBLEM: Existing usage errors change, including `gnd validate` with no model. The successor fixture records the changed stderr, contradicting the approved claim that `gnd validate -h` is the only existing CLI output that moves. This conclusion is by diff inspection only.  
FIX: Preserve the old usage-error bytes, or explicitly amend the compatibility claim to include them.

ID: P7  
SEVERITY: completeness  
LOCATION: tests/test_rof3_model_identity.py:209  
QUOTE: `except Exception: ... model = load_model(... "plain-small.orm.yaml")`  
PROBLEM: The intended loaded-depth case cannot exercise its assertion: the source model’s first fact type has no `derivation_rule`, so the mutation raises `KeyError` and the test falls back to an unrelated shallow model. T8 measures only the large model, so it does not test the claimed growth ratio; T12 parses JSON and uses `all(...)` over an empty digest list for plain payloads, so it does not pin those bytes. These are reading-only test-coverage conclusions.  
FIX: Build a valid deep field and assert it survived loading; compare both measured sizes; byte-compare the frozen outputs.

ID: P8  
SEVERITY: completeness  
LOCATION: tests/test_rof3_model_identity.py:138  
QUOTE: `json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)`  
PROBLEM: T1 and `derive_vectors.py` use the same Python JSON encoder and `datetime.isoformat()` behavior as production. They can detect a wrong call into GND’s helpers, but cannot independently detect an encoder spelling that disagrees with the normative interchange text. The timezone gap in P5 would pass both. This conclusion is by reading only.  
FIX: Add independently specified byte vectors for timezone values, exponent boundaries, and Unicode escaping, and compare production bytes to them.

CONFIRMED: By reading the specified diff only, the version 1 builder preserves the prior `reference_model_digest` expression for valid declarations; version 2 excludes operations and treats absent and empty reference populations alike; incompatible requested versions are refused; `--identity` combination checks use exit 64 and a model that fails to load follows the ordinary validation route; the production canonical walk and byte writer retain one home. The RF5, query-successor, dynamic-query-successor, and component changes appear scoped to the intended additions. I did not run the test suite.