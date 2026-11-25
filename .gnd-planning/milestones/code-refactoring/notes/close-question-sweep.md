# code-refactoring — open-item sweep for the milestone close

Read-only sweep, 2026-11-25, of worktree `issue-closure-review-c8a09e` at
`99cf3df2` (equal to `main`). Paths are relative to
`.gnd-planning/milestones/code-refactoring/` unless they start with `src/`.
`plan` = `notes/code-refactoring-plan.md`. `NNN:L` = record `NNN-*.md`, line L.

This file reports what the records say. It decides nothing. **DISAGREE** marks
rows where two records, or a record and the plan, state different things.

State vocabulary: **ruled** (decided, nothing owed); **closed by X**;
**open → close** (a record assigns it to the milestone close);
**carried → Y** (assigned to a named successor or owner outside this milestone);
**superseded by X**; **untracked** (raised once, no later record mentions it).

---

## A. Plan §10 decisions (plan:480–505)

| # | ID | Source | Text (under 30 words) | State per records | Flag |
|---|---|---|---|---|---|
| A1 | RF-D1 | plan:487 | All work in gnd-public; `runtime`/`test-acceptance` handoff stated in the RF0 record. | Ruled. Handoff stated at 004:74–82. The source-side control rests on owner attestation only (004:79–82); later records repeat this (007:290–291, phase-RF8-spec:90). | |
| A2 | RF-D2 | plan:488 | Sequencing with public-launch; tag condition. | Ruled, then satisfied by e1 (005:38, 005:41). Original text kept and marked superseded. | |
| A3 | RF-D3 | plan:503 (still under **Open**, "resolve by RF0") | Distribution manifest and release evidence procedure. | Ruled at RF0 as D4(b), "no edit" (004:72; notes/phase-RF0-spec.md:254). Superseded within its scope by RF2 D7, a bounded adaptation (007:293–299; notes/phase-RF2-spec.md:229, :458–467). Later phases adapted rows too (008:335, 012:167, 014:162, 016:133–136, 017:63). RF2-OQ3 sends the reconciliation to close (007:536–537). | **DISAGREE**: plan lists it as Open; 004 says ruled (b); 007 says RF2 D7 supersedes (b). |
| A4 | RF-D4 | plan:490 | Milestone name `code-refactoring`. | Ruled (003:36). | |
| A5 | **RF-D5** (shim retirement) | plan:504 (still under **Open**, "resolve by RF2") | Shims stay at least until the first public release after RF6; retirement is a later, separately approved phase. | Ruled at the RF2 gate as D1 (notes/phase-RF2-spec.md:223, owner marks :367; notes/shim-inventory.md:3–4 "owner ruling 2026-10-05"). No shim retired. Retirement carried → "first public release after RF6 plus explicit retirement approval" (007:538–539, 008:402, 009:331, 010:223, 011:129, 012:399 "Release owner", 014:215, 015:196–198, 016:438–440, 017:149). No record in 003–017 says whether that release has happened. | **DISAGREE**: plan §10 still shows it Open with owner RF2; the records treat it as ruled with a release trigger. |
| A6 | RF-D6 | plan:491 | Keep both resolver semantics behind a pinned variant; switching any caller to strict `is True` is RF7 successor work. | RF3 built the variant interface (008:342). Then RF7 C5 switched both spellings to literal-True semantics (notes/phase-RF7-spec.md:19; 013:152). RF9-F2 aligned an RF6 test with it (016:114–116). | **DISAGREE**: plan calls the switch successor work; RF7 executed it in this milestone. |
| A7 | RF-D7 | plan:489 | RF7 deferred to a successor in full, including YAML guards for two loaders. | Superseded for C1–C7 and the FIFO refusal by notes/RF7-plan-amendment.md:3 and by the RF9 amendment (plan:46–49). The rest of the RF7 list stays deferred (see B4). | **DISAGREE**: plan:489, :162, :353–361, :442, :472 still say deferred/not executed. |
| A8 | RF-D8 | plan:492 | Name the v8 literal in RF8; first-assignment removal withdrawn; rename `in_range` in RF6; "unknown version" text is RF7 successor work. | v8 literal named (014:158); first assignment kept (014:158; notes/phase-RF8-spec.md:16); `in_range` exposed (011:103); unknown-version text now lists 1–8 via RF7 C7 (013:154). | **DISAGREE**: plan still calls the message text successor work. |
| A9 | RF-D9 | plan:505 (still under **Open**, "each spec gate") | Approval instrument: corpus-first for RF1, spec prose for move phases. | Ruled at each gate: RF2 D5 (notes/phase-RF2-spec.md:227, :368), RF4 D1 (notes/phase-RF4-spec.md:64), RF6a D1 (notes/phase-RF6a-spec.md:45), RF7 corpus-first (notes/phase-RF7-spec.md:39–41), RF8 D1 (notes/phase-RF8-spec.md:84). | Plan row still reads Open (it is a per-gate standing item). |
| A10 | RF-D10 | plan:493 | A rename is non-observable when the old name stays importable via a listed shim. Any other rename needs its own ruling. | Ruled and applied (RF2 digest renames 007:316–319; safefs, oracle, best_identity). helper-families:30 says `c4e1c0f8` needs an RF-D10 rename ruling before any merge. No such ruling appears in 003–017. | |
| A11 | RF-D11 | plan:494 | Every RF0-diverged family keeps its variants, each pinned byte for byte. Merging is RF7 successor work. | RF7 spec rules on RF-D11 directly: "C6: merge input validators only (JSON/YAML/datetime/resolver)", and file-digest readers share one primitive (notes/phase-RF7-spec.md:20; 013:149–153). The RF7 amendment names only RF-D7 and RF-R1 as superseded (notes/RF7-plan-amendment.md:3). See families-ruling.md §C. | **DISAGREE**: predicate 3 (plan:75–77) and the risk row (plan:431) say variants are kept; RF7 merged the validator families without the amendment naming RF-D11. |
| A12 | RF-D12 | plan:495 | Public-launch gate name and stall route. | Ruled (003:34–35). Stall route not triggered (RF-D2 satisfied). | |
| A13 | RF-D13 | plan:496 | A missed target stops at the owner gate; the close table lists every original target that was missed. | Ruled. Re-targets from RF3 onward are delegated agent rulings under `auto=true` (008:333, notes/phase-RF4-spec.md:60, 012:159, 014:156), not owner readings. Missed-target list in §E below. | Note: plan says "the owner may re-target"; RF3–RF8 re-targets are delegated. |
| A14 | RF-D14 | plan:486 | RF9 registration and read-only review; fixes, close and merge remain separate. | Ruled. RF9 completed (015). Repairs separately approved: "you have my approval to fix the issues" (016:95–100) and "do repairs" (017:47–48). | |

