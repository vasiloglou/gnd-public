---
milestone: public-launch
station: phase-4.1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-4.1-runtimes
date: 2026-10-04
gate:
  command: ".venv/bin/python -m pytest -q tests/test_documentation_tutorials.py tests/test_external_runtime_tutorials.py tests/test_bookrec_tutorial.py tests/test_expense_tutorial.py tests/test_release_docs.py tests/test_release_examples.py tests/test_public_generated_examples.py tests/test_contributor_preparation.py tests/test_development_scaffold.py::test_readme_links_to_executable_getting_started --tb=short"
  exit: 0
  output: "143 passed in 37.76s"
  note: "Focused gate executed in the public implementation checkout; source record retains its evidence"
slow_cadence:
  command: "existing configured repository CI"
  trigger: "GitHub account runner availability restored and required candidate CI selected"
  reason: "The prior jobs did not start due billing; no broad local run or cloud pass is substituted"
evidence:
  - path: notes/phase-4.1-external-runtimes-spec.md
    sha256: 74268bb3bedf417477237fbd7aff33ca7ee7e10dcbd29c91459755bf6f2a45fa
  - path: notes/public-launch-plan-r4-runtime-extension.md
    sha256: 61fffe40b2f3e024f452d3bd9cb59962b3e71bf383ff100ea622d2f49b1ebb17
  - path: notes/phase-4.1-runtimes-codex-review.md
    sha256: 868c47e2cdc6482f9c121a8e64dfc5a3a98a0c43f27e08b911bf5127de690c04
  - path: evidence/phase-4.1-runtimes/evidence-sha256.json
    sha256: d3f4cea27017f2ec0a12b5ef557873a61d411661c891b2ec68d4c96d00d47ba8
  - path: evidence/phase-4.1-runtimes/implementation-sha256.json
    sha256: e5e43189aa99f690692be46bc7703e4203e7059f8facf0892c75706aedd506d4
---
# Phase 4.1 extension — release governance and external runtimes

Local implementation, actual native execution, independent review and affected
candidate preparation are complete. Cloud acceptance remains unavailable because
of the inherited GitHub billing blocker; final Phase 4 sign-off is pending.
Public record 007 and source counterpart 010 describe the same measured scope.
Earlier r4/Phase 3/Phase 4.1 records retain their bytes. The append-only r4
extension records the owner's explicit implementation instruction and changed
native-execution scope. The extension spec was prepared before implementation.

## What shipped

Five connected External runtimes pages cover setup, PyRel audits and relational
queries, Souffle dependency impact, finite Lean proofs and a release decision.
They include explanatory diagrams, explicit gnd-export/agent handoffs, deliberate
failures, repairs, exercises and source includes of the actual packaged programs.
Overview, gallery, exports and capability reference link the path.

The ten-component scenario has the requested nine edges, two vulnerabilities
and five releases. Distinct policy, derivation and proof views document their
facts and exclusions. Approval repair leaves checkout/payments/identity/ledger
affected; inventory/reporting are unaffected. Three requested releases remain
blocked by vulnerability impact. A patched catalogue removes all exposure.

The PyRel program executes public relational APIs on local DuckDB. Its joins,
negation and grouped distinct counts expose self-approval/conflicts/workload.
Generated audit completion is explicitly distinct from constraint satisfaction;
unsupported require execution is not treated as a verdict. An authorized-self
control passes exported policies and still produces the native self finding.

The reusable Souffle component teaches recursion, stratified negation and
aggregation. Exact extensions match GND's supported derivation export for baseline,
cycle/duplicate and patched cases. Positive witness replay is separate; negative
and aggregate witness requests refuse. An altered export bundle fails verification.
Developer sources never edit the verified generated bundle.

Lean imports verified Definitions into a separate developer proof workspace.
Concrete witness, existential satisfiability and generated redundancy propositions
are proved with ordinary tactics/decide. A reviewed-but-unapproved interpretation
refutes a tempting converse: the false proof fails compilation and the negation
compiles. Four #print axioms audits show ordinary foundational dependencies only,
without sorryAx/native computation axioms. Original metadata stays unproved.

The runner executes prerequisite blocks and explicit offline/pyrel/souffle/lean/all
lanes, fails requested missing/mismatched tools, and reports skipped native steps.
The isolated locked tutorial project avoids the observed Pydantic pin conflict;
base dependencies and GND runtime semantics are unchanged. Both lock copies are
byte checked, and installed resources contain the complete lessons/checkpoints.

## Gate output and candidate measurements

Focused gate (header), exit 0:

```text
143 passed in 37.76s
```

