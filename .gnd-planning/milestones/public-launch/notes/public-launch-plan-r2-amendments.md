> Public-safe adapted counterpart. Historical proposal/status sentences below
> are retained as history; [owner rulings](owner-rulings.md) establish current
> accepted status. Source originals remain authoritative for migration amendments.
> Original SHA-256: `05d539e9fc72378678a75e71dc110e6993d279e864b5804cee836974d4d3e0ba`.
> Links to private historical records/raw review are replaced by explicit limits
> and public-safe summaries. No panel opinion covers these adapted bytes.

# Public-launch r2 — review amendments

**Status:** proposed for the owner plan gate, 2026-10-01. Plan of record once
approved: [candidate r1](public-launch-manifesto-and-plan.md) plus these
amendments, with r2 taking precedence. The reviewed r1 bytes remain unchanged
at SHA-256 `ee92ef92097edaf9cbb02b27425b4d12102dcf069dc36e7da8560389cc62edb3`.

The original source-held panel report retains all 22 concerns from six complete
responses, and its private disposition table records each author decision.
The linked [public-safe review summary](review-summary.md) provides counts and
limits only; neither full concerns nor individual dispositions are republished. These amendments were written after the panel: no reviewer
opinion is claimed over r2. They change the proposed plan, not runtime behavior.

The name remains **public-launch**. P0–P5 own launch; P6–P7 are the separately
activated **public-transition** successor. No semantic version, license,
publication, delegated approval or retirement is inferred from the review.

## A1 — Harvest the whole governing plan

Replace section 8's selective harvest list with **all sections 0–10**, the
completion predicates, accepted amendments and applicable predecessor records.
The phase spec lists each binding obligation and its applicability, rather
than omitting a section because its rules are outside the phase bullets.
This includes section 2's record/amendment rules and section 3's authority,
handoff, reconciliation and rollback conditions.

This is a planning hardening correction. Gemini called the omission critical
and blocking; that assessment remains in the report. The author's narrower
assessment is that the omitted clauses already bind the plan, but the harvest
instruction could cause a spec to miss them. No runtime defect is established.

## A2 — Demonstrate the final contributor workflow before launch

P1's outcome and P1-C1 are explicitly conditional on its recorded temporary
bootstrap build/tool. They do not establish target-only contributor readiness.

Add **P4-C5**: from a fresh target-only checkout with the target-built candidate
wheel and no source checkout, editable source installation or private-document
dependency, verify removal of P1's temporary bootstrap, discovery in both
runtime roots, the fresh-contributor AGENTS/CONTRIBUTING instructions, and the
bounded phase-spec/record exercise. Inspect resolved tool/module/link paths.
Record actual commands, outcomes and the dependency boundary. This check joins
the section 9 P4 mandatory row and is required for the contributor claim at P5.

P1-C4 and the P4 exercise use a scratch tree or clearly labeled
`docs/development/examples/` artifacts outside real milestone record numbering.
Every sample states that it is a protocol exercise, not approval or completed
work. Its expected gates are not presented as executed production gates.

P1-C2 additionally checks zero dangling links in both discovery roots. The
existing P1 rule already forbids links whose targets do not exist. Defer all
installer-owned links until their packaged target trees are present, normally
P2; preserve their generated identities when they are actually introduced.

## A3 — Give public-owned work a public planning home immediately

Clarify section 2: until P6, the source owns **this migration's governing-plan
amendments and original migration records only**. When a unit becomes
public-owned, new development milestones, specs, records, decisions and
question entries for that unit are canonical in `gnd-public/.gnd-planning/`.
Public contributors never need write access to the source registry. If a
question crosses units, record one canonical owner plus cross-references.

Existing source questions keep their original IDs, origin and state. Any
ownership transfer has an explicit record in both ledgers, not two independent
canonical answers. P6 reconciles and retires remaining migration authority;
it does not postpone ordinary public development until an unscheduled date.

