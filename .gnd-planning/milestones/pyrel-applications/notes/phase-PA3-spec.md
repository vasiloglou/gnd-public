# PA3 — Native BookRec application (preparation)

PA2's hard prerequisite is still under final review. This draft authorizes no
PA3 implementation or gate before the PA2 completion record.

## Harvested obligations

| Source | Obligation | Proposed discharge |
|---|---|---|
| PA3-C1 | Deterministic native proposals, user/limits, advisory/strict/complete | CLI alternate backend and measured native query rows |
| PA3-C2 | Bad already-read/adult candidates rejected after proposal; advisory warning publishes | Mutated proposed candidate sent to independent exported checker |
| PA3-C3 | Missing recommendation/forged claims rejected; repair/recheck exact models | Complete native proposal + typed fault injection and re-proposal |
| PA3-C4 | Exact staged bytes, preserve input/existing output, independent query expectations | Bound snapshots/checker report and no-clobber publication |
| PA3-C5 | Catalogue/pairs/blocked/warning results for figures | Committed native source-to-figure data receipt |
| §0 PA-R1/R2/R3 | Independent native calculation and full checking | Separate developer query script and unchanged framework checker |
| PA-R4/R5 | Acceptance separate from audit; check exact candidate before output | CLI --accept in isolated checker subprocess, full binding/status validation |
| PA-R6/R7 | Optional local pinned runtime, limits, one semantic home | Explicit interpreter, gnd.process, public safefs; shared export applications home |
| PA-R8 /RF/public-launch|Finite observations, no authority/certification transfer|Bounded examples; no hosted service or shim retirement |
| §5/§9 | Preserve existing Python/GND app and tutorial resources | Existing test_bookrec_tutorial.py plus native consumer controls |
| PA2 carryovers | Full model validity is a prerequisite, not a native proof; typed fragment/empty states | Parent load_model_bytes declaration validation before native child; no GND policy check in native branch |
| §6 | Filtering hides bad candidates, claims trusted, byte races, ambient backend | Inject post-proposal faults; standalone fresh checker; captured bytes published |
| §10 | PA-D2–D5 inherited; PA-D7 figures later | No schema/runtime upgrade; ground PA5 data now |

## Proposed public interfaces and flow

Existing `python -m bookrec.cli recommend|complete` remains default GND behavior.
Add explicit `--backend pyrel --pyrel-python /absolute/pinned/python`. Native mode
requires the selected isolated interpreter; it never falls back to Python/GND
calculation or checking. Recommend preserves other users' recommendations;
complete computes claims and all preferred eligible recommendations for all users.
Existing --preferred-only retains advisory/strict repair behavior. Native limit
1..100; unknown preference-registered user3, bad limit2. Complete ignores limit
as the existing complete flow does and requires the complete model.

Shared `gnd.export.applications` parent orchestrator captures bounded model/input
bytes, validates model declarations via public load_model_bytes (not policy
checking), renders public standalone source from a captured snapshot and invokes
trusted explicit native interpreter through run_bounded_process. Model/seed byte
cap1MiB, native input/joins/results inherited, child wall60s, output streams bounded
1MiB and artifact reads4MiB. Temporary cwd and RAI_BUILD_DIR, -I, no PYTHONPATH,
explicit local backend/pinned versions. New module receives exact layer home;
new direct model queries are counted successors, never blanket allowances.

The separately packaged developer query script loads generated standalone runtime
via runpy; validates admitted source/profile shape, instantiates the same native
relations, and calculates eligibility, proposals and blocked explanations with
PyRel joins/negation. No GND import in child and no Python eligibility filter.
Python may deduplicate/order/present native tuples and wire candidate dictionaries.
Native complete proposals use framework-computed blocked/eligible relations,
never supplied claims. Absence of derived claims in a source seed means they
are generated in the candidate, not treated as validated original claims.
Unknown asserted coverage/listing refuses even during proposal generation.

Capture proposal bytes once; stage exactly them for a separate --accept checker
process. The parent verifies native schema/profile/backend, accepted/status/exit,
full expected obligation inventories, and exact model/population SHA bindings.
Publish the captured checked bytes via public artifact_publish_leaf_atomic with
expected absence. Never move a potentially changed child-writable candidate or
use os.replace over an existing output. Existing/symlink output and input/output
collision refuse; errors/timeouts/truncation/missing/malformed/misbound reports
withhold business output. Input bytes are unchanged on every path.

Library native publish/propose seams are testable with post-proposal candidate
faults; production CLI has no implementation fault flag. Successful output is the
population; report JSON printed separately exposes warnings/witnesses and native
calculation evidence. No actor/payment/transition permission or source truth.

