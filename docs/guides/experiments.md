# Run a bounded development experiment

Use a session when you need evidence about whether an agent can produce an
acceptable artifact under a declared contract. For example: “Can the agent
produce recommendations that satisfy these rules and include every required
reader?” The contract makes the inputs, expected outputs, acceptance relation,
and work bounds explicit before the attempt starts.

For ordinary extension-code work, focused tests and a smoke run may already
answer the question. A session is useful when convergence, retry behavior, or
agent-produced artifacts are themselves part of what you need to assess.

## Declare the question and acceptance mode

The session skill helps author `SPEC.md` and `session.contract.json`. The spec
contains named questions; the contract binds exact inputs, cases, outputs, the
verifier, and limits. Select an acceptance mode that matches the question:

| Mode | Good use | What it establishes |
|---|---|---|
| Exact bytes | One required serialized artifact | Exact agreement with a separately authored expectation |
| Constraint satisfaction | Several valid answers are acceptable | Checker acceptance plus any declared coverage floors |
| Tests | A software extension must pass selected tests | Declared sealed tests ran and passed |
| Transition | An agent proposes an operation walk | The declared transition relation and walk requirements hold |

Constraint acceptance should include meaningful minimum fact counts when an
empty or partial answer would be useless. Transition cases can require or
forbid named operations under supported contract versions. Tests-mode cases
must protect both the deciding test and any fixture or contract it reads.

Exact expectations are authored through `gnd exp author-expectation`, which
hashes the selected answer source, removes that source, and checks for equal
copies in the experiment. It is intentionally a mutating authoring command;
read its help and the contract before using it on an answer artifact.

## Validate the declaration, then run

These commands are contextual: the experiment directory, contract, protected
files, adapter tool, and selected credentials must already exist.

```sh
gnd exp validate EXP-001-recommendations
gnd exp run EXP-001-recommendations --adapter codex
```

The first command validates `SPEC.md`; it does not validate the whole session
contract. The run validates that contract and its bindings before invoking an
adapter. Legacy contract versions 1–5 select `--adapter codex` or
`--adapter claude`. Newer declared-policy contracts use a caller-trusted local
policy instead:

```sh
gnd exp run EXP-001-recommendations --adapter-policy /trusted/adapter.policy.json
```

The policy governs the command or supported endpoint; the committed candidate
does not choose its executable or credentials. Follow the workflow's trusted
credential environment. Never execute a repository `.env` as shell code.
These live commands are not prerequisites for the credential-free tutorials.

## Read acceptance and retained evidence

Exit `0` means required cases met their declared acceptance relation. Exit
`15` means a well-formed session ended without acceptance. The result names
the terminal disposition: accepted, agent failure, verifier failure,
stagnation, oscillation, or budget exhaustion. Child checker bands remain
per-case evidence; they do not replace the parent session exit.

Inspect `runs/run-NNNN/result.json`, each immutable attempt record, candidate
inventory, verifier output, and feedback. A retry receives structured feedback
for the attempt. A new run retains a new evidence directory instead of
rewriting the old attempt. A best-candidate ranking, when explicitly selected,
does not alter acceptance rules.

## Close the experiment explicitly

Write `CONCLUSIONS.md` answering every question ID and citing evidence inside
the experiment. Contextual close command:

```sh
gnd exp close EXP-001-recommendations
```

Closure is a completeness check, separate from session acceptance. It refuses
while questions, evidence, or kind-specific obligations remain unresolved.
A codegen experiment also needs conformance evidence; a work experiment needs
its latest required session acceptance. Do not describe `accepted` as “closed”
until closure itself succeeds.

Saved external judgments are another explicitly selected contract layer.
They can gate candidate admission using bound receipts, policy, and source
evidence; GND does not obtain those opinions or assume reported confidence is
calibrated correctness. Judgment results remain separate from mechanical
checking and carry no assurance upgrade.

The [session skill](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-dev-session/SKILL.md),
[patch/ranking contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-dev-session/references/session-v7-contract.md),
and [saved judgment contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-dev-session/references/judgment-contract.md)
define the version-specific fields and evidence.
