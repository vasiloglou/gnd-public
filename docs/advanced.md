# Build beyond the first check

Once you can validate a model and explain a failed population, choose the next
guide by the job your application needs to do. Each workflow produces a
specific artifact or result that you can inspect.

| Your next question | Guide |
|---|---|
| How do I translate requirements into checkable rules? | [Modeling](guides/modeling.md) |
| How do I derive eligibility, use a fixed catalog, or audit a change? | [Data and transitions](guides/data-and-transitions.md) |
| How do I generate application structure and detect drift? | [Generated projects](guides/generated-projects.md) |
| How do I exercise rules with synthetic cases? | [Synthetic data](guides/synthetic-data.md) |
| How do I change existing rules or recover a model from code? | [Evolution and recovery](guides/evolution-and-recovery.md) |
| How do I check facts extracted from a report? | [Documents](guides/documents.md) |
| How do I run a bounded agent experiment? | [Experiments](guides/experiments.md) |
| How do I explain a derived tuple or use a native export? | [Exports and witnesses](guides/exports.md) |
| How do I ask an agent to use these workflows? | [Agent skills](guides/agent-skills.md) |

For a continuous learning path, build [BookRec](bookrec/01-model.md), then try
the [expense application](expense/01-model.md). The
[capability matrix](reference/capabilities.md) shows which features compose and
which consumers have narrower support. The [CLI index](reference/cli.md) and
[Python API reference](reference/python-api.md) help you integrate the parts
you select.

The examples use synthetic public inputs and deterministic local checkpoints.
Saved proposals, transcripts, receipts, and replay artifacts retain their
original scope; replaying them is not evidence that a provider ran now.
Live agents, advisory reviewers, and native compilers have separately selected
prerequisites. A mechanical pass is distinct from formal assurance: missing or
stale evidence yields unavailable assurance. These tutorials do not recertify
changed bytes or claim a measured provider/native support profile.