## B. RF7 status

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| B1 | RF7-status | plan:162, :353–361, :437–442, :472; plan:46–49 | Plan body: RF7 deferred, not executed, "carried as an open question at milestone close". RF9 amendment: RF7 "pulled forward ... recorded in 013". | Executed and recorded in 013 under notes/RF7-plan-amendment.md (013:140–144). The plan says "The original scope text remains historical evidence pending close reconciliation" (plan:49). | **DISAGREE** inside the plan itself. |
| B2 | RF7-close-review | 013:382 | "Original plan amendment integration/required milestone-close review -> milestone close." | Open → close. Also: no plan-panel opinion covers the RF7 amendment (notes/RF7-plan-amendment.md:5; 013:142). | |
| B3 | RF-R1/predicate-1 vs RF7 | plan:64–66, :101; notes/RF7-plan-amendment.md:3; 013:156 | Predicate 1: "No pin's expected value has changed". RF7 binds 19 restriction successors. RF2 routed 4 session nodes to successor answers. | Amendment says old predicates are judged "using explicit original-vs-restriction successor distinctions, never an unchanged-pin claim". Also RF2 instrument successors (007:326–341). No record re-words predicate 1. | **DISAGREE**: predicate 1's literal text against 007 and 013. |
| B4 | RF7-remainder | plan:358–361; notes/RF7-plan-amendment.md:5; 013:372; notes/RF7-implementation-status.md:91 | Not done in RF7: media types, large validator rewrites, other YAML loaders, a common structured error policy, canonical-encoder/digest-meaning merges. | Carried → successor milestones (013:372, 013:379; notes/phase-RF7-spec.md:23). | |

