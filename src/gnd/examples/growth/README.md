# Growth example

A shop's model grown one round at a time, used by the how-to
"Grow a model by additions, with GND checking each round"
(`docs/how-to/grow-a-model.md`).

- `model.orm.yaml`: customers, orders and channels; two sample orders; one
  derived fact type.
- `round-1.proposal.json`: adds "Order is returned via Channel", which
  `--policy additive` admits and `--shape-report` matches against
  "Order arrives via Channel".
- `round-2.proposal.json`: adds a mandatory constraint on the populated
  `order_placed_by_customer`, which `--policy additive` refuses.

The proposals bind the model's digest; in the source repository, regenerate
them with `tools/build_growth_example.py` after any model edit.
