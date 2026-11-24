# Round summary fixtures (GO5)

`known-mix.round.json` is the host's round file of a round over
`tests/fixtures/evolve-policy/base.orm.yaml` whose proposal
(`tests/test_go5_round_summary.py::test_t2_the_known_mix_round`) has three
operations, built to give each bucket a known count:

| Operation | Built to be | Bucket |
|---|---|---|
| add object type `region` | new, nothing depends on a refusal | `admitted` |
| add a `mandatory` constraint on `customer_places_order` | a constraint on a populated fact type, which the additive policy refuses without `--check-population` | `refused-by-policy` |
| add fact type `customer_returns_order_via_channel` over customer, order, channel | the role players of `customer_places_order` | `admitted`, and one shape match group |

The round file adds one reused id (`customer_places_order`, which the reply
named and did not restate) and one host drop. The round is previewed and
not applied, so nothing is added.

`known-mix.expected.json` holds those counts: 3 proposed, 2 `admitted`,
1 `refused-by-policy`, 1 host drop, 1 reused, 0 added, 1 shape match.
`dropped-with` has its own case
(`test_t2_a_dropped_with_row_is_counted`), on a refused candidate.