## C. Items raised in records 003–017

### 003 plan gate and 005 erratum

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C1 | 002-routing | 003:58–59; 002-panel.md:72–87 | Residual r2 panel concerns, each routed to a named gate (F2–F10 and the divergent views). | Harvested by the named specs: notes/phase-RF0-spec.md:16–17, :45–52; notes/phase-RF1-spec.md:21–23, :56–59; notes/phase-RF2-spec.md:64 (F10 move unit); notes/phase-RF3-spec.md:22; notes/phase-RF5-spec.md:15; notes/phase-RF6a-spec.md:18. No record closes the list as a whole. | |
| C2 | distribution-lane | 003:61–62; 004:18; 006:31 | Curated-manifest distribution test already failing at `7e08e1e`; a public-launch repair, tracked in vasiloglou/gnd-public#8. | Carried → public-launch / #8. Every phase keeps `units.json` and the guard frozen (e.g. 016:133–136). No record says #8 is closed. | |
| C3 | e1-unreviewed | 005:48–49 | No panel reviewed the e1 erratum bytes. | Standing limitation. | |

### 004 RF0

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C4 | RF0-OQ1 | 004:129–131, :90 | Tests ceiling 650 missed (666); re-targeted to 700. | Closed (owner ruling). Must appear in the close table (§E). | |
| C5 | RF0-OQ2 | 004:132–133, :116–125 | Unify the two alias resolvers in `tools/gnd_arch.py`. | Closed by 006 (006:116, :172–174). | |
| C6 | RF0-OQ3 | 004:134–135 | RF1 strict-xfail list is the 27 wrong-way edges; `declared_clean` = entry, infrastructure. | Implemented as 16 strict-xfail layering pairs (006:106–107). RF3 removed all 16 (008:354); RF4 took wrong-way edges 8→0 (009:209). No record says "OQ3 closed", and none reconciles 27 edges with 16 pairs. | |
| C7 | RF0-OQ4 | 004:136–138 | The audit's identical canonical-JSON helpers are all diverged; accept or rule a normalized view. | Ruled at RF2 as D2: accept, consolidate only the report-text group (notes/phase-RF2-spec.md:224, :367). Plan text repair → RF2-OQ1 (C17). | |
| C8 | RF0-OQ5 | 004:139–144 | Dynamic `__import__` at `semantic_spec.py:1613` puts `semantic_spec` in the core cycle. | Closed by 008 (004:142–144; 008:360; 007:545–547). | |
| C9 | RF0-OQ6 | 004:145–147 | First `SESSION_CONTRACT_VERSION` assignment is live; RF-D8 removal withdrawn; plan text repaired at close. | RF8 kept it (notes/phase-RF8-spec.md:16; 014:158). The plan text was repaired by e1 (005:40; plan:369–372, :492). | **DISAGREE**: 005:50–52 says e1 resolves none of OQ4–OQ7 apart from OQ7's plan text, yet its table (005:40) repairs OQ6's text. |
| C10 | RF0-OQ7 | 004:148–149 | Repair predicate 5 (co-change) and RF-D2 (tag) text at close. | e1 did both (005:37, :41). "The close record still sweeps it" (005:57–58). | **DISAGREE**: the risk row plan:434 still says the close table reports co-change; predicate 5 (plan:85–87) removed it. |
| C11 | RF0-refuted-1 | 004:153–155 | RF-D8 premise that the first assignment is dead: refuted. | Plan repaired by e1 (005:40). | |
| C12 | RF0-refuted-2 | 004:156–157 | Co-change is measurable: refuted. | Repaired by e1 except plan:434 (see C10). | |
| C13 | RF0-refuted-3 | 004:158–159 | Audit's "11 identical canonical-bytes sites": none AST-identical. | Plan RF2 body (plan:261–263) still promises `canonical_bytes(v, *, newline, indent)`. → RF2-OQ1 (C17). | |
| C14 | RF0-09 | 004:99–100; notes/phase-RF0-codex-review.md:29 | Patches bound to non-`gnd` imports are omitted from the inventory. | Kept by design. 004:110–112 also records 71 statically unresolved patch targets as a limitation (RF2 measured 73; notes/phase-RF2-spec.md:308). | |

