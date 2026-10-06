Status: owner-decided; delegated approval (auto=true), 2026-10-06. Owner explicitly selected “yes implement RF7” and approved modifying affected tests for new restrictions.

# RF7 -- strict input policy and validator consolidation

## Provenance and explicit plan amendment

Base10608c4761bae7c0989b774a20de5f43c6350912. Whole r2+e1 plan and004--012 carryovers harvested in original-scope-note.md. Owner clarification supersedes RF-D7's full deferral for the seven RF7 input/validator tasks and FIFO refusal (RF1-OQ5). The current request expressly permits observable restriction changes and affected test updates; preserving accepted data/output/digest formats outside these restrictions remains required. Media types, large-section rewrites, session SCC/version strategy and source-owned OQs remain separate. No invented human reading: decisions here use explicit RF7 auto delegation.

The separate RF7-plan-amendment.md records the approved scope change; original plan/gate bytes and old corpus remain available in history. The earlier no-RF7-criteria row is superseded by C1--C7 below for this explicitly requested phase. No earlier plan panel opinion covers this amendment. This is the bounded owner-directed scope amendment necessary for RF7, not publication authority for an unrelated milestone.

## Obligations and decisions

| Obligation | Discharge / delegated ruling |
|---|---|
| Original RF7/D7 safe paths | C1: canonical POSIX relative spelling only, reject whitespace, backslash, dot/empty/parent components; every existing intermediate below root must be a real directory, never a symlink. Existing leaf-symlink replacement/classification policy remains. |
| RF7 strict JSON | C2: common loads/load/JSONDecoder enforcement for GND readers; reject duplicates, NaN/Infinity, floating overflow1e999, container depth>64 before decode. UTF8 byte cap10MiB default. Preserve ordinary int/float and explicit Decimal/custom hooks, legitimate finite exponents, domain root/error adapters. Generated external project/runtime source stays standalone. |
| RF7 two YAML readers | C3: pre-load byte/event/depth/alias guard for evolve._parse_model_text and souffle.parse; duplicate keys refused by safe loader; byte10MiB, events1million, depth64 (Souffle uses its declared smaller limits). Reject before constructing nodes. |
| RF7 ISO datetime | C4: one parser: ASCII YYYY-MM-DD, uppercase T, HH:mm with optional :ss/.fraction1--6, optional uppercase Z or ±HH:mm; actual calendar/time/offset hour<24 and minutes<60; naive preserved. Predicates/adapters retain return/error conventions, all direct GND datetime consumers and standalone PyRel copy use grammar. |
| RF-D6 resolver | C5: inherited reference only on literal True everywhere, including standalone PyRel; consolidate primitive algorithms at model_queries strict walk. Keep compatibility signatures/variant spellings, both spellings now select strict semantics. Missing/cycle/ambiguity refusal retained. |
| RF-D11 divergent helpers | C6: merge input validators only (JSON/YAML/datetime/resolver); different canonical encoders/newlines/preprocessing and three digest meanings remain intentional policy variants. File digest readers share regular-file nonblocking streaming primitive with raw/prefixed digest adapters. No gratuitous wire-format merger. |
| RF-D8 diagnostic | C7: unknown session version lists all supported1--8, no dispatch/version behavior change. |
| RF1-OQ5 | Timed FIFO refusal for provenance._sha256_file, promote._digest and transition.population_file_digest; regular file bytes preserve raw/prefixed digest. Preserve existing symlink-following policy for regular leaf targets, refuse special files before read; descriptor and size checks. |
| RF1-OQ6 | Media-type normalization remains successor, not implied by new input restrictions. |
| RF6 metadata/patch/scans | Old imports/signatures and actual defining-home patches retained; changed-body successor inventory explicit. Source scans widen to new input_policy home with omission/dirty negatives. RF6 old body-byte results unavailable for changed bodies, untouched definitions remain pinned. |
| Authority | units.json and distribution authority test frozen; bounded b3 adaptation rows retain originals; no source-side/installed/certificate/release claims. |

## Binding rules

RF-R1 explicitly amended for C1--C7 only; all other bytes/exits/semantics preserve. RF-R2 digest encoders unchanged. RF-R3 current predecessor observations before routing; original goldens remain archived, current tests get approved restriction successors. RF-R4 no move-only claim for deliberately changed validators. RF-R5 old aliases inventoried and actual patches preserved; no shim retirement. RF-R6 exhaustive lexical consumer census/source scope includes every introduced home, omissions fail. RF-R7 frozen authority/current attestation unavailable. RF-R8 release identity unavailable for changed bytes. RF-R9 measure actual baseline220 modules; no vacuous private-edge improvement, added shared intake dependencies reasoned. Budget <=180 touched, <=4000 nonrelocated source additions, <=5000 test/data additions, <=1800 non-evidence docs, moved<=1000 lines. RF-R10 no new commands/flags/schema/family. RF-R11 direct/focused closure under default filters, no broad replay.

