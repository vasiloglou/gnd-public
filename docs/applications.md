# Applications you can learn from

These examples explore different ways to use GND. They are small local
applications with synthetic data, designed for inspection and modification.

| Application | What you build or check | What it teaches |
|---|---|---|
| [BookRec](bookrec/01-model.md) | Python recommendation library and CLI | Hard rules, warnings, generated structure, checked publication, evolution and completeness |
| [Expense approvals](expense/01-model.md) | Approval and reporting CLI | Policy constraints, candidate states, explicit validation, currency evolution |
| [Warehouse dispatch](quickstart.md) | Shipping request against a fixed route catalogue | Deadlines, reference data, meaningful failure and repair |
| [Release readiness](release-example.md) | Release request against dependency facts | Applying the same checking approach to another domain |

## Built from earlier GND work

BookRec and expense approval extend independently authored public examples
already exercised by the public project's codegen/conformance tests. The teaching
sequence also draws on earlier GND application experiments. The tutorial bundles
are new public adaptations, not copies of historical agent runs or proof archives.
They carry their own models, code, checkpoints and current execution tests.

BookRec demonstrates legality under declared rules, not recommendation relevance
or ranking quality. Expense approval is a local example, not a production expense
service with authentication, persistence or payment integration. Dispatch and
release readiness check supplied facts rather than operating a shipping or
software deployment system.

## Bring your own application

Start with one concrete failure you want to catch. Write down the relationships
needed to express it, one passing example and one failing example. Use
[the modeling guide](guides/modeling.md) to construct a model, then embed
[an API check](reference/python-api.md) where your application proposes an output.
Expand only after you can explain why those two examples differ.