### 006 RF1

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C15 | RF1-OQ1 | 006:196–216 | Owed pins must land before the owning phase moves: RF2 measure/PyRel, RF4 `directory_identity`, RF5 handler bytes, RF6 import paths. | Each part annotated as discharged: RF2 (006:200–203), RF4 (006:204–207), RF5 (006:208–212), RF6b (006:213–216; 012:394). No record declares the whole question closed. | |
| C16 | RF1-OQ2 | 006:217–219 | CLI resume refuses v2/v3/v7/v8 after a completed result is removed; is it intended? | RF8 D3 preserved the behavior (notes/phase-RF8-spec.md:86; 014:211). Carried → session-controller successor. Still listed at 015:196, 016:438, 017:149. | |
| C17 | RF1-OQ3 | 006:122, :220–221 | RF1-C1 narrowed by three exempt meta nodes. | Open → close (007:542, 008:400, 009:331, 010:223). | |
| C18 | RF1-OQ4 | 006:182–183, :222–223 | Session prompt embeds the absolute contract path, so evidence digests depend on location. | RF8 D4 preserved it (notes/phase-RF8-spec.md:87; 014:212). Carried → session-portability successor. Still listed at 017:149. | |
| C19 | RF1-OQ5 | 006:184–185, :224–225 | Three file-digest readers block forever on a FIFO. | Closed by 013 (013:153, :386; annotation 006:185, :225). | |
| C20 | RF1-OQ6 | 006:186–187, :226 | Candidate media types depend on the interpreter's `mimetypes` table (Q5). | Carried → successor (notes/phase-RF7-spec.md:23; 013:379; 017:149). | |
| C21 | RF1-OQ7 | 006:190–192, :227–229 | Unify `scrub`/`normalize_text` in `tests/support/rf1_pins.py`; bind declared-input bytes (review RF1-05). | Open; owner is "the next phase that edits that module". Every later phase left the module unedited (007:347, 013:381, 014:213, 017:149). | |
| C22 | RF1-F7 batch emitter | 006:188–189 | Batch arm of `gnd check` writes to `sys.stdout.buffer`, bypassing the report emitter. "Recorded for the RF5 spec." | The RF5 spec preserves it as a separate byte contract (notes/phase-RF5-spec.md:26). Record 010 does not mention it. | |
| C23 | RF1-10 part | notes/phase-RF1-codex-review.md:31 | "An independent plan-surface list is deferred." | Untracked. | |
| C24 | RF1 quirks Q1–Q5 | 006:152–153; notes/phase-RF1-spec.md:456–469 | Behaviors pinned as found, not endorsed. | Q1 closed by RF7 C7 (013:154). Q4 closed by RF8, which named the v8 constant (014:158). Q5 = RF1-OQ6. Q2 (`cli._canonical_payload` lacks `allow_nan=False`) and Q3 (validator labels) are untracked. | |
| C25 | RF1-estimates | 006:132–133; notes/phase-RF1-spec.md:680–685 | `mutations.json` 1,705 vs 700; `test_rf1_helper_pins.py` 535 vs 350; owner accepted. | Must be "carried to the milestone close table as original estimates that were missed" (spec:684–685). | |

### 007 RF2

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C26 | RF2-OQ1 | 007:530–532, :555, :496–497 | Repair the plan's identical `canonical_bytes` premise and the family note's "compact" wording; the report group uses indent=2. | Open → close (008:400). plan:261–263 and helper-families:21 are unchanged. | |
| C27 | RF2-OQ2 | 007:533–535 | Standalone PyRel positional-ref routing vs. preserving its copied runtime and emitted bytes. | RF6a D4 preserved the bytes (notes/phase-RF6a-spec.md:48). Carried → "export-format successor" (011:121, :129; 012:388). | |
| C28 | RF2-OQ3 | 007:536–537; notes/phase-RF2-spec.md:467 | Reconcile the RF0 D4(b) manifest ruling and RF-D3 wording with the RF2 D7 bounded adaptation. | Open → close (008:400). See A3. | |
| C29 | RF2-refuted | 007:553–571 | Six refuted premises (parameterized canonical family; exit namespaces; producer identity; py314 portability; dual capture; RF0 authorized adaptation). | Historical. Only the canonical-family premise names a close repair (007:555 → C26). | |