Standing rules: total arbitrary input refusal and error adapters; caps before construction/read; timed depth/alias/FIFO cases; existing boundary validation order retained; shared input policy instead of per-kind copies; this spec is normative home for new restrictions; measurements decide compatibility, not prose. No performance claim.

## Design and exact interfaces

src/gnd/input_policy.py (~250lines), infrastructure: loads(raw: str|bytes|bytearray, **kwargs) -> Any; load(handle, **kwargs) -> Any (bounded read); JSONDecoder(**kwargs) with decode/raw_decode preserving native interfaces while validating parsed document depth/finiteness and duplicate pairs; guard_yaml(raw: str|bytes, *, max_bytes=10485760,max_events=1000000,max_depth=64) -> None; parse_datetime(value: str) -> datetime. Standard JSONDecodeError/ValueError are mapped by existing domain readers. Standard encoder APIs remain json.*, not this reader module. Standalone generated/export runtime gets local grammar, no GND import.

safefs adds file_sha256(path: str|Path) -> str with nonblocking regular-file descriptor, bounded1MiB chunks and identity/size stability check, always closes. Distinct prefix/symlink adapter contracts are explicit. Old installer lexical errors retained where already refused; newly refused spellings get canonical-path diagnostic.

## Corpus-first approval and implementability

Restriction tests/fixture narratives are authored and committed red before production changes; branch cases cover accepting/refusing siblings, custom decoder callbacks/Decimal, finite vs overflow, quoted delimiters vs real depth, UTF8, YAML alias/event/depth/byte limits, canonical vs normalized paths and nested file parent, valid/loose datetime, bool/nonbool inheritance, cycle/multiple parents, regular/FIFO and diagnostic8. Existing new scopes import checks can be red because shared helper absent. Each implementation lane gets direct and downstream green controls. Golden restriction changes require a before/after ledger, never blind bulk recapture. Budget/review bound declared now: independent native Codex initial plus at most one repair; reading not testing. Optional spec panel omitted under explicit scope amendment; no old panel opinion claimed.

## Verification selection

G0 run predecessor baseline observations and current relevant RF1 helper/semantic/session pins, retaining raw outputs before changed validators. G1 run tests/test_rf7_input_policy.py and tests/test_rf7_consumers.py plus new source-scope negatives, expected0 after separately observed red. G2 run selected population/model validation, synth values/boundary/provenance/measure promotion/transition, evolution, Souffle offline intake, public JSON boundary and session contract/store/adapter/review parsing controls; exact node list recorded from inventory before execution. Excluded native/proof/provider/historical nodes replaced only by bounded current successors; known old RF2 source observer and RF3 numerical assertion retain exact prior dispositions. G3 run actual current RF1 pins with explicitly approved successor expectations only where restrictions differ; unchanged goldens still checked. G4 explicit changed-path Ruff, gnd_arch measurement metrics-RF7.json and full layer/query/entry controls; expected0. G5 selected direct consumers on available Python3.11/3.13; no broad native lane. G6 independent Codex review, observed reproduction before fixes, at most one repair. Record/scaffold checks if docs changed.

Inheritance: original corpus snapshots/old certificates describe old bytes only. Cadence: full default, exhaustive historical, evidence/census/proof/distribution/external-oracle/network/native/certification remain explicit owner/separately scoped CI. No requested certification.

## Scope and budget decisions -- delegated approval, 2026-10-06

User's RF7 auto plus “yes implement RF7” and “modify any tests to respect the new restrictions” authorizes corpus-first C1--C7/FIFO and their named tests. Preserve digest meanings, valid inputs, import/patch/source scope, source-owned authority. Omit unrelated media/large rewrites and optional spec panel. Numeric budgets above approved before implementation. Exact spec snapshot SHA recorded by shasum before test/production authoring. User instruction overrides the prior RF7 deferral for this named work; no new authority is inferred elsewhere.

## Implementation findings and delegated dispositions -- 2026-10-06