Add **P0-C5** and an **obligation register** deliverable: enumerate inspected
carryovers with current state, origin, owner/milestone/repository and overlap
with migration units, including the v7.2 artifact-copy item, existing broad
historical-suite questions and any v7.3 work present at execution. Add this
register to section 9's P0 verification row. P0 records an explicit sequencing
decision for overlapping runtime work: finish it before that unit's handoff,
or transfer its ownership/scope through an owner ruling. It cannot silently
block handoff forever or disappear when paths move.

## A4 — Publish sufficient launch provenance at the right checkpoint

Add **P5-C5**: before the visibility change, the target contains public-safe
versions or summaries of the effective plan, decisions already made, selected
unit/batch ledger, coverage map, history mapping and candidate release dossier
with hashes. Each identifies its origin and any redaction or unavailable claim.
Internal originals may remain private, but no required public development or
verification step depends on inaccessible evidence. Add this obligation to
the section 9 P5 row and section 2's record-publication duties.

After publication checks, append actual release results. At the later
public-launch close, publish a public-safe close-panel outcome and close record
in the target as well as retaining source originals. The close gate verifies
their availability and the named P6 owner/trigger. **Future close results are
not prerequisites for the earlier visibility change or P5**, because the
public-index checks must happen before those results exist. This is the timing
correction to Qwen's otherwise useful proposal.

If the owner elects to retain any underlying item privately, the target carries
the explicit decision and verification limit. Such a limit cannot excuse a
missing dependency needed to build, check or maintain the advertised product.

## A5 — Review and authorize trial distribution before disclosure

P4-C1 uses **prepared release-candidate artifacts**: the phase's hash-recorded
wheel/sdist and documented inputs, installed into a fresh environment. It does
not require an earlier public-index upload.

Before any trial recipient receives an artifact or repository access, the P4
spec names the channel, payload identities, recipients/access scope and the
existing or new authorization covering that disclosure. Inspect the exact
candidate content before sharing. Repository access also requires checking
the refs/history and service surfaces that access exposes. Record any trial
terms consistently with the selected license; do not invent a confidentiality
or redistribution restriction that contradicts the granted license.

Extend P4-C4 and its section 9 row with that recorded disclosure check. Outreach
authorization and permission to send code/access are distinguished. Reuse valid
authorization within its stated scope. Unavailable trial participants remain
an observation/owner launch decision, never fabricated adoption evidence.

## A6 — Inventory public surfaces and stop on unintended exposure

R2 requires a content review of each import batch before it enters target
history. P5 inventories the surfaces that the selected visibility/release
action will expose: relevant refs (including PR refs where applicable), Git
history, releases and attachments, CI logs/artifacts, issues, discussions,
wiki/docs and other enabled surfaces. Classify surfaces that do not exist or
are not exposed; do not claim all platform behavior is known in advance.
P5 checks changes since the trial review as well as the final exposure scope.

Add **P5-C6**: that exposure inventory is dispositioned, and every migrated
unit in the public tree has a recorded authority/acceptance state. Ordinary
support files map to their owning unit. Unexplained staged/verified units fail
the gate. Explicitly retained source-owned/deferred examples or artifacts need
a visible disposition and cannot be advertised as accepted public functionality.
The entire supported runnable closure must have passed its applicable gates.

If private material is discovered, stop disclosure/publication. Select an
owner-authorized remedy appropriate to the affected surface. If a clean target
history must be reconstructed, preserve the rejected staging evidence under
restricted access, record old/new identities in the private provenance map
and a safe public summary, and repeat invalidated checks. Never rewrite source
history or update old evidence hashes to pretend no reconstruction happened.

## A7 — Promote the tested bytes and verify the served files

P4-C2's candidate comes from the same build-once workflow whose artifacts P5
promotes. Bind source revision, wheel and sdist identities, build environment,
checks and candidate approval in the release dossier. A rebuild creates a new
candidate and repeats its invalidated P4 checks; it is not a hash-equivalent
replacement by assertion. A wheel built from the sdist is separately tested
and identified; it is not assumed byte-identical to the release wheel.

