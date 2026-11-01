# Plan review -- round 1 disposition

2026-11-01. Instrument: four local reviewer agents (NM-D9, read from the owner's
`(o2)` reply; provisional until confirmed at the plan gate, per R3-F8). The
instrument choice approves no plan or spec bytes.

## Subjects and limits

| Subject | SHA-256 | Retained snapshot |
|---|---|---|
| plan r1 (with NM4) as reviewed | `ec9cea0eb204934a8cd390410bed31750312eb2db369bee186353ecdc6e5db63` | `evidence/plan-review-r1/why-not-near-misses-plan.md.snapshot` |
| NM1 spec r1 as reviewed | `e3855ca569e890a994f015b64f5c64c651f2416f7b4e7b499ec529737913b670` | `evidence/plan-review-r1/phase-NM1-spec.md.snapshot` |

All four readers verified both digests. They ran concurrently as local model
agents with fresh context and one lens each; no paid tools or credentials; the
only network read was issue #70. Probes ran only in the session scratchpad; no
reader wrote to the repository (checked with `git status`).

## Opinions

| Reader | Lens | Verdict | Blocking | Hardening | Completeness |
|---|---|---|---|---|---|
| [1](plan-review-r1-reader-1.md) | correctness against production semantics | request-changes | 3 | 4 | 2 |
| [2](plan-review-r1-reader-2.md) | implementability, pins and homes | request-changes | 5 | 3 | 2 |
| [3](plan-review-r1-reader-3.md) | protocol, authority, compatibility, privacy, docs plan | request-changes | 3 | 6 | 2 |
| [4](plan-review-r1-reader-4.md) | test design, falsifiability | request-changes | 2 | 6 | 2 |

Total: 40 findings, 13 blocking, which collapse into **7 distinct blocking
themes** (A-G). None was refuted.

## Coordinator reproduction

Run from the readers' scratch probes against `33c260e`:

- R2-F2 (`probe_repeat_free.py`): `WhyNotInternalError: a near-miss row matches
  exactly` on a valid rule with a repeated free variable. Confirms theme A.
- R2-F3 (`probe_public_probes.py`): public `work.probes` moves on g1 (4→6), g2
  (5→7), g14 (4→6), g19 (3→6); g9 differs too. Confirms theme B.
- R2-F8 (`probe_schema_view.py`): every raw golden relabelled `redacted` fails
  the current schema. Confirms theme H.
- `grep -rlE '"redact": *true' src/gnd/examples` (excluding recordings): 0 files.
  Confirms the missing example in theme O.

## Themes and proposed repairs

Blocking themes first. "Owner" marks a decision the plan author must not make.