## Narrated query expectations and figure sources

Synthetic catalogue: cosmos/science; map,night,read,river/fantasy. Ada is a minor;
night adult-rated; Ada/Ben rated read and prefer fantasy. Native default Ada
unread/age-appropriate pairs:cosmos,map,river. Limit2 proposes cosmos,map with one
advisory genre warning. Strict same candidate rejects; --preferred-only proposes
map,river and passes. Complete preferred eligible pairs:Ada(map,river),
Ben(map,night,river). Blocked adult pair:Ada/night. Already-read pairs:Ada/read,
Ben/read. Record exact facts and native outputs with model/input/candidate hashes
for PA5's catalogue, candidate-warning and complete-derivation graphics.

## Proposed verification

Corpus-first: named expectations above plus post-proposal mutation siblings.
Direct parent refusal/publication tests and native isolated commands must be red
before implementation. Native assertions independently compare exact pairs/order/
limits/blocked reasons, and cannot be satisfied by policy pass alone. Existing
Python/GND BookRec tests, framework acceptance/derivation/corpus controls and
focused layer/query/source compatibility gates are affected consumers.

Branches: native missing interpreter/wrong version; malformed model/input;
unknown reader/limits; unknown coverage even empty; source model/input stability;
post-proposal read/adult/strict-genre/omission/forged-claim faults; schema/identity/
status/exit/binding mismatch; timeout/error/truncated/missing report; output
exists/symlink/input collision; no-clobber race; repair/recheck; complete seed
without claims; actual native pairs and graphic mapping. No certificate or broad
historical suite. One initial Claude review and at most one bounded repair.

## Standing rules and sweep pending

Totality/bounds/validation order are enforced at each parent/child boundary.
Complete traversal belongs to the shared checker. The developer query is not a
second checker. Normative source remains runtime; all runtime facts are measured.
Final inherited-record/implementability sweep and budget precede the gate. No
GND model-evolve skill, hosted publisher, PA5 styling or PA6 wheel claim yet.

## Located public homes and pending final choices

Verified source seams: gnd.process.run_bounded_process(trusted_argv,*,cwd,env,
limits,stdin_bytes=None) returns bounded lifecycle evidence; ProcessLimits has
wall/grace/stdin/stdout/stderr/total budgets. Require successful cleanup, untruncated
streams and expected return code. gnd.safefs.artifact_read_regular_bounded(root,
relative,max_bytes) captures contained regular bytes and identity; public
artifact_publish_leaf_atomic(root,relative,data,expected=None) publishes complete
bytes with expected absence, supporting no-clobber race controls. Reuse those
variants rather than merge filesystem lifecycles or duplicate process cleanup.

The low model-layer load_model_bytes(data,source=...) validates the immutable
source declarations before native execution, avoiding an export-lane import of
entry-layer gnd.api. Native policy remains solely the independent exported
runtime; source validation is not GND population evaluation. Native calculation
and checking use primitive relationships/universes; legacy entity_concepts is
not a supported computed-query interface. Map shared parent home under export
lane with process/safefs/model/export dependencies and allowance0; example child
script remains a source-owned example under the existing documented exclusion,
not an extra semantic translation module.

## Implementability finding before gate

Pinned SDK Fragment.order_by/limit explicitly raise Feature unavailable in
semantics/frontend/base.py:6169/6177. Do not promise those methods work or upgrade
runtime silently. Eligible/blocked/pair selection predicates execute natively;
Python performs deterministic tuple deduplication, lexical presentation ordering
and the declared limit over bounded native results, permitted by the plan's
orchestration/presentation boundary. Native query controls assert the full pair
set independently, then assert the resulting deterministic proposal and limit.
No Python rating/age/genre predicate or GND check performs eligibility.

## Final interface and gate preparation

Shared parent API:
`execute_application(model_path,input_path,output_path,*,native_python,query_script,
query_args=(),candidate_transform=None)->dict`. The optional transform is a
library/test seam after native proposal generation, absent from CLI flags.
`verify_policy_report(report,model_doc,model_sha,population_sha,process_exit)->None`
raises on nonaccepted/malformed/partial/misbound reports. Result contains exit_code,
accepted, published, policy and calculation evidence; error reasons are bounded.
The BookRec wrapper selects its owned query_script; users select only interpreter
and business options. Parent model is validated from captured bytes through the
low model layer, preserving native checking independence and layer direction.