Extend P5-C2: download the served release files for the selected version,
compare wheel/sdist hashes to the accepted P4 candidate, then install and run
the advertised no-key introductory examples. Private/live/native advanced
examples retain their separate selected support/evidence limits. A mismatch
or failure blocks the release-success claim and uses the correction runbook.

P4's boundary becomes **no production upload or announcement**. The P4 spec
proposes a bounded TestPyPI rehearsal of the release workflow under separately
recorded disclosure/publishing authorization, or records an explicit owner
decision to omit that rehearsal with its untested service boundary. A rehearsal
is neither a production upload nor a new certification. It does not establish
that the production account's publishing configuration is correct.

## A8 — Match existing authorization to its actual scope

R10 and the P5 publication gate require a record connecting the current
candidate identities, destinations, version, visibility/access scope and
action to the authorization relied upon. For an approval explicitly limited
to exact bytes, changed bytes require renewed approval. For an explicitly
broader authorization, in-scope edits remain authorized; do not repeatedly
ask merely because a hash changed. Escalate only a material change outside the
granted scope or a genuinely missing decision.

Qwen's proposal to void every authorization on any byte change is not adopted.
It would override valid broader user instructions and create unnecessary gates.
The retained finding is addressed through explicit scope matching and evidence.

Plan approval adopts the agreed rules/sequence and expressly selected defaults.
The PL-D table is not blanket approval of every recommendation. Account,
license, release version and external announcement/disclosure choices remain
pending until a recorded owner ruling or an explicit delegation covering that
choice. A generic planning/review instruction supplies none of those decisions.

## A9 — Identify the launch-close reviewer execution home

The launch-close panel can run through preserved source-maintained tooling in
a disposable tree until the target's migrated review entry has a selected,
successful end-to-end run. State the execution home, exact implementation and
credential policy in the close record, and publish its public-safe outcome
under A4. The existing four-complete-response bar is unchanged.

Offline positive/negative launcher and transport controls remain in P1/P3.
No ordinary contributor needs provider keys. Before claiming the target review
entry is live-validated, select a bounded run explicitly in the relevant spec
or use an already-needed review with that exact target implementation. P6's
independent maintenance/release claims identify any still-unverified provider
boundary. Copying a launcher alone does not establish live service behavior.

## A10 — Keep launch and transition completion separate

Section 1's required retirement procedure and final source reconciliation are
**public-transition deliverables**, not P0–P5 launch gates. Public launch must
deliver the migration ledger and explicit successor owner/trigger; P6 develops
final reconciliation and P7 develops/executes the retirement procedure only
after its owner trigger. Section 2's ultimate P7/transition-close record home
remains the target before any old-repository archival.

## Added acceptance and verification rows

| Criterion | Obligation | Verification owner |
|---|---|---|
| P0-C5 | Carried-obligation register and explicit overlap/ownership decisions. | P0 spec and section 9 P0 row |
| P4-C5 | Final target-only contributor workflow, bootstrap removal, both roots and sample record labeling. | P4 spec and section 9 P4 row |
| P5-C5 | Public-safe pre-visibility provenance, later real release results, then close evidence at the close gate. | P5 spec and separate milestone-close gate |
| P5-C6 | Exposure inventory and dispositioned unit authority for the public tree. | P5 spec and section 9 P5 row |

The original 33 criteria remain, with the explicit refinements above; four new
criteria bring the plan total to **37**. Specs must harvest both r1 and r2.
These rows name required future checks, not completed checks or a claim that
the product already satisfies them. No broader test lane or certification is
implicitly selected.

## Review boundary and next gate

One external round ran; there is no second round selected and no claim of
reviewer approval for amended bytes. The author checked each concern against
the frozen r1, retained dissent, and checked amendment applicability and
timing. The next decision is the owner's plan gate over r1 plus r2 and the
[gate proposal](owner-rulings.md). After approval, Phase 0's spec is
the next artifact; its own protocol gate still precedes implementation.
