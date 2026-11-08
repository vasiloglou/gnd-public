# Plan review round 1: disposition

2026-11-07. Instrument: four local reviewer agents, UG-D1 (a) (owner ruling
relayed `(o1)`; the maintained six-seat panel remains the project's stated
bar and was not run). The instrument choice approves no bytes. This is
advisory evidence; it is not a plan-gate or spec approval.

## Subjects and limits

| Subject | SHA-256 | Retained snapshot |
|---|---|---|
| Plan r1.1 | `b2678c57e677525771a0eb921cdf1d6e188bbb488aca1c827a09e8f13e7c9946` | `evidence/plan-review-r1/unattended-model-growth-plan.md.snapshot` |
| UG1 spec r1.1 | `e7523244e4ab00a1a85f05590c592228e9a340c6f422e5d413c729b8ae96531e` | `evidence/plan-review-r1/phase-UG1-spec.md.snapshot` |

All four readers verified both digests, ran concurrently with fresh context and
one lens each, and read repository HEAD `5d9d8ba1` (source and tests identical
to the `12daa5b7` baseline). They used no credentials; the only network reads
were `gh issue view`. Probes ran in the session scratchpad. No reader wrote to
the repository. The snapshots keep the issue tracker labels that r1.2 drops
(UG-Q7). Reader reports were returned in-session; this file retains each
verdict and every finding with its disposition, condensed, not verbatim.

## Opinions

| Reader | Lens | Verdict | Blocking | Hardening | Completeness |
|---|---|---|---|---|---|
| 1 | correctness against production semantics | approve-with-fixes | 2 | 9 | 3 |
| 2 | implementability, pins and homes | approve-with-fixes | 0 | 10 (U1–U6, U9, F1, F2, F3, F5) | 4 (U7, U8, F4, F6) |
| 3 | protocol, authority, compatibility, privacy, docs | request-changes | 2 | 7 | 4 |
| 4 | test design, falsifiability | request-changes (UG1 spec); approve-with-fixes (plan) | 2 | 11 | 7 |

No reader contradicted an owner ruling. No reader found invented approval, a
downstream application name, or an action needing owner authorization.

## Triage method

A finding is accepted when it was reproduced by its reader or when the
plan author confirmed it against the repository. Spot checks by the author
(2026-11-07): the breaking `apply` stdin prompt (`evolve/cli_service.py`
about 716–731); the component index exists (`dev/components/`,
`scripts/components_index.py`, `project.md` last section); a deontic violation
yields `warning` (`checker/_core.py` about 2015); the validate payload is framed
(`payloads.py` comments on IF-P3-5); the population header carries an optional
`model_id` only; the `_sha256` helper-name ban; `evolve/service.py` is 2221
lines. Findings are unproved until reproduced; none is rejected as false.

## Disposition

`A` accepted and applied in r1.2; `P` accepted in part; `D` deferred to the
named spec with the obligation written into the plan; `O` owner question.

### Blocking

| Finding | Claim | Disposition |
|---|---|---|
| R1-B1, R4-B1 (and R2-F3) | UG1 T2/T3: `apply` of a rename/delete preview is breaking and prompts for the blast-radius digest; "exits 3" is false (11 on EOF, 74 under capture, hang on a tty). Reproduced by three readers | A: `_apply_breaking` helper, digest supplied via `builtins.input`; EOF case pinned to 11; T13 measured (UG1-Q1 answered); UG1-C8 |
| R1-B2, R4-B2 (and R2-F1) | T1 round 2 cannot yield a shape match: no existing fact type shares the signature; a non-empty group is true of any added fact type (mutant shows it vacuous) | A: round 2 adds `loan_is_due_on` restating `loan_has_due_date`; round 1 `existing == []` control; round 2 asserts `existing` names it |
| R3-B1 | "No component index" is false: `dev/components/` and `scripts/components_index.py` exist; `project.md` contradicts itself | A: reuse decision recorded (§1), `changed --strict` added to UG2/UG3/close gates and noted vacuous for UG1; O: UG-Q6 |
| R3-B2 (and R4-C4, R1-H7, R2-U6) | UG-R1 (byte-identical defaults) contradicts UG-D3 (c) "counts always reported"; the validate payload is framed and schema-closed | A: explicit UG-R1 carve-out (one `warnings` entry only when a span is unchecked), preferred design in §2.3 (ii), UG3-C3 redefined; if "always" cannot be met without a version bump the spec returns to the owner |

### Hardening

