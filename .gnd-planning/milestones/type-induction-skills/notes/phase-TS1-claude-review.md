# TS1 adversarial review (one reviewer)

One reviewer is one reviewer. Retained below the rule, verbatim except one
edit: the session scratch path is replaced by `<scratch>`. The
reviewer ran in a subagent over the uncommitted TS1 working tree against
`ad7c9de`. `R` is the session scratch directory (not retained); its
reproduction scripts are summarised in the phase record.

---

# TS1 adversarial review findings (working tree vs HEAD ad7c9ded)

All commands run from the worktree root; R = <scratch>/review

## F1 (high) Legitimate small input exits 70 "internal", nothing written
- Where: src/gnd/discover/type_evidence.py:172-188 (evidence_bytes raises TypeEvidenceOverflow); src/gnd/discover/service.py (except TypeEvidenceOverflow -> EXIT_INTERNAL).
- Defect: the spec's "groups alone cannot exceed the cap, argued from the population cap" premise is false. Each group costs about 260+ bytes of evidence but only about 40 bytes of population, so a 1.6 MB population (well under the 10 MiB cap) with 40,000 distinct attribute names makes the groups alone exceed 10 MiB. The run then exits 70 and writes neither the report nor the proposal. The same run without the option exits 0. docs/reference/discover.md "Size" does not mention exit 70.
- Repro: `uv run python $R/f1_overflow.py 40000`
- Observed: `population bytes 1629030` / `exit 70 secs 2.0` / `stderr ERROR: internal: the type evidence groups exceed the evidence cap` / `report written False evidence written False` / `without option exit 0`
- Reproduced: yes.

## F2 (medium) Time and memory are O(groups x candidates) and do not depend on rows; the standing rule 2 bound fails
- Where: src/gnd/discover/type_evidence.py:106-138 (one candidate dict for every group and every played fact type) and :175 (canonical_json_bytes of the whole untrimmed document before the cap trims it).
- Defect: the cache shares the pair sets, but every group still materialises every candidate entry, and the full document is serialised before any trimming. A model with a few hundred empty binary fact types and a population under 1 MB therefore uses gigabytes of memory. T20 uses only 1,200 groups and does not exercise this.
- Repro: `uv run python $R/f3_time.py 20000 200 with` (and `... 5000 100 with`, `... 5000 100 without` for scale)
- Observed:
  - 5000x100 with the option: `exit 0 secs 4.8`, max RSS 574,144,512.
  - 5000x100 without the option: `exit 0 secs 0.8`, max RSS 85,213,184.
  - 20000x200 with the option: model 33,728 bytes, population 809,030 bytes, `exit 0 secs 27.7`, max RSS 4,045,029,376, truncated 3,986,817.
  - Growth is linear at about 1 KB of RSS per candidate entry, so about 30k groups x 1000 candidates (still inside both 10 MiB input caps) extrapolates to about 30 GB.
- Reproduced: yes (measured; the 30 GB figure is an extrapolation and was not run).

## F3 (medium) overlap.pairs is null for DateTime groups against an identical DateTime binary
- Where: src/gnd/discover/type_evidence.py:67 (`types._kind(other[0].primitive) == kind`) together with types.py:282-284 `_kind` ("DateTime" -> "datetime"), while canonical_scalar's identity kinds are "datetime-aware" / "datetime-naive".
- Defect: the group kind ("datetime-aware") never equals `_kind("DateTime")` ("datetime"), so D2's "other role's primitive kind equals the group's" never holds for DateTime, and pairs comes out null. A pre-existing CT4 defect from the same mismatch shows in the same evidence: `value_primitive` is "String" and the proposal mints a String value type for DateTime data. That part is identical on HEAD: run with PYTHONPATH=$R/head/src and the proposal still carries `"primitive": "String"`.
- Repro: `uv run python $R/f2_datetime.py`
- Observed: `exit 0` / `status proposed value_primitive String signature ["item","item_has_attribute_induced_0_value"]` / `item_created_at signature_equal False overlap {'entities': 24, 'pairs': None}` (expected pairs 24, and an equal signature with value_primitive DateTime)
- Reproduced: yes.