Ruff on changed tools/tests and packaged native Python, exit 0:

```text
All checks passed!
```

Strict site and local links, exit 0:

```text
Build started
No issues found
Build finished in 0.20s
4564 local links/assets/anchors checked
```

Two installed wheel origins, outside the checkout, each exit 0:

```text
122 tutorial blocks passed
```

Final offline source was rerun after the instrument/command repair in both fresh
origin environments. Each run explicitly printed skipped native lanes. The wheel
rebuilt from the source archive equals the direct wheel:

```text
wheel SHA-256: 812bd814329321ec3d2e6573e9a7191d59bd29f38a4f5ee4fea70f519893cd1c
sdist SHA-256: 0914a1a1741577524d97974ba21a5bbd4b99cf1748505c6feb7acc7bf9adc1a8
uncompressed wheel payload: 6116293 bytes (<12582912-byte limit)
```

Real native paths used the installed direct candidate outside the checkout,
not an alternate lesson implementation. Each includes shared prerequisite blocks:

```text
Native lanes executed: pyrel
13 tutorial blocks passed
Native lanes executed: souffle
15 tutorial blocks passed
Native lanes executed: lean
12 tutorial blocks passed
```

Versions: PyRel 1.30.1 / DuckDB 1.5.5, Souffle 2.5 64-bit, Lean 4.34.0. Exact
native executable identities, commands, limits, normalized actual checkpoints,
input/output hashes and candidate origins are retained under evidence. The tested
candidate page names these current package bytes. Template compilation keeps
proof_status unproved; it does not create a GND positive proof-verification API.

## Independent review and coverage

One independent gpt-6-sol xhigh terminal reviewer inspected the staged extension
read-only with the prompt on stdin. It checked scenario mappings, checkpoint hashes,
matching lock copies, Souffle results and finite Lean sources. It did not rerun
native tools, build artifacts or render the site; those are root execution
measurements. Its final findings are retained with declared path substitutions.
One reviewer is one reviewer, not a panel.

Its missing DuckDB pin finding was reproduced. The new wrong-DuckDB regression
failed against pre-fix code (1 failed, 4 passed), then passed after both versions
were checked. The full focused gate and installed native path are green. No
follow-up round was needed for this bounded repair. Earlier actual Markdown
execution also rejected a wrong CLI flag; correcting --format json was verified
through the same learning path. Retained red controls are evidence, not gates
claimed green. Later interpreter-command clarification names the isolated Python
explicitly and was executed directly.

Coverage audit: C1 is supported by the roles/view comparison and reviewer reading;
C2/C3 by actual documented inputs, commands, semantic result assertions and native
execution; C4 by strict site/links and 1440x900 desktop, 390x844 mobile navigation,
search, code and diagram/theme review; C5 by exact matching installed artifacts.
No independent external-reader usability trial or cloud result is invented.

## Refactoring review

Executed: one parsed block stream now serves compatibility and lane execution;
source snippets render the actual packaged native files instead of a separately
maintained display copy. The PyRel dependency conflict revealed an environment
boundary and was solved with an isolated locked project, not a runtime refactor.
No core refactor is needed: exporters remain authoritative, existing witness and
compile commands are reused, and developer-owned examples stay outside bundles.
The maintained/packaged lock duplication is explicit and byte gated; no silent
future refactor is deferred.

## Boundary — what this result does NOT establish

No final Phase 4 sign-off, Phase 5 publication, hosted application, remote
provider/connection execution, new API/exporter semantics, runtime expansion or
certification. No source truth, production release authorization, universal
semantic equivalence, performance comparison or unrestricted completeness.
Finite proofs hold in the selected five-ID view; they do not prove arbitrary ORM
models or clear real-world vulnerabilities. Generated templates remain unproved.
The selected local macOS/Python 3.13 evidence does not replace required cloud CI.
Native steps explicitly skipped by offline CI cannot count as executed passes.

## Open questions

| Obligation | Target / next action |
|---|---|
| GitHub billing/runner availability | Account owner restores availability; execute required configured CI |
| Final exact candidate acceptance | Phase 4 sign-off after affected cloud validation |
| Publication | Phase 5; remains inactive |

## Refuted premises

PyRel's pinned version alone did not enforce the pinned DuckDB backend; the
reviewer's reproduced refusing control refutes that premise. A root optional
dependency group could not preserve both incompatible Pydantic pins; the isolated
project corrects that design. A successful generated approval audit is not full
business-policy coverage: the executed authorized-self control demonstrates why
native reports and model verdicts remain separate. None widens earlier claims.
