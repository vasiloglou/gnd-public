# Synthetic expense application checkpoints

These resources support the three-chapter expense tutorial in the documentation
site. Copy this directory from the installed `gnd` package; no source checkout,
provider account, employer data, or external service is needed.

The starting point is the public `public-generated-examples/expense` fixture's
approval/report CLI shape. The tutorial expands that design with synthetic
employees, amounts, category caps, approval limits, refusal checks and a real
additive currency proposal. The earlier expense-tracker application supplied the
lessons about approval chains, policy guards and currency evolution; its private
run archives and captured evidence are not copied here. These checkpoints are
new teaching inputs, not old test results or claims about an employer's policy.

The fictional exercise owner confirms these requirements for this example:

- Each expense has one submitter, one positive whole-number amount and one
  category. All amounts initially mean EUR; fractions are out of scope.
- Category limits: meals 75, training 1500, travel 2000, equipment 3000 EUR.
- The team-lead chain approves up to 100 EUR; finance approves up to 3000 EUR.
- An approval names a submitted expense and exactly one known approval chain.
- In the currency chapter, every expense names its currency explicitly. EUR is
  the only supported currency until conversion and currency-specific limits are
  deliberately modeled. This is a new, user-supplied requirement in the exercise.

The model's explicit/user-supplied provenance refers to this synthetic brief;
`confirmed` means confirmed for this exercise, not a real financial policy.

| Resource | Purpose |
|---|---|
| `model.orm.json` | Initial complete conceptual model (JSON is accepted YAML) |
| `seed.population.json` | Three submissions, including one existing finance approval |
| `approved.population.json` | Expected result after approving expense 101 |
| `invalid-chain.population.json` | Expense 102 improperly approved by the team lead |
| `invalid-meal.population.json` | Meal costs 90 EUR, above the 75 EUR cap |
| `extension.py`, `reporting.py` | Initial developer-owned CLI and report function |
| `native_query.py` | Optional developer-owned PyRel counts, sums, membership and candidate wiring |
| `architecture.contract.yaml` | Extension modules, command contract and smoke cases |
| `currency.orm.json` | Complete model after adding the currency requirement |
| `currency-missing.population.json` | Currency supplied for 103 but missing for 101/102 |
| `currency.population.json` | Complete migrated seed population |
| `currency_reporting.py` | Replacement report that exposes currency labels |
| `currency.architecture.contract.yaml` | Updated declared consumption of currency facts |
| `prepare_currency.py` | Builds the explicit, digest-bound additive proposal |

The optional native backend uses `--backend pyrel --pyrel-python
/absolute/pinned/python` on `report` or `approve`. Copy `native_query.py` beside
the copied `cli/expense_cli.py`, as well as the existing reporting module.
The selected interpreter must supply PyRel 1.30.1/DuckDB 1.5.5; GND remains in
its separate base interpreter. Native mode has no fallback to Python arithmetic
or GND population policy checking.

Native queries calculate submitted/approved counts and totals. Approval adds
only the approval and chain claims; an independent exported checker validates
the exact candidate before a fresh output is published. Report snapshots are
checked privately and removed; successful report JSON marks `published: false`.
Application guards for unknown/already-approved expenses or unsupported currency
are labeled separately from model verdicts. Refused CLI responses contain no
successful report arithmetic. A static accepted approval is not actor permission
or reimbursement authorization.

Baseline amounts are implicit EUR. The evolved model uses explicit EUR groups,
with no currency conversion. One missing currency produces a mandatory witness;
a fully empty covered currency relation retains the bounded profile's incomplete
refusal. Known-empty/zero-approval arithmetic does not make vacuous policy evidence
an accepted report.

`prepare_currency.py` does not apply the change. It uses GND's versioned evolution
proposal/roster support contracts, which are separate from the stable seven
functions in `gnd.api`. The tutorial's application uses only `gnd.api.check`.
The CLI support helper is pinned and tested with the package version that ships
it; it is not a promise of another stable application API.

The CLI deliberately writes approval results to a separate file. It checks both
the input population and proposed output and publishes only at exit zero. Static
post-state checks do not establish transition permissions, actor identity, a
concurrent storage transaction, a reimbursement or an accounting ledger.
