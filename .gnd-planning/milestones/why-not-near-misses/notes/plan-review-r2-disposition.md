# Plan review -- round 2 (confirmation) disposition

2026-11-01. Instrument: four local reviewer agents (NM-D9, provisional), run at
the owner's direction `(p1)`: "yes" to "apply all the proposed answers as
revision r2 and run a confirmation round on the blocking problems". The
direction approves no plan or spec bytes.

## Subjects and limits

| Subject | SHA-256 | Retained snapshot |
|---|---|---|
| plan r2 as reviewed | `211d9e018febdbcc4c2a76ebbb43fce631532fd3af8953f88694793490a665de` | `evidence/plan-review-r2/why-not-near-misses-plan.md.snapshot` |
| NM1 spec r2 as reviewed | `1b739a57ce49f7418936dabd82113a7f35579301c73015bef6a04a5087de1d72` | `evidence/plan-review-r2/phase-NM1-spec.md.snapshot` |

All four readers verified both digests, read the round-1 disposition and notes,
and diffed r1 against r2. Fresh context, one lens each (same lenses as round 1),
run concurrently as local model agents; no paid tools or credentials. Probes
only in the session scratchpad; nothing written to the repository.

## Opinions

| Reader | Lens | Verdict | Findings | Self-inflicted |
|---|---|---|---|---|
| [1](plan-review-r2-reader-1.md) | correctness | approve-with-fixes | 8 | 8 |
| [2](plan-review-r2-reader-2.md) | implementability | approve-with-fixes | 7 | 6 |
| [3](plan-review-r2-reader-3.md) | protocol, privacy, docs | approve-with-fixes (C3-F1 before the gate) | 11 | 8 |
| [4](plan-review-r2-reader-4.md) | test design | approve-with-fixes | 7 | 5 (C4-F7 counted pre-existing) |

## Round-1 blocking themes

| Theme | R1 | R2 | R3 | R4 | Result |
|---|---|---|---|---|---|
| A eligibility / crash | repaired | repaired | repaired | repaired | **repaired** (reader 1: 400-seed fuzz, keyed count = brute force, invariant never fired; reader 4: 200 SPELLING seeds, 0 errors, 0 disagreements) |
| B NM1 public diff | repaired | repaired | repaired | repaired | **repaired** |
| C cost / exit 4 | repaired | repaired | repaired | repaired | **repaired**; 512×512 now 1,024 inspections |
| D lock | repaired | partly | partly | repaired | **partly**: fail-open ordering (theme S) |
| E customer scope | repaired | repaired | partly | repaired | **repaired** in substance; wording (theme V) |
| F site inventory | repaired | partly | partly | partly | **partly**: default-raw sites invisible (theme T) |
| G agent streams | repaired | repaired | partly | repaired | **repaired**, but a neighbouring r2 edit reopens the risk (theme R) |

## Convergence: the stop rule

27 of 33 findings attack text added or changed in r2: a self-inflicted ratio of
**0.82**, above one half. Under `review-convergence.md` review stops here; a
further round would mostly review its own repairs. Precedent:
derivation-why-not stopped at 0.93 and applied the round-2 repairs as r3 with no
further round, the owner deciding plan approval over r3.

## Themes and proposed repairs (for r3)