### 008 RF3

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C30 | RF3-OQ1 | 008:397, :393 | Reconcile the original layer-wide SCC prose with RF0 D10's assurance/RF4 assignment and amendment A5. | Open → close (009:331, 010:223). | |
| C31 | RF3-OQ2 | 008:398, :387 | Remaining model intake/query package organization → RF6. | Closed by 012 (012:395). | |
| C32 | RF3-OQ3 | 008:399, :387 | Should two fixture-family `no_evaluator` helpers share an observed-effect guard primitive? | Carried → "separately scoped test-support successor". No later record. | |
| C33 | RF3-refuted | 008:409–416 | Eight refuted premises, among them "700 non-relocated lines" (A6) and "all core-layer SCCs belong to RF3" (A5). | Historical. A5 feeds RF3-OQ1; A6 feeds §E. | |

### 009 RF4

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C34 | RF4-wording | 009:331, :200; plan:294–299 | Reconcile the visibility-only filesystem decision and the shared-domain checking decision with the plan's move/direct-call wording. | Open → close (010:217, :223). | |
| C35 | RF4-plan-amend | 009:327 | "Plan amendments are reserved to milestone close." | Open → close. | |
| C36 | RF4-refuted | 009:335–338 | The claim that all compatibility bindings survived was false (20 restored). Original budgets did not fit. | Historical; budgets in §E. | |

### 010 RF5

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C37 | RF5-entry-predicate | 010:194, :223; plan:78–82, :177–181 | The promised RF0 entry-point predicate did not exist; RF5 supplied one. "Normative plan repair" goes to close. | Open → close. (RF0 had deferred the rule to RF5 as its D12: notes/phase-RF0-spec.md:263.) | |
| C38 | RF5-replan | 010:194; notes/phase-RF5-spec.md:22, :52 | Two consecutive original-budget misses triggered "an explicit delegated pre-phase re-plan". | Recorded as a delegated ruling under RF5 auto. | **DISAGREE** (possible): the plan's drift row says "the owner re-plans before the next phase begins" (plan:433). |

### 011 RF6a and 012 RF6b

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C39 | RF6a-completeness | 011:117; notes/phase-RF6a-spec.md:106, :110 | Missing two-parent closure and committed `rejected_proposals`/`deontic_notes` cases. | Carried → model-query successor. | |
| C40 | RF6a-traversals | 011:121, :129 | Individually allowed domain/raw/IR traversals and dynamic semantic routing need pinned successor routing. | Carried → model-query successor. RF9-F3 later widened the inventory with getattr reads (016:116–118). | |
| C41 | RF6a-A3 | 011:111, :129 | The promised extraction-only commit was not made; a same-module behavioral commit was used instead. | "The recorded A3 procedural departure stands." | |
| C42 | RF6a-cache | 011:235–243 | Cyclic-metadata cacheability walk timed out. | Closed by 012/60559aa (012:165). | |
| C43 | RF6b-facade | 012:366, :398, :403 | Model facade target of 400 lines missed; revised to 900 (A1). Repair the ideal facade wording. | Open → close. Also in §E. | |
| C44 | RF6b-RF7 | 012:396 | "Tightening, primitive variant consolidation and remaining procedural normalization are deferred" to RF7. | RF7 consolidated the primitives (013:152). "Large validator rewrites" stay with a successor (013:372). | |
| C45 | historical-observers | 011:111; 012:386; 013:370 | Historical RF3 numeric (expects 64) and RF2 encoder-source observers are deselected; they fail on their own archived bytes. | Grouped as "historical-body/ownership reconciliation" and kept with prior owners; "milestone close must sweep them explicitly" (015:196–198; 016:438–440). | |
| C46 | RF6b-getsource | 012:384 | `inspect.getsource` through historical module qualification is unavailable. | Standing limitation (also 010:196). | |

