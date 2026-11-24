# Loader single parse (2026-11-24)

The maintenance pass that growth-round-outcomes deferred as D9 (plan H9, GO1-D4
(b); `../../milestones/growth-round-outcomes/007-milestone-close.md` names it
"offered and not done"). The owner asked for it on 2026-11-24.

`load_model` parsed every model twice: `_load_model_at` parsed the root bytes
to see whether they declare includes, and a model without includes was then
validated by `load_model_bytes`, which parsed the same bytes again. Now
`load_model_bytes` is its parse followed by `_load_model_document`, and
`_load_model_at` hands that the document it already has.

- `tests/test_d9_loader_single_parse.py`: across every committed model fixture
  (418), validation writes nothing into the document, loaded or refused, and
  `load_model` parses the root bytes once (411 fixtures parsed them twice on
  `main`).
- `definition-successors.json`: the RF6 body pin of
  `gnd.model.load_model_bytes`, chained after the 2026-11-16 repair.
- `tests/test_reference_population_corpus.py`: the B11 model-swap cases hooked
  `load_model_bytes` as "after the model was read"; the loader no longer goes
  through that name, so the hook moved to `_load_model_document`, the same
  point after the read and before the references bind.

`gnd validate` on the 2,404-object-type model of GO1's timing case: 4.7 s on
`main`, 2.5 s with the change (one laptop, two runs each); the report and exit
are the same, as on the two smaller fixtures compared.

Not changed: `gnd.witness.service` parses a model with reference populations and
then calls `load_model_bytes` on the same bytes, a second parse outside the
loader.
