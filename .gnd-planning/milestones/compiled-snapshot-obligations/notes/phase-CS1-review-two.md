# CS1 focused local review 2 — possible-only derived inputs

2026-10-13. Independent read-only production review against `b57046f`.
Scope: the newly reproduced possible-only derived input, opt-in partial context,
known/default/reference neighbors. No provider call or certification.

## Finding — possible patterns can become false compiled failures

Blocking on the reviewed bytes: `compose` gathers unavailable relation IDs only
from unchecked derivation verdicts and checks dictionary values in effective
facts. A correct empty semiderived claim can pass its derivation check while
the extension contains possible-only patterns. `effective_view` returns the
definite fact view and does not preserve those patterns. Therefore compiled
matching can report a known missing fact when its presence is unknown.

Reproduction command:

```
uv run pytest -q tests/test_compiled_snapshot_obligations.py -k 'possible_only or reference_bound or effective_derived or dispositions or multiple_effects or anchor_route or silently_ignored' --tb=short
```

Observed: 12 passed, 1 failed. The possible-only test expected exit 4 and received
exit 1. Raw public report: `derivation:permitted` is `pass`; compiled
`$.operations[id=record].compiled[0]` is `fail`, reason null, witness `value=x`.
This is a compiled failure, not a legitimate derivation-claim mismatch.
Direct `checker.check(..., compiled_operations=True)` also returns band 1.

An additional admitted predicate case confirms the distinction: retain the
test's semiderived `seed($x) -> permitted($x)` rule but add
`where: [{operator: '=', left: '$x', right: 'x'}]`; seed contains the opaque value,
recorded contains `x`, and the permitted claim is empty. Public API again returns
derivation pass plus compiled fail, exit 1, with no admission issues. The
uncertain predicate can produce a matching permitted row; an empty definite view
does not justify the failure.

Relevant defining homes: `src/gnd/compiled_obligations.py:compose`,
`src/gnd/extensions.py:_PartialExtensions`, `effective_view`, and
`_constraint_view_dispatch`. The CS1 conservative unavailability rule requires
examining possible extension metadata rather than inferring it solely from
derivation claim verdicts.

## Context restoration and neighbors

A bounded `.venv/bin/python` probe independently checked `PARTIAL_OPAQUE` after
public API and direct checker success, nested invocation with an existing true
token, and an injected matcher exception. All restored the prior value. The
injection was process-local and restored its patched function; no source edits.

The 12 passing focused cases include known dispositions, effective known derived
facts, default/no-compilation-mutation behavior, reference binding, anchors, and
the admission conflict refusal. These checks do not establish a broad replay.
`uv run python` initially encountered a sandbox cache-read restriction; the
existing `.venv/bin/python` ran the equivalent diagnostic successfully.

Disposition: repair the new compiled evaluator's access to possible patterns,
then rerun the failing test and focused neighbors. No context-leakage finding.

## Repair verification

The repair explicitly retains calculated `possible`/`unavailable` metadata while
constructing the definite constraint view. Rechecked the same bounded selection
with `.venv/bin/python -m pytest`: 13 passed, 17 deselected. Independently reran
the admitted uncertain `where` case: API and direct checker both return band 4,
compiled reason `compiled-obligation-unavailable`, while the correct empty
derivation claim remains pass. Thus the repair addresses the reproduced cause
rather than replacing it with a derivation failure.

Repeated success, nested-true-context and injected matcher-exception restoration
probes all pass. The previously reproduced blocker is resolved on these bytes;
no unresolved finding remains in this focused review. No broader review or
certification claim is made.