Proposal envelope version1 has model/input hashes, candidate population, and
calculation pairs/blocked explanations. Both native children must finish under
bounded process lifecycle and clean their process group. Parent report validator
requires exact full constraint/head inventory, metadata, types, success/warning
composition and byte bindings before atomic publication of captured candidate.
No missing-field/default/exit-only acceptance shortcut. Existing output refuses
publication under the safefs expected-absence contract even in a race.

Required gate commands (exit0): direct `tests/test_pyrel_application_publication.py`
and `tests/test_bookrec_pyrel_application.py`; scoped native mark selection for
those phase files; existing `tests/test_bookrec_tutorial.py`; focused framework
acceptance/derivation/driver, exact RF6 and layering consumers. Source validation,
process timeout/truncation/status/report mutations and artifact absence/race
controls are meaningful direct boundaries, not just helper mirroring. Full137
corpus need not rerun when unchanged runtime/model bytes retain PA2's bound
receipt; new app paths instead receive actual native execution and independent
expected pair/candidate controls. Certification/broad replay remain unselected.

Budget:600parent source,300owned query/wrapper source,500direct/native test lines.
No production edit before corpus-first controls land red and delegated gate is
recorded. One Claude initial plus at most one bounded repair review remains the
selected phase instrument. Native source and filesystem/process APIs are located
and satisfy the sweep; SDK order/limit limitation is explicitly handled above.

## Delegated approval (auto=true), 2026-10-13

Approve preceding specification SHA-256 0697faf06cdb9c25e85541710de0ff950d7a430633227c6056d0b8d03ba32856. Authorization: named whole-milestone delegation; PA2 completed672bf35/006. Corpus-first: 19parent controls red because shared module is absent; 6actual native CLI controls red after explicit interface-presence precondition. The initial limit test accidentally matched argparse2; that earlier receipt is historical and not native execution evidence. Models/native logic are not credited by missing flags. Source/process/filesystem homes and SDK limitation satisfy implementability sweep; no optional spec panel. Selected Claude review one initial/at most one bounded repair. Budgets600parent+300examplesource/500tests, existing strict bounds/oldPythonpath/layer0 retained. No GND policy evaluation in native branch; immutable model declaration validation is separate. Parent publishes exact captured checked bytes with expected absence, not child-writable paths. No production edit preceded this gate.

## PA3 review amendment and delegated approval, 2026-10-13

Claude F1/F2 actual red controls reproduce query replacement of the checker and
erasure of an asserted rating to permit a bad recommendation. Add
owned_relations=() to the shared library API; BookRec explicitly owns only
recommendation. All other asserted fact multisets, instances, metadata and
coverage remain the captured source; computed heads may be generated. This is
source-checkpoint fidelity, not source truth or transition/actor authorization.
Checker staging is a new private directory created after query group cleanup,
with its own build directory and expected-absence regular runtime/candidate
artifacts from parent-captured bytes. No query-created runtime/path is reused.
Native children receive only selected system/locale/temp variables and explicit
local build configuration, without ambient credential/backend variables. Query
crash1 maps70; malformed checker candidate3 retains bounded diagnostic without
requiring a nonexistent policy report. Existing-output guards already cover
input/output collisions; remove the dead later collision check. These are
review-driven hardenings within PA3 and existing budgets, not a new semantic
checker. One bounded repair review remains; no extra reviewer is selected.

Delegated approval (auto=true): preceding original specification SHA-256 905d93908acfc790270ee2ed0195d9c0e628d4b0c96e2033bcebdf42d2b3a2fb. Named whole-milestone authorization persists; this bounded interface/staging amendment is approved before owned repairs are accepted. The actual red controls were run before their fixes. No merge, certification or release is authorized.

## Final bounded repair scope and delegated approval, 2026-10-13

The selected repair review is exhausted. R1/R2 identify metadata scalar-type
preservation and staged model-name collisions. Reproduce each red, then make
owned final repairs: compare metadata/instances using type-exact JSON forms and
use a fixed private source-model name. Extend test budget500 to560 lines for
these regressions plus exact preservation/ownership and credential-file discovery
controls requested in R3/R4. Parent600/examples300 remain unchanged. No third
review round; final code is owned/verified and the review's reading limits stay
explicit. Do not repurpose HOME; inspect the explicit Config path and measure
credential-file access with denial instrumentation instead. No host sandbox
claim follows from process-group cleanup or fresh artifact staging.

Delegated approval (auto=true), named whole-milestone authority: preceding
specification SHA-256 e973010b4502c7c82798cbb45ccc9b7662f1cf18041ba1393cf53f6725294464. Bounded final fixes and budget increase
approved before production edits. Record actual red/green evidence and final
post-repair gates before PA3 completion; no release, certificate or merge.
