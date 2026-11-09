# UG2 corpus: population-checked constraint admission

The approval corpus for phase UG2 of the unattended-model-growth milestone
(spec: `.gnd-planning/milestones/unattended-model-growth/notes/phase-UG2-spec.md`,
§8 and §11). Read the stories below and decide, for each, what GND should do.
Then compare with the answer key, `expected.json`, which is kept apart so this
page can be read blind. The harness is `tests/test_evolve_population_check.py`.

## The model

`base.orm.yaml` (`model_id: ug2-orders`) has customers who place orders, orders
with amounts, orders with memos, and orders that arrive by a channel.

- `customer_places_order` already has one rule: order numbers lie between 1 and
  1000 (`llm-inferred`, `proposed`, `deontic`).
- `order_has_amount` already has one rule: amounts lie between 0 and 1000 (same
  provenance).
- `order_has_memo` has no rule.
- `order_has_channel` carries two sample rows inside the model itself.

In every story the host runs `gnd evolve preview --policy additive` and, where
it says so, `gnd evolve apply` with the options listed. `--populated X` tells
the policy that fact type X already holds data. `--check-population F` hands
GND the file `populations/F`, the data the host has extracted so far.

## The populations

| File | What it holds |
|---|---|
| `clean.json` | customer 1 placed order 10, customer 2 placed order 11; amounts 40 and 75 |
| `clean-changed.json` | the same, except order 11's amount is 76 |
| `violating.json` | customers 1 and 2 both placed order 10; order 10's amount is 40 |
| `amounts-only.json` | one amount row; no one placed any order |
| `older-rule-violated.json` | as `clean.json`, but order 10's amount is 5000 |
| `no-model-id.json` | as `clean.json`, with no `model_id` in its header |
| `other-model.json` | as `clean.json`, with `model_id: other-model` |
| `small-orders.json` | the two placements of `clean.json`; no amounts, no memos |
| `channel.json` | customer 1 placed order 10; order 10 arrived by web |

## The stories

### C01
The host proposes a new rule on `customer_places_order`: each order is placed by
one customer (uniqueness on `order`; `llm-inferred`, `proposed`, `deontic`). It
says the fact type holds data and hands over `clean.json`. Then it applies with
the same options.

### C02
The host proposes to tighten the existing order-number rule from at most 1000 to
at most 100, with `clean.json`. Then it applies with the same options.

### C03
The C01 rule, handed `violating.json`, where one order has two customers. The
host then tries to apply with the same options.

### C04
The C01 rule, handed `amounts-only.json`, which says nothing about who placed
which order.

### C05
A new model-level rule: every order with a memo is an order someone placed
(subset from `order_has_memo` to `customer_places_order`; `llm-inferred`,
`proposed`, `deontic`). The host says both fact types hold data and hands over
`small-orders.json`, which has placements but no memos.

### C06
The C01 rule, handed `older-rule-violated.json`: the placements are fine for the
new rule, but one amount breaks the older amount rule. Then apply with the same
options.

### C07a
The C01 rule, handed `no-model-id.json`.

### C07b
The C01 rule, handed `other-model.json`.

### C08a
The C01 rule written as a confirmed, alethic, user-supplied rule instead of a
proposed, deontic one, with `clean.json`.

### C08b
The host proposes to change the existing order-number rule from a range into a
list of allowed values (10 and 11), with `clean.json`. Changing a range into a
list is neither a tightening nor a loosening.

### C09
A new rule on `order_has_channel`: each order arrives by one channel
(`llm-inferred`, `proposed`, `deontic`). That fact type holds data as sample
rows in the model. The host hands over `channel.json`.

### C10
The C01 rule, with `--check-population clean.json` but without `--policy`.

### C11a
The C01 story, but the host applies without `--check-population`.

### C11b
The C01 rule, previewed without `--check-population`; the host then applies with
`--check-population clean.json`.

### C11c
The C01 story, but between preview and apply someone replaces `clean.json` with
the bytes of `clean-changed.json`. The host applies with the same options.

## Parity

`parity-baseline.json` records, for six of these proposals, the status code and the
preview's SHA-256 without `--check-population` (with `--policy additive` and
with no policy), captured on `8eb4fe60` before any source edit. UG2 must not
move them.