### 013 RF7

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C47 | RF7-R5 | 013:168, :378; notes/phase-RF7-spec.md:72 | Private `evolve._parse_model_text` leaks ruamel `ParserError`; no exposed route found. | Carried → input-boundary hardening successor (014:214; 017:149). | |
| C48 | RF7-excluded-nodes | 013:370; notes/phase-RF7-spec.md:62 | v3 fresh/resume nodes and the Souffle setuid node were excluded from final gates. | v3: closed by RF8 A1, a PATH instrument fix (notes/phase-RF8-spec.md:137–144; 014:168). Souffle setuid (4700→0700 locally): no later record. | |
| C49 | RF7-json-caps | 013:372 | Not every producer's upstream file read uses bounded I/O. | Standing limitation. | |
| C50 | RF7-replay | 013:174 | An accidental 30-seed replay was stopped (exit 2 after 686 passed). It is not evidence. | Historical. | |

### 014 RF8

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C51 | RF8-V72-hashes | 014:199, :216; notes/phase-RF8-spec.md:146–151 | Three frozen V72 reader-body hashes already differed at the RF8 base. | Open → close ("milestone-close plan/measurement integration"). | |
| C52 | RF8-primitive-guard | 014:205, :216; notes/phase-RF8-spec.md:168–174 | A package-wide primitive ownership guard flags `safefs.read_regular_file_bytes`; red at the exact base. | Open → close ("ownership disposition"). The node stays excluded. | |
| C53 | RF8-owed-from-013 | 014:220; 013:360 | Session profile/merge/SCC work owed by 013. | Closed by 014. | |

### 015 RF9, 016 RF9-repair, 017 RF9-ci-repair

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C54 | RF9-F1/F7 | 015:185–186; notes/phase-RF9-review.md:20, :149 | Terminal acceptance not bound to case acceptance; missing best crashes the declared-case helper. | Closed by 016 (016:102–109, :433–435). | |
| C55 | RF9-F2 | 015:187–188 | An RF6 test contradicts RF7 literal-True semantics. | Closed by 016 (016:114–116). | |
| C56 | RF9-F3 | 015:189 | The RF6 exact query inventory misses fixed getattr reads. | Closed by 016 (016:116–118; 016:336–341). | |
| C57 | RF9-F4 | 015:190 | Serializing a contract changes contract equality. | Closed by 016 (016:110–112). | |
| C58 | RF9-F5 | 015:191 | RF8 body observer hides an early identity-cache write. | Closed by 016 (016:118–121). | |
| C59 | RF9-F6 | 015:192–193 | Graph omits implicit package-parent execution; shared output placement. | Closed by 016 (output moved to `gnd.output`; parent-initializer edges measured, 016:122–132). Leaves C63. | |
| C60 | RF9-F8 | 015:194 | Moved digest helpers lose runtime annotation resolution. | Closed by 016 (016:112–113). | |
| C61 | RF9-F9 | 015:195 | Legacy offline scan misses the from-import form. | Target guard repaired by 016 (016:129–132). The source-owned OQ-V52-P1-IMPORTWALK-1 stays open (016:436–437). | |
| C62 | RF9-R3-unreviewed | 016:368–372 | The final terminal-reference clause has no third native assessment; the two-review budget is exhausted. | Standing limitation (local RED/GREEN evidence only). | |
| C63 | combined-SCCs | 016:343–345, :396–398, :441–442; 017:132, :151–152 | Package re-exports create seven combined package-initializer SCCs; "not a zero-cycle claim". | Open → close ("milestone-close architecture reconciliation"). | Possible conflict with predicate 2 (plan:72–74). |
| C64 | RF9-ci-pool | 017:140 | "Pool byte-cap plain ValueError remains outside this named repair scope." | Residual; no owner named. | |
| C65 | RF9-close-sweep | 015:196–198; 016:438–440 | Prior RF1-OQ2/4/6/7, source-owned questions, RF6b/RF7/RF8 budget misses, historical-body reconciliation and shim retirement: "milestone close must sweep them explicitly". | Open → close (this sweep). | |

### Cross-record carried items