## F4 (low, policy) Under customer, a redacted candidate value role still gets an equality count against the generic's values
- Where: src/gnd/discover/type_evidence.py:56-73 (no redaction check on candidate roles).
- Defect: overlap.pairs is computed over a role marked `redact: true`. The evidence therefore states how many entities' redacted value equals their generic value (here, "5 persons have diagnosis == note value"). Spec §6.3 only sanctions counts on a redacted entity role and says nothing about value roles. Elsewhere, discover skips redacted value roles entirely (skipped_redacted_value_roles).
- Repro: `uv run python $R/f4_redacted_candidate.py`
- Observed: `exit 0` / `g0 person_has_diagnosis {'entities': 24, 'pairs': 5}` under GND_DISCLOSURE=customer
- Reproduced: yes (the behaviour is reproduced; whether it counts as a defect is the owner's call).

## F5 (high, gate) The RF6 dynamic-read inventory grows by 30; the TS1 gate test fails
- Where: src/gnd/discover/type_evidence.py (26 new reads) and src/gnd/discover/types.py (GroupRecord/TypeProposals annotations, `group['rows'][:ROW_IDS_MAX]`).
- Defect: TS-R7 expects zero RF6 growth. tests/test_rf6_query_policy.py is in the plan §9 gate and fails: test_dynamic_candidate_inventory_is_complete_and_live and test_dynamic_duplicate_inventory_row_is_refused.
- Repro: `uv run pytest -q -p no:cacheprovider tests/test_rf6_query_policy.py` and `uv run python $R/rf6_delta.py`
- Observed: `2 failed`; `extra 30 missing 0`, all entries in type_evidence.py or types.py (for example `origins 'origin[key]'` x2, `_candidate_facts 'view.roles[fact_id]'`, `propose "group['rows'][:ROW_IDS_MAX]"`)
- Reproduced: yes.

## F6 (high, gate) The RF1 golden manifest was not updated
- Where: the RF1 goldens manifest, beside tests/fixtures/rf1-pins/goldens (checked by tests/test_rf1_pin_harness.py:39-53).
- Defect: three goldens were re-pinned but the manifest digests were not, so a gate test fails.
- Repro: `uv run pytest -q -p no:cacheprovider tests/test_rf1_pin_harness.py::test_golden_manifest`
- Observed: `AssertionError: goldens changed: ['cli-exit/gnd_discover.json', 'cli-help/gnd_discover.json', 'cli/tree.json']`
- Reproduced: yes.

## F7 (low) The internal API without the family raises AttributeError
- Where: src/gnd/discover/service.py, the evidence block (`result["type_proposals"].redacted_generics` when type_proposals is None).
- Defect: `_cmd_discover(..., families=("uniqueness",), type_evidence=...)` crashes. Only the CLI guards this (64); TS-D8 says there is no Python API, hence the low severity.
- Repro: `uv run python $R/f5_api_without_family.py`
- Observed: `raised AttributeError 'NoneType' object has no attribute 'redacted_generics'`
- Reproduced: yes.

## Checked, no defect found
- TS-R1 parity against HEAD without the option: git archive HEAD src into $R/head, then `uv run python $R/parity.py`. 29 cases covering 3 fixtures x 3 modes x show-values, default and combined families, existing --out, symlinked --out, same path, bad model, missing out dir, missing report dir, proposed groups, and a malformed origin. Exit, stdout, stderr and all written bytes are identical, apart from absolute paths in one traceback. The written-bytes drop_last path is also identical (`$R/parity_droplast.py <src> {2,50,100000}`, report bytes path-normalised).
- Totality over shapes (`uv run python $R/totality.py`): unary, ring (both roles item), 4-ary, two generics on one entity, a fully redacted candidate, an empty generic population, `induced_from: null` (3, by design), and provenance as a list (3, loader). No tracebacks.
- The cap loop terminates: each pass pops at least one candidate or raises, and `truncated` equals the number popped. The T14 accounting holds.
- Customer digests: only model_sha256 and population_sha256 are 64-hex. signature_equal: json.loads gives a list of str and the helper gives a tuple of str turned into a list, so they compare correctly.
- Tests: the focused file passes (45). T16 compares with and without the option on new code only, so on its own it cannot catch a regression shared by both paths; my HEAD parity run covers that gap.

## Pre-existing (identical on HEAD, outside TS1)
- A malformed YAML model (`not: [a`) gives a Traceback and exit 1 with or without --type-evidence (`$R/parity.py` case bad-model, both trees).
- DateTime attributes are proposed with a String value type (F3, second half).
