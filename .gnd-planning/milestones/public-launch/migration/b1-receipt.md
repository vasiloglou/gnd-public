# B1 private push receipt — 2026-10-01

Source runtime baseline: `ac4be67afdddde0b2b2095a6cd383bc13852758c`.
Source P0/spec approval commit: `9b3da000aaf938435d700d16a1f23597d9e77645`.
Initial target commit: `eacc2ec7dc450a89b20766ab6e5d092a408a6afc`.
`git push -u origin main` exited 0; local and remote main identities matched.
Target `vasiloglou/gnd-public` remains private; default branch main. This is
private staging, not public visibility or package publication.

Exact initial B1 manifest SHA-256: `7e2bcccd41671743fdcedad2a856c78b59da7265256c0955256964554bb29c87`.
Initial [Phase 1 record](../001-phase-1.md) SHA-256: `7e58f617b5cee4468f520d45c2a61fb3b2a56b886fa826f8909b9f78ac19a65d`.
Its references bind the committed initial scaffold, not future changed bytes.
This subsequent receipt adds observed remote/CI results without rewriting it.

[Scoped scaffold CI](https://github.com/vasiloglou/gnd-public/actions/runs/36912844523)
completed successfully for the initial target commit: Ubuntu runner, CPython
3.11.16, selected two-file scaffold/credential suite only.

```text
41 passed in 0.34s
```

The CI job selected no live panel, native or broad/certification lane. Local
isolated CPython 3.13.12 checks previously exited 0, 41 cases. These observations
cover the scaffold, not a generic runtime support matrix or P4-C5 wheel readiness.

B1 is staged only: all 12 units remain source-owned, no authority transfer, no
new canonical question owner, no target publisher. Original source questions keep
IDs/states/mints/owners/triggers. Later source deltas need explicit reconciliation
against initial B1 source digests before handoff; no automatic synchronization.
P2 reconciles early normative resources; P3 accepts current behavioral successors;
P4 removes conditional bootstrap and proves source-free installed workflow;
P5 controls exposure/publication. Source originals remain migration authority.