- Blocking F1: eager parent-map construction regressed the existing4000-parameter semantic validation control (current4.07s, isolated3.59s, exact106 predecessor passes). Retain that control; use the same strict walk with lazy direct-parent lookup instead of per-resolution whole-map construction. Focused repair313 passes, including this unchanged test. No performance claim beyond that gate.
- Blocking F2: explicit JSON model overflow refusal fell through to YAML/schema validation. fallback-red demonstrates ModelValidationError instead of input refusal. Explicit .json and shared policy refusals now raise ModelLoadError before YAML; YAML flow mappings with unquoted keys remain accepted through their existing YAML path.
- Compatibility diagnostics: preserve original directory IsADirectoryError, old unsafe-path diagnostic order, custom numeric-hook refusals and custom duplicate-hook messages. New policy refusals subclass JSONDecodeError with message-only text to avoid fabricated line coordinates.
- Decoder encoding clarification: standard BOM/UTF16/UTF32 byte interpretation remains supported. Both original byte length and UTF8 decoded byte length are capped10MiB. This preserves the existing native encoding controls while enforcing C2; no UTF8-only admission restriction is intended.
- Consumer scope: the75-call AST inventory covers importable GND modules. Standalone packaged example programs (six exact paths in the routing test) and three skill executables retain their own parsers (verify_migration.py, validate_model.py, update_harnesses.py); generated external project/runtime source likewise remains standalone. Native adjacent Souffle proof JSONDecoder is the one stream-specific module exemption. Current routing test names these exclusions and rejects new module-reader omissions.
- Current golden successor19 rows retain all original fixtures and input digest, per-field old/new observations and reasons. Three digest directory diagnostics were repaired rather than recaptured. RF6 changed definition5-row successor retains original body hashes. Dynamic syntax inventory successor retains old/new delta; literal query allow-list and ceilings unchanged.
- Shared input parsing exceptions are exactly commands.checking and commands.exp -> input_policy, with reasons; no global CLI import exemption.
- Proven predecessor/environment failures: v3 verifier fresh/resume refuse before any RF7 production edit, including unrestricted retry; Souffle setuid test fails exact106 archive because requested4700 becomes0700 here. Only these exact3 nodes are deselected in the corresponding final closures. Historical RF2 encoder source and RF3/RF4 old numeric/body comparisons retain earlier invalidation dispositions; current RF7 graph has live dirty controls and makes no old private-edge count claim.

## Independent review dispositions -- delegated approval, 2026-10-06

Owner explicitly approved the pending RF7 Codex provider transmission, initial plus one repair. Initial review over35aa122 produced three blocking issues, one hardening issue and one completeness issue. One reviewer is one reviewer; small read-only probes ran, no suite. Review retained verbatim with declared path substitutions.

- R1 blocking: raw NaN/Infinity callback refusal had no InputRefusal cause and could fall through into YAML strings for JSON-shaped .yaml source. Reproduced red for all three literals; retain genuine unquoted YAML flow mappings, but fallback only on actual native JSON syntax errors, never policy/domain refusals.
- R2 blocking: sibling walks shared visited state and hid ambiguity in a valid diamond model. Reproduced both variants red; the standalone primitive copy has the same independently observed red. Use branch-local visited sets while preserving the shared primitive entry's caller-visible visited union and initial seen exclusions. Strict flag rule unchanged.
- R3 blocking: provenance sidecar read was unbounded and byte-cap ValueError escaped SidecarError. Reproduced red. Bound binary read to MAX_BYTES+1, reject oversize before UTF8 decode, preserve original strict UTF8 interpretation, and map read/policy refusals to SidecarError.
- R4 hardening accepted: object_pairs_hook can mutate the list and erase duplicates. Reproduced red; remember the duplicate predicate before calling the hook, retain existing hook-specific refusal text, and apply refusal after a successful callback.
- R5 completeness deferred: direct evolve._parse_model_text malformed YAML leaks ruamel ParserError; reviewer did not establish an exposed service route, and inspected callers validate first. Retain original conventions now; target the input-boundary hardening successor milestone for uniform private-helper parser adapters. No unproved public exploit or new phase regression is claimed.

review-all-red:7failed6passed before any source repairs; standalone-review-red:1failed. Original approved corpus meanings remain unchanged; separately identified adversarial siblings are additions. At most one repair review, as declared before invocation.

## Evidence-file budget amendment -- delegated approval, 2026-10-06

Measured touched-file count183 exceeds the original180 after retaining independent-review reproductions, the isolated predecessor check, and separate original/repair lint evidence. Under the owner's RF7 auto delegation, raise only touched-file ceiling180 ->210 before the remaining repair review and completion artifacts. Arithmetic: current183 plus at most27 remaining review/metric/record/CI evidence artifacts =210. Production module count and implementation scope stay fixed; source-addition4000, test/data5000, non-evidence-doc1800 and moved1000 ceilings remain. This is a recorded delegated budget ruling, not a claim that the original limit passed or a human reading of amended bytes.