| Finding | Claim | Disposition |
|---|---|---|
| R1-H1, R2-U4, R4-C1 | "Clean population" is undefined; deontic violation is `warning`, `gnd check`'s exit band ignores it; vacuous/unchecked leave nothing checked | A: §2.2 defines clean as the constraint's verdict `pass`; UG2-C1/C2 enumerate warning/vacuous/unchecked/ledger/other-constraint/wrong-model cases |
| R1-H2 | Per-file checking is unsound for cross-file violations | A: UG-Q3 widened (composed input) and §2.2 |
| R1-H3 | Constraints have no stable id; checker message carries values | A: §2.2 maps by operation index and reference, counts only; UG-R6 reworded |
| R1-H4, R3-H3 | No model digest in the population header; `model_id` optional/warning | A: §2.2 and §6 reworded to layer-2 validity plus `model_id`; spec decides mandatory; exit bands 66/74/3 |
| R1-H5 | The modify cell fires on "neither" keys | A: §2.2 clears strengthening only |
| R1-H6 | UG2 plumbing under-specified (`models.py`, apply ordering, already-live branch) | A: §3 file list, §2.2 ordering and branch |
| R1-H8, R2-U7 | New locator traps: policy falls through to admit; `entries` min_length; replay; terminology | A: §2.3 (i) names the sites and the three traps; locator union terminology fixed |
| R1-H9, R4-H4 | T14 unsatisfiable as worded (preview embeds model text) | A: T14 uses canaries and an exclusion list |
| R2-U1, R1-C1 | UG-Q1 answerable now: edge allowed, zero allowances | A: UG-Q1 answered; risk row replaced; `policy.py` stays I/O-free |
| R2-U2 | UG2 sizing and pin files understated (MG2 about 650 source, 1016 test) | A: re-estimated; RF1 goldens for three interpreters, `tree.json`, `goldens.sha256`, `MANIFEST_SHA256`, `cli.md` listed |
| R2-U3 | RF6 risk row wrong: no `service.py` ceiling; the dynamic-candidate hash chain and package ceilings bind; phases must land serially | A: risk row replaced; §3 landing order; successor evidence in deliverables |
| R2-U5 | Population input handling: workspace/`safefs`; contract line "evolution does not … open the artifact"; a population-kind locator already exists | A: UG-R5 single-read/`safefs`; contract line listed for amendment; UG-Q3 first reading |
| R2-U6 | Counts cannot be added keys (schema `additionalProperties: false`) | A: see R3-B2 |
| R2-F2, R4-H3 | Final validate over three documents leaves the seed's `source.txt` spans unchecked; a tampered span on an unsupplied document exits 0 | A: fourth `--document`, exact argument list asserted; T9 per round with paired omit run pinned as the O14 deviation |
| R2-F3/F4/F5, R1-C2 | Replay harness traps: stdin hang, `--out` reuse, `proposal_id`, cwd, `_sha256` helper ban | A: §6.2 helpers; `support.digests`; UG-Q4 answered |
| R4-H1 | T5 does not discriminate "every" over existing subjects | A: T5(c) populated plus unpopulated existing pair; populated operand on both sides |
| R4-H2 | Exit 3 alone is vacuous | A: `_assert_refused`, UG1-C8; T3 uses unreferenced elements |
| R4-H5 | T4 control confounded | A: same-fact-type-without-`--populated` control added |
| R4-H6 | T-anon is not a real check | A: out-of-repo pattern file, digest and count only, positive control, wider scope |
| R4-H7 | T-src has no base and ignores untracked | A: base `12daa5b7`, `git status --porcelain` |
| R4-H8, H9, H11 | Per-round paths, stderr option naming, T13 unfalsifiable, T8d two cases, T11 prefix, fixture details | A: in T-table and §6.2 |
| R4-H10 | Matrix claims exceed the cases (75 reference scheme and strengthening; 104-1 shape only); evidence reference is a human check | A: existing nodes cited at record time; 104-1 "met (output shape only)"; mechanical node-id check |
| R3-H1 | Preview must not record the operator's path | A: ordinals plus digests (UG-R5, §2.2) |
| R3-H2 | Disclosure implications unaddressed (redact roles, count oracle) | A: UG-R6 and a UG2 spec obligation; disclosure row corrected (R2-U9) |
| R3-H4 | TOCTOU and `safefs` not pinned | A: UG-R5 |
| R3-H5 | Ruling provenance thin, untagged, versions inconsistent | A: `(o1)` tags, revision history, labels; D: the plan-gate record must carry the owner's verbatim message and re-confirm UG-D2/D3/D9 |
| R3-H6 | Tracker labels in README/plan | A: removed; O: UG-Q7 |
| R3-H7, R1-H8 | UG3 (i) understates the contract change (versions 1/2/3, forward-incompat, consumers) | A: UG-Q5 widened; release note in UG3's own deliverables; consumer tests in the gate |
| R4-C2, C3 | UG2-C4 "3 or 11" and wall-clock time-bound | A: one exit per case; counting spies |
| R4-C5, C6 | UG3 span locations, malformed/undeclared counting, strict-flag-without-`--document`; locator "modified/removed/duplicate" and golden bytes | A: UG3-C1/C2/C7; UG1 may pin golden proposal bytes |

### Completeness

| Finding | Disposition |
|---|---|
| R3-C1 docs one-home inventory incomplete; "cite, do not restate" untrue today | A: §5 adds `cli.md`, `docs/agents/evolve.md`, `gnd-model-evolve/SKILL.md`; contract wins; UG4-C5 grep |
| R3-C2, R2-U8 release notes and skill pins too late; census tests do not discharge | A: release notes in UG2/UG3; pins named in the UG2/UG3 gates; sentence corrected; UG4-C3 |
| R3-C3 evidence record | A: the D-13 record carries the population digests (§2.2) |
| R3-C4 stray tab, disposition-note count | A |
| R2-F6, R1-C3 sizing, gate mismatch, O13/T11 mapping, T12(b) service-level clause, T6 contract citation | A |
| R4-C7 UG4-C1/C4 have no executable result | P: UG4-C1 gains the UG4-C5 grep; UG4-C4 stays `inspected`, stated |

### Not accepted

None rejected. Two items are deferred rather than applied: the exact
exit (3 or 11) of a changed population at the same path (UG2 spec pins it, the
plan names the choice), and whether the strict flag's no-op against a model
without the mode is an error (UG3 spec pins it).

## Stop rule

Round 1 produced four blocking text defects and a long hardening list, mostly
accurate and mostly about the UG1 spec's exit claims and UG2/UG3 definitions.
The plan's stop rule (at most one confirmation round after round 1, restricted
to blocking themes) leaves a confirmation round to the owner: r1.2 is
repaired, not re-read. The author recommends the owner rule on whether to run
it before the plan gate.
