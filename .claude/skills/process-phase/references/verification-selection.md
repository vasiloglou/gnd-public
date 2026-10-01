# Verification selection and inheritance

Use this reference when authoring a phase's verification contract and when
executing step 3. Its purpose is to make the repository health check
proportional to the phase without turning an old green result into evidence for
changed bytes.

Certification and recertification are opt-in under the owner's 2026-09-28
ruling. Do not add them as `run` or `cadence` merely because a source changed,
a phase or milestone ended, or an older plan prescribed a recurring matrix.
Only an explicit current owner request for a named subject and scope selects
one. Record the owner ruling as the amendment when an older plan clause would
otherwise mandate a run. This does not waive direct or affected-consumer tests;
an old certificate continues to describe only its original bytes.

## Focused public selection — imported owner ruling, 2026-09-29

Ordinary phase verification uses a reduced selection: the phase's direct tests
and focused downstream nodes selected by changed behavior, under the current target configuration. The original v6.3 source lane ledger
and conftest are not imported in P1. P3 must establish target-local current
controls and collection policy; missing historical inputs are not green skips.
During P1, use `python -m pytest -q tests/test_development_scaffold.py
tests/test_review_credential_launcher.py` in the declared scaffold environment. For example:

```bash
python -m pytest -q tests/<phase-tests>.py tests/<affected-consumer-tests>.py --tb=short
```

Do not override `addopts` or use `-m` to bring the evidence, census, proof,
distribution, external-oracle or other excluded lanes into an ordinary gate.
If a necessary changed contract has only an excluded historical test, select
a bounded current-behavior successor and record the old claim as unavailable
on changed bytes. Explicitly requested special-lane work retains its own scope.
The owner or a separately configured CI job must explicitly select a full
default run, broad evidence/census run or exhaustive historical replay. Source
changes, phase completion, milestone completion and old plan defaults do not
select those runs. This ruling supersedes earlier automatic broad-run clauses.

## Required selection ledger

Before the owner gate, the spec records one row per logical verification gate:

| Field | Required content |
|---|---|
| Obligation | The plan clause, phase criterion, changed contract, or downstream risk the gate discharges |
| Disposition | `run`, `inherit`, or `cadence` |
| Command or evidence | Exact command and expected exit for `run`; path, SHA-256, source identity, command, and result for `inherit`; named CI or milestone-close lane for `cadence` |
| Input boundary | Files, schemas, fixtures, configuration, toolchain, environment, and generated inputs whose change can affect the result |
| Justification | Why this gate and the other selected gates close the impact surface without an unlisted replay |
| Invalidation | The concrete changes that force reconsideration or execution of the gate |

An inherited or cadence row is not omitted work. It is an explicit statement of
what the phase is and is not claiming.

## Selection rules

1. **Run plan-mandated gates verbatim unless the owner amends them.** Record an
   explicit owner amendment at the original gate's site in the phase spec. If
   a mandated command is invalid, unavailable, or contradicts the phase,
   record a refuted premise and return to the owner gate. Do not silently
   substitute a narrower command.
2. **Run the phase's direct tests.** Every new or changed branch, refusal,
   serialization, public behavior, and regression finding needs a case capable
   of failing it.
3. **Close the impact surface.** Add focused tests for downstream consumers of
   changed production code, schemas, package data, build rules, shared helpers,
   fixtures, or generated artifacts. Test selection follows dependencies and
   contracts, not filename vintage.
4. **Record the selected gate, not an implicit full-suite replay.** On each
   edit, run the direct tests and affected consumers. A phase record's `gate`
   names the exact selected command and its exit. Use the reduced v6.3
   selection above. A full default or broad `evidence or census` run requires
   explicit owner or separately configured CI selection. When impact cannot
   be bounded, report the missing assurance and the specific additional gate
   needed; do not automatically launch the broader lane. A phase that does not
   run the broad lane records `slow_cadence` with the command, trigger, and
   reason. If it runs the broad lane, it records `slow_gate` with its actual
   exit. Collection-only checks establish selection, never a run outcome.
5. **Review the claim before moving a test.** Runtime and age alone justify
   neither selection nor removal. Keep direct current-behavior checks in the
   ordinary lane. Reserve `census` for exhaustive tracked-tree assertions and
   `evidence` for historical bytes, fixed-commit replays, and retained-output
   pins. A broad gate omitted from the phase must have a named `cadence`
   disposition, such as milestone close. If one of its tests covers an affected
   contract, include that relevant test in the phase's impact closure even
   when the remainder stays on its broader cadence. Delete or consolidate a
   redundant assertion only after identifying the surviving protective case.

## Frozen v5.1 report-golden replay — explicit request only

The 664-row, 1,328-command replay is exhaustive historical work outside the
reduced phase selection. Changes to CLI, API, report renderers, normalizers or
population classifiers invalidate old evidence; they do not automatically
select this replay. Run focused legacy/report controls from the reduced lane
and state the limits of their current-byte claim. This frozen source replay is unavailable in the P1 target; neither its runner
nor answer manifests are shipped. If later explicitly selected, first restore
its exact reviewed dependency closure and amend the applicable spec. The original
source command, retained as historical context only, was:

```bash
uv run python tools/run_v51_historical_replay.py --workers 8
```

This runner accepts exact frozen pytest-module and answer-manifest digests,
runs all text/JSON observations in separate processes with at most eight
children, and requires the pinned mismatch set. A digest refusal, census or
model-binding change, missing/extra job, malformed observation or changed
mismatch set fails that explicitly selected claim; do not silently substitute
a subset. The reduced current-behavior gate is a different, narrower claim.
Do not select the legacy 664-row serial pytest node for ordinary phase work.
Run an expressly selected exhaustive replay in isolation and record worker
count, elapsed time, row count, command count and exit separately.

## Inheritance and invalidation

`inherit` is admissible only when durable evidence identifies the exact prior
command, result, source or artifact identity, and every input in the declared
boundary. Confirm that none of those inputs changed. Cite the evidence by path
and SHA-256.

Never describe inherited evidence as a verdict over changed bytes. When a phase
changes an input to a prior gate, either run that gate, replace it with a
justified current-commit impact closure, or give it a cadence disposition that
makes clear it is not part of phase acceptance.

At minimum, reconsider the selection ledger when the phase changes:

- global pytest configuration, markers, collection rules, plugins, or shared
  fixtures;
- dependency locks, build backends, package manifests, generated-file rules, or
  supported runtime/toolchain identities;
- a public schema, common loader, shared evaluator, CLI dispatch, or other
  surface with consumers beyond the named phase tests;
- an input, classifier, normalizer, expected-answer source, or environment used
  by inherited evidence.

If those effects cannot be bounded, state the missing assurance and name the
additional gate for explicit selection. A convenient focused set is not evidence
of bounded impact by itself; uncertainty does not authorize a broad replay.

## Parallel execution

Independent gates may run concurrently only when their state is isolated. Use
separate clean checkouts, containers, or CI jobs for tests that can share fixed
paths, caches, ports, mutable environment variables, or load-sensitive timing.
Do not introduce `pytest-xdist` as a semantic change merely to make a health
check faster.

Keep each gate's exact command, exit, output, duration, and evidence separate.
Dependencies remain serial: a consumer gate cannot begin before the artifact it
consumes exists. Parallel scheduling does not merge unlike claims.

## Phase record

Copy the final selection ledger into the completion record. For every `run`,
record the actual command and exit verbatim. For every `inherit`, record the
evidence digest and the unchanged-input check. For every `cadence`, name the
lane that retains the test and state why it is outside this phase's acceptance
claim.
