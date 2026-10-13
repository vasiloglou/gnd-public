# Local CI query and family inventory diagnosis — seat four

2026-10-13; current candidate `f446dc1`. Read-only production diagnosis; only
this note written. No provider calls or broad suite execution.

## Reproduced findings

```text
.venv/bin/python -m pytest -q tests/test_rf6_query_policy.py tests/test_rf6_registry.py::test_every_production_entry_resolves_all_hooks --tb=short
3 failed, 8 passed in 7.61s
```

**P2 / live syntax evidence:** both dynamic inventory tests fail before their
negative controls because the historical RF9 inventory no longer equals current
syntax. The static exact query policy and original query metric pass. Comparing
the test's `dynamic_reads(sources())` Counter against retained rows shows
17 added occurrences and four removed occurrences; no blanket query exception
is necessary. This scanner intentionally counts syntax candidates, including
type annotations, rather than proving these are model queries.

Added exact successor tuples (path, nearest owner, expression, delta count):

```text
src/gnd/redaction.py | RedactionPolicy | frozenset[tuple[str, str]] | 1
src/gnd/redaction.py | RedactionPolicy | Mapping[str, frozenset[tuple[str, str]]] | 1
src/gnd/redaction.py | RedactionPolicy | tuple[str, str] | 1
src/gnd/redaction.py | verdict_roles | self._compiled_roles[reference] | 1
src/gnd/redaction.py | from_model | derivation_roles.get(str(entry['subset']['of']), frozenset()) | 1
src/gnd/branches.py | _compiled_snapshot_rows | Iterator[Branch] | 1
src/gnd/compiled_obligations.py | offending_rows | list[Any] | 1
src/gnd/compiled_obligations.py | offending_rows | dict[str, Any] | 1
src/gnd/compiled_obligations.py | compose | operation['preconditions'][entry['source_index']] | 1
src/gnd/compiled_obligations.py | offending_rows | facts.get(str(subset['in']), ()) | 1
src/gnd/compiled_obligations.py | offending_rows | facts.get(str(subset['of']), ()) | 1
src/gnd/compiled_obligations.py | compose | entry['subset'][side] | 1
src/gnd/compiled_obligations.py | compose | extensions.get(head) | 1
src/gnd/compiled_obligations.py | key | row.get(pair[side]) | 1
src/gnd/compiled_obligations.py | key | pair[side] | 1
src/gnd/compiled_obligations.py | compose | view.facts.get(subject, ()) | 1
src/gnd/compiled_obligations.py | compose | view.facts.get(of) | 1
```

Removed exact predecessor tuples, all count one in `src/gnd/transition.py`,
owner `_compiled_verdicts`:

```text
(pre.facts or {}).get(str(subset['in']), [])
(pre.facts or {}).get(str(subset['of']), [])
fact.get(of_role)
other.get(in_role)
```

Preserve historical `code-refactoring/evidence/RF9-repair/dynamic-query-candidates.json`
bytes. Retain a new digest-bound milestone successor that explicitly removes
those four entries and adds the 17 counted occurrences above. Three additions
increment existing annotation keys, so a patch format must add counts rather
than append duplicate rows. The live test should select that explicit successor
and retain duplicate/new/stale/missing-row rejection controls. Generating a
broader runtime waiver or changing the scanner would evade the intended gate.

**P2 / family inventory mismatch:** the hook test also fails in this fresh
focused process, disproving the suite-pollution hypothesis. At
`src/gnd/semantic_adapter.py:51`, `_FAMILIES` derives from every snapshot branch.
The new generated `compiled-subset` report branch therefore enters that set,
but authored dispatch registry `constraint_families.FAMILIES` lacks it.
`tests/test_rf6_registry.py:53` detects the difference. Actual adaptation uses
`FAMILIES` for refusal and dispatch (`semantic_adapter.py:411`, `:473`).

Repair the compatibility inventory to describe authored family dispatch, with
`FAMILIES` as its explicit normative source or a documented generated-family
exclusion. Retain independent authored hook checks and generated compiled branch
checks. Adding fake authored hooks for `compiled-subset` solely to equalize the
sets would falsely broaden the authored constraint contract.

## Limits

This diagnosis does not establish full CI correctness or provenance of unrelated
late failures. The proposed repairs require fresh focused controls and updated
current close evidence; earlier phase records remain historical. No production
repair or evidence inventory mutation was performed by this reviewer.

## Authorized implementation follow-up

The root subsequently delegated only the live query test and a new milestone
syntax successor to this seat. Implemented
`evidence/CI/dynamic-query-successor.json` with the exact 17 added occurrences
and four removed occurrences above, digest-bound to the unchanged RF9 inventory.
The root's authored-family `_FAMILIES = frozenset(FAMILIES)` repair contributes
no additional dynamic syntax candidate delta.

Historical inventory SHA-256 remains
`5ee422365202e3c12082cd62f6b4a7666cd867d86c220a3e1a63400bc0844531`.
Successor SHA-256:
`abc67856029a0b41bcf2965be72f30767096830fe6139b09dbca06b8d7c5fc69`.
The predecessor has 5,759 distinct rows / 7,260 counted occurrences; the current
successor has 5,769 distinct rows / 7,273 occurrences. The additional annotation
counts are applied to existing keys without duplicate rows.

`tests/test_rf6_query_policy.py` now applies and validates that explicit counted
delta. It refuses duplicate additions/removals, a stale predecessor digest,
missing/extra additions, impossible removals and vanished live candidates.
Existing injected new-read and duplicate effective-row controls remain intact.
The scanner and static exact query policy are unchanged. Runtime production
files and historical evidence were not edited by this reviewer.

```text
/private/tmp/gnd-pr19-ci/dev311/bin/python -m pytest -q tests/test_rf6_query_policy.py --tb=short
17 passed in 8.04s
/private/tmp/gnd-pr19-ci/dev313/bin/python -m pytest -q tests/test_rf6_query_policy.py --tb=short
17 passed in 7.73s
.venv/bin/ruff check tests/test_rf6_query_policy.py
All checks passed!
git diff --check -- tests/test_rf6_query_policy.py
exit 0
```

No commits made by this seat. The query-inventory findings are discharged for
these exact successor/test bytes; root owns registry verification and final CI
evidence binding.