| # | ID | Source | Text | State per records | Flag |
|---|---|---|---|---|---|
| C66 | source-owned OQs | plan:443–446; 007:548–549; 008:403; 009:331; 016:436; 017:150 | OQ-V72-P1-ARTIFACT-COPIES, OQ-V52-CLOSE-CANONJSON-1, OQ-V52-P1-IMPORTWALK-1, OQ-V63-CLOSE-HELPER-TAIL-1. | Carried → source owners. No transfer ruling. | |
| C67 | CI/billing | 006:156; 009:327; 013:384; 014:218; 015:178–181, :199; 016:443; 017:143–145 | GitHub runs refused before steps (payments/spending limit). | Carried → repository owner/platform "before any merge". | |
| C68 | Linux/installed | 006:156–158; 007:520–521; 016:404–415 | Only macOS 3.11/3.13/3.14 exercised; no Linux, installed or release verdict. | Standing limitation. | |

---

## D. Every place that says what the close must reconcile or include

| Source | What it says the close must do |
|---|---|
| plan:49 | Reconcile the original scope text (RF7 deferral) — "pending close reconciliation". |
| plan:64–66 | Predicate 1: RF1 suite green at close, no pin expected value changed (see B3). |
| plan:72–74 | Predicate 2: no multi-module SCC in the model, population, checking or semantics layers (see C63). |
| plan:75–77 | Predicate 3: one home per identical family; diverged families keep their variants (see families-ruling.md). |
| plan:83–90 | Predicate 5: commit a before/after table; list each missed and re-targeted original with its measured value and ruling. |
| plan:355–356 | RF7 "carried as an open question at milestone close" (superseded in part, B1). |
| plan:434 | Close table reports private imports and co-change alongside SCCs (co-change removed elsewhere, C10). |
| plan:496 | RF-D13: the close table lists every original target that was missed. |
| 004:90, :130–131 | RF0 tests ceiling miss "stays listed in the close table". |
| 004:145–149 | RF0-OQ6 and OQ7 plan-text repair at close (done by e1; 005:57–58 says the close still sweeps OQ7). |
| notes/phase-RF0-spec.md:274, :373; notes/rf0-baseline.md:120, :132 | Plan-text repairs at close (predicate 5, RF-D2, RF-D8), all done by e1. |
| 006:220–221 | RF1-OQ3 meta-node exemption → close. |
| notes/phase-RF1-spec.md:684–685 | RF1 estimate overruns → close table. |
| 007:530–537, :542, :555; notes/phase-RF2-spec.md:224, :467 | RF2-OQ1 (canonical premise and "compact"), RF2-OQ3 (manifest ruling vs RF-D3), RF1-OQ3. |
| 008:397, :400 | RF3-OQ1 SCC wording; RF2-OQ1/3 and RF1-OQ3. |
| 009:327, :331 | Plan amendments reserved to close; RF4 visibility-only filesystem and shared-checking wording; RF3-OQ1; RF1 meta-node. |
| 010:194, :217, :223 | RF5 entry predicate "normative plan repair"; RF1 meta-node; RF3 SCC wording; RF4 wording. |
| 011:125, :129 | "Milestone-close wording/helper questions" stay with close. |
| 012:398, :403 | Model facade wording; 400-line target miss "stands for milestone-close plan repair". |
| 013:382 | Plan amendment integration and "required milestone-close review". |
| 014:193, :199, :216; notes/phase-RF8-spec.md:174, :186–188, :200, :209; notes/RF8-implementation-status.md:46, :57 | RF8 90/650 misses ("the close table must list original 650 and 90"); V72 hashes; primitive guard ownership; earlier RF6b/RF7 misses. |
| 015:196–198 | "Milestone close must sweep them explicitly." |
| 016:396–402, :438–442 | Combined SCC "milestone-close architecture reconciliation"; historical body/ownership, shim retirement and budget misses. |
| 017:132, :151–152 | Combined package-initializer SCC remains a close question. |

## E. Original targets missed (close-table input under RF-D13 and predicate 5)

