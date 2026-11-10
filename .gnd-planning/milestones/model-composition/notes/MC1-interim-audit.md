# MC1 interim coverage audit at the size pause

2026-11-09. This is an incomplete implementation audit, not a completed phase
or an independent review. Source edits paused when the conservative gross
source/schema count reached 763, against the 750-line stop. The size choice
is pending with the owner. No implementation commit or PR claims acceptance.

## Observed results

- Frozen beast-3 census at 459ca8d2: 400 members, 334 successful loads,
  66 load refusals, one canonical-identity refusal among the successful loads.
- Both serializer experiments (explicit JSON exclusion and wrapping serializer)
  match every baseline observable; the wrapping serializer is selected.
- Baseline and candidate `ruff check src tests`: 13 errors each. These are
  known reds, independently reproduced on the frozen baseline. Full lint
  is not reported as green. The baseline output is retained, with declared
  operator-home sanitization.
- The full default baseline suite remains running on beast-3 in its isolated
  checkout. Launch is not a completed gate. Candidate full/default and broad
  census gates remain owed after source completion.
- The initial refusal corpus produced 45 failures against the old loader;
  `evidence/MC1/red-refusals.txt` retains the pre-implementation output.
- Current guard controls expose an unfixed API judgments refusal: the public
  adapter changes `include:unsupported-route` into its generic binding error.
  It returns band 3 but fails the distinct-reason criterion. Fixing it is
  deferred until the size gate is ruled.
- `git diff --check` also reports a new trailing blank line in `_validation.py`;
  removing it is deferred with source edits, rather than claiming cleanliness.

## Remaining audit work before a completion claim

| Contract | Current evidence / remaining work |
|---|---|
| MC1-C1 / T1-T4 | Composed content and check JSON twin comparisons exist, with violating and truly clean populations. Add explicit validate twin text/JSON coverage, retain a committed independently authored twin and assert allowlisted fields separately. |
| MC1-C2 / T5-T19 | Initial refusal controls cover all major boundary reasons and the direct new functions. Expand shape-position, integer/depth/nonfinite cases and text/JSON CLI coverage for each refusal. Root symlink refusal needs its own case. |
| MC1-C3 / T21 | All-paths-before-hash and hash-before-parse controls exist. Add forbidden-before-standalone and collision-before-composed-validation sentinels. |
| MC1-C4 / T22 | New merge/index timing and a quadratic negative control run directly on the new layer. Retain observed medians and ratios in evidence, not only pass assertions. |
| MC1-C5 / T23-T24 | Producer and marked census test exist. Run the explicitly selected broad candidate gate on beast-3, demonstrate the dirty comparator control, and publish original/new member counts. |
| MC1-C6 / T25-T26 | Unrooted refusals, orphan attachments and rooted bytes composition tested. |
| MC1-C7 / T27-T29 | Both loader routes bind included reference-owned fact types against the existing dispatch reference corpus. Add check comparison and an own operation attempting to write a reference-owned included relation. |
| MC1-C8 / T30-T33 | Acyclic attachment twin behavior and invalid target are tested. Add mandatory attachment behavior, own-target refusal, and included plus attached constraints on one host with both enforced. |
| MC1-C9 / T34-T40 | Own operations compile, subtype/rejected history load, note order and metadata are tested. Add derived own fact type crossing the include boundary and full source-mode direction controls. Extend subtype coverage to check parity. |
| MC1-C10 / T41 | Actual guard tests cover all inventory rows, split where they have multiple public entry points; one judgments API case remains red. Audit named runtime/oracle sites again; no exported runtime bytes are edited. Re-run each changed adapter's affected consumer controls. |
| Identity / T42-T43 | Independent loaded envelope and declaration-path mutation tested. Add included-content mutation independently of declaration-path mutation. |
| Origins / T44-T45b | Owned attachment error remaps to its authored location. Complete anonymous included constraint and mixed-host included/owned warning cases; pin selector-path spelling to the normative format. |
| Homes / T46 | Graph dirty controls pass after eliminating a new CLI entrypoint edge. Alias identity controls exist; source-scan observer and affected patch sites still need final audit. |
| Temporal / T47-T48 | Plain version-4/version-5 temporal model load parity exists; add a version-3/4 temporal vocabulary included by version 5. |
| Frozen exceptions/runtime / T49-T51 | Oversized include-free diff spelling and runtime byte identity tested. Add the independent baseline exported-program byte comparison; retain its source identity and settings. |
| Index and normative prose | Component entries updated and generated views regenerated. Reread unchanged descriptions of affected consumers and resolve any generated staleness after final source edits. Existing format version prose needs to cite/admit version 5 consistently. |
| Review and record | No independent phase reviewer has run yet. A Codex CLI phase diff review, reproduced findings, refactoring disposition, exact gate evidence and a completed phase record remain owed. |

The following gates are separate: baseline default suite; candidate focused
checks; candidate broad census; candidate default suite; lint; components;
independent diff review; delegated completion ruling. No successful subset
stands in for the remainder. MC2-MC4 and the owner docs checkpoint have not
started; merge, publication, certification and issue closure remain outside
this partial checkpoint.
