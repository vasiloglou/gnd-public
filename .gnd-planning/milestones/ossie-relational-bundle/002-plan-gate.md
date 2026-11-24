---
milestone: ossie-relational-bundle
station: plan-gate
scope: plan-gate
date: 2026-11-24
skill: "start-milestone (planning); the gate ruled by the owner, auto=false"
gates:
  - command: "uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/ossie-relational-bundle/evidence/plan-review-r1/review-request.json --out .gnd-planning/milestones/ossie-relational-bundle/evidence/plan-review-r1/panel-run --effort high --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
  - command: "ruling: owner approved .gnd-planning/milestones/ossie-relational-bundle/notes/ossie-relational-bundle-plan.md sha256 52d946a48c7acd82562afbbd6a8057fe7da8a58bac328218c0a483eab13c6e1d"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/plan-review-r1/PANEL-REVIEW.md
    sha256: 40a36b724d5e682185a3c9d9fbaf76af658ac9ffcde9b47a3c0a5a2cb86c8203
  - path: .gnd-planning/milestones/ossie-relational-bundle/001-panel.md
---

# Plan gate: ossie-relational-bundle r2

Date: 2026-11-24. `auto=false`.

## Gate output (verbatim)

The gate is the owner's ruling, given in the planning session on 2026-11-24
after PR #264 was opened with r2. The owner wrote:

> Approve r2 with the proposed rulings

The digest of the approved bytes was computed from the committed file
(commit `808c328f`) before this record was written:

| Artifact | SHA-256 |
|---|---|
| `notes/ossie-relational-bundle-plan.md` (r2) | `52d946a48c7acd82562afbbd6a8057fe7da8a58bac328218c0a483eab13c6e1d` |

**The plan is not edited to record its own approval.** Its status line still
reads "Not approved", and its §10 says "All open at r2". This record is
what changes that, following the literature-host-interfaces precedent.

**Review state of the approved bytes.** The light panel reviewed r1
([record](001-panel.md)). r2 applies all 16 of its fixes and was **not**
reviewed. The owner approved r2 knowing that; this is the D9 ruling below.

## Rulings

The gate rules all eleven decisions as plan r2 §10 proposes them:

| ID | Ruling |
|---|---|
| D1 | Reopen ossie-interchange OD1 to (b), ontology plus the relational layer. Take OD3 through an **external** binding file, with no model-format change. This supersedes OD1 and OD3 for this milestone's scope only. |
| D2 | (a). By default, export writes five files, and `--ontology-only` keeps today's three. `--relational` is not added. |
| D3 | The `--max-output-bytes` ceiling is 256 MiB (268435456). (b): OB1 also adds `--max-input-bytes` to `gnd import ossie`. It moves the read, YAML guard, JSON `loads` and loss-size caps, and keeps `model-size` and `MAX_MODEL_BYTES`. |
| D4 | Non-primary confirmed alethic uniqueness within one table becomes `Dataset.unique_keys`. Uniqueness spanning tables goes in the `GND` extension. |
| D5 | Ruled inside OB2 from the OB2-C5 measurement, at an owner gate before OB2 is recorded. The proposed defaults are Halpin's (absorb; first id). This ruling approves that procedure, not a variant. |
| D6 | No population rows in any relational file, and the loss-report refusal stays. The semantic model, and the mapping minus its binding fields, are byte-identical with and without a population. OB3-C7 asserts how the other files differ. |
| D7 | A GND-owned schema `gnd-physical-binding/1`, with the issue's member names and a closed SQL-type map. |
| D8 | NFKC, then casefold, then keep only Unicode L* and N*. Empty results and collisions are refused. The four contradiction classes of r2 §10 D8 are refused. |
| D9 | Go to the plan gate with r2 unreviewed. No second panel round. |
| D10 | Ask the reporter for: the three local diffs (reference only), the size of their flattened model, the meaning of `extension_roles`, and whether they can run the external acceptance. File the three issues on GitHub. |
| D11 | Deferred: decide after D10's answer and the output-to-source ratio OB1-C2 measures. If needed, add a phase OB1b. |

## Effects

- **OB1 is unblocked at plan level.** D3 is ruled. Its spec, the
  [OB1 spec r2](notes/phase-OB1-spec.md) (sha256 `068f24c4…3824`), still
  needs its own owner gate before any code. Approving the plan does not
  approve the spec.
- **OB2 is unblocked at plan level.** D1 is ruled, so its spec can be
  drafted.
- **OB3 and OB4** are ruled on D2, D4, D6, D7 and D8, and remain sequenced
  after OB2 and OB3 respectively.
- **D10 involves two acts outside this repository.** Contacting the
  reporter, and filing three public GitHub issues, are each confirmed with
  the owner before they happen, including the text. That text names no
  downstream project or customer.
- **Merge.** Merging PR #264 remains the owner's separate decision.