| Phase | Original | Measured / re-target | Ruling | Source |
|---|---|---|---|---|
| RF0 | tests ≤650 lines | 666; re-target 700 | owner, RF-D13 | 004:90, :129–131 |
| RF1 | `mutations.json` est. 700 | 1,705 | owner accepted | 006:132; notes/phase-RF1-spec.md:680–685 |
| RF1 | `test_rf1_helper_pins.py` est. 350 | 535 | owner accepted | 006:133 |
| RF3 | non-relocated added ≤700 | 1,987; re-target 2,200 | delegated A6 | 008:362, :414 |
| RF4 | non-relocated ≤2,200 | 3,971; re-target 4,200 | delegated A6 | 009:311 |
| RF4 | total tests/data ≤1,800 | 3,515; re-target 3,600 | delegated A9 | 009:311 |
| RF4 | touched files 130 / docs 180 | re-target 250 / 800 | delegated A5 | 009:311; notes/phase-RF4-spec.md:132 |
| RF6b | model facade ≤400 | 758; re-target 900 | delegated A1 | 012:366 |
| RF7 | touched files ≤180 | 183; re-target 210 | delegated | 013:358 |
| RF8 | touched files ≤90 | re-target 120, then 140 | delegated A4/A6 | 014:193 |
| RF8 | non-relocated ≤650 | 1,005; re-target 1,100 | delegated A5 | 014:191 |
| RF8 | `session_v7` estimate 937 | measured 976 at base (goal ≤60 met: 58) | estimate error | 014:191 |
| RF9-ci-repair | touched paths ≤80 | exceeded; delegated 90 | delegated | 017:112–114 |

RF9 (24/25 paths, 015:105–107) and RF9-repair ("no original ceiling was missed", 016:350) report no miss.

---

## F. Close dispositions (2026-11-25)

Sections A to E above are the read-only sweep, kept as written. This section
gives each row the records left to the close, left untracked or marked
DISAGREE a disposition. "Carried" rows go to the repository owner's backlog;
none names a successor milestone yet. Plan repairs CR1 to CR13 are in the
plan's "Close repairs".

| Rows | Disposition |
|---|---|
| A3, C28 | repaired: CR7 |
| A5 | repaired: CR12. RF-D5's trigger (the first public release after RF6) has happened: 0.2.0 to 0.5.0 are published. Shim retirement still needs its own approved phase; carried |
| A6, A8, A9 | repaired: CR12 |
| A7, B1, B4 | repaired: CR1; the RF7 remainder is carried |
| A11 | repaired: CR3 |
| A13, C38 | accepted: delegated re-targets and the RF5 re-plan are listed in close-results.md as delegated, not the owner's |
| B2 | the close review is the light GND panel over record 018 |
| B3 | repaired: CR2 |
| C2 | closed: vasiloglou/gnd-public#8 is a merged pull request ("Drop whole-tree attribution from the ledger check"), checked at the close |
| C6, C15 | closed: the layering test has no xfail and every owed pin landed (006:196–216) |
| C9, C10, C12 | repaired: CR13 removes the last co-change promise; e1 had done the rest |
| C16, C18, C20, C39, C40, C47 | carried as the records carried them (session controller, session portability, media types, model queries, input-boundary hardening) |
| C17 | accepted: three exempt meta nodes narrow RF1-C1, as 006:122 recorded |
| C21 | carried: RF1-OQ7, to whichever change next edits `tests/support/rf1_pins.py` |
| C23, C24 (Q2, Q3), C48 (Souffle setuid node), C64 | carried: raised once, never owned; listed here so they are not lost |
| C26 | repaired: CR6 |
| C30 | repaired: CR8 |
| C34, C35 | repaired: CR9 |
| C37 | repaired: CR10 |
| C43 | repaired: CR11, and listed in the missed-target table |
| C45 | accepted: the historical observers stay deselected with their prior owners; they test archived bytes |
| C51 | accepted: the three V72 reader-body hashes already differed at the RF8 base |
| C52 | carried: the package-wide primitive ownership guard stays excluded; its owner is the safefs maintainer |
| C63 | owner decision C-D1 (close-results.md) |
| C65 | this section |
| C66 | carried to the source owners, as recorded |
| C67 | accepted: cloud CI is not a required check (AGENTS.md); the full lane ran on beast-3 instead |
| C68 | accepted limitation: macOS only |
| families: four never-ruled groups | owner decision C-D2 |

Every row of sections A to C not listed here is ruled, closed or historical
as its "State per records" column says.
