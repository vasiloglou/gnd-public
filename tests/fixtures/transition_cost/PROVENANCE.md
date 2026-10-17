# Provenance: issue #24 reproduction workload

The reporter's reproduction bundle for [issue #24](https://github.com/vasiloglou/gnd-public/issues/24)
holds the exact 13 public GND calls (7 `api.check`, 6 one-step `api.transition`) that a
downstream application made while running one 5-step program (scan, traverse, filter,
aggregate SUM, answer) over the packaged `expense` example. Everything in it is built from
packaged example data. The reporter's driver script is not committed. The measurement tool
`tools/measure_transition_cost.py` reimplements its call logic.

Imported for TP0 of the `transition-check-performance` milestone by `anonymize.py`, with the
owner-approved transform (TP0 spec D7):

1. `model_id` is set to `urn:gnd-fixture:steps@1` in the model and every population.
2. Every provenance `user_note` is set to `Sealed step programs.`
3. Each step document's `model` is set to `steps.orm.json`. Its `model_digest` and
   `operations_digest` were verified against the source model, then recomputed.

Files are re-serialized as sorted, indented JSON. The evidence that the transform preserves
results is `.gnd-planning/milestones/transition-check-performance/evidence/TP0/import.json`.

| File | SHA-256 before transform | SHA-256 after transform (committed) |
|---|---|---|
| `00-check-population.json` | `c6e23297eb28b25e9b5caf105e0391cbf5fd0eb460c16af8aae9a331d31bdc16` | `e94e635857ef47f18d8bf2a95d8da228c6bd9505433b115e7abd9e5335ee293c` |
| `01-transition-population.json` | `c6e23297eb28b25e9b5caf105e0391cbf5fd0eb460c16af8aae9a331d31bdc16` | `e94e635857ef47f18d8bf2a95d8da228c6bd9505433b115e7abd9e5335ee293c` |
| `01-transition-steps.json` | `4e46af704512d96a1b5daa45b6d8f462571f97d488346bc5c5ff812df3a26a4b` | `163917297345c9deb32e7438396cfe7ae58e552a6d5e78664cafa674fcd96f2f` |
| `02-check-population.json` | `44b5076dd201a199913a7f95dbfcb04972d906ae692c5b2b0d827340f282db76` | `5207394afcd046df08382b2532f47659d9c1f6f9e1803e061b99819ea4e338a6` |
| `03-transition-population.json` | `44b5076dd201a199913a7f95dbfcb04972d906ae692c5b2b0d827340f282db76` | `5207394afcd046df08382b2532f47659d9c1f6f9e1803e061b99819ea4e338a6` |
| `03-transition-steps.json` | `787369711605b923a76473e91b2361ec6182589e186fd5e94d68c97f49b5164c` | `c5d0c7ead6217d6b376eb00d8a47ce0d72e0f84dc2881aa58692d7077dcf8348` |
| `04-check-population.json` | `7f52e892db3f2f3f5a35c5937ff57124105ff34f154655bce2d612f6e8112058` | `0b219ab3ae4801fedc15be7b76f83883fc58bf6663ce80e55de1591e755f582a` |
| `05-transition-population.json` | `7f52e892db3f2f3f5a35c5937ff57124105ff34f154655bce2d612f6e8112058` | `0b219ab3ae4801fedc15be7b76f83883fc58bf6663ce80e55de1591e755f582a` |
| `05-transition-steps.json` | `d9059830d657259a7bdefec0a98ed8b36955a345a97aa68252ffedb4ae3d4017` | `91ce31532293f8bbf9aa3b0ebc7b9ff36dfa98fc2ce51bd165650fbd51ea1d7c` |
| `06-check-population.json` | `67d9f6c1a921c74425221257fda23ed2f6efb0b45aa2b85ee56e1ca3de3370e8` | `fc4521c85bf83feab7e144ed456250497104d14d4d0d0f8158358181ee426c19` |
| `07-transition-population.json` | `67d9f6c1a921c74425221257fda23ed2f6efb0b45aa2b85ee56e1ca3de3370e8` | `fc4521c85bf83feab7e144ed456250497104d14d4d0d0f8158358181ee426c19` |
| `07-transition-steps.json` | `a07fa2ed45b182f9990ff8efefa399a4f4e8007bda286af0290735f110de378a` | `ac19994ffbed4f99b9d60343f20d47348dce1a0297773842acf54550ed1911d4` |
| `08-check-population.json` | `3ce49a5ecc1d70d44ae2c427c53f41e3cfbc37e0d09bec481bc202182bf4d68e` | `3cc7cef427683e859aee62db1a297d3d2c924798d6fc6f9ba23e7fc841249199` |
| `09-transition-population.json` | `3ce49a5ecc1d70d44ae2c427c53f41e3cfbc37e0d09bec481bc202182bf4d68e` | `3cc7cef427683e859aee62db1a297d3d2c924798d6fc6f9ba23e7fc841249199` |
| `09-transition-steps.json` | `d46031a8e81ea6b4755f5757fa650bf0dc9a482e4e6a0ad653aa345d5d149c0e` | `b7c5fcbb7af8ce68173823b9c78c5a62d33e2ed5b1be621c4d90183d39950e35` |
| `10-check-population.json` | `4597b7fe11cf4c8aa4478c7059574a2edbeb566508e32ae3d5f735ae22ceeed9` | `57e4a6c9024e7c59b254f468dc9f4343cd897414139b02b2a93b07ee885a21e9` |
| `11-transition-population.json` | `4597b7fe11cf4c8aa4478c7059574a2edbeb566508e32ae3d5f735ae22ceeed9` | `57e4a6c9024e7c59b254f468dc9f4343cd897414139b02b2a93b07ee885a21e9` |
| `11-transition-steps.json` | `790f3fd3dbb77bbb02620e8b9d55a9821e89ffa6bc49456410cf37bd20da3209` | `0807f8b844729e71a9e90c4e557eadfa839d6fb0f8c61ac951bcf04c65a85e79` |
| `12-check-population.json` | `f855cf2e2b0c0fa89c84797bcfc994d93ee464e23defdc6a4313f7fbaeca65bf` | `fdbef5cf5bacf7cc42334674901e4534f685d55af215812bc078db2f182bdccb` |
| `calls.json` | `eb4c882561fe034354475f00a5ca9035ac119dc580d7466fbfa6e514fbe60687` | `d843ec0261700d213b0090b4182f6883dff2e322171ae0f121f237f87e83e39a` |
| `steps.orm.json` | `622a27d7c65e3d2dc888ed870f6ac87b4c92bb75e402dc200e70e15678cad0ff` | `b96f7ace89b0e0313e0e43c9ad5d6397dfc8428a4527c118c7de3970d3efbf76` |
