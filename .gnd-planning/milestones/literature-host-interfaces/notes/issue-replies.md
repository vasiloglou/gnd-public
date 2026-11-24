# Drafted replies to #216 and #215

Drafted at milestone close for the owner to post (plan §5). Posted on the
owner's request on 2026-11-23 (comments on #216 and #215 at 23:44 UTC), with
the text below unchanged; both issues were closed as completed on
2026-11-24.

This note previously read "Not posted." `006-milestone-close.md` cites this
file's digest as it was then (sha256 `cb18a957…d3a2`); only this note has
changed since.

## #216: drive the reading example from a host

The reading example now takes your producer. Put a `profile.json` in a
root beside your roster, your `<id>.txt` sources and your reading model with
its includes, and call:

```python
from gnd.examples.literature import reading
report = reading.run(out, fixture=root, producer=your_producer)
reading.replay(out, fixture=root, expected_evidence_sha256=report["evidence_sha256"])
```

- **Producer protocol.** Your producer gets a `ProducerCall` with the
  section's bytes, its digest and the open questions on it, and answers
  `accepted`, `empty` or `refused` with facts. The loop counts the calls.
- **Stop rule per document.** `document_budget` bounds the bytes read from
  each source, beside the global `budget`; each source gets its own stop
  reason in the report's `documents`. A document whose required questions
  are answered still gets its other scheduled reads.
- **Caps as parameters.** `ReadingLimits` makes seven caps parameters: the
  roster, the largest budget, the per-file input, the response, the route
  timeout, the route output and the retained file. Each defaults to today's
  value and has a hard ceiling.
- **Replay against your root.** `replay(out, fixture=root)` re-derives the
  run with no producer call, from the settings and tables the run kept.
- Steps your profile does not declare (review, calibration, conflict,
  absence) are recorded `skipped`, never as passed. The exits of `verify`
  and `check` on your model are recorded (0, 1, 2 or 4); a completed run is
  not a verified one, and your host gates on those exits.

Not done here: the run over your corpus with a provider budget stays with
the literature-identity follow-up. Everything is described in
`src/gnd/examples/literature/reading_fixture/README.md`, "Drive it from your
host".

## #215: admit your own assertion entity

`assertion_admission.admit()` now takes a shape and rules:

```python
shape = {"format": "literature-assertion-shape/1", "assertion": "claim", "follow": ["quantity"]}
rules = {"format": "literature-admission-rules/1", "requirements": [
    {"id": "positive", "fact_type": "claim_polarity", "role": "polarity",
     "admissible": ["asserts"], "reasons": [{"value": "negates", "reason": "negated"}]}]}
admission.admit(model, raw, policy, receipts, evidence, out, shape=shape, rules=rules, max_targets=512)
```

- **Identity** is your assertion entity's own handle.
- **Every fact row of an admitted assertion is kept**: every fact type the
  entity plays a role in, plus the facts of the entity types you list in
  `follow`, such as a quantity with its value and unit.
- **Optional roles are optional**: an assertion with no row of a fact type
  simply has none, and no value means "absent".
- **Polarity and attribution rules are data**, with a distinct status: a
  reviewed assertion your rules refuse is `policy-refused`, not `fail`.
- **`max_targets`** is a parameter.
- Include roots are admitted with their includes.

Not done here, by decision: 1,024 targets per call is `gnd judgments
check`'s own cap, so a larger set is admitted in several calls. An entity
that objectifies a fact type is refused, so an assertion needs its own
handle. Following an entity type you do not list is not done. If your model
does not fit these, say so here. The shape, the rules and the record are
described in `src/gnd/examples/literature/README.md`, "Admitting your own
assertion entity".