| Theme | Findings | Defect | Proposed repair |
|---|---|---|---|
| **A** | R1-F1, R2-F2, R4-F2 | A row inconsistent on a repeated free variable is offered as a near-miss and trips the exactness invariant: valid input crashes. | Definition: a candidate row must pass production's per-row checks except the bound-role comparisons (constants exact, repeated non-bound variables consistent by identity). Index over that filter; same rule in the oracle; consistent and inconsistent repeated-variable cases. |
| **B** | R1-F2, R2-F3, R4-F1 | NM1's public parity (T15) cannot hold: the search charges public `work.probes`; the docs example also moves; the strip is recursive. | Proposed: the kernel takes `near_misses: bool = False`; the service does not enable it until NM3, so NM1 has no public diff and no strip. **Owner** may instead accept the probe changes in NM1. |
| **C** | R2-F1 (blocking); R1-F3, R4-F4, R3-F6 | The search is quadratic in pairs and, charged to the shared `probes` ceiling, can turn exit 0 into exit 4, contradicting NM-R1. | Proposed: count without enumerating pairs (per normalized key, distinct samples × distinct rows) and build only the 5 smallest pairs, so cost is rows + bindings + 5, charged to `probes`; plus a separate search cap that, if reached, sets `near_miss_truncated: true` and never fails the request. NM-R1 then holds literally. **Owner** may instead accept a recorded exit-4 exposure. |
| **D** | R1-F4, R3-F1; R2-F6 | `--disclosure internal` overrides `GND_DISCLOSURE=customer`: the lock can be bypassed. | The option may only tighten (`customer` wins from either source; `--disclosure internal` under a customer environment exits 3). One context-variable resolver set by the CLI and read by API functions. State the threat model: the lock binds out-of-process callers of the public CLI and `gnd.api.__all__`, not code running inside the Python process. |
| **E** | R3-F2; R1-F6 | "Customer withholds population values" contradicts mapping customer to declared redaction, which hides only declared roles (none in any packaged example). | **Owner:** (a) customer = declared-role redaction in the check family plus fully redacted witness-lane views and why-not, refusing every raw request; or (b) customer withholds every population value everywhere: a new whole-value projection for 13 output kinds plus `discover` and ILP export, with real scope and compatibility cost. Author's proposal: (a), with the leak test's secret set defined per convention. |
| **F** | R3-F3, R2-F4; R1-F7 | The site inventory misses `witness-view --raw`, four (not two) export raw parsers and their Python `raw=` functions, `EvaluationSession` and `judgments` keywords, `api.witness`/`replay`, ILP export and `discover`; the proposed table test cannot see API sites. | Enumerate every site in §1 and NM2-C2. Build the table test from the parser walk (`--raw`/`--unredacted` actions), `inspect.signature` over `gnd.api.__all__`, its classes and `gnd.export.service`, and `emitter_specs()`. Decide per site, including `api.witness`'s certificate and `--out`. |
| **G** | R2-F5; R3-F4 | Session outputs are fixed at `applied` in the wire format, and session feedback goes to agents that may be external providers; `internal` cannot unredact them without a wire change and may send sensitive values out. The 2026-10-25 ruling on `discover` is not cited. | Proposed: agent-bound streams (session feedback, attempts, results) and `discover` stay as today in every mode; ILP export keeps refusing declared roles. Cite the 2026-10-25 ruling. **Owner** confirms. |
| H | R1-F5, R2-F8, R3-F8 | WN2-R1/R2/R3 were fixed in WN2; the plan calls them open. | Drop O8 and the carryovers; NM3-C2 adds the two fields to `$defs/blocker` and `near_misses: const "redacted"` to `redacted_clause.blocker`. |
| I | R3-F8 | Provenance overclaims: §1 says `(o1)` rules NM-D2..D6; §2.1 tags NM-D6 `(o1)`; NM-D9 marked "Ruled". | §1: `(o1)` covers D1, D3, D4, D5. Remove the D6 tag. NM-D9 provisional, confirmed at the gate. |
| J | R1-F8, R2-F7, R3-F6 | NM-R5 "unset is byte-identical" contradicts the why-not v2 payload and the root help; 12 RF1 exit goldens, `cli/tree.json` and 3 help goldens change. | Scope NM-R5 to disclosure decisions, excepting the enumerated why-not v2 changes and root help/usage; list the regenerated RF1 goldens; fix §5's "opt-in only". |
| K | R3-F7, R2-F6 | Refusal bands and envelopes are unspecified; a bad `--disclosure` value exits 64 through `_BandSafeParser`; check-family exit 3 means `ill_formed`; why-not and judgment reason enums are closed. | Pin: 64 for usage errors on the option; a bad variable exits 3 only on disclosure-bearing commands; per-lane refusal payload specified in the NM2 spec, with any enum addition recorded as a schema change; mixed case refused. Add 64 to NM-D10. |
| L | R3-F5 | The mode does not reach child processes (`solve` stations, `exp run` agents). | Forward the resolved mode to `solve` children; add `GND_DISCLOSURE` to the agent environment allowlist; one test per spawner. |
| M | R3-F9, R2-F9 | An ambient `GND_DISCLOSURE` would change every test and docs result. | Autouse fixture and `run_pages` scrub (NM2); docs blocks set the mode inline; a negative control. |
| N | R3-F10 | Docs ownership contradicts itself between predicates 4-5, NM3-C4 and NM4. | NM3 writes the normative near-miss section of `why-not.md` (the home moves with the field) and the spelling-gap how-to section; NM4 owns everything else. Predicates reworded. |
| O | R3-F11, R2-F9 | The inventory misses 6 grep hits (incl. the `redact` declaration's home); no packaged example declares `redact`; new pages are not registered in `run_tutorials.py` groups. | Add the six rows; add a packaged redaction example (NM2) and its installed-docs entry; register groups and parametrization in NM4; add a real-run checkpoint after NM1 (DC1b) besides the illustrative DC1. |
| P | R4-F3, F5, F6, F7, F8, F9, F10; R2-F10 | Test-design gaps: T16 unreachable; the generated oracle corpus never produces a near-miss; T1 misses punctuation-to-space and step order; T8 unbuildable; no dedup discriminator; counters disagree; wrong to-update list; T10 input unspecified; sizes missing. | Apply each reader's fix: T16 via hand-built `previous`; spelling variants in the generator with a minimum non-zero count; T1 adds `ACME-CORP`/`ACMECORP`, `Acme . Corp`, full-width punctuation, and pins `ACME-CORP` ≠ `ACME CORP`; T8 as a key-function unit test plus a Number case; dedup fixtures; counters = `probes` only; correct literal list (t2, t13b, t13c, kernel:373, :416); T10 on an enveloped kernel dict with descent; per-phase sizes; RF5 fixture under NM3-C2. |
| Q | R1-F9 | Normalization depends on the interpreter's Unicode database. | State it in the normative text; test inputs stable across 3.11+; record `unidata_version` in the NM1 record. |

## Owner decisions raised by this round

1. **E:** what `customer` withholds -- (a) declared roles + all witness-lane
   values (proposed), or (b) every population value everywhere.
2. **C:** whether the search may fail a request -- truncate with a flag
   (proposed), or accept a recorded exit-4 exposure.
3. **B:** NM1 public diff -- search off on the service path until NM3
   (proposed), or accept probe changes in NM1.
4. **G:** agent-bound session streams, `discover` and ILP export unchanged in
   every mode (proposed).

## Convergence

This is round 1 over draft bytes, so the self-inflicted ratio is not defined.
Majority of findings are hardening, not completeness, so the round does not hit
the completeness stop rule. Per `review-convergence.md`, a confirmation round
over the blocking themes is expected after repair, if the owner selects one.
Repaired bytes carry no review opinion until then.