| Theme | Findings | Defect | Proposed repair |
|---|---|---|---|
| **R** (blocking) | C3-F1, C1-F7, C2-F4, C3-F7 | Forwarding the resolved mode to `exp run` agents sends `internal` to possibly external agents, undoing the protection G set out; a schema-v6 agent path, other spawners and the verifier environment are unaddressed; `gnd.agents` cannot import the resolver. | Forward only `customer`; under `internal` or unset, child environments are as today. Pass the value as a parameter from `gnd.exp` (layer-legal), covering both agent paths (`agents._private_environment`, `exp/adapter_policy.py:303-312`). Enumerate spawners mechanically (callers of `run_bounded_process`, `Popen`, `create_subprocess_exec`) with a rule per spawner; pin that `verifier_environment()` never carries the mode. `solve` forwards via environment (argv records unchanged). Spawners are disclosure-bearing, so a malformed value exits 3. Docs: forwarding sets a default for children, not a lock. |
| S | C1-F8, C2-F2, C3-F2, C3-F3, C2-F6 | Fail-open: a malformed variable plus `--disclosure internal` yields `internal`; a context value outranks a `customer` environment; the context variable is not reset. | The resolver validates `GND_DISCLOSURE` first (malformed → exit 3 on disclosure-bearing commands, even with the option); `customer` from either source wins inside the resolver, not only in the CLI; `main` resets the token in `finally`; the option is root-only (stated in help and `cli.md`). NM2-C1 cases for each. |
| T | C2-F1, C3-F6, C4-F5 | Discovery sees only flagged sites; `api.why_not`, `api.witness`, `api.replay` (raw by default), `api.judgments` (not in `__all__`), `admission`, `fidelity`, ILP export and `discover` escape; hand rows are never checked against code. | Every parser leaf (57) and every public callable of `gnd.api` (module level), its classes and `gnd.export.service` must have a row: *site*, *value-free*, or *emits values in every mode*. A reverse check that every row resolves to live code. Rows added for `api.why_not` and `admission`; `fidelity` and ILP export classified "emits values in every mode" and listed in `disclosure.md`. NM-R4's runtime home is `gnd.disclosure`; the table is the coverage test. |
| U | C2-F3 | The projection point per lane is unspecified; projecting in the shared `witness.service` function breaks `gnd witness` (`KeyError` at `witness/cli.py:68`); check-family handlers use private `api._run_*`. | The plan names the rule and the NM2 spec the code: witness-lane projection happens in thin `gnd.api` wrappers (ending the identity aliases, recorded in the shim inventory) and in the CLI after it has read the certificate; check-family resolution happens in the shared `_run_*` helpers. |
| V | C2-F5, C3-F5, C3-F8 | "Every value in export outputs" contradicts ILP "unchanged"; NM-D12's export extension is broader than the accepted proposal; "raw request on these still refused" is vacuous; §5 overclaims. | Say "witness-lane, `lean` and `souffle*` outputs" everywhere; record the `lean`/`souffle*` extension as the author's reading (their default outputs are value-free), not as covered by `(p1)`; drop the vacuous sentence; scope §5 to "mode unset" and list customer-mode contract changes for the release note. |
| W | C3-F4, C3-F9 | Threat model contradicts itself for API callers; the redacted near-miss count is a normalized membership oracle under `--row`. | Protected party: end users whose requests an operator-controlled wrapper forwards into CLI argv or API arguments; in-process, the mode is a guard. Name the membership signal in `disclosure.md`; proposed to keep the count. **Owner** may instead choose a boolean in customer mode. |
| X | C1-F1, C4-F2, C4-F4, C4-F1 | The default cap is unreachable (inspections ≤ `work.probes` ≤ 200,000); predicate 1 asks for truncated generated reports nothing produces; the oracle cannot match truncated reports; rows-first truncation reports 0. | State the invariant; the cap guards lowered limits; inspect bindings before rows; predicate 1 and NM1-C3 drop "truncated"; a T18b pass with a lowered cap checks kernel count ≤ oracle and pairs ⊆ oracle pairs; exact truncated values as kernel literals; docs say the flag is false at default limits. |
| Y | C1-F2, C1-F3, C1-F4, C1-F5, C4-F6, C4-F7(d,e) | Definitions imprecise: representative of identity-equal values depends on order; the count is over distinct projections but worded per row; the eligibility relaxation for repeated bound variables is unstated; cost wording disagrees; T19 unbuildable. | Representative = canonical minimum of each identity group (kernel and oracle); `near_miss_count` defined over distinct (binding-projection, row-projection) pairs; state that bound repeated variables are compared to the binding rather than checked for in-row consistency, and why the invariant still holds; "every row of the fact type plus every binding; at most 25 pairs per key, 5 reported"; a named `_eligible_rows(atom, bound)`; T19 compares binding keys of assignments; a B-non-empty eligibility unit test. |
| Z | C4-F3, C4-F7(a,b,c) | Counter tests cannot catch per-pair enumeration; T1 misses NFKC-order variants; T4 has no literals; T11 does not span keys. | T12c counts pair constructions (≤ 25 per key); T1 adds `℅` → `co`; T4 pins count and pairs; T11 spans two keys with interleaved order; T12b observes inspections by bracketing the cap; T12b/T12c fixtures pinned with rows spelled differently from bindings. |
| AA | C1-F6, C2-F7, C3-F10, C3-F11 | Schema shapes unstated; RF1 manifest pin omitted; the spec drops NM-R2; DC1b's move unrecorded. | NM3-C2: `near_misses` `oneOf [array maxItems 5, const "redacted"]` in the shared closed blocker, required only when `kind` is `atom`, per-length `if/then` for count ≥ length; NM2-C5 adds `goldens.sha256`, `MANIFEST_SHA256` and `tests/test_rf1_pin_harness.py`; NM1 spec binds NM-R2; one sentence records DC1b moving to after NM2 (NM1 has no public path). |

## Owner decisions raised by this round

1. **Stop-rule outcome:** apply themes R-AA as r3 with no further review round,
   then decide plan approval over r3 (proposed, following precedent); or run a
   third round.
2. **R:** forward only `customer` to child processes (proposed).
3. **W:** keep the redacted `near_miss_count` and name the membership signal in
   the threat model (proposed), or show only a boolean in customer mode.

r3 bytes, if written, carry no review opinion.

## Owner direction on this disposition

2026-11-01 `(p2)`: asked "Should I write r3 with all of these fixes and no
further review round, then hand you the plan-approval decision? Or would you
rather I run a third review round over r3?", the owner replied, quoted: "Yes,
write r3". Read as decision 1 (apply R-AA as r3, no further round), decision 2
(forward only `customer`, ruled as NM-D16) and decision 3 (keep the redacted
count and name the membership signal, ruled as NM-D17). The direction approves
no plan or spec bytes; plan approval over r3 remains the owner's decision.
